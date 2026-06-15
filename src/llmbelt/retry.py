"""A small, dependency-free retry decorator with exponential backoff + jitter.

Network calls to LLM APIs fail transiently (rate limits, 5xx). This wraps a
function so it retries those automatically.
"""

from __future__ import annotations

import functools
import random
import time
from collections.abc import Callable


def retry(
    attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    sleep: Callable[[float], None] = time.sleep,
):
    """Retry a function on failure with exponential backoff.

    Args:
        attempts: total number of tries before giving up.
        base_delay: initial wait (seconds) between tries.
        max_delay: cap on the wait between tries.
        backoff: multiplier applied to the delay after each failure.
        jitter: randomize the wait in [0, delay] to avoid thundering herds.
        exceptions: which exception types should trigger a retry.
        sleep: the sleep function (injectable for testing).

    Example::

        @retry(attempts=3, exceptions=(ConnectionError,))
        def call_api():
            ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exc: BaseException | None = None
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if i == attempts - 1:
                        break
                    wait = min(delay, max_delay)
                    if jitter:
                        wait = random.uniform(0, wait)
                    sleep(wait)
                    delay *= backoff
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator
