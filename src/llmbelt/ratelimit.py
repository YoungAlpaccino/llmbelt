"""A small, thread-safe token-bucket rate limiter for throttling API calls.

LLM providers cap requests per minute; exceed it and you get 429s. Wrap your
calls with a :class:`RateLimiter` to smoothly stay under the limit (with bursts
allowed up to a capacity).
"""

from __future__ import annotations

import functools
import threading
import time
from collections.abc import Callable


class RateLimiter:
    """Allow ``rate`` operations per ``per`` seconds (token-bucket).

    Tokens refill continuously; a call :meth:`acquire` blocks (sleeps) until a
    token is available. Short bursts up to ``capacity`` tokens are allowed. Use
    it three ways::

        limiter = RateLimiter(rate=60, per=60)   # 60/min

        limiter.acquire()          # gate before a call
        with limiter:              # context manager
            call_api()

        @limiter                   # decorator
        def call_api(): ...

    Thread-safe. ``sleep`` and ``monotonic`` are injectable for testing.
    """

    def __init__(
        self,
        rate: float,
        per: float = 60.0,
        capacity: float | None = None,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ):
        if rate <= 0:
            raise ValueError("rate must be positive")
        if per <= 0:
            raise ValueError("per must be positive")
        self.rate = rate
        self.per = per
        self.capacity = float(capacity if capacity is not None else rate)
        self._fill_rate = rate / per  # tokens per second
        self._tokens = self.capacity
        self._sleep = sleep
        self._monotonic = monotonic
        self._last = monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = self._monotonic()
        elapsed = now - self._last
        self._last = now
        self._tokens = min(self.capacity, self._tokens + elapsed * self._fill_rate)

    def acquire(self, tokens: float = 1) -> None:
        """Block until ``tokens`` are available, then consume them."""
        if tokens > self.capacity:
            raise ValueError(
                f"requested {tokens} tokens exceeds capacity {self.capacity}"
            )
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                wait = (tokens - self._tokens) / self._fill_rate
            self._sleep(wait)

    def __enter__(self) -> RateLimiter:
        self.acquire()
        return self

    def __exit__(self, *exc_info) -> bool:
        return False

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.acquire()
            return func(*args, **kwargs)

        return wrapper
