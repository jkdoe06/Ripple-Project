---
name: canvas-sync
description: Canvas LMS → Google Calendar sync agent. Pulls assignments, creates calendar events, flags urgent deadlines.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🎓"
    requires:
      bins:
        - gog
        - curl
      env:
        - CANVAS_API_TOKEN
        - CANVAS_API_URL
        - GOG_ACCOUNT
    primaryEnv: CANVAS_API_TOKEN
---

# Canvas Sync

Syncs UC Berkeley Canvas LMS assignments and deadlines to Google Calendar. Uses the Canvas REST API directly with curl.

## Setup

```bash
# Canvas API token from: bcourses.berkeley.edu → Account → Settings → New Access Token
export CANVAS_API_TOKEN=your_token_here
export CANVAS_API_URL=https://bcourses.berkeley.edu/api/v1

# Google Calendar access
gog auth login --scopes calendar
export GOG_ACCOUNT=you@gmail.com
```

Verify Canvas token:
```bash
curl -s -H "Authorization: Bearer $CANVAS_API_TOKEN" "$CANVAS_API_URL/users/self" | jq '.name'
```

## Behavior

### Step 1: Fetch Active Courses

```bash
curl -s -H "Authorization: Bearer $CANVAS_API_TOKEN" \
  "$CANVAS_API_URL/courses?enrollment_state=active&per_page=50" | jq '.[].name'
```

Filter to these target courses:
- **SCANDIN R5B**
- **MATH 55**
- **INDENG 162**
- **UGBA 135**

Match by checking if the course name contains any target name (case-insensitive).

### Step 2: Fetch Upcoming Assignments

For each matched course:
```bash
curl -s -H "Authorization: Bearer $CANVAS_API_TOKEN" \
  "$CANVAS_API_URL/courses/<course_id>/assignments?order_by=due_at&per_page=100&bucket=upcoming" | \
  jq '.[] | {name, due_at, points_possible, html_url}'
```

Filter to assignments with a `due_at` in the future.

### Step 3: Cross-Reference with Google Calendar

For each assignment, check if a matching event already exists:
```bash
gog calendar events list \
  --calendar-id primary \
  --time-min "<due_date - 2h>" \
  --time-max "<due_date + 2h>" \
  --query "<assignment_name>" \
  --json
```

If an event with a similar name exists near the due date, skip it.

### Step 4: Create Missing Calendar Events

For each assignment NOT already on the calendar:

```bash
gog calendar events create \
  --calendar-id primary \
  --summary "[<COURSE_NAME>] <assignment_name>" \
  --description "Canvas Assignment: <name>\nCourse: <course>\nPoints: <points>\nURL: <html_url>" \
  --start "<due_at>" \
  --end "<due_at + 1h>" \
  --color-id 9 \
  --reminders "popup:10080,popup:4320,popup:1440,popup:60"
```

Reminder schedule (in minutes):
- `10080` = 1 week before
- `4320` = 3 days before
- `1440` = 1 day before
- `60` = 1 hour before

All academic events use **colorId 9 (Blueberry)**.

### Step 5: Flag Urgent Deadlines

Any assignment due within 48 hours from now:

**Immediately output a prominent alert:**
```
⚠️ URGENT DEADLINE:
  Course: <course_name>
  Assignment: <assignment_name>
  Due: <formatted_date_time>
  Points: <points>
  URL: <canvas_url>
```

### Step 6: Summary

Output a summary:
```
Canvas Sync Complete:
  Courses found: X
  Assignments scanned: X
  New events created: X
  Already on calendar: X
  Urgent (due <48h): X
```

## Canvas API Pagination

Canvas uses Link header pagination. If the response includes a `Link` header with `rel="next"`, follow it:

```bash
# Check for next page
next_url=$(curl -sI -H "Authorization: Bearer $CANVAS_API_TOKEN" "$url" | grep -i 'rel="next"' | sed 's/.*<\(.*\)>.*/\1/')
```

Continue fetching until no next page exists.

## Safety Rules

1. Never modify or submit assignments — read-only Canvas access
2. Don't create duplicate calendar events — always check first
3. If Canvas API returns an error, log it and continue with other courses
4. All times are in Pacific Time (America/Los_Angeles)

## Cron Integration

```bash
# Sync every 12 hours
openclaw cron add --name "Canvas Sync" --cron "0 8,20 * * *" --message "Run /canvas-sync"

# Urgent deadline check every 4 hours
openclaw cron add --name "Canvas Urgent" --cron "0 */4 * * *" --message "Check Canvas for assignments due within 48 hours"
```
