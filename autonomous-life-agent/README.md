# Autonomous Life Agent

> **OpenClaw-powered agentic system** that organizes your Gmail, Google Calendar, Canvas LMS, and autonomously scouts + executes income opportunities — running 24/7 with safety guardrails.

Built on [OpenClaw](https://openclaw.ai/) (247K+ GitHub stars). Uses SKILL.md agent skills, `gog` CLI for Google Workspace, Canvas REST API, and autonomous Python tools for money-making.

---

## Architecture

```
OpenClaw Gateway (ws://127.0.0.1:18789)
  │
  ├── Skill: gmail-organizer     → Auto-label, trash junk, star, flag unreplied
  ├── Skill: calendar-manager    → Create/color calendars, reminders, conflicts
  ├── Skill: canvas-sync         → Pull assignments → Calendar events
  ├── Skill: money-engine        → Arbitrage scanner, freelance, passive income
  │
  ├── Tools (Python)
  │   ├── earnings_tracker.py    → Track every dollar earned
  │   ├── price_scanner.py       → Monitor arbitrage price differentials
  │   ├── domain_scout.py        → Find & manage domain investments
  │   ├── gumroad_manager.py     → Sell digital products autonomously
  │   └── stripe_manager.py      → Collect payments via Stripe
  │
  ├── Cron Jobs (9 automated tasks)
  │   ├── Gmail organize         → every 3 hours
  │   ├── Calendar organize      → every 6 hours
  │   ├── Canvas sync            → 8am + 8pm daily
  │   ├── Money scan             → 9am daily
  │   ├── Price monitor          → every 2 hours
  │   ├── Domain scout           → 10am daily
  │   ├── Earnings report        → Sunday 6pm
  │   ├── Urgent deadline check  → every 4 hours
  │   └── Morning briefing       → 7am weekdays
  │
  └── Security
      ├── Docker sandbox (non-root)
      ├── Command allowlist/blocklist
      ├── Human-in-the-loop for financial actions
      ├── File system boundaries
      └── VirusTotal skill scanning
```

---

## Quick Start

### 1. Install OpenClaw

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

### 2. Install Google Workspace CLI (gog)

```bash
brew install steipete/tap/gogcli
gog auth login --scopes gmail,calendar
```

### 3. Install Python Tools

```bash
cd autonomous-life-agent
pip install -r requirements.txt
```

### 4. Configure Credentials

```bash
cp .env.example .env
# Edit .env with your tokens:
#   GOG_ACCOUNT, CANVAS_API_TOKEN, GUMROAD_ACCESS_TOKEN,
#   STRIPE_API_KEY, OPENCLAW_GATEWAY_PASSWORD
```

### 5. Run

```bash
# Option A: Direct (development)
openclaw gateway --port 18789 --verbose

# Option B: Docker (production, recommended for safety)
docker compose up -d

# Option C: Python orchestrator (standalone, no OpenClaw needed)
python main.py
python main.py --dry-run     # Preview mode
python main.py --module gmail # Single module
```

---

## Skills (OpenClaw SKILL.md)

### `/gmail-organizer` — Gmail Agent

| Action | Description |
|--------|-------------|
| Auto-label | 7 categories: Travel, Finance, School & Greek Life, Jobs & Internships, Housing, Professional, Social |
| Auto-trash | 13 junk sender domains |
| Star | Professional emails from real humans |
| Flag | Unreplied emails after 48 hours |
| Protect | VIP senders: amaris.charton@gmail.com, sigmachi.org, berkeley.edu, delta.com, booking.com |

### `/calendar-manager` — Calendar Agent

| Action | Description |
|--------|-------------|
| Create | Professional (Basil) + Travel (Sage) calendars |
| Colors | Classes → Blueberry, FUN!! → Flamingo, Family → Sage, Primary/Holidays → Graphite |
| Reminders | 15-min popup on all class events |
| Categorize | Auto-move events by keywords (Professional, Travel, School, Fun, Family) |
| Conflicts | Detect and flag overlapping events |
| Weekly view | `/calendar-manager week` for formatted weekly summary |
| Quick add | `/calendar-manager add <description>` for natural language event creation |

### `/canvas-sync` — Canvas Agent

| Action | Description |
|--------|-------------|
| Courses | SCANDIN R5B, MATH 55, INDENG 162, UGBA 135 |
| Sync | Pull all upcoming assignments → create Google Calendar events |
| Color | All academic deadlines → Blueberry (colorId 9) |
| Reminders | 1 week, 3 days, 1 day, 1 hour before each deadline |
| Urgent | Flag anything due within 48 hours |

### `/money-engine` — Money Engine (12 Strategies)

#### Arbitrage Opportunities

| # | Strategy | Margin | Startup | Risk |
|---|----------|--------|---------|------|
| 1 | Textbook Arbitrage | 200-500% | $20-50 | Very low |
| 2 | Wine Arbitrage (Travel) | 100-800% | $10-50/bottle | Low |
| 3 | Japanese Electronics/Collectibles | 50-700% | $50-200 | Low-Med |
| 4 | Concert/Event Tickets | 30-200% | $50-500 | Medium |
| 5 | Thrift Store/Estate Sale Flips | 100-1000% | $10-50 | Low |
| 6 | Domain Name Flipping | 500-10000% | $8-50 | Medium |
| 7 | Sneaker/Streetwear | 30-300% | $100-300 | Med-High |

#### Passive/Active Income

| # | Strategy | Rate | Effort |
|---|----------|------|--------|
| 8 | Course Notes & Study Guides (Gumroad) | $5-15/sale | Create once, sell forever |
| 9 | Micro-Freelancing (Upwork/Fiverr) | $25-100/hr | Per project |
| 10 | Paid Research Studies | $15-300/study | 1-2 hrs each |
| 11 | Print-on-Demand | $5-15/sale | Upload once |
| 12 | Crypto Airdrop Farming | $0-10,000+ | Speculative |

#### Autonomous Execution Tools

| Tool | What It Does |
|------|-------------|
| `earnings_tracker.py` | Logs every dollar, categorizes, generates reports |
| `price_scanner.py` | Monitors 6 markets for arbitrage differentials every 2 hours |
| `domain_scout.py` | Finds trending domains, checks availability, manages portfolio |
| `gumroad_manager.py` | Creates/manages digital product listings, tracks sales |
| `stripe_manager.py` | Creates payment links, tracks revenue, checks balance |

---

## Security Guardrails

This system implements all 5 layers of OpenClaw safety:

### 1. Environment Sandboxing
- Docker container with non-root user (`agent`)
- Read-only skill mounting
- Restricted tmpfs
- `no-new-privileges` security option

### 2. Permissions & Access Controls
- **Command allowlist**: only `gog`, `curl`, `python3`, `git`, `jq`, etc.
- **Command blocklist**: `rm -rf`, `sudo`, `chmod 777`, `shutdown`, etc.
- **File system boundary**: locked to project directory
- **Blocked paths**: `~/.ssh`, `~/.gnupg`, `~/.aws`, `/etc`, `/var`

### 3. Human-in-the-Loop (HITL)
Actions requiring approval (via Telegram/WhatsApp):
- Financial transactions
- Account creation
- Sending emails
- File deletion
- Domain registration
- Purchases

Auto-approved (safe actions):
- Email labeling, junk trashing
- Calendar color updates, reminder adds
- Canvas reads
- Price scanning
- Earnings logging

### 4. Skill Security
- VirusTotal scanning enabled
- Only curated skills allowed
- Unverified skills blocked

### 5. Network Hardening
- Gateway bound to `127.0.0.1` (localhost only)
- Password authentication required
- Tailscale recommended for remote access

---

## Project Structure

```
autonomous-life-agent/
├── openclaw.json              # OpenClaw config (gateway, security, cron)
├── Dockerfile                 # Docker sandbox
├── docker-compose.yml         # Production deployment
├── main.py                    # Standalone Python orchestrator
├── requirements.txt           # Python dependencies
├── .env.example               # Credential template
│
├── skills/                    # OpenClaw SKILL.md agents
│   ├── gmail-organizer/
│   │   └── SKILL.md
│   ├── calendar-manager/
│   │   └── SKILL.md
│   ├── canvas-sync/
│   │   └── SKILL.md
│   └── money-engine/
│       └── SKILL.md
│
├── agents/                    # Python agent modules (standalone mode)
│   ├── base_agent.py
│   ├── gmail_agent.py
│   ├── calendar_agent.py
│   ├── canvas_agent.py
│   └── opportunity_agent.py
│
├── tools/                     # Autonomous execution tools
│   ├── earnings_tracker.py
│   ├── price_scanner.py
│   ├── domain_scout.py
│   ├── gumroad_manager.py
│   └── stripe_manager.py
│
├── auth/                      # Authentication handlers
│   ├── google_auth.py
│   └── canvas_auth.py
│
├── config/
│   └── settings.py            # Centralized configuration
│
├── utils/
│   ├── logger.py              # Audit logging
│   └── retry.py               # Exponential backoff
│
└── logs/                      # Audit logs, reports, earnings
    ├── audit_YYYYMMDD.log
    ├── earnings.json
    ├── price_scan.json
    ├── domain_portfolio.json
    └── report_*.json
```

---

## Two Modes of Operation

| Mode | How | Best For |
|------|-----|----------|
| **OpenClaw** | `openclaw gateway` or `docker compose up` | Full autonomous 24/7 operation with cron, multi-channel messaging, HITL |
| **Standalone Python** | `python main.py` | Quick runs, testing, no OpenClaw dependency |

Both modes use the same underlying logic and configuration.

---

## License

MIT
