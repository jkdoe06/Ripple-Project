"""
Stablecoin Depeg Arbitrage
===========================
Stablecoins (USDT, USDC, DAI, TUSD, BUSD) should be worth $1.00.
When they temporarily depeg (drop to $0.995 or spike to $1.005),
buy the cheap one and sell for the expensive one.

This happens multiple times per day during high volatility.
Guaranteed to converge back to $1.00 — free money if you're fast.

Also catches stablecoin-to-stablecoin swaps when one side is cheaper.
"""

import time
from dataclasses import dataclass

from exchanges.manager import ExchangeManager
from config import MAX_TRADE_USD
from logger import log


# Stablecoin pairs to monitor
STABLE_PAIRS = [
    "USDT/USD",
    "USDC/USD",
    "DAI/USD",
    "USDT/USDC",
    "DAI/USDT",
    "DAI/USDC",
    "TUSD/USDT",
    "BUSD/USDT",
]

# Depeg threshold: how far from $1.00 before we trade
DEPEG_THRESHOLD = 0.002   # 0.2% — buy if a stable is at $0.998 or less
PREMIUM_THRESHOLD = 0.002  # 0.2% — sell if a stable is at $1.002 or more


@dataclass
class DepegOpportunity:
    pair: str
    exchange: str
    direction: str        # "buy_depeg" or "sell_premium"
    price: float          # current price
    deviation: float      # how far from $1.00
    estimated_profit: float
    timestamp: float


class StablecoinDepegStrategy:
    """
    Monitors stablecoin prices and trades when they deviate from peg.
    """

    def __init__(self, manager: ExchangeManager):
        self.manager = manager
        self.opportunities: list[DepegOpportunity] = []

    async def scan(self) -> list[DepegOpportunity]:
        self.opportunities = []

        for ex_name, exchange in self.manager.exchanges.items():
            fee = self.manager.fees.get(ex_name, 0.001)

            for pair in STABLE_PAIRS:
                if pair not in exchange.markets:
                    continue

                ticker = await self.manager.fetch_ticker(pair, ex_name)
                if not ticker:
                    continue

                bid = ticker["bid"]
                ask = ticker["ask"]

                # For stablecoin pairs, the "fair value" is 1.0
                # (or very close to it for stable/stable pairs)
                fair_value = 1.0

                # Check for depeg (price below fair value) — BUY opportunity
                if ask < fair_value and (fair_value - ask) > DEPEG_THRESHOLD:
                    deviation = fair_value - ask
                    net_profit = deviation - (2 * fee * ask)  # fees for buy + eventual sell

                    if net_profit > 0:
                        profit_on_trade = MAX_TRADE_USD * (net_profit / ask)
                        opp = DepegOpportunity(
                            pair=pair,
                            exchange=ex_name,
                            direction="buy_depeg",
                            price=ask,
                            deviation=deviation,
                            estimated_profit=profit_on_trade,
                            timestamp=time.time(),
                        )
                        self.opportunities.append(opp)
                        log.info(
                            "DEPEG [%s/%s] Price: $%.5f (%.3f%% below peg) | Est: $%.3f",
                            pair, ex_name, ask, deviation * 100, profit_on_trade,
                        )

                # Check for premium (price above fair value) — SELL opportunity
                if bid > fair_value and (bid - fair_value) > PREMIUM_THRESHOLD:
                    deviation = bid - fair_value
                    net_profit = deviation - (2 * fee * bid)

                    if net_profit > 0:
                        profit_on_trade = MAX_TRADE_USD * (net_profit / bid)
                        opp = DepegOpportunity(
                            pair=pair,
                            exchange=ex_name,
                            direction="sell_premium",
                            price=bid,
                            deviation=deviation,
                            estimated_profit=profit_on_trade,
                            timestamp=time.time(),
                        )
                        self.opportunities.append(opp)
                        log.info(
                            "PREMIUM [%s/%s] Price: $%.5f (%.3f%% above peg) | Est: $%.3f",
                            pair, ex_name, bid, deviation * 100, profit_on_trade,
                        )

                # Cross-stable arbitrage: USDT/USDC should be ~1.0000
                # If USDT/USDC = 0.998, buy USDT with USDC (USDT is cheap)
                # When it reverts to 1.000, you gained 0.2%
                if "/" in pair:
                    base, quote = pair.split("/")
                    if base != "USD" and quote != "USD":
                        # Both sides are stablecoins
                        if ask < (fair_value - DEPEG_THRESHOLD):
                            deviation = fair_value - ask
                            profit_on_trade = MAX_TRADE_USD * (deviation - 2 * fee)
                            if profit_on_trade > 0:
                                opp = DepegOpportunity(
                                    pair=pair,
                                    exchange=ex_name,
                                    direction="buy_depeg",
                                    price=ask,
                                    deviation=deviation,
                                    estimated_profit=profit_on_trade,
                                    timestamp=time.time(),
                                )
                                self.opportunities.append(opp)

        self.opportunities.sort(key=lambda o: o.estimated_profit, reverse=True)
        return self.opportunities

    async def execute(self, opp: DepegOpportunity) -> dict | None:
        """Execute a depeg trade."""
        log.info("EXECUTING DEPEG: %s %s on %s (price: $%.5f, dev: %.3f%%)",
                 opp.direction, opp.pair, opp.exchange, opp.price, opp.deviation * 100)

        if opp.direction == "buy_depeg":
            # Buy the depegged stablecoin — it will revert to $1.00
            result = await self.manager.execute_buy(opp.exchange, opp.pair, MAX_TRADE_USD)
            if not result:
                return None

            cost = result["cost"] + result.get("fee", 0)
            # Expected value when peg restores
            expected_revenue = result["quantity"] * 1.0  # fair value
            expected_profit = expected_revenue - cost

            return {
                "strategy": "stablecoin_depeg",
                "direction": opp.direction,
                "pair": opp.pair,
                "exchange": opp.exchange,
                "buy": result,
                "cost": cost,
                "expected_profit": expected_profit,
                "profit": expected_profit,  # approximate — actual depends on exit
                "profit_pct": (expected_profit / cost) * 100 if cost > 0 else 0,
                "deviation_at_entry": opp.deviation,
                "timestamp": time.time(),
                "note": "Holding until peg restores. Sell when price >= 0.9995",
            }

        elif opp.direction == "sell_premium":
            # We need to have the stablecoin already to sell at premium
            # For now, skip if we don't hold it
            base = opp.pair.split("/")[0]
            balance = self.manager.balances.get(opp.exchange, {}).get(base, 0)
            if balance < 1:
                log.info("No %s balance on %s to sell premium", base, opp.exchange)
                return None

            quantity = min(balance, MAX_TRADE_USD / opp.price)
            result = await self.manager.execute_sell(opp.exchange, opp.pair, quantity)
            if not result:
                return None

            revenue = result["revenue"] - result.get("fee", 0)
            cost = quantity * 1.0  # fair value of what we sold
            profit = revenue - cost

            return {
                "strategy": "stablecoin_depeg",
                "direction": opp.direction,
                "pair": opp.pair,
                "exchange": opp.exchange,
                "sell": result,
                "revenue": revenue,
                "cost": cost,
                "profit": profit,
                "profit_pct": (profit / cost) * 100 if cost > 0 else 0,
                "timestamp": time.time(),
            }

        return None
