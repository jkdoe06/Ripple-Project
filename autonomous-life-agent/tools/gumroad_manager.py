#!/usr/bin/env python3
"""
Gumroad Manager — create and manage digital product listings on Gumroad.
Used for selling study guides, templates, and digital products autonomously.

Usage:
    python gumroad_manager.py create --name "Product" --price 999 --description "..." --file "path"
    python gumroad_manager.py list
    python gumroad_manager.py sales
    python gumroad_manager.py revenue

Requires: GUMROAD_ACCESS_TOKEN env var
Get token from: https://app.gumroad.com/settings/advanced#application-form
"""

import argparse
import json
import os
import sys
from datetime import datetime

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.logger import get_logger

log = get_logger("gumroad_manager")

GUMROAD_API = "https://api.gumroad.com/v2"
TOKEN = os.getenv("GUMROAD_ACCESS_TOKEN", "")
PRODUCTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "gumroad_products.json")


def _headers():
    return {"Authorization": f"Bearer {TOKEN}"}


def _check_token():
    if not TOKEN:
        print("❌ GUMROAD_ACCESS_TOKEN not set.")
        print("   Get yours from: https://app.gumroad.com/settings/advanced#application-form")
        print("   Then: export GUMROAD_ACCESS_TOKEN=your_token")
        sys.exit(1)


def create_product(name: str, price: int, description: str, file_path: str = None):
    """Create a product on Gumroad. Price in cents (999 = $9.99)."""
    _check_token()

    data = {
        "name": name,
        "price": price,
        "description": description,
    }

    files = {}
    if file_path and os.path.exists(file_path):
        files["file"] = open(file_path, "rb")

    try:
        resp = requests.post(
            f"{GUMROAD_API}/products",
            headers=_headers(),
            data=data,
            files=files if files else None,
        )
        resp.raise_for_status()
        product = resp.json().get("product", {})

        print(f"✅ Product created: {product.get('name')}")
        print(f"   ID: {product.get('id')}")
        print(f"   URL: {product.get('short_url')}")
        print(f"   Price: ${price / 100:.2f}")

        # Save locally
        products = _load_products()
        products.append({
            "id": product.get("id"),
            "name": name,
            "price": price,
            "url": product.get("short_url"),
            "created": datetime.now().isoformat(),
            "sales": 0,
            "revenue": 0,
        })
        _save_products(products)
        return product

    except requests.HTTPError as e:
        log.error("Failed to create product: %s", e)
        print(f"❌ Failed: {e}")
    finally:
        for f in files.values():
            f.close()


def list_products():
    """List all products."""
    _check_token()
    try:
        resp = requests.get(f"{GUMROAD_API}/products", headers=_headers())
        resp.raise_for_status()
        products = resp.json().get("products", [])

        print(f"\n{'=' * 60}")
        print(f"  📦 GUMROAD PRODUCTS ({len(products)})")
        print(f"{'=' * 60}")
        for p in products:
            sales = p.get("sales_count", 0)
            revenue = p.get("sales_usd_cents", 0) / 100
            print(f"  {p.get('name', 'Unnamed'):<35} ${p.get('price', 0) / 100:>6.2f}")
            print(f"    Sales: {sales} | Revenue: ${revenue:.2f} | {p.get('short_url', '')}")
        print(f"{'=' * 60}\n")
    except requests.HTTPError as e:
        log.error("Failed to list products: %s", e)


def get_sales():
    """Get recent sales."""
    _check_token()
    try:
        resp = requests.get(f"{GUMROAD_API}/sales", headers=_headers())
        resp.raise_for_status()
        sales = resp.json().get("sales", [])

        print(f"\n{'=' * 60}")
        print(f"  💵 RECENT SALES ({len(sales)})")
        print(f"{'=' * 60}")
        total = 0
        for s in sales[:20]:
            amount = float(s.get("price", 0)) / 100
            total += amount
            print(f"  {s.get('created_at', '')[:10]}  ${amount:>7.2f}  {s.get('product_name', '')}")
        print(f"{'─' * 60}")
        print(f"  Total shown: ${total:.2f}")
        print(f"{'=' * 60}\n")
    except requests.HTTPError as e:
        log.error("Failed to get sales: %s", e)


def get_revenue():
    """Calculate total revenue."""
    _check_token()
    try:
        resp = requests.get(f"{GUMROAD_API}/products", headers=_headers())
        resp.raise_for_status()
        products = resp.json().get("products", [])

        total_sales = sum(p.get("sales_count", 0) for p in products)
        total_revenue = sum(p.get("sales_usd_cents", 0) for p in products) / 100

        print(f"\n  💰 Total Revenue: ${total_revenue:.2f} from {total_sales} sales")
        return total_revenue
    except requests.HTTPError as e:
        log.error("Failed to get revenue: %s", e)
        return 0


def _load_products() -> list:
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE) as f:
            return json.load(f)
    return []


def _save_products(products: list):
    os.makedirs(os.path.dirname(PRODUCTS_FILE), exist_ok=True)
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Gumroad Manager")
    sub = parser.add_subparsers(dest="command")

    create_p = sub.add_parser("create", help="Create a product")
    create_p.add_argument("--name", required=True)
    create_p.add_argument("--price", required=True, type=int, help="Price in cents (999 = $9.99)")
    create_p.add_argument("--description", required=True)
    create_p.add_argument("--file", help="Path to digital file to sell")

    sub.add_parser("list", help="List all products")
    sub.add_parser("sales", help="View recent sales")
    sub.add_parser("revenue", help="Total revenue")

    args = parser.parse_args()
    if args.command == "create":
        create_product(args.name, args.price, args.description, args.file)
    elif args.command == "list":
        list_products()
    elif args.command == "sales":
        get_sales()
    elif args.command == "revenue":
        get_revenue()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
