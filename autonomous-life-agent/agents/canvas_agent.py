"""
Module 3: Canvas LMS Agent
- Connect to Canvas at berkeley.edu via REST API
- Pull all upcoming assignments, due dates, exams
- Cross-reference with Google Calendar
- Auto-create missing events (color: Blueberry)
- Set multiple reminders per deadline
- Flag assignments due within 48 hours
"""

from datetime import datetime, timedelta, timezone
import requests
from googleapiclient.discovery import build

from agents.base_agent import BaseAgent
from auth.google_auth import get_google_credentials
from auth.canvas_auth import get_canvas_session
from config.settings import CANVAS_API_URL, CANVAS_COURSES, DRY_RUN
from utils.retry import with_retry


# Blueberry colorId for academic events
ACADEMIC_COLOR_ID = "9"

# Reminder schedule for deadlines (in minutes before)
DEADLINE_REMINDERS = [
    7 * 24 * 60,   # 1 week
    3 * 24 * 60,   # 3 days
    1 * 24 * 60,   # 1 day
    60,             # 1 hour
]


class CanvasAgent(BaseAgent):
    def __init__(self):
        super().__init__("CanvasAgent")
        self.canvas: requests.Session = get_canvas_session()
        creds = get_google_credentials()
        self.cal_service = build("calendar", "v3", credentials=creds)
        self.courses: list[dict] = []
        self.assignments: list[dict] = []

    # ── Canvas API Helpers ───────────────────────────────────────────────

    @with_retry
    def _canvas_get(self, endpoint: str, params: dict = None) -> list[dict]:
        """GET with pagination support."""
        results = []
        url = f"{CANVAS_API_URL}{endpoint}"
        while url:
            resp = self.canvas.get(url, params=params)
            resp.raise_for_status()
            results.extend(resp.json() if isinstance(resp.json(), list) else [resp.json()])
            # Canvas pagination via Link header
            links = resp.headers.get("Link", "")
            url = None
            for part in links.split(","):
                if 'rel="next"' in part:
                    url = part.split("<")[1].split(">")[0]
            params = None  # params only needed for first request
        return results

    def _fetch_courses(self) -> list[dict]:
        """Fetch active courses, filtering to our known set."""
        all_courses = self._canvas_get(
            "/courses",
            params={"enrollment_state": "active", "per_page": 50}
        )
        matched = []
        for course in all_courses:
            name = course.get("name", "") or course.get("course_code", "")
            for target in CANVAS_COURSES:
                if target.lower() in name.lower():
                    course["_matched_name"] = target
                    matched.append(course)
                    break
        self.courses = matched
        return matched

    def _fetch_assignments(self) -> list[dict]:
        """Fetch all upcoming assignments across matched courses."""
        now = datetime.now(timezone.utc)
        assignments = []
        for course in self.courses:
            try:
                course_assignments = self._canvas_get(
                    f"/courses/{course['id']}/assignments",
                    params={
                        "order_by": "due_at",
                        "per_page": 100,
                        "bucket": "upcoming",
                    }
                )
                for a in course_assignments:
                    due = a.get("due_at")
                    if due:
                        due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
                        if due_dt > now:
                            a["_course_name"] = course.get("_matched_name", course.get("name", ""))
                            a["_due_dt"] = due_dt
                            assignments.append(a)
            except Exception as e:
                self.record_error("fetch_assignments", f"Course {course.get('name')}: {e}")

        self.assignments = sorted(assignments, key=lambda a: a["_due_dt"])
        return self.assignments

    # ── Google Calendar Helpers ──────────────────────────────────────────

    def _find_academic_calendar(self) -> str | None:
        """Find or identify the primary calendar to add academic events to."""
        cals = self.cal_service.calendarList().list().execute().get("items", [])
        # Look for a calendar with a class name or use primary
        for cal in cals:
            summary = cal.get("summary", "").lower()
            for cn in CANVAS_COURSES:
                if cn.lower() in summary:
                    return cal["id"]
        return "primary"

    def _event_already_exists(self, calendar_id: str, title: str, due_dt: datetime) -> bool:
        """Check if an event with this title near this time already exists."""
        time_min = (due_dt - timedelta(hours=2)).isoformat()
        time_max = (due_dt + timedelta(hours=2)).isoformat()
        try:
            events = self.cal_service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                q=title[:30],
                singleEvents=True,
            ).execute().get("items", [])
            return len(events) > 0
        except Exception:
            return False

    @with_retry
    def _create_calendar_event(self, calendar_id: str, assignment: dict):
        """Create a calendar event for an assignment with reminders."""
        due_dt = assignment["_due_dt"]
        title = f"[{assignment['_course_name']}] {assignment.get('name', 'Assignment')}"

        if self._event_already_exists(calendar_id, title, due_dt):
            self.log.info("Event already exists: %s", title)
            return False

        event_body = {
            "summary": title,
            "description": (
                f"Canvas Assignment: {assignment.get('name')}\n"
                f"Course: {assignment['_course_name']}\n"
                f"Points: {assignment.get('points_possible', 'N/A')}\n"
                f"URL: {assignment.get('html_url', 'N/A')}"
            ),
            "start": {"dateTime": due_dt.isoformat(), "timeZone": "America/Los_Angeles"},
            "end": {
                "dateTime": (due_dt + timedelta(hours=1)).isoformat(),
                "timeZone": "America/Los_Angeles",
            },
            "colorId": ACADEMIC_COLOR_ID,
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": m} for m in DEADLINE_REMINDERS
                ],
            },
        }

        if not DRY_RUN:
            self.cal_service.events().insert(
                calendarId=calendar_id, body=event_body
            ).execute()
        self.record_action("create_event", title)
        return True

    # ── Lifecycle ────────────────────────────────────────────────────────

    def audit(self) -> dict:
        courses = self._fetch_courses()
        return {
            "matched_courses": [c.get("_matched_name") for c in courses],
            "total_canvas_courses": len(courses),
        }

    def plan(self) -> list[str]:
        self._fetch_assignments()
        actions = [
            f"Found {len(self.courses)} matching courses on Canvas",
            f"Found {len(self.assignments)} upcoming assignments/deadlines",
            "Cross-reference each with Google Calendar",
            "Create calendar events for any missing deadlines (colorId: 9 Blueberry)",
            "Set reminders: 1 week, 3 days, 1 day, 1 hour before each",
        ]

        # Flag urgent items
        now = datetime.now(timezone.utc)
        urgent = [a for a in self.assignments if a["_due_dt"] - now < timedelta(hours=48)]
        if urgent:
            for a in urgent:
                actions.append(
                    f"⚠ URGENT: '{a.get('name')}' ({a['_course_name']}) "
                    f"due {a['_due_dt'].strftime('%b %d %H:%M')}"
                )
        return actions

    def execute(self) -> dict:
        stats = {
            "courses_found": len(self.courses),
            "assignments_found": len(self.assignments),
            "events_created": 0,
            "already_existed": 0,
            "urgent_flagged": 0,
        }

        cal_id = self._find_academic_calendar()
        self.log.info("Using calendar ID: %s for academic events", cal_id)

        now = datetime.now(timezone.utc)

        for assignment in self.assignments:
            try:
                created = self._create_calendar_event(cal_id, assignment)
                if created:
                    stats["events_created"] += 1
                else:
                    stats["already_existed"] += 1

                # Flag urgent
                if assignment["_due_dt"] - now < timedelta(hours=48):
                    self.flag_for_review(
                        f"DUE WITHIN 48H: [{assignment['_course_name']}] "
                        f"{assignment.get('name')} — "
                        f"Due: {assignment['_due_dt'].strftime('%a %b %d at %I:%M %p')}"
                    )
                    stats["urgent_flagged"] += 1

            except Exception as e:
                self.record_error(
                    "create_event",
                    f"{assignment.get('name')}: {e}"
                )

        return stats
