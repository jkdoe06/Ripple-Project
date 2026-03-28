"""
Logging setup for the arbitrage bot.
"""

import logging
import os
from datetime import datetime
from config import LOG_LEVEL

log = logging.getLogger("arb-bot")
log.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

fmt = logging.Formatter(
    "[%(asctime)s] %(levelname)-7s %(message)s",
    datefmt="%H:%M:%S",
)

# Console
ch = logging.StreamHandler()
ch.setFormatter(fmt)
log.addHandler(ch)

# File
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
fh = logging.FileHandler(os.path.join(log_dir, f"bot_{datetime.now():%Y%m%d}.log"))
fh.setFormatter(logging.Formatter(
    "[%(asctime)s] %(levelname)-7s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))
log.addHandler(fh)
