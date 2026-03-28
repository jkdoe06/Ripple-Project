# Autonomous Life Agent

> **4-module agentic system** that organizes your Gmail, Google Calendar, Canvas LMS, and scouts income opportunities — all running autonomously with human-in-the-loop approval gates.

---

## Architecture

```
main.py (Orchestrator)
  ├── Module 1: GmailAgent
  │   └── Auto-label, trash junk, star professional, flag unreplied
  ├── Module 2: CalendarAgent
  │   └── Create calendars, set colors, add reminders, detect conflicts
  ├── Module 3: CanvasAgent
  │   └── Pull assignments, sync to Calendar, flag urgent deadlines
  └── Module 4: OpportunityAgent
      └── Search freelance gigs, evaluate arbitrage strategies, rank by ROI
```

Each module follows the **audit → plan → approve → execute → report** lifecycle.

## Quick Start

### 1. Install Dependencies

```bash
cd autonomous-life-agent
pip install -r requirements.txt
```

### 2. Set Up Google OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use existing)
3. Enable **Gmail API** and **Google Calendar API**
4. Go to **APIs & Services → Credentials**
5. Create **OAuth 2.0 Client ID** (type: Desktop App)
6. Download the JSON file
7. Save it as `credentials.json` in this directory

### 3. Set Up Canvas API Token

1. Go to [bCourses](https://bcourses.berkeley.edu)
2. Navigate to **Account → Settings → New Access Token**
3. Copy the token
4. Create a `.env` file:

```bash
cp .env.example .env
# Edit .env and paste your Canvas token
```

### 4. Run

```bash
# Interactive mode — approve each module before execution
python main.py

# Auto-approve all modules
python main.py --auto

# Run only one module
python main.py --module gmail
python main.py --module calendar
python main.py --module canvas
python main.py --module opportunity

# Preview mode — see what would happen without making changes
python main.py --dry-run
```

## Modules

### Module 1: Gmail Agent

| Action | Description |
|--------|-------------|
| **Auto-label** | Classifies emails into 7 categories: Travel, Finance, School & Greek Life, Jobs & Internships, Housing, Professional, Social |
| **Auto-trash** | Removes emails from 13 known junk senders (Babbel, Walgreens, Ryanair, etc.) |
| **Star** | Stars professional emails from real humans (not noreply/automated) |
| **Flag** | Flags emails needing a response after 48 hours without reply |
| **Protect** | Never deletes emails from VIP senders (amaris.charton@gmail.com, sigmachi.org, berkeley.edu, delta.com, booking.com) |

### Module 2: Calendar Agent

| Action | Description |
|--------|-------------|
| **Create calendars** | Professional (Basil) and Travel (Sage) |
| **Update colors** | Class calendars → Blueberry, FUN!! → Flamingo, Family → Sage, Primary/Holidays → Graphite |
| **Reminders** | Adds 15-min popup reminders to all class events |
| **Categorize** | Auto-moves events to Professional/Travel calendars by keywords |
| **Conflicts** | Detects and flags overlapping events |

### Module 3: Canvas Agent

| Action | Description |
|--------|-------------|
| **Sync courses** | SCANDIN R5B, MATH 55, INDENG 162, UGBA 135 |
| **Pull assignments** | All upcoming assignments, due dates, exams |
| **Create events** | Adds missing deadlines to Google Calendar (Blueberry) |
| **Reminders** | 1 week, 3 days, 1 day, 1 hour before each deadline |
| **Urgent alerts** | Flags anything due within 48 hours |

### Module 4: Opportunity Scout + Arbitrage Agent

| Action | Description |
|--------|-------------|
| **Web search** | Scans for freelance gigs, research studies, tutoring, beta testing |
| **Profile matching** | Scores opportunities against your skills/interests |
| **Arbitrage strategies** | Evaluates 7 real-world buy-low-sell-high strategies |
| **Top picks** | Textbook flipping, wine arbitrage, digital products, domain flipping, event tickets |
| **Safety** | Never auto-executes — presents findings for manual review |

## Safety & Rules

- Every action is logged to `logs/audit_YYYYMMDD.log`
- **Never deletes** emails from real humans or financial/travel confirmations
- **Never auto-creates** accounts on third-party platforms
- **Approval gates** before each module executes (unless `--auto`)
- **Dry run mode** available (`--dry-run`) to preview all actions
- Retries failed API calls up to 3 times with exponential backoff
- Uncertain emails are skipped and flagged for manual review

## Project Structure

```
autonomous-life-agent/
├── main.py                    # Orchestrator — entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Template for credentials
├── credentials.json           # (you provide) Google OAuth2
├── token.json                 # (auto-generated) OAuth token cache
│
├── config/
│   └── settings.py            # All rules, labels, colors, keywords
│
├── auth/
│   ├── google_auth.py         # Google OAuth2 flow
│   └── canvas_auth.py         # Canvas API token handler
│
├── agents/
│   ├── base_agent.py          # Base class: audit → plan → execute
│   ├── gmail_agent.py         # Module 1: Gmail organization
│   ├── calendar_agent.py      # Module 2: Calendar management
│   ├── canvas_agent.py        # Module 3: Canvas → Calendar sync
│   └── opportunity_agent.py   # Module 4: Income opportunity scout
│
├── utils/
│   ├── logger.py              # Audit logging (console + file)
│   └── retry.py               # Exponential backoff decorator
│
└── logs/                      # Audit logs and reports
    ├── audit_YYYYMMDD.log
    └── report_YYYYMMDD_HHMMSS.json
```

## Configuration

All rules are centralized in `config/settings.py`:

- **GMAIL_LABELS** — Label categories and classification keywords
- **AUTO_TRASH_SENDERS** — Domains to auto-trash
- **PROTECTED_SENDERS** — Domains/addresses to never delete
- **CALENDAR_COLORS** — Calendar → colorId mapping
- **CANVAS_COURSES** — Courses to sync from Canvas
- **OPPORTUNITY_SEARCH_TERMS** — Web search queries
- **ARBITRAGE_STRATEGIES** — Buy-low-sell-high opportunity database

## License

MIT
