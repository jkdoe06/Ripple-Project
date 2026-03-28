"""
Retry decorator with exponential backoff.
"""

import time
import functools
from config.settings import MAX_RETRIES, RETRY_BASE_DELAY
from utils.logger import get_logger

log = get_logger("retry")


def with_retry(func):
    """Retry a function up to MAX_RETRIES times with exponential backoff."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                delay = RETRY_BASE_DELAY ** attempt
                log.warning(
                    "%s attempt %d/%d failed: %s — retrying in %ds",
                    func.__name__, attempt, MAX_RETRIES, e, delay,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(delay)
        log.error("%s failed after %d attempts: %s", func.__name__, MAX_RETRIES, last_error)
        raise last_error
    return wrapper
