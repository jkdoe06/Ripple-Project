#!/usr/bin/env python3
"""
Stripe Manager — create payment links and track revenue for StudyForge and other products.
Connects directly to Stripe API for autonomous payment collection.

Usage:
    python stripe_manager.py create-link --product "StudyForge Pro" --price 999 --recurring monthly
    python stripe_manager.py create-link --product "Study Guide" --price 499
    python stripe_manager.py balance
    python stripe_manager.py payouts
    python stripe_manager.py revenue

Requires: STRIPE_API_KEY env var (sk_live_... or sk_test_...)
"""

import argparse
import json
import os
import sys
from datetime import datetime

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.logger import get_logger

log = get_logger("stripe_manager")

STRIPE_API = "https://api.stripe.com/v1"
STRIPE_KEY = os.getenv("STRIPE_API_KEY", "")
LINKS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "stripe_links.json")


def _headers():
    return {"Authorization": f"Bearer {STRIPE_KEY}"}


def _check_key():
    if not STRIPE_KEY:
        print("❌ STRIPE_API_KEY not set.")
        print("   Get yours from: https://dashboard.stripe.com/apikeys")
        print("   Then: export STRIPE_API_KEY=sk_live_...")
        sys.exit(1)


def create_payment_link(product_name: str, price_cents: int, recurring: str = None):
    """Create a Stripe payment link."""
    _check_key()

    # Step 1: Create or find product
    resp = requests.post(f"{STRIPE_API}/products", headers=_headers(), data={
        "name": product_name,
    })
    resp.raise_for_status()
    product_id = resp.json()["id"]
    log.info("Product created: %s (%s)", product_name, product_id)

    # Step 2: Create price
    price_data = {
        "product": product_id,
        "unit_amount": price_cents,
        "currency": "usd",
    }
    if recurring:
        price_data["recurring[interval]"] = recurring

    resp = requests.post(f"{STRIPE_API}/prices", headers=_headers(), data=price_data)
    resp.raise_for_status()
    price_id = resp.json()["id"]

    # Step 3: Create payment link
    resp = requests.post(f"{STRIPE_API}/payment_links", headers=_headers(), data={
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": 1,
    })
    resp.raise_for_status()
    link = resp.json()

    payment_url = link.get("url", "")
    print(f"✅ Payment link created!")
    print(f"   Product: {product_name}")
    print(f"   Price: ${price_cents / 100:.2f}" + (f"/{recurring}" if recurring else ""))
    print(f"   URL: {payment_url}")
    print(f"   Share this link to collect payments.")

    # Save locally
    links = _load_links()
    links.append({
        "product": product_name,
        "price_cents": price_cents,
        "recurring": recurring,
        "url": payment_url,
        "created": datetime.now().isoformat(),
        "product_id": product_id,
        "price_id": price_id,
    })
    _save_links(links)
    return payment_url


def get_balance():
    """Check Stripe account balance."""
    _check_key()
    resp = requests.get(f"{STRIPE_API}/balance", headers=_headers())
    resp.raise_for_status()
    balance = resp.json()

    print(f"\n{'=' * 50}")
    print(f"  💳 STRIPE BALANCE")
    print(f"{'=' * 50}")
    for b in balance.get("available", []):
        print(f"  Available: ${b['amount'] / 100:.2f} {b['currency'].upper()}")
    for b in balance.get("pending", []):
        print(f"  Pending:   ${b['amount'] / 100:.2f} {b['currency'].upper()}")
    print(f"{'=' * 50}\n")


def get_payouts():
    """List recent payouts."""
    _check_key()
    resp = requests.get(f"{STRIPE_API}/payouts", headers=_headers(), params={"limit": 10})
    resp.raise_for_status()
    payouts = resp.json().get("data", [])

    print(f"\n{'=' * 50}")
    print(f"  🏦 RECENT PAYOUTS")
    print(f"{'=' * 50}")
    for p in payouts:
        date = datetime.fromtimestamp(p["arrival_date"]).strftime("%Y-%m-%d")
        print(f"  {date}  ${p['amount'] / 100:>8.2f}  {p['status']}")
    print(f"{'=' * 50}\n")


def get_revenue():
    """Calculate total revenue from charges."""
    _check_key()
    resp = requests.get(f"{STRIPE_API}/charges", headers=_headers(), params={
        "limit": 100,
    })
    resp.raise_for_status()
    charges = resp.json().get("data", [])

    total = sum(c["amount"] for c in charges if c["paid"] and not c["refunded"])
    count = sum(1 for c in charges if c["paid"] and not c["refunded"])

    print(f"\n  💰 Stripe Revenue: ${total / 100:.2f} from {count} charges")
    return total / 100


def _load_links() -> list:
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE) as f:
            return json.load(f)
    return []


def _save_links(links: list):
    os.makedirs(os.path.dirname(LINKS_FILE), exist_ok=True)
    with open(LINKS_FILE, "w") as f:
        json.dump(links, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Stripe Manager")
    sub = parser.add_subparsers(dest="command")

    create_p = sub.add_parser("create-link", help="Create payment link")
    create_p.add_argument("--product", required=True)
    create_p.add_argument("--price", required=True, type=int, help="Price in cents")
    create_p.add_argument("--recurring", choices=["month", "year"], help="Subscription interval")

    sub.add_parser("balance", help="Check balance")
    sub.add_parser("payouts", help="View payouts")
    sub.add_parser("revenue", help="Total revenue")

    args = parser.parse_args()
    if args.command == "create-link":
        create_payment_link(args.product, args.price, args.recurring)
    elif args.command == "balance":
        get_balance()
    elif args.command == "payouts":
        get_payouts()
    elif args.command == "revenue":
        get_revenue()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
