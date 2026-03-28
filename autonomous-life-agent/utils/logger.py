"""
Audit logger — every agent action is logged to both console and file.
"""

import logging
import os
from datetime import datetime

from config.settings import LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    fmt = logging.Formatter(
        "[%(asctime)s] %(name)-24s %(levelname)-7s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler — audit log
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"audit_{datetime.now():%Y%m%d}.log")
    fh = logging.FileHandler(log_file)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
