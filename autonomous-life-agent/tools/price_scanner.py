#!/usr/bin/env python3
"""
Price Scanner — monitors price differentials across markets for arbitrage.
Scans textbooks, domains, electronics, and event tickets.

Usage:
    python price_scanner.py --categories textbooks,domains
    python price_scanner.py --categories all --alert-threshold 3.0
"""

import argparse
import json
import os
import sys
from datetime import datetime
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.logger import get_logger

log = get_logger("price_scanner")

RESULTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "price_scan.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def scan_textbooks() -> list[dict]:
    """Scan for textbook arbitrage opportunities."""
    log.info("Scanning textbook prices...")
    opportunities = []

    # High-value textbook ISBNs commonly used at Berkeley
    # In production, these would come from Canvas course syllabi
    sample_searches = [
        "linear algebra UC Berkeley textbook",
        "operations research textbook IEOR",
        "business administration strategy textbook",
        "scandinavian literature textbook",
        "calculus multivariable textbook Berkeley",
    ]

    for query in sample_searches:
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query + ' used cheap')}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select(".result__body")[:3]:
                    title = result.select_one(".result__title")
                    snippet = result.select_one(".result__snippet")
                    if title:
                        opportunities.append({
                            "type": "textbook",
                            "title": title.get_text(strip=True)[:100],
                            "snippet": snippet.get_text(strip=True)[:200] if snippet else "",
                            "query": query,
                            "timestamp": datetime.now().isoformat(),
                        })
        except Exception as e:
            log.warning("Textbook scan error for '%s': %s", query, e)

    return opportunities


def scan_domains() -> list[dict]:
    """Scan for trending terms that might make valuable domains."""
    log.info("Scanning domain opportunities...")
    opportunities = []

    trending_queries = [
        "new AI startup launch 2026",
        "trending tech product launch this week",
        "new SaaS tool announcement",
    ]

    for query in trending_queries:
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select(".result__body")[:3]:
                    title = result.select_one(".result__title")
                    if title:
                        text = title.get_text(strip=True)
                        # Extract potential product names (capitalized words)
                        words = [w for w in text.split() if w[0].isupper() and len(w) > 3]
                        for word in words[:2]:
                            domain = f"{word.lower()}.com"
                            opportunities.append({
                                "type": "domain",
                                "domain": domain,
                                "source": text[:80],
                                "action": f"Check availability: whois {domain}",
                                "estimated_value": "$100-5000 if relevant",
                                "cost": "$8-12 to register",
                                "timestamp": datetime.now().isoformat(),
                            })
        except Exception as e:
            log.warning("Domain scan error: %s", e)

    return opportunities


def scan_events() -> list[dict]:
    """Scan for upcoming Bay Area events that might sell out."""
    log.info("Scanning event ticket opportunities...")
    opportunities = []

    event_queries = [
        "Bay Area electronic music event 2026 tickets",
        "San Francisco concert sold out soon",
        "Oakland festival tickets on sale",
    ]

    for query in event_queries:
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select(".result__body")[:3]:
                    title = result.select_one(".result__title")
                    snippet = result.select_one(".result__snippet")
                    if title:
                        opportunities.append({
                            "type": "event_ticket",
                            "event": title.get_text(strip=True)[:100],
                            "details": snippet.get_text(strip=True)[:200] if snippet else "",
                            "action": "Check if presale available, estimate sellout probability",
                            "timestamp": datetime.now().isoformat(),
                        })
        except Exception as e:
            log.warning("Event scan error: %s", e)

    return opportunities


def scan_thrift() -> list[dict]:
    """Scan for upcoming estate sales and thrift store opportunities."""
    log.info("Scanning estate sales and thrift opportunities...")
    opportunities = []

    queries = [
        "estate sale Berkeley Oakland this weekend",
        "garage sale Bay Area electronics",
    ]

    for query in queries:
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select(".result__body")[:3]:
                    title = result.select_one(".result__title")
                    snippet = result.select_one(".result__snippet")
                    if title:
                        opportunities.append({
                            "type": "thrift_estate",
                            "listing": title.get_text(strip=True)[:100],
                            "details": snippet.get_text(strip=True)[:200] if snippet else "",
                            "action": "Check listings for high-value items",
                            "timestamp": datetime.now().isoformat(),
                        })
        except Exception as e:
            log.warning("Thrift scan error: %s", e)

    return opportunities


