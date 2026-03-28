---
name: calendar-manager
description: General-purpose Google Calendar manager — creates calendars, sets colors, adds reminders, detects conflicts, auto-categorizes events.
version: 1.0.0
metadata:
  openclaw:
    emoji: "📅"
    requires:
      bins:
        - gog
      env:
        - GOG_ACCOUNT
    primaryEnv: GOG_ACCOUNT
---

# Calendar Manager

General-purpose Google Calendar organization and automation. Works with any Google account, auto-adapts to whatever calendars you have.

## Setup

```bash
gog auth login --scopes calendar
export GOG_ACCOUNT=you@gmail.com
```

## Commands

### `/calendar-manager setup` — First-Time Setup

Run the full initial setup sequence:

#### 1. Audit Existing Calendars

```bash
gog calendar list --json
```

List all calendars with their current IDs, names, and colors. Present to user before making changes.

#### 2. Create Missing Calendars

Create these calendars if they don't already exist:

| Calendar | Color | colorId |
|----------|-------|---------|
| Professional | Basil | 10 |
| Travel | Sage | 2 |

```bash
gog calendar create --summary "Professional" --timezone "America/Los_Angeles"
gog calendar update <calendar-id> --color-id 10
```

```bash
gog calendar create --summary "Travel" --timezone "America/Los_Angeles"
gog calendar update <calendar-id> --color-id 2
```

#### 3. Update Calendar Colors

Update existing calendars to their target colors. Use the calendarList PATCH endpoint (not events).

| Calendar | Target Color | colorId |
|----------|-------------|---------|
| COMPSCI 47B | Blueberry | 9 |
| MATH 55 | Blueberry | 9 |
| SCANDIN R5B | Blueberry | 9 |
| UGBA 135 | Blueberry | 9 |
| INDENG 162 | Blueberry | 9 |
| FUN!! | Flamingo | 4 |
| Family | Sage | 2 |
| Primary | Graphite | 8 |
| Holidays | Graphite | 8 |

For each:
```bash
gog calendar update <calendar-id> --color-id <colorId>
```

If a calendar isn't found by exact name, try fuzzy matching and ask user to confirm.

### `/calendar-manager organize` — Ongoing Organization

Run this on a schedule or manually to keep calendars organized.

#### 1. Auto-Categorize Future Events

Fetch all future events:
```bash
gog calendar events list --time-min "now" --max-results 250 --json
```

Move events to the right calendar based on keywords:

| Target Calendar | Keywords |
|----------------|----------|
| Professional | meeting, interview, networking, conference, pitch, startup, studyforge, mentor, office hours, career fair, 1:1, standup, sync, demo |
| Travel | flight, airport, hotel, trip, travel, vacation, road trip, airbnb, check-in, departure, arrival, layover |
| School & Greek Life | class, lecture, section, lab, exam, midterm, final, study group, sigma chi, chapter, rush, philanthropy |
| FUN!! | party, concert, festival, game, tailgate, hangout, dinner, brunch, hike, beach, bar, club, rave |
| Family | family, mom, dad, brother, sister, thanksgiving, christmas, birthday |

To move an event between calendars:
```bash
gog calendar events move <event-id> --from <source-calendar-id> --to <target-calendar-id>
```

#### 2. Add Reminders to Class Events

For any event matching a course name (COMPSCI, MATH, SCANDIN, UGBA, INDENG) that has only default reminders, update:
```bash
gog calendar events update <event-id> --reminders "popup:15"
```

#### 3. Detect Scheduling Conflicts

Compare all events sorted by start time. If event A's end time > event B's start time, flag:

"CONFLICT: '<Event A>' (start–end) overlaps with '<Event B>' (start–end)"

Present all conflicts to the user.

### `/calendar-manager add` — Quick Add Event

Usage: `/calendar-manager add <natural language description>`

Parse the description and create an event on the appropriate calendar based on keywords. Use `gog calendar events create` with appropriate fields.

### `/calendar-manager week` — Weekly Summary

Show a formatted summary of the current week's events across all calendars, grouped by day.

## Google Calendar Color Reference

| colorId | Name | Hex |
|---------|------|-----|
| 1 | Lavender | #7986cb |
| 2 | Sage | #33b679 |
| 3 | Grape | #8e24aa |
| 4 | Flamingo | #e67c73 |
| 5 | Banana | #f6c026 |
| 6 | Tangerine | #f5511d |
| 7 | Peacock | #039be5 |
| 8 | Graphite | #616161 |
| 9 | Blueberry | #3f51b5 |
| 10 | Basil | #0b8043 |
| 11 | Tomato | #d60000 |

## Safety Rules

1. Never delete events without user confirmation
2. Before moving an event, verify the target calendar exists
3. Log every action with event title, source calendar, and destination
4. If unsure about categorization, leave the event where it is and flag it

## Cron Integration

```bash
# Run organization every 6 hours
openclaw cron add --name "Calendar Organize" --cron "0 */6 * * *" --message "Run /calendar-manager organize"

# Morning briefing at 7am
openclaw cron add --name "Calendar Brief" --cron "0 7 * * *" --message "Run /calendar-manager week"
```
