#!/usr/bin/env python3
"""
Live Terminal Dashboard — watch the bot in real-time.
Updates every 2 seconds with P&L, active strategies, recent trades.

Usage:
    python dashboard.py          # Live dashboard
    python dashboard.py --once   # Print once and exit
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
TRADES_FILE = os.path.join(LOGS_DIR, "trades.json")
SUMMARY_FILE = os.path.join(LOGS_DIR, "summary.json")
PID_FILE = os.path.join(LOGS_DIR, "bot.pid")

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def color_pnl(value: float) -> str:
    if value > 0:
        return f"{GREEN}+${value:.4f}{RESET}"
    elif value < 0:
        return f"{RED}-${abs(value):.4f}{RESET}"
    return f"${value:.4f}"


def is_running() -> tuple[bool, int]:
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, 0)
            return True, pid
        except OSError:
            pass
    return False, 0


def load_trades() -> list[dict]:
    if os.path.exists(TRADES_FILE):
        with open(TRADES_FILE) as f:
            return json.load(f)
    return []


def load_summary() -> dict:
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE) as f:
            return json.load(f)
    return {}


def render():
    trades = load_trades()
    summary = load_summary()
    running, pid = is_running()

    session = summary.get("session", {})
    today = summary.get("today", {})
    all_time = summary.get("all_time", {})

    # Clear screen
    print("\033[2J\033[H", end="")

    # Header
    status = f"{GREEN}RUNNING{RESET} (PID: {pid})" if running else f"{RED}STOPPED{RESET}"
    print(f"{BOLD}╔══════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}║  ARBITRAGE BOT — LIVE DASHBOARD                 {status:>15}  ║{RESET}")
    print(f"{BOLD}║  {datetime.now():%Y-%m-%d %H:%M:%S}                                           ║{RESET}")
    print(f"{BOLD}╚══════════════════════════════════════════════════════════════╝{RESET}")

    # P&L Summary
    print(f"\n{BOLD}  P&L Summary{RESET}")
    print(f"  {'─' * 56}")

    for label, data in [("Session", session), ("Today", today), ("All Time", all_time)]:
        pnl = data.get("pnl", 0)
        trades_count = data.get("trades", 0)
        win_rate = data.get("win_rate", 0)
        print(f"  {label:<10}  {color_pnl(pnl):>22}  "
              f"{trades_count:>4} trades  "
              f"{win_rate:>5.1f}% WR")

    # Strategy breakdown
    if trades:
        print(f"\n{BOLD}  Strategy Breakdown{RESET}")
        print(f"  {'─' * 56}")

        by_strat = {}
        for t in trades:
            s = t.get("strategy", "unknown")
            if s not in by_strat:
                by_strat[s] = {"count": 0, "pnl": 0, "wins": 0}
            by_strat[s]["count"] += 1
            by_strat[s]["pnl"] += t.get("profit", 0)
            if t.get("profit", 0) > 0:
                by_strat[s]["wins"] += 1

        for strat, data in sorted(by_strat.items(), key=lambda x: -x[1]["pnl"]):
            wr = (data["wins"] / data["count"] * 100) if data["count"] > 0 else 0
            print(f"  {strat:<22}  {color_pnl(data['pnl']):>22}  "
                  f"{data['count']:>4} trades  {wr:>5.1f}% WR")

    # Recent trades
    recent = trades[-10:] if trades else []
    if recent:
        print(f"\n{BOLD}  Recent Trades{RESET}")
        print(f"  {'─' * 56}")
        print(f"  {'Time':<10} {'Strategy':<18} {'Pair':<12} {'P&L':>12}")
        print(f"  {'─' * 56}")

        for t in reversed(recent):
            ts = t.get("recorded_at", t.get("timestamp", ""))
            if isinstance(ts, str):
                ts = ts[11:19] if len(ts) > 19 else ts[:8]
            else:
                ts = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

            strat = t.get("strategy", "?")[:16]
            pair = t.get("pair", "?")
            profit = t.get("profit", 0)
            pnl_str = color_pnl(profit)

            print(f"  {ts:<10} {strat:<18} {pair:<12} {pnl_str:>22}")

    # Projections
    if session.get("trades", 0) > 0 and session.get("pnl", 0) != 0:
        updated = summary.get("updated", "")
        if updated:
            print(f"\n{DIM}  Updated: {updated}{RESET}")

    # Footer
    print(f"\n{DIM}  Press Ctrl+C to exit dashboard (bot keeps running){RESET}")


def main():
    parser = argparse.ArgumentParser(description="Live Dashboard")
    parser.add_argument("--once", action="store_true", help="Print once and exit")
    args = parser.parse_args()

    if args.once:
        render()
        return

    try:
        while True:
            render()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nDashboard closed. Bot still running (check: python start.py --status)")


if __name__ == "__main__":
    main()
