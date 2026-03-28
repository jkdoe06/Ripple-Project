#!/usr/bin/env python3
"""
Arbitrage Bot — Main Runner
=============================
Runs 24/7, scanning all five strategies in parallel:
  1. Cross-exchange arbitrage (buy low on A, sell high on B)
  2. Triangular arbitrage (3-pair loops on one exchange)
  3. Spread scalping (wide spread → buy bid, sell ask)
  4. Stablecoin depeg (buy depegged stables, sell premiums)
  5. Micro-momentum (ride short-term price spikes)

Usage:
    python bot.py                # Run with paper trading (default)
    python bot.py --live         # Real money (careful!)
    python bot.py --report       # Show P&L report and exit
    python bot.py --scan-only    # Scan for opportunities, don't execute

Runs forever until Ctrl+C or circuit breaker trips.
"""

import argparse
import asyncio
import os
import signal
import sys
import time
from datetime import datetime

from config import (
    SCAN_INTERVAL, LIVE_TRADING, MAX_TRADE_USD,
    COOLDOWN_AFTER_TRADE, PAIRS,
)
from exchanges.manager import ExchangeManager
from strategies.cross_exchange import CrossExchangeStrategy
from strategies.triangular import TriangularStrategy
from strategies.spread_scalp import SpreadScalpStrategy
from strategies.stablecoin_depeg import StablecoinDepegStrategy
from strategies.momentum import MomentumStrategy
from tracker import PnLTracker
from logger import log


