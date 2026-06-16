"""A small, dependency-free retry decorator with exponential backoff + jitter.

Network calls to LLM APIs fail transiently (rate limits, 5xx). This wraps a
function so it retries those automatically. The same decorator works on both
sync and ``async def`` functions — it detects coroutine functions and awaits
them, using ``asyncio.sleep`` for the backoff so the event loop isn't blocked.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
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
    async_sleep: Callable[[float], object] | None = None,
):
    """Retry a function on failure with exponential backoff.

    Works on both regular and ``async def`` functions; the wrapper matches the
    wrapped function (a coroutine function stays awaitable).

    Args:
        attempts: total number of tries before giving up.
        base_delay: initial wait (seconds) between tries.
        max_delay: cap on the wait between tries.
        backoff: multiplier applied to the delay after each failure.
        jitter: randomize the wait in [0, delay] to avoid thundering herds.
        exceptions: which exception types should trigger a retry.
        sleep: the sleep function for sync targets (injectable for testing).
        async_sleep: the awaitable sleep for async targets
            (defaults to ``asyncio.sleep``; injectable for testing).

    Example::

        @retry(attempts=3, exceptions=(ConnectionError,))
        def call_api():
            ...

        @retry(attempts=3, exceptions=(ConnectionError,))
        async def call_api_async():
            ...
    """
    if async_sleep is None:
        async_sleep = asyncio.sleep

    def _next_wait(delay: float) -> float:
        wait = min(delay, max_delay)
        return random.uniform(0, wait) if jitter else wait

    def decorator(func):
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                delay = base_delay
                last_exc: BaseException | None = None
                for i in range(attempts):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exc = e
                        if i == attempts - 1:
                            break
                        await async_sleep(_next_wait(delay))
                        delay *= backoff
                assert last_exc is not None
                raise last_exc

            return async_wrapper

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
                    sleep(_next_wait(delay))
                    delay *= backoff
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator
