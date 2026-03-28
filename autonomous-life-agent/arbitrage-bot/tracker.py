"""
P&L Tracker — tracks every trade, calculates running totals,
enforces daily loss limits, and generates reports.
"""

import json
import os
import time
from datetime import datetime, timedelta
from config import MAX_DAILY_LOSS_USD, MAX_CONSECUTIVE_LOSSES, MAX_DAILY_TRADES
from logger import log

TRADES_FILE = os.path.join(os.path.dirname(__file__), "logs", "trades.json")
SUMMARY_FILE = os.path.join(os.path.dirname(__file__), "logs", "summary.json")


class PnLTracker:
    def __init__(self):
        self.trades: list[dict] = []
        self.session_start = time.time()
        self.consecutive_losses = 0
        self._load()

    def _load(self):
        if os.path.exists(TRADES_FILE):
            try:
                with open(TRADES_FILE) as f:
                    self.trades = json.load(f)
            except Exception:
                self.trades = []

    def _save(self):
        os.makedirs(os.path.dirname(TRADES_FILE), exist_ok=True)
        with open(TRADES_FILE, "w") as f:
            json.dump(self.trades, f, indent=2)

    def record_trade(self, trade: dict):
        """Record a completed trade."""
        trade["recorded_at"] = datetime.now().isoformat()
        self.trades.append(trade)
        self._save()

        profit = trade.get("profit", 0)
        if profit >= 0:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1

        # Update summary
        self._update_summary()

    def _today_trades(self) -> list[dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        return [t for t in self.trades if t.get("recorded_at", "").startswith(today)]

    def _session_trades(self) -> list[dict]:
        return [t for t in self.trades if t.get("timestamp", 0) >= self.session_start]

    def should_stop(self) -> tuple[bool, str]:
        """Check if we should stop trading (circuit breakers)."""
        today = self._today_trades()

        # Daily trade limit
        if len(today) >= MAX_DAILY_TRADES:
            return True, f"Daily trade limit reached ({MAX_DAILY_TRADES})"

        # Daily loss limit
        daily_pnl = sum(t.get("profit", 0) for t in today)
        if daily_pnl < -MAX_DAILY_LOSS_USD:
            return True, f"Daily loss limit hit (${daily_pnl:.2f} < -${MAX_DAILY_LOSS_USD})"

        # Consecutive losses
        if self.consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
            return True, f"Too many consecutive losses ({self.consecutive_losses})"

        return False, ""

    def get_stats(self) -> dict:
        """Get current session and all-time stats."""
        all_profits = [t.get("profit", 0) for t in self.trades]
        today_trades = self._today_trades()
        today_profits = [t.get("profit", 0) for t in today_trades]
        session_trades = self._session_trades()
        session_profits = [t.get("profit", 0) for t in session_trades]

        def _calc(profits):
            if not profits:
                return {"trades": 0, "pnl": 0, "wins": 0, "losses": 0, "win_rate": 0, "avg": 0}
            wins = [p for p in profits if p > 0]
            losses = [p for p in profits if p < 0]
            return {
                "trades": len(profits),
                "pnl": sum(profits),
                "wins": len(wins),
                "losses": len(losses),
                "win_rate": len(wins) / len(profits) * 100 if profits else 0,
                "avg": sum(profits) / len(profits) if profits else 0,
                "best": max(profits) if profits else 0,
                "worst": min(profits) if profits else 0,
            }

        return {
            "all_time": _calc(all_profits),
            "today": _calc(today_profits),
            "session": _calc(session_profits),
            "consecutive_losses": self.consecutive_losses,
        }

    def _update_summary(self):
        stats = self.get_stats()
        os.makedirs(os.path.dirname(SUMMARY_FILE), exist_ok=True)
        with open(SUMMARY_FILE, "w") as f:
            json.dump({
                "updated": datetime.now().isoformat(),
                **stats,
            }, f, indent=2)

    def print_report(self):
        """Print a formatted P&L report."""
        stats = self.get_stats()

        print(f"\n{'=' * 60}")
        print(f"  ARBITRAGE BOT — P&L REPORT")
        print(f"  {datetime.now():%Y-%m-%d %H:%M:%S}")
        print(f"{'=' * 60}")

        for period_name, period_key in [("Session", "session"), ("Today", "today"), ("All Time", "all_time")]:
            s = stats[period_key]
            print(f"\n  {period_name}:")
            pnl = s['pnl']
            sign = "+" if pnl >= 0 else ""
            print(f"    P&L:       {sign}${pnl:.4f}")
            print(f"    Trades:    {s['trades']} ({s['wins']}W / {s['losses']}L)")
            print(f"    Win Rate:  {s['win_rate']:.1f}%")
            print(f"    Avg Trade: ${s['avg']:.4f}")
            if s['trades'] > 0:
                print(f"    Best:      ${s['best']:.4f}")
                print(f"    Worst:     ${s['worst']:.4f}")

        print(f"\n{'─' * 60}")
        print(f"  Consecutive losses: {stats['consecutive_losses']}")

        # Extrapolate
        session = stats["session"]
        if session["trades"] > 0 and session["pnl"] > 0:
            session_elapsed = time.time() - self.session_start
            if session_elapsed > 60:
                rate_per_hour = (session["pnl"] / session_elapsed) * 3600
                rate_per_day = rate_per_hour * 24
                print(f"\n  Projected (if current rate holds):")
                print(f"    Per hour:  ${rate_per_hour:.2f}")
                print(f"    Per day:   ${rate_per_day:.2f}")
                print(f"    Per month: ${rate_per_day * 30:.2f}")

        print(f"{'=' * 60}\n")

    def get_by_strategy(self) -> dict:
        """Break down P&L by strategy."""
        by_strat = {}
        for t in self.trades:
            strat = t.get("strategy", "unknown")
            if strat not in by_strat:
                by_strat[strat] = {"trades": 0, "pnl": 0, "wins": 0}
            by_strat[strat]["trades"] += 1
            by_strat[strat]["pnl"] += t.get("profit", 0)
            if t.get("profit", 0) > 0:
                by_strat[strat]["wins"] += 1
        return by_strat
