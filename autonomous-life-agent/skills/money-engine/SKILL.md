---
name: money-engine
description: Autonomous money-making engine — arbitrage scanner, freelance matcher, passive income tracker, and opportunity executor.
version: 1.0.0
metadata:
  openclaw:
    emoji: "💰"
    requires:
      bins:
        - python3
        - curl
      env:
        - STRIPE_API_KEY
      config:
        - money_engine.profile
---

# Money Engine

Autonomous income generation system. Scans for arbitrage, freelance gigs, passive income streams, and micro-earning opportunities. Tracks every dollar. Executes safe, legal opportunities with no human intervention where possible.

## Setup

```bash
pip install -r {baseDir}/../../requirements.txt
export STRIPE_API_KEY=sk_live_...  # Optional: for payment collection via Stripe
```

## Commands

### `/money-engine scan` — Full Opportunity Scan

Runs all scanners and produces a ranked report.

### `/money-engine arbitrage` — Arbitrage Opportunities Only

### `/money-engine freelance` — Freelance/Gig Scan Only

### `/money-engine passive` — Passive Income Ideas Only

### `/money-engine execute <opportunity-id>` — Execute a Specific Opportunity

### `/money-engine report` — Earnings Report

### `/money-engine track` — Update Earnings Tracker

---

## Profile

```yaml
name: UC Berkeley Undergrad
school: UC Berkeley (Spring 2026)
major_skills:
  - Python (advanced)
  - AI/ML (intermediate-advanced)
  - Data Science (intermediate)
  - Web Development (full-stack)
  - JavaScript/TypeScript
  - SQL & databases
courses: [Scandinavian R5B, Math 55, IEOR 162, Business Admin 135]
fraternity: Sigma Chi (executive leadership)
interests: [AI, electronic music, gaming, entrepreneurship]
project: StudyForge (AI study tool for Berkeley students)
location: Berkeley, CA / Bay Area
available_hours: 10-15/week
risk_tolerance: low-medium
startup_capital: $50-200
```

---

## CATEGORY 1: ARBITRAGE OPPORTUNITIES (Buy Low, Sell High)

### 1.1 Textbook Arbitrage (★★★★★ — Best for students)

**The Play:** Buy textbooks at end-of-semester for $2-15 at campus buyback/thrift. Sell on Amazon/Chegg for $30-150.

**Execution Steps:**
1. Check Berkeley ASUC Bookswap, Free & For Sale Facebook group, and campus bookstore clearance bins
2. Before buying, verify resale value:
   ```bash
   curl -s "https://www.bookscouter.com/prices/<ISBN>" | grep "best_price"
   ```
3. Only buy if resale price ≥ 3x purchase price
4. List on Amazon FBA (highest margin) or Chegg buyback (fastest payout)
5. Ship using USPS Media Mail ($3-5 for any book)

**Margin:** 200-500% per book
**Startup:** $20-50
**Time:** 2-4 hrs/week
**Risk:** Very low — books always have a floor price
**Legal:** 100% legal, standard commerce

**Best timing:** Finals week buyback (May/December), thrift store Tuesday restocks

**Auto-execute steps the agent CAN do:**
- Search current textbook prices via BookScouter API
- Monitor Berkeley Free & For Sale posts (RSS/scrape)
- Calculate profit margins automatically
- Track inventory and earnings in `{baseDir}/../../logs/earnings.json`

---

### 1.2 Wine Arbitrage (Travel-Based) (★★★★☆)

**The Play:** When traveling to wine regions, buy at local prices and bring back for resale.

**Key Routes:**

| Origin | Buy Price | US Resale | Margin |
|--------|-----------|-----------|--------|
| Burgundy, France (Pinot Noir) | €5-15/bottle | $40-120 | 300-800% |
| Bordeaux, France (Cabernet blends) | €8-20/bottle | $35-90 | 200-450% |
| Rioja, Spain (Tempranillo) | €4-10/bottle | $25-60 | 250-500% |
| Tuscany, Italy (Chianti/Brunello) | €6-18/bottle | $30-100 | 200-550% |
| Porto, Portugal (Port wine) | €5-12/bottle | $25-70 | 200-500% |
| Mendoza, Argentina (Malbec) | $3-8/bottle | $20-50 | 250-600% |

