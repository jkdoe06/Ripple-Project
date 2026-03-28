"""
Cross-Exchange Arbitrage Strategy
==================================
The classic: buy on the exchange with the lowest ask,
sell on the exchange with the highest bid.

Profit = (highest_bid - lowest_ask) - fees_on_both_sides

Works best when you hold balances on multiple exchanges
so you can buy+sell simultaneously (no transfer delay).
"""

import asyncio
import time
from dataclasses import dataclass

from exchanges.manager import ExchangeManager
from config import MIN_SPREAD, MAX_TRADE_USD, PAIRS
from logger import log


@dataclass
class ArbitrageOpportunity:
    pair: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float       # ask on cheap exchange
    sell_price: float      # bid on expensive exchange
    spread: float          # absolute price difference
    spread_pct: float      # spread as percentage
    net_profit_pct: float  # after fees
    estimated_profit_usd: float  # on MAX_TRADE_USD
    timestamp: float


class CrossExchangeStrategy:
    """
    Scans all pairs across all exchanges. When the bid on exchange A
    is higher than the ask on exchange B (minus fees), we have an
    arbitrage opportunity.
    """

    def __init__(self, manager: ExchangeManager):
        self.manager = manager
        self.opportunities: list[ArbitrageOpportunity] = []

    async def scan(self) -> list[ArbitrageOpportunity]:
        """Scan all pairs for cross-exchange arbitrage opportunities."""
        self.opportunities = []

        for pair in PAIRS:
            tickers = await self.manager.fetch_all_tickers(pair)
            if len(tickers) < 2:
                continue

            exchanges = list(tickers.keys())

            # Compare every pair of exchanges
            for i in range(len(exchanges)):
                for j in range(len(exchanges)):
                    if i == j:
                        continue

                    buy_ex = exchanges[i]   # buy where ask is low
                    sell_ex = exchanges[j]   # sell where bid is high

                    ask = tickers[buy_ex]["ask"]    # price to buy
                    bid = tickers[sell_ex]["bid"]    # price to sell

                    if ask <= 0 or bid <= 0:
                        continue

                    spread = bid - ask
                    spread_pct = spread / ask

                    # Account for fees on both sides
                    buy_fee = self.manager.fees.get(buy_ex, 0.001)
                    sell_fee = self.manager.fees.get(sell_ex, 0.001)
                    total_fee_pct = buy_fee + sell_fee

                    net_profit_pct = spread_pct - total_fee_pct

                    if net_profit_pct > MIN_SPREAD:
                        estimated_profit = MAX_TRADE_USD * net_profit_pct
                        opp = ArbitrageOpportunity(
                            pair=pair,
                            buy_exchange=buy_ex,
                            sell_exchange=sell_ex,
                            buy_price=ask,
                            sell_price=bid,
                            spread=spread,
                            spread_pct=spread_pct,
                            net_profit_pct=net_profit_pct,
                            estimated_profit_usd=estimated_profit,
                            timestamp=time.time(),
                        )
                        self.opportunities.append(opp)
                        log.info(
                            "OPPORTUNITY [%s] Buy@%s $%.4f → Sell@%s $%.4f | "
                            "Spread: %.3f%% | Net: %.3f%% | Est profit: $%.2f",
                            pair, buy_ex, ask, sell_ex, bid,
                            spread_pct * 100, net_profit_pct * 100, estimated_profit,
                        )

        # Sort by profit potential
        self.opportunities.sort(key=lambda o: o.net_profit_pct, reverse=True)
        return self.opportunities

    async def execute(self, opp: ArbitrageOpportunity) -> dict | None:
        """
        Execute a cross-exchange arbitrage:
        1. Buy on cheap exchange
        2. Sell on expensive exchange (simultaneously)

        Requires holding base currency on the sell exchange
        AND quote currency on the buy exchange.
        """
        trade_usd = min(MAX_TRADE_USD, MAX_TRADE_USD)

        log.info(
            "EXECUTING: Buy %s on %s @ $%.4f, Sell on %s @ $%.4f (est: $%.2f profit)",
            opp.pair, opp.buy_exchange, opp.buy_price,
            opp.sell_exchange, opp.sell_price, opp.estimated_profit_usd,
        )

        # Execute buy and sell simultaneously
        buy_task = self.manager.execute_buy(opp.buy_exchange, opp.pair, trade_usd)
        sell_quantity = trade_usd / opp.buy_price  # approximate quantity
        sell_task = self.manager.execute_sell(opp.sell_exchange, opp.pair, sell_quantity)

        buy_result, sell_result = await asyncio.gather(buy_task, sell_task)

        if not buy_result or not sell_result:
            log.warning("Trade partially failed: buy=%s, sell=%s", buy_result, sell_result)
            return None

        # Calculate actual P&L
        total_cost = buy_result["cost"] + buy_result.get("fee", 0)
        total_revenue = sell_result["revenue"] - sell_result.get("fee", 0)
        profit = total_revenue - total_cost

        result = {
            "strategy": "cross_exchange",
            "pair": opp.pair,
            "buy": buy_result,
            "sell": sell_result,
            "cost": total_cost,
            "revenue": total_revenue,
            "profit": profit,
            "profit_pct": (profit / total_cost) * 100 if total_cost > 0 else 0,
            "timestamp": time.time(),
        }

        if profit > 0:
            log.info("PROFIT: $%.4f (%.3f%%) on %s", profit, result["profit_pct"], opp.pair)
        else:
            log.warning("LOSS: $%.4f (%.3f%%) on %s — spread may have closed", profit, result["profit_pct"], opp.pair)

        return result
