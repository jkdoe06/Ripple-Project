"""
Module 2: Google Calendar Agent
- Create Professional and Travel calendars
- Update calendar colors per specification
- Auto-categorize future events by keywords
- Add 15-min reminders to class events missing them
- Flag scheduling conflicts
"""

from datetime import datetime, timezone
from googleapiclient.discovery import build

from agents.base_agent import BaseAgent
from auth.google_auth import get_google_credentials
from config.settings import (
    CALENDAR_COLORS,
    PRIMARY_CALENDAR_COLOR,
    HOLIDAYS_CALENDAR_COLOR,
    CALENDAR_EVENT_KEYWORDS,
    DRY_RUN,
)
from utils.retry import with_retry


# Course names to match against for class events
CLASS_NAMES = ["COMPSCI 47B", "MATH 55", "SCANDIN R5B", "UGBA 135", "INDENG 162"]


class CalendarAgent(BaseAgent):
    def __init__(self):
        super().__init__("CalendarAgent")
        creds = get_google_credentials()
        self.service = build("calendar", "v3", credentials=creds)
        self.calendar_list: list[dict] = []

    # ── Helpers ──────────────────────────────────────────────────────────

    def _fetch_calendar_list(self) -> list[dict]:
        """Fetch all calendars the user has access to."""
        calendars = []
        page_token = None
        while True:
            resp = self.service.calendarList().list(pageToken=page_token).execute()
            calendars.extend(resp.get("items", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        self.calendar_list = calendars
        return calendars

    def _find_calendar_by_summary(self, summary: str) -> dict | None:
        for cal in self.calendar_list:
            if cal.get("summary", "").strip().lower() == summary.strip().lower():
                return cal
        return None

    @with_retry
    def _create_calendar(self, summary: str) -> str:
        """Create a new calendar, return its ID."""
        if DRY_RUN:
            self.log.info("[DRY RUN] Would create calendar: %s", summary)
            return "dry-run-id"
        body = {"summary": summary, "timeZone": "America/Los_Angeles"}
        result = self.service.calendars().insert(body=body).execute()
        cal_id = result["id"]
        self.record_action("create_calendar", f"{summary} → {cal_id}")
        return cal_id

    @with_retry
    def _update_calendar_color(self, calendar_id: str, color_id: str, summary: str):
        """Update a calendar's color via calendarList.patch (not events)."""
        if DRY_RUN:
            self.log.info("[DRY RUN] Would set %s to colorId %s", summary, color_id)
            return
        self.service.calendarList().patch(
            calendarId=calendar_id,
            body={"colorId": color_id},
        ).execute()
        self.record_action("update_color", f"{summary} → colorId {color_id}")

    @with_retry
    def _update_event(self, calendar_id: str, event_id: str, body: dict):
        if not DRY_RUN:
            self.service.events().patch(
                calendarId=calendar_id, eventId=event_id, body=body
            ).execute()

    def _is_class_event(self, summary: str) -> bool:
        if not summary:
            return False
        summary_lower = summary.lower()
        return any(cn.lower() in summary_lower for cn in CLASS_NAMES)

    def _categorize_event(self, summary: str) -> str | None:
        """Return target calendar name based on keywords, or None."""
        if not summary:
            return None
        text = summary.lower()
        for cal_name, keywords in CALENDAR_EVENT_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return cal_name
        return None

    # ── Lifecycle ────────────────────────────────────────────────────────

    def audit(self) -> dict:
        cals = self._fetch_calendar_list()
        return {
            "total_calendars": len(cals),
            "calendar_names": [c.get("summary", "(no name)") for c in cals],
        }

    def plan(self) -> list[str]:
        actions = []
        # Check which calendars need to be created
        for name, cfg in CALENDAR_COLORS.items():
            if cfg.get("create"):
                existing = self._find_calendar_by_summary(name)
                if not existing:
                    actions.append(f"Create calendar: {name}")
                else:
                    actions.append(f"Calendar '{name}' already exists — will update color")

        # Color updates
        for name, cfg in CALENDAR_COLORS.items():
            actions.append(f"Set '{name}' → colorId {cfg['color']}")
        actions.append(f"Set Primary → colorId {PRIMARY_CALENDAR_COLOR} (Graphite)")
        actions.append(f"Set Holidays → colorId {HOLIDAYS_CALENDAR_COLOR} (Graphite)")

        actions.append("Scan future events and auto-categorize by keywords")
        actions.append("Add 15-min reminders to class events missing them")
        actions.append("Detect and flag scheduling conflicts")
        return actions

    def execute(self) -> dict:
        stats = {
            "calendars_created": 0,
            "colors_updated": 0,
            "events_categorized": 0,
            "reminders_added": 0,
            "conflicts_found": 0,
        }

        self._fetch_calendar_list()

        # ── Step 1: Create calendars ──
        for name, cfg in CALENDAR_COLORS.items():
            if cfg.get("create"):
                existing = self._find_calendar_by_summary(name)
                if not existing:
                    cal_id = self._create_calendar(name)
                    self._update_calendar_color(cal_id, cfg["color"], name)
                    stats["calendars_created"] += 1
                    # Refresh list
                    self._fetch_calendar_list()
                else:
                    self.log.info("Calendar '%s' already exists, updating color.", name)

        # ── Step 2: Update colors ──
        for name, cfg in CALENDAR_COLORS.items():
            cal = self._find_calendar_by_summary(name)
            if cal:
                try:
                    self._update_calendar_color(cal["id"], cfg["color"], name)
                    stats["colors_updated"] += 1
                except Exception as e:
                    self.record_error("update_color", f"{name}: {e}")
            else:
                self.flag_for_review(f"Calendar not found for color update: {name}")

        # Primary calendar
        try:
            self._update_calendar_color("primary", PRIMARY_CALENDAR_COLOR, "Primary")
            stats["colors_updated"] += 1
        except Exception as e:
            self.record_error("update_color", f"Primary: {e}")

        # Holidays — find by keyword
        for cal in self.calendar_list:
            if "holiday" in cal.get("summary", "").lower():
                try:
                    self._update_calendar_color(cal["id"], HOLIDAYS_CALENDAR_COLOR, cal["summary"])
                    stats["colors_updated"] += 1
                except Exception as e:
                    self.record_error("update_color", f"Holidays: {e}")

        # ── Step 3: Scan future events ──
        now = datetime.now(timezone.utc).isoformat()
        all_events = []

        for cal in self.calendar_list:
            try:
                events_resp = self.service.events().list(
                    calendarId=cal["id"],
                    timeMin=now,
                    maxResults=250,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()
                for ev in events_resp.get("items", []):
                    ev["_source_calendar"] = cal["id"]
                    ev["_source_name"] = cal.get("summary", "")
                    all_events.append(ev)
            except Exception as e:
                self.record_error("list_events", f"{cal.get('summary')}: {e}")

        self.log.info("Found %d future events across all calendars.", len(all_events))

        # ── Step 3a: Add reminders to class events ──
        for ev in all_events:
            summary = ev.get("summary", "")
            if self._is_class_event(summary):
                reminders = ev.get("reminders", {})
                if reminders.get("useDefault", True) or not reminders.get("overrides"):
                    # Add 15-min reminder
                    try:
                        self._update_event(ev["_source_calendar"], ev["id"], {
                            "reminders": {
                                "useDefault": False,
                                "overrides": [{"method": "popup", "minutes": 15}],
                            }
                        })
                        self.record_action("add_reminder", f"15min → {summary}")
                        stats["reminders_added"] += 1
                    except Exception as e:
                        self.record_error("add_reminder", f"{summary}: {e}")

        # ── Step 3b: Auto-categorize events ──
        for ev in all_events:
            summary = ev.get("summary", "")
            target_cal_name = self._categorize_event(summary)
            if target_cal_name and ev["_source_name"].lower() != target_cal_name.lower():
                target_cal = self._find_calendar_by_summary(target_cal_name)
                if target_cal:
                    try:
                        # Move event: copy to target, delete from source
                        if not DRY_RUN:
                            self.service.events().move(
                                calendarId=ev["_source_calendar"],
                                eventId=ev["id"],
                                destination=target_cal["id"],
                            ).execute()
                        self.record_action(
                            "categorize_event",
                            f"'{summary}' → {target_cal_name}"
                        )
                        stats["events_categorized"] += 1
                    except Exception as e:
                        self.record_error("categorize_event", f"{summary}: {e}")

        # ── Step 4: Detect conflicts ──
        # Sort all events by start time and check overlaps
        timed_events = []
        for ev in all_events:
            start = ev.get("start", {}).get("dateTime")
            end = ev.get("end", {}).get("dateTime")
            if start and end:
                timed_events.append({
                    "summary": ev.get("summary", "(no title)"),
                    "start": start,
                    "end": end,
                })

        timed_events.sort(key=lambda e: e["start"])
        for i in range(len(timed_events) - 1):
            if timed_events[i]["end"] > timed_events[i + 1]["start"]:
                conflict = (
                    f"CONFLICT: '{timed_events[i]['summary']}' "
                    f"({timed_events[i]['start']} – {timed_events[i]['end']}) "
                    f"overlaps with '{timed_events[i+1]['summary']}' "
                    f"({timed_events[i+1]['start']})"
                )
                self.flag_for_review(conflict)
                stats["conflicts_found"] += 1

        return stats
