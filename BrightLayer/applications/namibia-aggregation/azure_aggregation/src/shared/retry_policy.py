from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


def with_retry(fn: Callable[[], T], max_retries: int = 3, base_delay_seconds: int = 10) -> T:
    """Retry helper with exponential backoff."""
    attempts = 0
    while True:
        try:
            return fn()
        except Exception:
            attempts += 1
            if attempts >= max_retries:
                raise
            delay = base_delay_seconds * (2 ** (attempts - 1))
            time.sleep(delay)
