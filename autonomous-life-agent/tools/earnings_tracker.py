#!/usr/bin/env python3
"""
Earnings Tracker — logs every dollar earned, categorizes, and reports.
Used by the Money Engine skill for autonomous earning tracking.

Usage:
    python earnings_tracker.py add --category textbook_arbitrage --amount 45.00 --description "Sold book"
    python earnings_tracker.py report
    python earnings_tracker.py report --period week
    python earnings_tracker.py export --format csv
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

EARNINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "earnings.json")

CATEGORIES = [
    "textbook_arbitrage",
    "wine_arbitrage",
    "electronics_arbitrage",
    "ticket_resale",
    "thrift_flipping",
    "domain_flipping",
    "digital_products",
    "freelance",
    "research_studies",
    "print_on_demand",
    "crypto_airdrops",
    "studyforge",
    "other",
]


def _load() -> dict:
    if os.path.exists(EARNINGS_FILE):
        with open(EARNINGS_FILE) as f:
            return json.load(f)
    return {
        "total_earned": 0.0,
        "total_invested": 0.0,
        "net_profit": 0.0,
        "opportunities_executed": 0,
        "opportunities_pending": [],
        "earnings_by_category": {cat: 0.0 for cat in CATEGORIES},
        "investments_by_category": {cat: 0.0 for cat in CATEGORIES},
        "transactions": [],
    }


def _save(data: dict):
    os.makedirs(os.path.dirname(EARNINGS_FILE), exist_ok=True)
    with open(EARNINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_earning(category: str, amount: float, description: str, investment: float = 0.0):
    data = _load()
    tx = {
        "id": len(data["transactions"]) + 1,
        "timestamp": datetime.now().isoformat(),
        "type": "earning",
        "category": category,
        "amount": amount,
        "investment": investment,
        "profit": amount - investment,
        "description": description,
    }
    data["transactions"].append(tx)
    data["total_earned"] += amount
    data["total_invested"] += investment
    data["net_profit"] = data["total_earned"] - data["total_invested"]
    data["opportunities_executed"] += 1
    if category in data["earnings_by_category"]:
        data["earnings_by_category"][category] += amount
    if category in data.get("investments_by_category", {}):
        data["investments_by_category"][category] += investment
    _save(data)
    print(f"✅ Logged: +${amount:.2f} ({category}) — {description}")
    print(f"   Total earned: ${data['total_earned']:.2f} | Net profit: ${data['net_profit']:.2f}")


def add_pending(opportunity: str, category: str, estimated_value: float):
    data = _load()
    data["opportunities_pending"].append({
        "added": datetime.now().isoformat(),
        "opportunity": opportunity,
        "category": category,
        "estimated_value": estimated_value,
        "status": "pending",
    })
    _save(data)
    print(f"📌 Pending: {opportunity} (est. ${estimated_value:.2f})")


def report(period: str = "all"):
    data = _load()

    if period == "week":
        cutoff = (datetime.now() - timedelta(weeks=1)).isoformat()
        txs = [t for t in data["transactions"] if t["timestamp"] >= cutoff]
        label = "Last 7 Days"
    elif period == "month":
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        txs = [t for t in data["transactions"] if t["timestamp"] >= cutoff]
        label = "Last 30 Days"
    else:
        txs = data["transactions"]
        label = "All Time"

    period_earned = sum(t["amount"] for t in txs)
    period_invested = sum(t.get("investment", 0) for t in txs)
    period_profit = period_earned - period_invested

    print(f"\n{'=' * 60}")
    print(f"  💰 EARNINGS REPORT — {label}")
    print(f"{'=' * 60}")
    print(f"  Total Earned:    ${period_earned:>10.2f}")
    print(f"  Total Invested:  ${period_invested:>10.2f}")
    print(f"  Net Profit:      ${period_profit:>10.2f}")
    print(f"  Transactions:    {len(txs):>10}")
    print(f"{'─' * 60}")

    # By category
    cat_totals = {}
    for t in txs:
        cat = t.get("category", "other")
        cat_totals[cat] = cat_totals.get(cat, 0) + t["amount"]

    if cat_totals:
        print("  By Category:")
        for cat, total in sorted(cat_totals.items(), key=lambda x: -x[1]):
            bar = "█" * int(total / max(cat_totals.values()) * 20) if cat_totals else ""
            print(f"    {cat:<25} ${total:>8.2f}  {bar}")

    # Recent transactions
    recent = txs[-10:] if txs else []
    if recent:
        print(f"\n{'─' * 60}")
        print("  Recent Transactions:")
        for t in reversed(recent):
            date = t["timestamp"][:10]
            print(f"    {date}  +${t['amount']:>7.2f}  {t['category']:<20} {t['description'][:30]}")

    # Pending opportunities
    pending = data.get("opportunities_pending", [])
    active_pending = [p for p in pending if p.get("status") == "pending"]
    if active_pending:
        print(f"\n{'─' * 60}")
        print(f"  Pending Opportunities ({len(active_pending)}):")
        est_total = sum(p["estimated_value"] for p in active_pending)
        for p in active_pending[:5]:
            print(f"    • {p['opportunity'][:50]} (est. ${p['estimated_value']:.2f})")
        print(f"    Total estimated pipeline: ${est_total:.2f}")

    print(f"\n{'=' * 60}\n")


def export_csv():
    data = _load()
    print("timestamp,type,category,amount,investment,profit,description")
    for t in data["transactions"]:
        desc = t["description"].replace(",", ";")
        print(f"{t['timestamp']},{t['type']},{t['category']},"
              f"{t['amount']},{t.get('investment', 0)},{t.get('profit', 0)},{desc}")


def main():
    parser = argparse.ArgumentParser(description="Earnings Tracker")
    sub = parser.add_subparsers(dest="command")

    add_p = sub.add_parser("add", help="Log an earning")
    add_p.add_argument("--category", required=True, choices=CATEGORIES)
    add_p.add_argument("--amount", required=True, type=float)
    add_p.add_argument("--description", required=True)
    add_p.add_argument("--investment", type=float, default=0.0)

    pending_p = sub.add_parser("pending", help="Add a pending opportunity")
    pending_p.add_argument("--opportunity", required=True)
    pending_p.add_argument("--category", required=True, choices=CATEGORIES)
    pending_p.add_argument("--estimated-value", required=True, type=float)

    report_p = sub.add_parser("report", help="View earnings report")
    report_p.add_argument("--period", choices=["week", "month", "all"], default="all")

    sub.add_parser("export", help="Export as CSV")

    args = parser.parse_args()
    if args.command == "add":
        add_earning(args.category, args.amount, args.description, args.investment)
    elif args.command == "pending":
        add_pending(args.opportunity, args.category, args.estimated_value)
    elif args.command == "report":
        report(args.period)
    elif args.command == "export":
        export_csv()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
