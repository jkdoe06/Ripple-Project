#!/usr/bin/env python3
"""
Domain Scout — finds, evaluates, and manages domain name investments.
Monitors trending tech/AI terms and checks domain availability.

Usage:
    python domain_scout.py scan                    # Find opportunities
    python domain_scout.py check example.com       # Check specific domain
    python domain_scout.py portfolio               # View your portfolio
    python domain_scout.py add example.com 12.00   # Add to portfolio
"""

import argparse
import json
import os
import socket
import sys
from datetime import datetime
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.logger import get_logger

log = get_logger("domain_scout")

PORTFOLIO_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "domain_portfolio.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Valuable TLD suffixes
TLDS = [".com", ".ai", ".io", ".co", ".app", ".dev"]

# Patterns that make good domains
DOMAIN_PATTERNS = [
    "{name}ai.com", "get{name}.com", "{name}app.com", "{name}tool.com",
    "{name}.ai", "{name}.io", "use{name}.com", "try{name}.com",
    "{name}hub.com", "{name}lab.com", "{name}pro.com",
]


def check_domain_available(domain: str) -> bool:
    """Quick availability check via DNS lookup. Not registered = likely available."""
    try:
        socket.gethostbyname(domain)
        return False  # resolves = taken
    except socket.gaierror:
        return True  # doesn't resolve = possibly available


def find_trending_terms() -> list[str]:
    """Scrape trending tech/AI terms from news sources."""
    terms = []
    queries = [
        "new AI tool launch site:producthunt.com",
        "new SaaS startup launch 2026",
        "trending AI product this week",
    ]

    for query in queries:
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select(".result__title")[:5]:
                    text = result.get_text(strip=True)
                    # Extract capitalized words as potential brand names
                    words = [w.strip("()[].,!?:") for w in text.split()
                             if w[0].isupper() and len(w) >= 4 and w.isalpha()]
                    terms.extend(words)
        except Exception as e:
            log.warning("Trending scan error: %s", e)

    # Deduplicate and filter
    seen = set()
    unique = []
    for t in terms:
        lower = t.lower()
        if lower not in seen and len(lower) >= 4 and lower not in {"this", "that", "with", "from", "your", "what", "here", "they", "about"}:
            seen.add(lower)
            unique.append(lower)
    return unique[:20]


def scan_domains():
    """Full domain opportunity scan."""
    print(f"\n{'=' * 60}")
    print(f"  🌐 DOMAIN SCOUT — {datetime.now():%Y-%m-%d %H:%M}")
    print(f"{'=' * 60}\n")

    terms = find_trending_terms()
    print(f"  Found {len(terms)} trending terms: {', '.join(terms[:10])}...\n")

    opportunities = []
    for term in terms:
        for pattern in DOMAIN_PATTERNS[:4]:  # Check top 4 patterns per term
            domain = pattern.replace("{name}", term)
            available = check_domain_available(domain)
            status = "AVAILABLE" if available else "taken"
            if available:
                opp = {
                    "domain": domain,
                    "source_term": term,
                    "estimated_cost": "$8-12",
                    "potential_value": "$100-5000+",
                    "status": "available",
                    "checked": datetime.now().isoformat(),
                }
                opportunities.append(opp)
                print(f"  ✅ {domain:<30} {status}")
            else:
                log.debug("  ❌ %s — %s", domain, status)

    print(f"\n{'─' * 60}")
    print(f"  Available domains found: {len(opportunities)}")

    if opportunities:
        print(f"\n  Top opportunities:")
        for opp in opportunities[:10]:
            print(f"    • {opp['domain']:<30} (from: {opp['source_term']})")
        print(f"\n  To register: namecheap.com or Google Domains")
        print(f"  To sell: list on Afternic, Sedo, or Dan.com")

    print(f"{'=' * 60}\n")
    return opportunities


def check_specific(domain: str):
    """Check a specific domain."""
    available = check_domain_available(domain)
    print(f"  {domain}: {'✅ LIKELY AVAILABLE' if available else '❌ TAKEN'}")
    if available:
        print(f"  → Register at: https://www.namecheap.com/domains/registration/results/?domain={domain}")


def load_portfolio() -> dict:
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE) as f:
            return json.load(f)
    return {"domains": [], "total_invested": 0.0, "total_sold": 0.0}


def save_portfolio(data: dict):
    os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_to_portfolio(domain: str, cost: float):
    portfolio = load_portfolio()
    portfolio["domains"].append({
        "domain": domain,
        "cost": cost,
        "acquired": datetime.now().isoformat(),
        "status": "holding",
        "listed_on": [],
        "offers": [],
    })
    portfolio["total_invested"] += cost
    save_portfolio(portfolio)
    print(f"  ✅ Added {domain} to portfolio (cost: ${cost:.2f})")
    print(f"  Total invested: ${portfolio['total_invested']:.2f}")


def show_portfolio():
    portfolio = load_portfolio()
    domains = portfolio.get("domains", [])
    print(f"\n{'=' * 60}")
    print(f"  🌐 DOMAIN PORTFOLIO")
    print(f"{'=' * 60}")
    print(f"  Total domains: {len(domains)}")
    print(f"  Total invested: ${portfolio.get('total_invested', 0):.2f}")
    print(f"  Total sold: ${portfolio.get('total_sold', 0):.2f}")
    print(f"  Net P&L: ${portfolio.get('total_sold', 0) - portfolio.get('total_invested', 0):.2f}")
    print(f"{'─' * 60}")
    for d in domains:
        status = d.get("status", "holding")
        print(f"  {d['domain']:<30} ${d['cost']:>6.2f}  [{status}]  {d.get('acquired', '')[:10]}")
    print(f"{'=' * 60}\n")


def main():
    parser = argparse.ArgumentParser(description="Domain Scout")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("scan", help="Scan for domain opportunities")
    check_p = sub.add_parser("check", help="Check specific domain")
    check_p.add_argument("domain")
    sub.add_parser("portfolio", help="View portfolio")
    add_p = sub.add_parser("add", help="Add domain to portfolio")
    add_p.add_argument("domain")
    add_p.add_argument("cost", type=float)

    args = parser.parse_args()
    if args.command == "scan":
        scan_domains()
    elif args.command == "check":
        check_specific(args.domain)
    elif args.command == "portfolio":
        show_portfolio()
    elif args.command == "add":
        add_to_portfolio(args.domain, args.cost)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