**Legal Details:**
- US Customs allows **1 liter duty-free** per person (1 standard bottle = 750ml ✓)
- Additional bottles: ~$1-2 duty per bottle (still very profitable)
- **Carry-on:** 1 bottle in carry-on is fully TSA compliant if purchased after security or packed properly
- Check-in luggage: Use wine shipping sleeves ($5 on Amazon), can bring 6+ bottles
- California allows **private sales** of wine without a license for personal collections

**Where to sell:**
- Wine collector Facebook groups
- Vivino marketplace
- Local wine bars (consignment)
- Private tastings (charge $30-50/person, pour $5 wine)
- Berkeley wine enthusiast groups

**Auto-execute steps the agent CAN do:**
- Monitor flight deals to wine regions via Google Flights API
- Track wine-searcher.com for price differentials
- Calculate per-bottle profit after duty/shipping
- Log travel dates and potential buying windows

---

### 1.3 Japanese Electronics & Collectibles Arbitrage (★★★★☆)

**The Play:** Japanese retro games, anime figures, vinyl, and limited electronics are 30-70% cheaper in Japan.

**Hot items:**

| Item | Japan Price | US eBay Price | Margin |
|------|------------|---------------|--------|
| Retro game cartridges (SNES/N64) | ¥500-3000 ($3-20) | $25-150 | 300-700% |
| Anime figures (limited) | ¥2000-8000 ($13-53) | $60-300 | 200-500% |
| Japanese vinyl records | ¥500-2000 ($3-13) | $20-80 | 300-600% |
| Pokemon cards (Japanese) | ¥300-5000 ($2-33) | $15-200 | 300-600% |
| Mechanical keyboards (Topre) | ¥15000 ($100) | $250-400 | 150-300% |

**Where to buy:** Akihabara (Tokyo), Nakano Broadway, Book Off, Hard Off, Mandarake
**Where to sell:** eBay, Mercari, r/GameSale, Depop, TCGPlayer

**Auto-execute steps:**
- Monitor eBay sold listings for trending Japanese items
- Calculate margin including shipping ($15-30 EMS from Japan)
- Track exchange rate fluctuations (JPY/USD)

---

### 1.4 Concert & Event Ticket Arbitrage (★★★★☆)

**The Play:** Buy presale tickets at face value. Resell when events sell out.

**Best for your profile:** Electronic music events (you know the market)

**Execution:**
1. Sign up for artist presale lists (Spotify fans, artist newsletters)
2. Get credit card presale codes (Amex, Chase, Citi all have different events)
3. Buy 2-4 tickets at face value when presale opens
4. List on StubHub/SeatGeek once general sale sells out
5. California has **no price cap on ticket resale** since 2019

**Hot Bay Area venues:** The Midway, Bill Graham Civic, Greek Theatre, Fox Oakland, Shoreline

**Margin:** 30-200% (varies wildly — electronic/DJ events tend to be highest)
**Risk:** Medium — event might not sell out

**Auto-execute steps:**
- Monitor Songkick/Bandsintown for new Bay Area event announcements
- Check Spotify monthly listener trends (rising = likely sellout)
- Alert when presale links become available
- Track StubHub price trends for similar past events

---

### 1.5 Thrift Store & Estate Sale Flipping (★★★★☆)

**The Play:** Bay Area thrift stores and estate sales are goldmines. Electronics, vintage clothing, mid-century furniture.

**What to look for:**

| Item | Thrift Price | Resale Price | Where to Sell |
|------|-------------|-------------|---------------|
| Vintage band tees | $3-8 | $30-150 | Depop, Grailed |
| Electronics (tested working) | $5-20 | $40-200 | eBay |
| Cast iron cookware | $5-15 | $40-120 | eBay, FB Marketplace |
| Vintage Pyrex | $2-5 | $20-80 | eBay, Etsy |
| Designer clothing (tagged) | $10-30 | $50-300 | Poshmark, The RealReal |
| Board games (complete) | $2-5 | $20-80 | eBay, BoardGameGeek |
| Vinyl records (specific artists) | $1-3 | $15-100 | Discogs |

**Bay Area spots:** Goodwill (Oakland), Out of the Closet, Salvation Army (Berkeley), Alameda Flea Market (1st Sunday), estate sales (EstateSales.net)

**Rule:** Always check eBay sold listings before buying. Use the eBay app barcode scanner in-store.

