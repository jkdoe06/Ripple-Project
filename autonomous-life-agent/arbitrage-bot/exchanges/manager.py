"""
Exchange Manager — handles connections, orderbooks, and trade execution
across multiple exchanges via ccxt.
"""

import asyncio
import time
import ccxt.async_support as ccxt
from config import EXCHANGES, DEFAULT_TAKER_FEE, LIVE_TRADING, MAX_TRADE_USD
from logger import log


class ExchangeManager:
    """Manages multiple exchange connections and provides unified price access."""

    def __init__(self):
        self.exchanges: dict[str, ccxt.Exchange] = {}
        self.fees: dict[str, float] = {}           # exchange_id → taker fee
        self.balances: dict[str, dict] = {}         # exchange_id → {currency: amount}
        self._last_prices: dict[str, dict] = {}     # pair → {exchange: price_data}

    async def connect_all(self):
        """Initialize all configured exchanges."""
        for name, creds in EXCHANGES.items():
            try:
                exchange_class = getattr(ccxt, name)
                exchange = exchange_class({
                    **creds,
                    "enableRateLimit": True,
                    "timeout": 10000,
                })
                if hasattr(exchange, "set_sandbox_mode") and not LIVE_TRADING:
                    try:
                        exchange.set_sandbox_mode(True)
                        log.info("[%s] Sandbox/testnet mode enabled", name)
                    except Exception:
                        log.info("[%s] No sandbox available, using paper trading logic", name)

                await exchange.load_markets()
                self.exchanges[name] = exchange

                # Fetch trading fees
                try:
                    fee_info = exchange.fees.get("trading", {})
                    self.fees[name] = fee_info.get("taker", DEFAULT_TAKER_FEE)
                except Exception:
                    self.fees[name] = DEFAULT_TAKER_FEE

                log.info("[%s] Connected — %d markets, taker fee: %.4f",
                         name, len(exchange.markets), self.fees[name])

            except Exception as e:
                log.error("[%s] Failed to connect: %s", name, e)

        if len(self.exchanges) < 2:
            log.warning("Only %d exchange(s) connected. Cross-exchange arb needs ≥2.", len(self.exchanges))

        return self.exchanges

    async def close_all(self):
        for name, exchange in self.exchanges.items():
            try:
                await exchange.close()
            except Exception:
                pass

    async def fetch_balances(self):
        """Fetch balances from all exchanges."""
        for name, exchange in self.exchanges.items():
            try:
                balance = await exchange.fetch_balance()
                # Only track non-zero balances
                self.balances[name] = {
                    currency: float(amount)
                    for currency, amount in balance.get("free", {}).items()
                    if float(amount) > 0
                }
            except Exception as e:
                log.warning("[%s] Balance fetch failed: %s", name, e)

    async def fetch_ticker(self, pair: str, exchange_name: str) -> dict | None:
        """Fetch current bid/ask for a pair on a specific exchange."""
        exchange = self.exchanges.get(exchange_name)
        if not exchange:
            return None

        if pair not in exchange.markets:
            return None

        try:
            ticker = await exchange.fetch_ticker(pair)
            return {
                "exchange": exchange_name,
                "pair": pair,
                "bid": float(ticker.get("bid", 0) or 0),
                "ask": float(ticker.get("ask", 0) or 0),
                "last": float(ticker.get("last", 0) or 0),
                "volume": float(ticker.get("baseVolume", 0) or 0),
                "timestamp": ticker.get("timestamp", int(time.time() * 1000)),
            }
        except Exception as e:
            log.debug("[%s] Ticker fetch failed for %s: %s", exchange_name, pair, e)
            return None

    async def fetch_all_tickers(self, pair: str) -> dict[str, dict]:
        """Fetch tickers for a pair across ALL connected exchanges."""
        tasks = {
            name: self.fetch_ticker(pair, name)
            for name in self.exchanges
        }
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        tickers = {}
        for name, result in zip(tasks.keys(), results):
            if isinstance(result, dict) and result.get("bid") and result.get("ask"):
                tickers[name] = result
        return tickers

    async def execute_buy(self, exchange_name: str, pair: str, amount_usd: float) -> dict | None:
        """Place a market buy order. Returns order info or None."""
        exchange = self.exchanges.get(exchange_name)
        if not exchange:
            return None

        try:
            ticker = await exchange.fetch_ticker(pair)
            price = float(ticker["ask"])
            if price <= 0:
                return None

            # Calculate quantity
            quantity = amount_usd / price

            # Respect minimum order size
            market = exchange.markets.get(pair, {})
            min_amount = market.get("limits", {}).get("amount", {}).get("min", 0) or 0
            if quantity < min_amount:
                log.warning("[%s] Order too small: %.8f < min %.8f", exchange_name, quantity, min_amount)
                return None

            if not LIVE_TRADING:
                # Paper trade
                fee = amount_usd * self.fees.get(exchange_name, DEFAULT_TAKER_FEE)
                log.info("[PAPER] BUY %.6f %s on %s @ $%.2f ($%.2f, fee: $%.4f)",
                         quantity, pair, exchange_name, price, amount_usd, fee)
                return {
                    "side": "buy",
                    "exchange": exchange_name,
                    "pair": pair,
                    "quantity": quantity,
                    "price": price,
                    "cost": amount_usd,
                    "fee": fee,
                    "paper": True,
                    "timestamp": time.time(),
                }

            # Live trade
            order = await exchange.create_market_buy_order(pair, quantity)
            filled_price = float(order.get("average", price))
            filled_cost = float(order.get("cost", amount_usd))
            fee_cost = float(order.get("fee", {}).get("cost", 0))
            log.info("[LIVE] BUY %.6f %s on %s @ $%.2f (fee: $%.4f)",
                     quantity, pair, exchange_name, filled_price, fee_cost)
            return {
                "side": "buy",
                "exchange": exchange_name,
                "pair": pair,
                "quantity": float(order.get("filled", quantity)),
                "price": filled_price,
                "cost": filled_cost,
                "fee": fee_cost,
                "order_id": order.get("id"),
                "paper": False,
                "timestamp": time.time(),
            }

        except Exception as e:
            log.error("[%s] Buy failed for %s: %s", exchange_name, pair, e)
            return None

    async def execute_sell(self, exchange_name: str, pair: str, quantity: float) -> dict | None:
        """Place a market sell order. Returns order info or None."""
        exchange = self.exchanges.get(exchange_name)
        if not exchange:
            return None

        try:
            ticker = await exchange.fetch_ticker(pair)
            price = float(ticker["bid"])
            if price <= 0:
                return None

            if not LIVE_TRADING:
                revenue = quantity * price
                fee = revenue * self.fees.get(exchange_name, DEFAULT_TAKER_FEE)
                log.info("[PAPER] SELL %.6f %s on %s @ $%.2f ($%.2f, fee: $%.4f)",
                         quantity, pair, exchange_name, price, revenue, fee)
                return {
                    "side": "sell",
                    "exchange": exchange_name,
                    "pair": pair,
                    "quantity": quantity,
                    "price": price,
                    "revenue": revenue,
                    "fee": fee,
                    "paper": True,
                    "timestamp": time.time(),
                }

            order = await exchange.create_market_sell_order(pair, quantity)
            filled_price = float(order.get("average", price))
            revenue = float(order.get("cost", quantity * price))
            fee_cost = float(order.get("fee", {}).get("cost", 0))
            log.info("[LIVE] SELL %.6f %s on %s @ $%.2f (fee: $%.4f)",
                     quantity, pair, exchange_name, filled_price, fee_cost)
            return {
                "side": "sell",
                "exchange": exchange_name,
                "pair": pair,
                "quantity": float(order.get("filled", quantity)),
                "price": filled_price,
                "revenue": revenue,
                "fee": fee_cost,
                "order_id": order.get("id"),
                "paper": False,
                "timestamp": time.time(),
            }

        except Exception as e:
            log.error("[%s] Sell failed for %s: %s", exchange_name, pair, e)
            return None
