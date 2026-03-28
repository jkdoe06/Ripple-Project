#!/usr/bin/env python3
"""
Start Script — One command to run everything.
Runs all strategies in parallel, doesn't stop until you say so.

Usage:
    python start.py              # Run in foreground (Ctrl+C to stop)
    python start.py --bg         # Run as background daemon
    python start.py --stop       # Stop the background daemon
    python start.py --status     # Check if running + quick P&L
"""

import argparse
import asyncio
import os
import signal
import subprocess
import sys
import time

PID_FILE = os.path.join(os.path.dirname(__file__), "logs", "bot.pid")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")


def ensure_setup():
    """Check if .env exists, run setup if not."""
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_file):
        print("First run detected — launching setup wizard...\n")
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "setup.py")])
        if not os.path.exists(env_file):
            print("Setup was not completed. Exiting.")
            sys.exit(1)


def start_foreground():
    """Run the bot in foreground."""
    ensure_setup()
    print("Starting arbitrage bot (Ctrl+C to stop)...\n")
    bot_path = os.path.join(os.path.dirname(__file__), "bot.py")
    os.execv(sys.executable, [sys.executable, bot_path])


def start_background():
    """Run the bot as a background daemon."""
    ensure_setup()
    os.makedirs(LOG_DIR, exist_ok=True)

    bot_path = os.path.join(os.path.dirname(__file__), "bot.py")
    log_file = os.path.join(LOG_DIR, "daemon.log")

    with open(log_file, "a") as log_out:
        process = subprocess.Popen(
            [sys.executable, bot_path],
            stdout=log_out,
            stderr=log_out,
            start_new_session=True,
            cwd=os.path.dirname(__file__),
        )

    # Save PID
    with open(PID_FILE, "w") as f:
        f.write(str(process.pid))

    print(f"  ✅ Bot started in background (PID: {process.pid})")
    print(f"  Logs: {log_file}")
    print(f"  Stop: python start.py --stop")
    print(f"  Status: python start.py --status")


def stop_daemon():
    """Stop the background daemon."""
    if not os.path.exists(PID_FILE):
        print("  No running bot found.")
        return

    with open(PID_FILE) as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, signal.SIGTERM)
        print(f"  ✅ Bot stopped (PID: {pid})")

        # Wait for clean shutdown
        for _ in range(10):
            try:
                os.kill(pid, 0)  # Check if still running
                time.sleep(0.5)
            except OSError:
                break

    except OSError:
        print(f"  Bot was not running (PID: {pid})")

    os.remove(PID_FILE)


def check_status():
    """Check if bot is running and show quick P&L."""
    running = False
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, 0)
            running = True
        except OSError:
            pass

    if running:
        print(f"  ✅ Bot is RUNNING (PID: {pid})")
    else:
        print("  ❌ Bot is NOT running")

    # Show quick P&L
    summary_file = os.path.join(LOG_DIR, "summary.json")
    if os.path.exists(summary_file):
        import json
        with open(summary_file) as f:
            summary = json.load(f)

        session = summary.get("session", {})
        today = summary.get("today", {})
        all_time = summary.get("all_time", {})

        print(f"\n  Session P&L:  ${session.get('pnl', 0):.4f} ({session.get('trades', 0)} trades)")
        print(f"  Today P&L:    ${today.get('pnl', 0):.4f} ({today.get('trades', 0)} trades)")
        print(f"  All Time P&L: ${all_time.get('pnl', 0):.4f} ({all_time.get('trades', 0)} trades)")
        print(f"  Win Rate:     {all_time.get('win_rate', 0):.1f}%")
        print(f"  Updated:      {summary.get('updated', 'N/A')}")
    else:
        print("  No trade data yet.")

    # Tail last few log lines
    daemon_log = os.path.join(LOG_DIR, "daemon.log")
    if os.path.exists(daemon_log):
        print(f"\n  Last 5 log lines:")
        with open(daemon_log) as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(f"    {line.rstrip()}")


def main():
    parser = argparse.ArgumentParser(description="Arbitrage Bot Launcher")
    parser.add_argument("--bg", action="store_true", help="Run as background daemon")
    parser.add_argument("--stop", action="store_true", help="Stop background daemon")
    parser.add_argument("--status", action="store_true", help="Check status + P&L")
    args = parser.parse_args()

    if args.stop:
        stop_daemon()
    elif args.status:
        check_status()
    elif args.bg:
        start_background()
    else:
        start_foreground()


if __name__ == "__main__":
    main()
