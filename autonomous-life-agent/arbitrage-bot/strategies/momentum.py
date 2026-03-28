"""
Micro-Momentum Strategy
========================
Detects sharp, short-term price moves and rides the momentum
for a few seconds to a few minutes.

NOT a prediction — it's a reaction. When price spikes 0.5%+
in under 30 seconds, there's often a continuation for another
0.2-0.5% before it reverses. We capture that continuation.

Combined with a tight stop-loss, this prints small consistent gains.
Works best during high-volume hours (US market open, news events).
"""

import time
from collections import deque
from dataclasses import dataclass

from exchanges.manager import ExchangeManager
from config import MAX_TRADE_USD, PAIRS
from logger import log


# How many price snapshots to keep per pair
HISTORY_LENGTH = 30

# Minimum price move to trigger entry
MIN_MOMENTUM_PCT = 0.005  # 0.5% in the lookback window

# Lookback window in seconds
LOOKBACK_SECONDS = 30

# Take profit and stop loss
TAKE_PROFIT_PCT = 0.003   # 0.3% — exit with profit
STOP_LOSS_PCT = 0.002     # 0.2% — cut losses quick


@dataclass
class PriceSnapshot:
    price: float
    timestamp: float


@dataclass
class MomentumSignal:
    pair: str
    exchange: str
    direction: str      # "long" or "short"
    entry_price: float
    momentum_pct: float
    take_profit: float
    stop_loss: float
    estimated_profit: float
    timestamp: float


