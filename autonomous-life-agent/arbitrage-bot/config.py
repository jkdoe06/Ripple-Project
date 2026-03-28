"""
Bot configuration — loads from .env and provides sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _float(key: str, default: float) -> float:
    return float(os.getenv(key, str(default)))


def _int(key: str, default: int) -> int:
    return int(os.getenv(key, str(default)))


def _bool(key: str, default: bool) -> bool:
    return os.getenv(key, str(default)).lower() in ("true", "1", "yes")


def _list(key: str, default: str) -> list[str]:
    return [x.strip() for x in os.getenv(key, default).split(",") if x.strip()]


# ── Exchange credentials ─────────────────────────────────────────────────
EXCHANGES = {}

if os.getenv("COINBASE_API_KEY"):
    EXCHANGES["coinbase"] = {
        "apiKey": os.getenv("COINBASE_API_KEY"),
        "secret": os.getenv("COINBASE_SECRET"),
    }

if os.getenv("KRAKEN_API_KEY"):
    EXCHANGES["kraken"] = {
        "apiKey": os.getenv("KRAKEN_API_KEY"),
        "secret": os.getenv("KRAKEN_SECRET"),
    }

if os.getenv("BINANCEUS_API_KEY"):
    EXCHANGES["binanceus"] = {
        "apiKey": os.getenv("BINANCEUS_API_KEY"),
        "secret": os.getenv("BINANCEUS_SECRET"),
    }

if os.getenv("KUCOIN_API_KEY"):
    EXCHANGES["kucoin"] = {
        "apiKey": os.getenv("KUCOIN_API_KEY"),
        "secret": os.getenv("KUCOIN_SECRET"),
        "password": os.getenv("KUCOIN_PASSPHRASE"),
    }

# ── Trading parameters ───────────────────────────────────────────────────
MIN_SPREAD = _float("MIN_SPREAD", 0.003)        # 0.3% minimum spread
MAX_TRADE_USD = _float("MAX_TRADE_USD", 25.0)   # Max per trade
MAX_TOTAL_CAPITAL = _float("MAX_TOTAL_CAPITAL", 200.0)
PAIRS = _list("PAIRS", "BTC/USDT,ETH/USDT,SOL/USDT,XRP/USDT,DOGE/USDT,AVAX/USDT,LINK/USDT,DOT/USDT")
SCAN_INTERVAL = _int("SCAN_INTERVAL", 5)        # seconds
LIVE_TRADING = _bool("LIVE_TRADING", False)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ── Safety limits ────────────────────────────────────────────────────────
MAX_DAILY_TRADES = 200           # circuit breaker
MAX_DAILY_LOSS_USD = 10.0        # stop trading if down this much today
MAX_CONSECUTIVE_LOSSES = 5       # pause and alert after 5 losses in a row
COOLDOWN_AFTER_TRADE = 2         # seconds to wait after executing a trade

# ── Fee estimates (conservative — actual fees fetched from exchange) ─────
DEFAULT_TAKER_FEE = 0.001        # 0.1% (most exchanges)
DEFAULT_MAKER_FEE = 0.0008       # 0.08%