**Auto-execute steps:**
- Scrape EstateSales.net for Bay Area listings
- Monitor Goodwill auction site (shopgoodwill.com) for underpriced items
- Track trending vintage items on Depop/Grailed

---

### 1.6 Domain Name Flipping (★★★★★ — Zero physical effort)

**The Play:** Register domains related to trending AI/tech topics. Sell for 10-100x.

**Strategy:**
1. Monitor AI product launches, new startups, trending tech terms
2. Register variants: `<product>app.com`, `<product>tool.com`, `get<product>.com`, `<product>ai.com`
3. Cost: $8-12/domain on Namecheap
4. List on Afternic (auto-listed on GoDaddy), Sedo, and Flippa
5. Respond to inbound inquiries via Dan.com (handles escrow)

**Recent examples of domains that sold:**
- AI-related .com domains: $500-50,000
- SaaS-related .io domains: $200-5,000
- Crypto/Web3 domains: $100-10,000

**Auto-execute steps the agent CAN do:**
- Monitor ProductHunt, HackerNews, TechCrunch RSS for new product names
- Check domain availability via `curl "https://api.domainr.com/v2/status?domain=<name>.com"`
- Auto-register available high-value domains via Namecheap API
- List on Afternic/Sedo automatically via their APIs
- Track portfolio value and incoming offers

---

### 1.7 Sneaker & Streetwear Arbitrage (★★★☆☆)

**The Play:** Cop limited releases at retail, resell on StockX/GOAT.

**Execution:**
1. Monitor Nike SNKRS, Adidas Confirmed, Supreme drops
2. Use multiple devices/accounts for raffles (your frat brothers can help)
3. Sell immediately on StockX or GOAT while hype is high

**Margin:** 30-300% (highly variable)
**Risk:** Medium-high — not every release resells well

---

### 1.8 Course Notes & Study Guides (★★★★★ — Perfect for you)

**The Play:** You're already building StudyForge. Create premium study guides for your exact courses and sell them.

**Execution:**
1. After each exam, compile your notes into a polished PDF/Notion template
2. Price: $5-15 per guide
3. Sell via Gumroad (instant setup, keeps 10%)
4. Promote in Berkeley class group chats, Reddit r/berkeley, Greek life channels
5. **StudyForge integration:** Bundle with your AI tool

**Why this is perfect:** You already take the notes. Marginal effort to package them. Berkeley has 45,000 students.

**Margin:** Near 100% (digital product, zero COGS)
**Auto-execute steps:**
- Create Gumroad product listings via API
- Auto-generate study guide templates from Canvas assignment data
- Track sales and revenue

---

### 1.9 Micro-Freelancing (★★★★☆)

**The Play:** Quick tasks on freelance platforms matching your AI/data skills.

**Best platforms for your profile:**

| Platform | Best Tasks | Rate |
|----------|-----------|------|
| Upwork | Python/AI scripts, data analysis | $30-75/hr |
| Fiverr | ChatGPT prompt engineering, data viz | $25-100/gig |
| Contra | AI consulting, startup advising | $50-100/hr |
| Toptal | (if accepted) premium freelancing | $75-150/hr |
| DataAnnotation.tech | AI training data labeling | $20-40/hr |
| Outlier.ai | AI model evaluation | $25-50/hr |
| Scale AI | RLHF tasks | $20-40/hr |
| Remotasks | Quick data tasks | $10-25/hr |

**Auto-execute steps:**
- Monitor Upwork RSS feeds for matching jobs
- Auto-generate proposal templates based on job description
- Track applications, responses, and earnings

---

### 1.10 Paid Research Studies (★★★★☆)

**The Play:** Berkeley and Bay Area institutions constantly run paid studies.

**Where to find them:**

| Source | Typical Pay | Type |
|--------|------------|------|
| Berkeley SONA (psychology) | $15-30/hr | In-person/online |
| Prolific.co | $8-15/study | Online surveys |
| UserTesting.com | $10-60/test | Website/app testing |
| dscout | $25-200/study | Diary studies |
| Respondent.io | $75-300/study | Interviews |
| Berkeley ISSI studies | $20-50/hr | Social science |

**Auto-execute steps:**
- Monitor Prolific for new studies matching demographics
- Check Berkeley SONA for available studies
- Auto-accept high-paying studies on UserTesting
- Track completed studies and total earnings

---

### 1.11 Print-on-Demand (★★★☆☆)

