# Get Paid TODAY — Quick Start

## Step 1: Gumroad (5 minutes — sells study guides for you)

1. Go to [gumroad.com](https://gumroad.com) → Sign up (free)
2. Create 5 products:

| Product | File | Price |
|---------|------|-------|
| MATH 55 Study Guide | `products/study-guides/math55-study-guide.md` | $9 |
| IEOR 162 Study Guide | `products/study-guides/ieor162-study-guide.md` | $9 |
| UGBA 135 Study Guide | `products/study-guides/ugba135-study-guide.md` | $9 |
| SCANDIN R5B Study Guide | `products/study-guides/scandinr5b-study-guide.md` | $7 |
| All 4 Bundle | Upload all 4 files | $19 |

3. For each: click "New Product" → set name/price → upload the .md file → Publish
4. Copy your product URLs into `products/studyforge-landing/index.html`

## Step 2: Share (10 minutes — gets buyers)

Post in these Berkeley channels TODAY:

**Message template (copy-paste):**
```
Hey! I made comprehensive study guides for MATH 55, IEOR 162, UGBA 135, and SCANDIN R5B.
Each one has full chapter summaries, worked examples, exam strategies, and cheat sheets.
$9 each or $19 for all 4: [your gumroad link]
Made by a Berkeley student who took the courses. Good luck on finals!
```

**Where to post:**
- [ ] Berkeley Free & For Sale (Facebook group — 30K+ members)
- [ ] r/berkeley (Reddit — time it for evening, 6-9pm)
- [ ] Class-specific group chats (Discord/GroupMe for each course)
- [ ] Sigma Chi chapter group chat
- [ ] Berkeley Panhellenic/IFC networks
- [ ] Berkeley Memes for Edgy Teens (if appropriate)

## Step 3: Landing Page (optional, 2 minutes)

Open `products/studyforge-landing/index.html` in your browser to preview.
To make it live for free:
1. Push to a GitHub repo
2. Enable GitHub Pages (Settings → Pages → Deploy from main)
3. Now you have a free URL: `yourusername.github.io/repo-name`

OR use [Netlify Drop](https://app.netlify.com/drop) — drag the folder, get a live URL instantly.

## Step 4: Stripe (if you want StudyForge subscriptions)

```bash
export STRIPE_API_KEY=sk_test_...  # from dashboard.stripe.com/apikeys
python tools/stripe_manager.py create-link \
  --product "StudyForge Pro — Monthly" \
  --price 999 \
  --recurring month
```

This gives you a payment link. Share it anywhere.

## Step 5: Domain Scout (find domains to flip)

```bash
python tools/domain_scout.py scan
```

This searches trending AI/tech terms and checks domain availability.
Register any good ones on [Namecheap](https://namecheap.com) ($8-12 each).
List on [Afternic](https://afternic.com) (auto-listed on GoDaddy marketplace).

## Step 6: Track Everything

```bash
# Log a sale
python tools/earnings_tracker.py add \
  --category digital_products \
  --amount 9.00 \
  --description "Sold MATH 55 study guide on Gumroad"

# View your earnings
python tools/earnings_tracker.py report
```

## Revenue Projections

**Conservative (just study guides):**
- 4 courses × 50-100 students per course × 10% conversion = 20-40 sales
- 20 sales × $9 avg = **$180** minimum
- Bundle buyers boost this to **$250-400**

**With promotion (Greek life + Reddit):**
- Berkeley has 45,000 students. Even 0.1% = 45 sales = **$400+**

**Recurring (StudyForge subscriptions):**
- 20 subscribers × $9.99/mo = **$200/month passive**

The study guides are done. The landing page is done. The only thing between you and money is uploading to Gumroad and posting the link.
