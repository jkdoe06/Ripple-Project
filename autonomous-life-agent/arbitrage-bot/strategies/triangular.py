"""
Triangular Arbitrage Strategy
==============================
Exploit price inconsistencies between 3 trading pairs on a SINGLE exchange.

Example cycle: USDT → BTC → ETH → USDT
  1. Buy BTC with USDT (BTC/USDT)
  2. Buy ETH with BTC (ETH/BTC)
  3. Sell ETH for USDT (ETH/USDT)

If the final USDT > starting USDT (after fees), it's profitable.

Advantage: No transfers between exchanges needed.
Runs entirely within one exchange = faster execution.
"""

import time
from dataclasses import dataclass
from itertools import permutations

from exchanges.manager import ExchangeManager
from config import MIN_SPREAD, MAX_TRADE_USD
from logger import log


# Common triangular routes (base currency = USDT)
TRIANGULAR_ROUTES = [
    # (pair1, pair2, pair3, direction)
    # direction: "buy" or "sell" for each leg
    ("BTC/USDT", "ETH/BTC", "ETH/USDT"),
    ("BTC/USDT", "SOL/BTC", "SOL/USDT"),
    ("BTC/USDT", "XRP/BTC", "XRP/USDT"),
    ("BTC/USDT", "DOGE/BTC", "DOGE/USDT"),
    ("BTC/USDT", "LINK/BTC", "LINK/USDT"),
    ("BTC/USDT", "AVAX/BTC", "AVAX/USDT"),
    ("BTC/USDT", "DOT/BTC", "DOT/USDT"),
    ("ETH/USDT", "SOL/ETH", "SOL/USDT"),
    ("ETH/USDT", "LINK/ETH", "LINK/USDT"),
    ("ETH/USDT", "AVAX/ETH", "AVAX/USDT"),
]


@dataclass
class TriangularOpportunity:
    exchange: str
    route: tuple[str, str, str]
    prices: tuple[float, float, float]  # execution prices for each leg
    start_amount: float                 # USDT in
    end_amount: float                   # USDT out
    profit: float                       # end - start
    profit_pct: float                   # profit as percentage
    timestamp: float


class TriangularStrategy:
    """
    Scans for triangular arbitrage within a single exchange.
    """

    def __init__(self, manager: ExchangeManager):
        self.manager = manager
        self.opportunities: list[TriangularOpportunity] = []

    async def scan(self, exchange_name: str = None) -> list[TriangularOpportunity]:
        """Scan for triangular arbitrage on one or all exchanges."""
        self.opportunities = []
        exchanges_to_scan = [exchange_name] if exchange_name else list(self.manager.exchanges.keys())

        for ex_name in exchanges_to_scan:
            exchange = self.manager.exchanges.get(ex_name)
            if not exchange:
                continue

            fee = self.manager.fees.get(ex_name, 0.001)

            for route in TRIANGULAR_ROUTES:
                pair1, pair2, pair3 = route

                # Check all pairs exist on this exchange
                if not all(p in exchange.markets for p in route):
                    continue

                try:
                    # Fetch all three tickers concurrently
                    t1 = await self.manager.fetch_ticker(pair1, ex_name)
                    t2 = await self.manager.fetch_ticker(pair2, ex_name)
                    t3 = await self.manager.fetch_ticker(pair3, ex_name)

                    if not all([t1, t2, t3]):
                        continue

                    # Forward path: USDT → A → B → USDT
                    # Leg 1: Buy A with USDT (use ask price)
                    amount_usdt = MAX_TRADE_USD
                    amount_a = (amount_usdt / t1["ask"]) * (1 - fee)

                    # Leg 2: Buy B with A (use ask price)
                    amount_b = (amount_a / t2["ask"]) * (1 - fee)

                    # Leg 3: Sell B for USDT (use bid price)
                    final_usdt = (amount_b * t3["bid"]) * (1 - fee)

                    profit = final_usdt - amount_usdt
                    profit_pct = (profit / amount_usdt) * 100

                    # Reverse path: USDT → B → A → USDT
                    amount_b_rev = (amount_usdt / t3["ask"]) * (1 - fee)
                    amount_a_rev = (amount_b_rev * t2["bid"]) * (1 - fee)
                    final_usdt_rev = (amount_a_rev * t1["bid"]) * (1 - fee)
                    profit_rev = final_usdt_rev - amount_usdt
                    profit_pct_rev = (profit_rev / amount_usdt) * 100

                    # Check forward path
                    if profit_pct > MIN_SPREAD * 100:
                        opp = TriangularOpportunity(
                            exchange=ex_name,
                            route=route,
                            prices=(t1["ask"], t2["ask"], t3["bid"]),
                            start_amount=amount_usdt,
                            end_amount=final_usdt,
                            profit=profit,
                            profit_pct=profit_pct,
                            timestamp=time.time(),
                        )
                        self.opportunities.append(opp)
                        log.info(
                            "TRI-ARB [%s] %s → %s → %s | $%.2f → $%.2f | "
                            "Profit: $%.4f (%.3f%%)",
                            ex_name, pair1, pair2, pair3,
                            amount_usdt, final_usdt, profit, profit_pct,
                        )

                    # Check reverse path
                    if profit_pct_rev > MIN_SPREAD * 100:
                        opp = TriangularOpportunity(
                            exchange=ex_name,
                            route=(pair3, pair2, pair1),
                            prices=(t3["ask"], t2["bid"], t1["bid"]),
                            start_amount=amount_usdt,
                            end_amount=final_usdt_rev,
                            profit=profit_rev,
                            profit_pct=profit_pct_rev,
                            timestamp=time.time(),
                        )
                        self.opportunities.append(opp)
                        log.info(
                            "TRI-ARB [%s] %s → %s → %s (REVERSE) | $%.2f → $%.2f | "
                            "Profit: $%.4f (%.3f%%)",
                            ex_name, pair3, pair2, pair1,
                            amount_usdt, final_usdt_rev, profit_rev, profit_pct_rev,
                        )

                except Exception as e:
                    log.debug("Tri-arb scan error on %s %s: %s", ex_name, route, e)

        self.opportunities.sort(key=lambda o: o.profit_pct, reverse=True)
        return self.opportunities

    async def execute(self, opp: TriangularOpportunity) -> dict | None:
        """
        Execute a triangular arbitrage by placing 3 sequential market orders.
        Speed is critical — prices can shift between legs.
        """
        pair1, pair2, pair3 = opp.route
        ex = opp.exchange
        fee = self.manager.fees.get(ex, 0.001)

        log.info("EXECUTING TRI-ARB on %s: %s → %s → %s ($%.2f target profit)",
                 ex, pair1, pair2, pair3, opp.profit)

        # Leg 1: Buy first asset with USDT
        leg1 = await self.manager.execute_buy(ex, pair1, MAX_TRADE_USD)
        if not leg1:
            log.error("Leg 1 failed — aborting")
            return None

        # Leg 2: Trade first asset for second asset
        # Need to determine direction based on pair structure
        quantity_a = leg1["quantity"]
        base2 = pair2.split("/")[0]
        quote2 = pair2.split("/")[1]

        # If we hold the quote currency of pair2, we buy
        # If we hold the base currency of pair2, we sell
        base1 = pair1.split("/")[0]
        if base1 == quote2:
            # We hold quote2, so buy base2
            cost_in_a = quantity_a * leg1["price"]  # roughly
            leg2 = await self.manager.execute_buy(ex, pair2, cost_in_a * (1 - fee))
        else:
            # We hold base2 equivalent, sell it
            leg2 = await self.manager.execute_sell(ex, pair2, quantity_a * (1 - fee))

        if not leg2:
            log.error("Leg 2 failed — you may have an open position in %s on %s", base1, ex)
            return {"status": "partial_failure", "leg1": leg1, "leg2": None, "leg3": None}

        # Leg 3: Convert back to USDT
        quantity_b = leg2.get("quantity", 0)
        if leg2["side"] == "buy":
            quantity_b = leg2["quantity"]
        leg3 = await self.manager.execute_sell(ex, pair3, quantity_b * (1 - fee))

        if not leg3:
            log.error("Leg 3 failed — you may have an open position")
            return {"status": "partial_failure", "leg1": leg1, "leg2": leg2, "leg3": None}

        # Calculate P&L
        total_cost = leg1["cost"] + leg1.get("fee", 0)
        total_revenue = leg3.get("revenue", 0) - leg3.get("fee", 0)
        profit = total_revenue - total_cost

        result = {
            "strategy": "triangular",
            "exchange": ex,
            "route": opp.route,
            "legs": [leg1, leg2, leg3],
            "cost": total_cost,
            "revenue": total_revenue,
            "profit": profit,
            "profit_pct": (profit / total_cost) * 100 if total_cost > 0 else 0,
            "timestamp": time.time(),
        }

        if profit > 0:
            log.info("TRI-ARB PROFIT: $%.4f (%.3f%%)", profit, result["profit_pct"])
        else:
            log.warning("TRI-ARB LOSS: $%.4f (%.3f%%)", profit, result["profit_pct"])

        return result