class MomentumStrategy:
    """
    Tracks short-term price momentum and enters when a sharp move is detected.
    """

    def __init__(self, manager: ExchangeManager):
        self.manager = manager
        self.price_history: dict[str, deque] = {}  # "pair:exchange" → deque of PriceSnapshot
        self.open_positions: dict[str, dict] = {}   # "pair:exchange" → position info
        self.signals: list[MomentumSignal] = []

    def _key(self, pair: str, exchange: str) -> str:
        return f"{pair}:{exchange}"

    def _record_price(self, pair: str, exchange: str, price: float):
        key = self._key(pair, exchange)
        if key not in self.price_history:
            self.price_history[key] = deque(maxlen=HISTORY_LENGTH)
        self.price_history[key].append(PriceSnapshot(price=price, timestamp=time.time()))

    def _get_momentum(self, pair: str, exchange: str) -> float | None:
        """Calculate momentum: price change % over lookback window."""
        key = self._key(pair, exchange)
        history = self.price_history.get(key)
        if not history or len(history) < 5:
            return None

        now = time.time()
        # Find the oldest price within the lookback window
        oldest_in_window = None
        for snap in history:
            if now - snap.timestamp <= LOOKBACK_SECONDS:
                oldest_in_window = snap
                break

        if not oldest_in_window:
            return None

        current = history[-1]
        if oldest_in_window.price <= 0:
            return None

        return (current.price - oldest_in_window.price) / oldest_in_window.price

    async def scan(self) -> list[MomentumSignal]:
        """Scan for momentum opportunities."""
        self.signals = []

        for ex_name in self.manager.exchanges:
            fee = self.manager.fees.get(ex_name, 0.001)

            for pair in PAIRS:
                ticker = await self.manager.fetch_ticker(pair, ex_name)
                if not ticker or not ticker["last"]:
                    continue

                price = ticker["last"]
                self._record_price(pair, ex_name, price)

                momentum = self._get_momentum(pair, ex_name)
                if momentum is None:
                    continue

                key = self._key(pair, ex_name)

                # Check for strong upward momentum
                if momentum >= MIN_MOMENTUM_PCT and key not in self.open_positions:
                    take_profit = price * (1 + TAKE_PROFIT_PCT)
                    stop_loss = price * (1 - STOP_LOSS_PCT)
                    est_profit = MAX_TRADE_USD * (TAKE_PROFIT_PCT - 2 * fee)

                    if est_profit > 0:
                        signal = MomentumSignal(
                            pair=pair,
                            exchange=ex_name,
                            direction="long",
                            entry_price=price,
                            momentum_pct=momentum,
                            take_profit=take_profit,
                            stop_loss=stop_loss,
                            estimated_profit=est_profit,
                            timestamp=time.time(),
                        )
                        self.signals.append(signal)
                        log.info(
                            "MOMENTUM [%s/%s] ↑%.2f%% in %ds | Entry: $%.4f | "
                            "TP: $%.4f | SL: $%.4f | Est: $%.3f",
                            pair, ex_name, momentum * 100, LOOKBACK_SECONDS,
                            price, take_profit, stop_loss, est_profit,
                        )

                # Check for strong downward momentum (short opportunity)
                if momentum <= -MIN_MOMENTUM_PCT and key not in self.open_positions:
                    # For shorting, we sell first then buy back cheaper
                    take_profit = price * (1 - TAKE_PROFIT_PCT)
                    stop_loss = price * (1 + STOP_LOSS_PCT)
                    est_profit = MAX_TRADE_USD * (TAKE_PROFIT_PCT - 2 * fee)

                    if est_profit > 0:
                        signal = MomentumSignal(
                            pair=pair,
                            exchange=ex_name,
                            direction="short",
                            entry_price=price,
                            momentum_pct=momentum,
                            take_profit=take_profit,
                            stop_loss=stop_loss,
                            estimated_profit=est_profit,
                            timestamp=time.time(),
                        )
                        self.signals.append(signal)
                        log.info(
                            "MOMENTUM [%s/%s] ↓%.2f%% in %ds | Entry: $%.4f | "
                            "TP: $%.4f | SL: $%.4f",
                            pair, ex_name, abs(momentum) * 100, LOOKBACK_SECONDS,
                            price, take_profit, stop_loss,
                        )

        self.signals.sort(key=lambda s: abs(s.momentum_pct), reverse=True)
        return self.signals

    async def execute(self, signal: MomentumSignal) -> dict | None:
        """Enter a momentum trade."""
        key = self._key(signal.pair, signal.exchange)

        if signal.direction == "long":
            result = await self.manager.execute_buy(signal.exchange, signal.pair, MAX_TRADE_USD)
            if not result:
                return None

            self.open_positions[key] = {
                "direction": "long",
                "entry": result,
                "take_profit": signal.take_profit,
                "stop_loss": signal.stop_loss,
                "entry_time": time.time(),
            }

            log.info("MOMENTUM LONG: %s on %s @ $%.4f (TP: $%.4f, SL: $%.4f)",
                     signal.pair, signal.exchange, result["price"],
                     signal.take_profit, signal.stop_loss)

            return {
                "strategy": "momentum",
                "status": "position_opened",
                "direction": "long",
                "pair": signal.pair,
                "exchange": signal.exchange,
                "entry_price": result["price"],
                "quantity": result["quantity"],
                "momentum_at_entry": signal.momentum_pct,
                "timestamp": time.time(),
            }

        return None

    async def manage_positions(self) -> list[dict]:
        """Check open positions for take-profit or stop-loss hits."""
        closed = []

        for key, pos in list(self.open_positions.items()):
            pair = key.split(":")[0]
            exchange = key.split(":")[1]

            ticker = await self.manager.fetch_ticker(pair, exchange)
            if not ticker:
                continue

            current_price = ticker["last"]
            entry = pos["entry"]

            if pos["direction"] == "long":
                # Check take profit
                if current_price >= pos["take_profit"]:
                    sell = await self.manager.execute_sell(exchange, pair, entry["quantity"])
                    if sell:
                        profit = sell["revenue"] - sell.get("fee", 0) - entry["cost"] - entry.get("fee", 0)
                        closed.append({
                            "strategy": "momentum",
                            "pair": pair,
                            "exchange": exchange,
                            "direction": "long",
                            "exit_reason": "take_profit",
                            "buy": entry,
                            "sell": sell,
                            "profit": profit,
                            "profit_pct": (profit / entry["cost"]) * 100 if entry["cost"] > 0 else 0,
                            "hold_time": time.time() - pos["entry_time"],
                            "timestamp": time.time(),
                        })
                        log.info("MOMENTUM TP HIT: $%.4f profit on %s", profit, pair)
                        del self.open_positions[key]

                # Check stop loss
                elif current_price <= pos["stop_loss"]:
                    sell = await self.manager.execute_sell(exchange, pair, entry["quantity"])
                    if sell:
                        profit = sell["revenue"] - sell.get("fee", 0) - entry["cost"] - entry.get("fee", 0)
                        closed.append({
                            "strategy": "momentum",
                            "pair": pair,
                            "exchange": exchange,
                            "direction": "long",
                            "exit_reason": "stop_loss",
                            "buy": entry,
                            "sell": sell,
                            "profit": profit,
                            "profit_pct": (profit / entry["cost"]) * 100 if entry["cost"] > 0 else 0,
                            "hold_time": time.time() - pos["entry_time"],
                            "timestamp": time.time(),
                        })
                        log.warning("MOMENTUM SL HIT: $%.4f loss on %s", profit, pair)
                        del self.open_positions[key]

                # Timeout: close after 5 minutes regardless
                elif time.time() - pos["entry_time"] > 300:
                    sell = await self.manager.execute_sell(exchange, pair, entry["quantity"])
                    if sell:
                        profit = sell["revenue"] - sell.get("fee", 0) - entry["cost"] - entry.get("fee", 0)
                        closed.append({
                            "strategy": "momentum",
                            "pair": pair,
                            "exchange": exchange,
                            "direction": "long",
                            "exit_reason": "timeout",
                            "buy": entry,
                            "sell": sell,
                            "profit": profit,
                            "profit_pct": (profit / entry["cost"]) * 100 if entry["cost"] > 0 else 0,
                            "hold_time": time.time() - pos["entry_time"],
                            "timestamp": time.time(),
                        })
                        log.info("MOMENTUM TIMEOUT: $%.4f on %s (closed after 5m)", profit, pair)
                        del self.open_positions[key]

        return closed
