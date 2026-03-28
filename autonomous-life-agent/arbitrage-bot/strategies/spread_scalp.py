"""
Spread Scalping Strategy
=========================
The simplest, most consistent money-maker.

Monitor bid-ask spreads on a single exchange. When the spread is
abnormally wide (>2x normal), place a limit buy at the bid and
a limit sell at the ask. If both fill, you pocket the spread.

Also known as "market making lite". Works on less liquid pairs
where spreads are wider.

This is the strategy that stacks the fastest with small amounts
because it trades frequently on any exchange, no transfers needed.
"""

import time
import statistics
from dataclasses import dataclass, field

from exchanges.manager import ExchangeManager
from config import MIN_SPREAD, MAX_TRADE_USD, LIVE_TRADING
from logger import log


# Pairs that tend to have wider spreads (less liquid = more opportunity)
SCALP_PAIRS = [
    "DOT/USDT", "AVAX/USDT", "LINK/USDT", "DOGE/USDT",
    "XRP/USDT", "SOL/USDT", "MATIC/USDT", "ATOM/USDT",
    "FIL/USDT", "NEAR/USDT", "APT/USDT", "ARB/USDT",
]


@dataclass
class SpreadSnapshot:
    pair: str
    exchange: str
    bid: float
    ask: float
    spread: float
    spread_pct: float
    timestamp: float


@dataclass
class ScalpOpportunity:
    pair: str
    exchange: str
    bid: float
    ask: float
    spread_pct: float
    avg_spread_pct: float
    spread_multiple: float    # how many times wider than average
    estimated_profit: float
    timestamp: float


class SpreadScalpStrategy:
    """
    Tracks spread history and trades when spreads are unusually wide.
    """

    def __init__(self, manager: ExchangeManager):
        self.manager = manager
        self.spread_history: dict[str, list[float]] = {}  # "pair:exchange" → [spread_pcts]
        self.max_history = 100  # keep last N spread readings
        self.opportunities: list[ScalpOpportunity] = []

    def _key(self, pair: str, exchange: str) -> str:
        return f"{pair}:{exchange}"

    def _record_spread(self, pair: str, exchange: str, spread_pct: float):
        key = self._key(pair, exchange)
        if key not in self.spread_history:
            self.spread_history[key] = []
        self.spread_history[key].append(spread_pct)
        # Trim history
        if len(self.spread_history[key]) > self.max_history:
            self.spread_history[key] = self.spread_history[key][-self.max_history:]

    def _get_avg_spread(self, pair: str, exchange: str) -> float:
        key = self._key(pair, exchange)
        history = self.spread_history.get(key, [])
        if len(history) < 5:
            return 0.0  # not enough data yet
        return statistics.mean(history)

    async def scan(self) -> list[ScalpOpportunity]:
        """Scan for wide-spread scalping opportunities."""
        self.opportunities = []

        for ex_name in self.manager.exchanges:
            exchange = self.manager.exchanges[ex_name]
            fee = self.manager.fees.get(ex_name, 0.001)

            for pair in SCALP_PAIRS:
                if pair not in exchange.markets:
                    continue

                ticker = await self.manager.fetch_ticker(pair, ex_name)
                if not ticker or not ticker["bid"] or not ticker["ask"]:
                    continue

                bid = ticker["bid"]
                ask = ticker["ask"]
                spread = ask - bid
                spread_pct = spread / ask if ask > 0 else 0

                # Record for history
                self._record_spread(pair, ex_name, spread_pct)

                avg_spread = self._get_avg_spread(pair, ex_name)
                if avg_spread <= 0:
                    continue  # not enough history

                spread_multiple = spread_pct / avg_spread

                # Trade when spread is ≥ 2x normal AND profitable after fees
                net_profit_pct = spread_pct - (2 * fee)  # buy + sell fees

                if spread_multiple >= 2.0 and net_profit_pct > MIN_SPREAD:
                    estimated_profit = MAX_TRADE_USD * net_profit_pct

                    opp = ScalpOpportunity(
                        pair=pair,
                        exchange=ex_name,
                        bid=bid,
                        ask=ask,
                        spread_pct=spread_pct,
                        avg_spread_pct=avg_spread,
                        spread_multiple=spread_multiple,
                        estimated_profit=estimated_profit,
                        timestamp=time.time(),
                    )
                    self.opportunities.append(opp)
                    log.info(
                        "SCALP [%s/%s] Spread: %.3f%% (%.1fx avg) | "
                        "Bid: $%.4f Ask: $%.4f | Est: $%.3f",
                        pair, ex_name, spread_pct * 100,
                        spread_multiple, bid, ask, estimated_profit,
                    )

        self.opportunities.sort(key=lambda o: o.estimated_profit, reverse=True)
        return self.opportunities

    async def execute(self, opp: ScalpOpportunity) -> dict | None:
        """
        Execute spread scalp: buy at bid, sell at ask.
        In practice, use limit orders for better fills.
        For simplicity, using market orders with tight timing.
        """
        log.info("EXECUTING SCALP: %s on %s (spread: %.3f%%, %.1fx avg)",
                 opp.pair, opp.exchange, opp.spread_pct * 100, opp.spread_multiple)

        # Buy
        buy_result = await self.manager.execute_buy(opp.exchange, opp.pair, MAX_TRADE_USD)
        if not buy_result:
            return None

        # Immediately sell
        sell_result = await self.manager.execute_sell(
            opp.exchange, opp.pair, buy_result["quantity"]
        )
        if not sell_result:
            log.error("Sell failed after buy — open position in %s on %s",
                      opp.pair, opp.exchange)
            return {"status": "partial", "buy": buy_result, "sell": None}

        cost = buy_result["cost"] + buy_result.get("fee", 0)
        revenue = sell_result["revenue"] - sell_result.get("fee", 0)
        profit = revenue - cost

        result = {
            "strategy": "spread_scalp",
            "pair": opp.pair,
            "exchange": opp.exchange,
            "buy": buy_result,
            "sell": sell_result,
            "cost": cost,
            "revenue": revenue,
            "profit": profit,
            "profit_pct": (profit / cost) * 100 if cost > 0 else 0,
            "spread_multiple": opp.spread_multiple,
            "timestamp": time.time(),
        }

        if profit > 0:
            log.info("SCALP PROFIT: $%.4f (%.3f%%)", profit, result["profit_pct"])
        else:
            log.warning("SCALP LOSS: $%.4f (spread closed too fast)", profit)

        return result
