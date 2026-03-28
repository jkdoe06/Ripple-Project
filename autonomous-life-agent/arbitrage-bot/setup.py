#!/usr/bin/env python3
"""
One-Click Setup — Interactive credential wizard + dependency installer.
Run this ONCE, then use start.py to run the bot forever.

Usage:
    python setup.py
"""

import os
import subprocess
import sys
import getpass

ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")


def banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           ARBITRAGE BOT — ONE-CLICK SETUP                   ║
║           ──────────────────────────────                     ║
║  This wizard will:                                          ║
║    1. Install Python dependencies                           ║
║    2. Ask for your exchange API keys (stored locally only)  ║
║    3. Set your payout preferences                           ║
║    4. Configure safety limits                               ║
║                                                             ║
║  Nothing leaves your machine. Keys stored in .env only.     ║
╚══════════════════════════════════════════════════════════════╝
    """)


def install_deps():
    print("[1/4] Installing dependencies...")
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", req_file, "-q"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print("  ✅ Dependencies installed.\n")
    else:
        print(f"  ⚠️  pip install had issues: {result.stderr[:200]}")
        print("  Continuing anyway...\n")


def setup_exchanges() -> dict:
    print("[2/4] Exchange API Keys")
    print("  You need at least 1 exchange. For cross-exchange arb, you need 2+.")
    print("  Create API keys with TRADE permission only (never enable withdraw).\n")

    env_vars = {}

    exchanges = [
        ("Coinbase", "COINBASE", "https://www.coinbase.com/settings/api"),
        ("Kraken", "KRAKEN", "https://www.kraken.com/u/security/api"),
        ("Binance US", "BINANCEUS", "https://www.binance.us/settings/api-management"),
        ("KuCoin", "KUCOIN", "https://www.kucoin.com/account/api"),
    ]

    configured = 0
    for name, prefix, url in exchanges:
        print(f"  ── {name} ──")
        print(f"  Get keys from: {url}")
        answer = input(f"  Set up {name}? [y/N]: ").strip().lower()
        if answer != "y":
            print(f"  Skipping {name}.\n")
            continue

        api_key = getpass.getpass(f"  {name} API Key: ")
        secret = getpass.getpass(f"  {name} Secret: ")

        if api_key and secret:
            env_vars[f"{prefix}_API_KEY"] = api_key
            env_vars[f"{prefix}_SECRET"] = secret
            if name == "KuCoin":
                passphrase = getpass.getpass(f"  {name} Passphrase: ")
                env_vars[f"{prefix}_PASSPHRASE"] = passphrase
            configured += 1
            print(f"  ✅ {name} configured.\n")
        else:
            print(f"  Skipped (empty input).\n")

    if configured == 0:
        print("  ⚠️  No exchanges configured. Bot will run in scan-only mode.")
        print("  You can add keys later by editing .env\n")

    return env_vars


def setup_payout() -> dict:
    print("[3/4] Payout Preferences")
    print("  Where should profits go? (For tracking — the bot doesn't move funds off exchanges)")
    print()
    print("  Your money stays on the exchange. Withdraw manually when ready.")
    print("  We just need to know where you WANT to eventually withdraw to.\n")

    env_vars = {}

    print("  Supported payout methods:")
    print("    1. PayPal")
    print("    2. Bank account (ACH via exchange)")
    print("    3. Crypto wallet (withdraw to your own wallet)")
    print("    4. Skip for now")

    choice = input("\n  Choose [1-4]: ").strip()

    if choice == "1":
        email = input("  PayPal email: ").strip()
        env_vars["PAYOUT_METHOD"] = "paypal"
        env_vars["PAYOUT_PAYPAL_EMAIL"] = email
        print(f"  ✅ PayPal ({email}) saved for tracking.\n")
    elif choice == "2":
        env_vars["PAYOUT_METHOD"] = "bank_ach"
        print("  ✅ Bank ACH selected. Withdraw directly from your exchange.\n")
    elif choice == "3":
        wallet = input("  Wallet address (USDT/USDC): ").strip()
        env_vars["PAYOUT_METHOD"] = "crypto_wallet"
        env_vars["PAYOUT_WALLET"] = wallet
        print(f"  ✅ Crypto wallet saved.\n")
    else:
        env_vars["PAYOUT_METHOD"] = "none"
        print("  Skipped. You can set this later in .env\n")

    return env_vars


def setup_limits() -> dict:
    print("[4/4] Safety Limits")

    env_vars = {}

    print(f"  How much capital should the bot use total? (Default: $200)")
    cap = input("  Max capital [$200]: ").strip()
    env_vars["MAX_TOTAL_CAPITAL"] = cap if cap else "200"

    print(f"\n  How much per individual trade? (Default: $25)")
    trade = input("  Max per trade [$25]: ").strip()
    env_vars["MAX_TRADE_USD"] = trade if trade else "25"

    print(f"\n  Start with paper trading (fake money) first? (Recommended)")
    paper = input("  Paper trading? [Y/n]: ").strip().lower()
    env_vars["LIVE_TRADING"] = "false" if paper != "n" else "true"

    if env_vars["LIVE_TRADING"] == "true":
        print("\n  ⚠️  LIVE TRADING enabled. Real money will be used.")
        confirm = input("  Type 'CONFIRM' to proceed: ").strip()
        if confirm != "CONFIRM":
            env_vars["LIVE_TRADING"] = "false"
            print("  Switched to paper trading for safety.")

    print()
    return env_vars


def write_env(all_vars: dict):
    lines = [
        "# ══════════════════════════════════════════════════════════",
        "# Arbitrage Bot Configuration",
        f"# Generated: {__import__('datetime').datetime.now():%Y-%m-%d %H:%M}",
        "# ══════════════════════════════════════════════════════════",
        "",
    ]

    sections = {
        "Exchange Keys": ["COINBASE_", "KRAKEN_", "BINANCEUS_", "KUCOIN_"],
        "Payout": ["PAYOUT_"],
        "Trading Limits": ["MAX_", "LIVE_"],
    }

    written = set()
    for section_name, prefixes in sections.items():
        section_vars = {k: v for k, v in all_vars.items()
                        if any(k.startswith(p) for p in prefixes)}
        if section_vars:
            lines.append(f"# ── {section_name} ──")
            for k, v in section_vars.items():
                lines.append(f"{k}={v}")
                written.add(k)
            lines.append("")

    # Defaults
    lines.append("# ── Defaults ──")
    defaults = {
        "PAIRS": "BTC/USDT,ETH/USDT,SOL/USDT,XRP/USDT,DOGE/USDT,AVAX/USDT,LINK/USDT,DOT/USDT",
        "MIN_SPREAD": "0.003",
        "SCAN_INTERVAL": "5",
        "LOG_LEVEL": "INFO",
    }
    for k, v in defaults.items():
        if k not in written:
            lines.append(f"{k}={v}")

    with open(ENV_FILE, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  ✅ Configuration saved to {ENV_FILE}")
    print(f"  ⚠️  This file contains secrets — never commit it to git.\n")


def main():
    banner()
    install_deps()

    all_vars = {}
    all_vars.update(setup_exchanges())
    all_vars.update(setup_payout())
    all_vars.update(setup_limits())

    write_env(all_vars)

    print("═" * 60)
    print("  SETUP COMPLETE!")
    print("═" * 60)
    print()
    print("  To start the bot:")
    print("    python start.py          # Runs forever in foreground")
    print("    python start.py --bg     # Runs as background daemon")
    print("    python bot.py --report   # Check P&L anytime")
    print()
    print("  The bot starts in PAPER TRADING mode by default.")
    print("  Once you verify it's finding opportunities, switch to")
    print("  live trading by setting LIVE_TRADING=true in .env")
    print()


if __name__ == "__main__":
    main()