def scan_freelance() -> list[dict]:
    """Scan for freelance gigs matching profile."""
    log.info("Scanning freelance opportunities...")
    opportunities = []

    queries = [
        "python AI freelance gig Upwork new",
        "data science freelance task quick",
        "prompt engineering freelance",
        "web scraping freelance project",
        "AI model evaluation paid task",
    ]

    for query in queries:
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select(".result__body")[:3]:
                    title = result.select_one(".result__title")
                    snippet = result.select_one(".result__snippet")
                    link = result.select_one(".result__url")
                    if title:
                        opportunities.append({
                            "type": "freelance",
                            "title": title.get_text(strip=True)[:100],
                            "details": snippet.get_text(strip=True)[:200] if snippet else "",
                            "url": link.get_text(strip=True) if link else "",
                            "timestamp": datetime.now().isoformat(),
                        })
        except Exception as e:
            log.warning("Freelance scan error: %s", e)

    return opportunities


def scan_research_studies() -> list[dict]:
    """Scan for paid research studies."""
    log.info("Scanning paid research studies...")
    opportunities = []

    queries = [
        "paid research study UC Berkeley 2026",
        "Prolific academic study sign up",
        "UserTesting new tests available",
        "Respondent.io paid interview technology",
    ]

    for query in queries:
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select(".result__body")[:3]:
                    title = result.select_one(".result__title")
                    snippet = result.select_one(".result__snippet")
                    if title:
                        opportunities.append({
                            "type": "research_study",
                            "title": title.get_text(strip=True)[:100],
                            "details": snippet.get_text(strip=True)[:200] if snippet else "",
                            "timestamp": datetime.now().isoformat(),
                        })
        except Exception as e:
            log.warning("Research study scan error: %s", e)

    return opportunities


def run_scan(categories: list[str], alert_threshold: float = 3.0):
    all_opportunities = []

    scanners = {
        "textbooks": scan_textbooks,
        "domains": scan_domains,
        "events": scan_events,
        "thrift": scan_thrift,
        "freelance": scan_freelance,
        "research": scan_research_studies,
    }

    if "all" in categories:
        categories = list(scanners.keys())

    for cat in categories:
        if cat in scanners:
            results = scanners[cat]()
            all_opportunities.extend(results)
            log.info("  %s: %d opportunities found", cat, len(results))

    # Save results
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    scan_result = {
        "scan_time": datetime.now().isoformat(),
        "categories_scanned": categories,
        "total_opportunities": len(all_opportunities),
        "opportunities": all_opportunities,
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(scan_result, f, indent=2)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"  🔍 PRICE SCAN COMPLETE — {datetime.now():%Y-%m-%d %H:%M}")
    print(f"{'=' * 60}")
    print(f"  Categories scanned: {', '.join(categories)}")
    print(f"  Total opportunities: {len(all_opportunities)}")
    print(f"{'─' * 60}")

    by_type = {}
    for opp in all_opportunities:
        t = opp.get("type", "other")
        by_type[t] = by_type.get(t, 0) + 1

    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t:<20} {count} opportunities")

    print(f"\n  Results saved to: {RESULTS_FILE}")
    print(f"{'=' * 60}\n")

    return all_opportunities


def main():
    parser = argparse.ArgumentParser(description="Price Scanner")
    parser.add_argument("--categories", default="all",
                        help="Comma-separated: textbooks,domains,events,thrift,freelance,research,all")
    parser.add_argument("--alert-threshold", type=float, default=3.0,
                        help="Alert when margin >= this multiplier")
    args = parser.parse_args()

    categories = [c.strip() for c in args.categories.split(",")]
    run_scan(categories, args.alert_threshold)


if __name__ == "__main__":
    main()
