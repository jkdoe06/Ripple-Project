---
name: gmail-organizer
description: Autonomous Gmail organizer — auto-labels, trashes junk, stars professional emails, flags unreplied threads.
version: 1.0.0
metadata:
  openclaw:
    emoji: "📧"
    requires:
      bins:
        - gog
      env:
        - GOG_ACCOUNT
    primaryEnv: GOG_ACCOUNT
---

# Gmail Organizer

Autonomous inbox organization for Gmail. Uses `gog` CLI for all Gmail operations.

## Setup

```bash
gog auth login --scopes gmail
export GOG_ACCOUNT=you@gmail.com
```

## Behavior

When invoked (manually via `/gmail-organizer` or via cron heartbeat), perform ALL of the following steps in order. Verify each step before proceeding.

### Step 1: Ensure Labels Exist

Check for and create these labels if missing:

- `Travel`
- `Finance`
- `School & Greek Life`
- `Jobs & Internships`
- `Housing`
- `Professional`
- `Social`

Use `gog gmail labels list --json` to check existing labels, then `gog gmail labels create <name>` for any missing.

### Step 2: Auto-Trash Junk Senders

Search for and trash emails from these domains. **Never trash if sender also matches a protected domain.**

Junk domains:
- `babbel.com`, `walgreens.com`, `ryanairemail.com`, `staples.com`
- `kinguin.net`, `big5sportinggoods.com`, `skool.com`, `hostelworld.com`
- `feverup.com`, `fandango.com`, `e.goat.com`, `bandsintown.com`, `pinterest.com`

For each domain:
```bash
gog gmail messages search --query "from:@<domain>" --json
```
Then trash each message:
```bash
gog gmail messages trash <message-id>
```

### Step 3: Classify and Label Inbox Emails

Fetch recent inbox messages:
```bash
gog gmail messages search --query "in:inbox newer_than:7d" --json --max-results 100
```

Classify each email by matching subject + snippet against these keyword sets:

| Label | Keywords |
|-------|----------|
| **Travel** | flight, booking, hotel, airbnb, delta, united, reservation, itinerary, check-in, boarding pass, trip, travel |
| **Finance** | invoice, payment, bank, credit, debit, transaction, statement, venmo, zelle, paypal, tax, financial aid, scholarship, refund |
| **School & Greek Life** | berkeley, bcourses, canvas, assignment, lecture, exam, midterm, final, professor, gsi, sigma chi, fraternity, greek, chapter, rush |
| **Jobs & Internships** | internship, job, career, recruiting, handshake, linkedin, application, interview, offer, resume, hiring |
| **Housing** | lease, rent, apartment, housing, roommate, landlord, move-in, deposit, utilities |
| **Professional** | meeting, conference, networking, mentor, startup, founder, investor, pitch, studyforge, partnership |
| **Social** | party, event, hangout, dinner, lunch, concert, festival, game, tailgate |

Apply label:
```bash
gog gmail messages modify <message-id> --add-labels "<label-name>"
```

If no keywords match, **skip the email** and log it: "SKIPPED: <subject> from <sender> — no classification match"

### Step 4: Star Professional Emails from Real Humans

For emails classified as `Professional` or `Jobs & Internships`, check if the sender is a real human (NOT noreply, no-reply, notifications, mailer-daemon, donotreply):

```bash
gog gmail messages modify <message-id> --add-labels "STARRED"
```

### Step 5: Flag Unreplied Emails (48+ hours)

Search for emails older than 2 days that haven't been replied to:
```bash
gog gmail messages search --query "in:inbox older_than:2d -label:sent" --json
```

For each, check the thread for a SENT message. If no reply exists, star it and log:
"NEEDS RESPONSE: <subject> from <sender> — no reply in 48+ hours"

### Step 6: Protect VIP Senders

**NEVER delete, trash, or archive** emails from these senders/domains:
- `amaris.charton@gmail.com`
- `sigmachi.org`
- `berkeley.edu`
- `delta.com`
- `booking.com`

Always check sender against this list before any destructive action.

## Safety Rules

1. **Never delete emails from real humans** — only trash known junk domains
2. **Never delete financial or travel confirmations** — even from junk-listed domains
3. **If unsure whether an email is junk, skip it** — log for manual review
4. Before any trash/delete: verify sender is NOT in the protected list
5. Log every action taken with timestamp, message ID, subject, and action

## Cron Integration

Add to OpenClaw cron for autonomous operation:
```bash
openclaw cron add --name "Gmail Organizer" --cron "0 */3 * * *" --message "Run /gmail-organizer"
```
This runs every 3 hours.