**The Play:** Design Berkeley/Greek life/AI themed merchandise. Zero inventory.

**Platforms:** Redbubble, TeePublic, Merch by Amazon, Printful + Etsy
**Ideas:** "Sigma Chi" designs, Berkeley memes, AI/tech humor tees, electronic music art
**Margin:** $5-15 per sale, fully passive after upload

---

### 1.12 Crypto Airdrop Farming (★★★☆☆)

**The Play:** Interact with new DeFi protocols that haven't launched tokens yet. When they airdrop, free money.

**Strategy:**
1. Follow airdrop trackers (Airdrops.io, DeFi Llama)
2. Interact with testnets and new protocols (bridge, swap, provide liquidity)
3. Recent airdrops paid $500-10,000+ to early users

**Risk:** Time investment with no guaranteed payout
**Cost:** Gas fees ($5-50 per protocol)

---

## CATEGORY 2: AUTONOMOUS EARNING EXECUTION

These are opportunities the agent can execute with **zero human intervention** once set up.

### 2.1 Gumroad Digital Product Sales (Auto-Pilot)

Setup once, then fully autonomous:

```bash
# Create a product on Gumroad
python3 {baseDir}/../../tools/gumroad_manager.py create \
  --name "MATH 55 Complete Study Guide — Spring 2026" \
  --price 999 \
  --description "50+ pages of notes, practice problems, and exam strategies" \
  --file "/path/to/study-guide.pdf"
```

The agent monitors sales via Gumroad webhook → logs earnings automatically.

### 2.2 Stripe Payment Collection (For StudyForge)

```bash
# Create a Stripe payment link for StudyForge subscriptions
python3 {baseDir}/../../tools/stripe_manager.py create-link \
  --product "StudyForge Pro" \
  --price 999 \
  --recurring monthly
```

Stripe handles everything: payment, receipts, subscriptions. Money lands in your bank.

### 2.3 Automated Price Monitoring

The agent continuously monitors price differentials:

```bash
# Run price scanner
python3 {baseDir}/../../tools/price_scanner.py \
  --categories textbooks,domains,electronics \
  --alert-threshold 3.0  # Alert when margin ≥ 300%
```

### 2.4 Automated Domain Portfolio

```bash
# Check trending terms and available domains
python3 {baseDir}/../../tools/domain_scout.py scan
# Auto-register high-value domains
python3 {baseDir}/../../tools/domain_scout.py register --domain "example.com" --registrar namecheap
# List for sale
python3 {baseDir}/../../tools/domain_scout.py list --marketplace afternic
```

---

## CATEGORY 3: EARNINGS TRACKING

All earnings are logged to `{baseDir}/../../logs/earnings.json`:

```json
{
  "total_earned": 0.00,
  "opportunities_executed": 0,
  "opportunities_pending": [],
  "earnings_by_category": {
    "textbook_arbitrage": 0.00,
    "digital_products": 0.00,
    "freelance": 0.00,
    "research_studies": 0.00,
    "domain_flipping": 0.00,
    "ticket_resale": 0.00,
    "other": 0.00
  },
  "transactions": []
}
```

Update earnings:
```bash
python3 {baseDir}/../../tools/earnings_tracker.py add \
  --category "textbook_arbitrage" \
  --amount 45.00 \
  --description "Sold Linear Algebra textbook on Amazon"
```

View report:
```bash
python3 {baseDir}/../../tools/earnings_tracker.py report
```

---

## Safety & Legal Rules

1. **Never do anything illegal** — all strategies are standard commerce
2. **Never violate platform ToS** — read each platform's rules
3. **Never spam or scam** — all sales are of real products/services
4. **Never invest more than you can afford to lose** — cap at $200 startup
5. **Track everything** — full audit log of every action and dollar
6. **Tax awareness** — earnings over $600/year require 1099 reporting
7. **When in doubt, flag for human review** — don't auto-execute uncertain opportunities

## Cron Integration

```bash
# Full scan daily at 9am
openclaw cron add --name "Money Scan" --cron "0 9 * * *" --message "Run /money-engine scan"

# Price monitoring every 2 hours
openclaw cron add --name "Price Monitor" --cron "0 */2 * * *" --message "Run price scanner for textbooks and domains"

# Weekly earnings report on Sunday
openclaw cron add --name "Earnings Report" --cron "0 18 * * 0" --message "Run /money-engine report"
```