class ArbitrageBot:
    def __init__(self, scan_only: bool = False):
        self.manager = ExchangeManager()
        self.tracker = PnLTracker()
        self.scan_only = scan_only
        self.running = True
        self.scan_count = 0
        self.trade_count = 0

        # Strategies
        self.cross_exchange = None
        self.triangular = None
        self.spread_scalp = None
        self.stablecoin_depeg = None
        self.momentum = None

    async def start(self):
        """Initialize exchanges and start the main loop."""
        self._print_banner()

        # Connect to exchanges
        log.info("Connecting to exchanges...")
        await self.manager.connect_all()

        if not self.manager.exchanges:
            log.error("No exchanges connected. Set API keys in .env")
            return

        # Fetch initial balances
        await self.manager.fetch_balances()
        self._print_balances()

        # Initialize all 5 strategies
        self.cross_exchange = CrossExchangeStrategy(self.manager)
        self.triangular = TriangularStrategy(self.manager)
        self.spread_scalp = SpreadScalpStrategy(self.manager)
        self.stablecoin_depeg = StablecoinDepegStrategy(self.manager)
        self.momentum = MomentumStrategy(self.manager)

        log.info("Bot started — 5 strategies running in parallel")
        log.info("Scanning every %ds. Mode: %s",
                 SCAN_INTERVAL, "LIVE" if LIVE_TRADING else "PAPER")
        log.info("Monitoring %d pairs across %d exchanges",
                 len(PAIRS), len(self.manager.exchanges))
        log.info("Strategies: CrossExchange | Triangular | SpreadScalp | StablecoinDepeg | Momentum")
        log.info("Max per trade: $%.2f | Min spread: %.2f%%",
                 MAX_TRADE_USD, 0.3)

        # Main loop
        try:
            while self.running:
                await self._scan_cycle()
                self.scan_count += 1

                # Check circuit breakers
                should_stop, reason = self.tracker.should_stop()
                if should_stop:
                    log.warning("CIRCUIT BREAKER: %s", reason)
                    log.info("Bot pausing for 1 hour...")
                    await asyncio.sleep(3600)
                    self.tracker.consecutive_losses = 0
                    continue

                # Print periodic status
                if self.scan_count % 60 == 0:  # Every ~5 minutes
                    self._print_status()

                if self.scan_count % 720 == 0:  # Every ~1 hour
                    self.tracker.print_report()
                    await self.manager.fetch_balances()

                await asyncio.sleep(SCAN_INTERVAL)

        except asyncio.CancelledError:
            pass
        finally:
            log.info("Shutting down...")
            self.tracker.print_report()
            await self.manager.close_all()

    async def _scan_cycle(self):
        """Run one full scan cycle across ALL 5 strategies in parallel."""
        best_opportunity = None
        best_profit = 0
        best_strategy = None

        # ── Manage existing momentum positions first ──
        try:
            closed_positions = await self.momentum.manage_positions()
            for pos in closed_positions:
                if "profit" in pos:
                    self.tracker.record_trade(pos)
                    self.trade_count += 1
        except Exception as e:
            log.debug("Momentum position management error: %s", e)

        # ── Strategy 1: Cross-exchange ──
        if len(self.manager.exchanges) >= 2:
            try:
                opps = await self.cross_exchange.scan()
                if opps and opps[0].estimated_profit_usd > best_profit:
                    best_profit = opps[0].estimated_profit_usd
                    best_opportunity = opps[0]
                    best_strategy = "cross_exchange"
            except Exception as e:
                log.debug("Cross-exchange scan error: %s", e)

        # ── Strategy 2: Triangular ──
        try:
            opps = await self.triangular.scan()
            if opps and opps[0].profit > best_profit:
                best_profit = opps[0].profit
                best_opportunity = opps[0]
                best_strategy = "triangular"
        except Exception as e:
            log.debug("Triangular scan error: %s", e)

        # ── Strategy 3: Spread scalp ──
        try:
            opps = await self.spread_scalp.scan()
            if opps and opps[0].estimated_profit > best_profit:
                best_profit = opps[0].estimated_profit
                best_opportunity = opps[0]
                best_strategy = "spread_scalp"
        except Exception as e:
            log.debug("Spread scalp scan error: %s", e)

        # ── Strategy 4: Stablecoin depeg ──
        try:
            opps = await self.stablecoin_depeg.scan()
            if opps and opps[0].estimated_profit > best_profit:
                best_profit = opps[0].estimated_profit
                best_opportunity = opps[0]
                best_strategy = "stablecoin_depeg"
        except Exception as e:
            log.debug("Stablecoin depeg scan error: %s", e)

        # ── Strategy 5: Momentum ──
        try:
            signals = await self.momentum.scan()
            if signals and signals[0].estimated_profit > best_profit:
                best_profit = signals[0].estimated_profit
                best_opportunity = signals[0]
                best_strategy = "momentum"
        except Exception as e:
            log.debug("Momentum scan error: %s", e)

        # ── Execute best opportunity ──
        if best_opportunity and not self.scan_only:
            log.info("Best opportunity: %s (est $%.4f profit)", best_strategy, best_profit)

            result = None
            if best_strategy == "cross_exchange":
                result = await self.cross_exchange.execute(best_opportunity)
            elif best_strategy == "triangular":
                result = await self.triangular.execute(best_opportunity)
            elif best_strategy == "spread_scalp":
                result = await self.spread_scalp.execute(best_opportunity)
            elif best_strategy == "stablecoin_depeg":
                result = await self.stablecoin_depeg.execute(best_opportunity)
            elif best_strategy == "momentum":
                result = await self.momentum.execute(best_opportunity)

            if result and "profit" in result:
                self.tracker.record_trade(result)
                self.trade_count += 1
                await asyncio.sleep(COOLDOWN_AFTER_TRADE)

    def _print_banner(self):
        mode = "LIVE TRADING" if LIVE_TRADING else "PAPER TRADING"
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║              ARBITRAGE BOT v1.0                             ║
║              ─────────────────                              ║
║  Cross-Exchange · Triangular · Spread Scalping              ║
║  Mode: {mode:<20}                              ║
╚══════════════════════════════════════════════════════════════╝
        """)

    def _print_balances(self):
        print(f"\n{'─' * 50}")
        print("  Exchange Balances:")
        for ex_name, balances in self.manager.balances.items():
            total_usd = 0
            for currency, amount in balances.items():
                if currency in ("USDT", "USD", "USDC", "BUSD"):
                    total_usd += amount
            print(f"    {ex_name}: ~${total_usd:.2f} available")
            for currency, amount in list(balances.items())[:5]:
                print(f"      {currency}: {amount:.6f}")
        print(f"{'─' * 50}\n")

    def _print_status(self):
        stats = self.tracker.get_stats()
        session = stats["session"]
        pnl = session["pnl"]
        sign = "+" if pnl >= 0 else ""
        log.info(
            "STATUS | Scans: %d | Trades: %d | Session P&L: %s$%.4f | "
            "Win Rate: %.0f%% | Consecutive Losses: %d",
            self.scan_count, session["trades"], sign, pnl,
            session["win_rate"], stats["consecutive_losses"],
        )

    def stop(self):
        self.running = False


async def main():
    parser = argparse.ArgumentParser(description="Arbitrage Bot")
    parser.add_argument("--live", action="store_true", help="Enable live trading")
    parser.add_argument("--report", action="store_true", help="Show P&L report and exit")
    parser.add_argument("--scan-only", action="store_true", help="Scan without executing")
    args = parser.parse_args()

    if args.report:
        tracker = PnLTracker()
        tracker.print_report()
        return

    if args.live:
        os.environ["LIVE_TRADING"] = "true"
        print("\n⚠️  LIVE TRADING MODE — Real money will be used!")
        print("    Press Ctrl+C to stop at any time.\n")

    bot = ArbitrageBot(scan_only=args.scan_only)

    # Handle graceful shutdown
    loop = asyncio.get_event_loop()

    def shutdown_handler(sig, frame):
        log.info("Received shutdown signal...")
        bot.stop()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
