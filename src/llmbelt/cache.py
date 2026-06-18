"""Memoize expensive or billable calls (e.g. LLM requests) on their arguments.

Unlike :func:`functools.lru_cache`, arguments don't need to be hashable — they're
serialized to a stable key — and entries can expire via an optional ``ttl``. The
same decorator works on sync and ``async def`` functions. Handy for not paying
twice for an identical prompt while developing or running evals.
"""

from __future__ import annotations

import functools
import hashlib
import inspect
import json
import time
from collections.abc import Callable

_NO_EXPIRY = None


def _make_key(args: tuple, kwargs: dict) -> str:
    """Build a stable cache key from a call's arguments."""
    try:
        payload = json.dumps([args, kwargs], sort_keys=True, default=str)
    except TypeError:
        payload = repr((args, sorted(kwargs.items())))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def cached(
    maxsize: int = 128,
    ttl: float | None = None,
    clock: Callable[[], float] = time.monotonic,
):
    """Cache a function's return value keyed on its arguments.

    Args:
        maxsize: max entries kept; the oldest is evicted past this (0 = unbounded).
        ttl: seconds before an entry expires (``None`` = never).
        clock: time source (injectable for testing).

    The wrapped function gains ``.cache_clear()`` and ``.cache_info()`` helpers.
    """
    def decorator(func):
        store: dict[str, tuple[object, float | None]] = {}
        order: list[str] = []  # keys oldest-first, for eviction

        def lookup(key: str):
            hit = store.get(key)
            if hit is None:
                return _MISS
            value, expires = hit
            if expires is not _NO_EXPIRY and expires <= clock():
                store.pop(key, None)
                if key in order:
                    order.remove(key)
                return _MISS
            return value

        def remember(key: str, value: object) -> None:
            expires = clock() + ttl if ttl else _NO_EXPIRY
            store[key] = (value, expires)
            order.append(key)
            if maxsize and len(order) > maxsize:
                store.pop(order.pop(0), None)

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                key = _make_key(args, kwargs)
                value = lookup(key)
                if value is not _MISS:
                    return value
                value = await func(*args, **kwargs)
                remember(key, value)
                return value

        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                key = _make_key(args, kwargs)
                value = lookup(key)
                if value is not _MISS:
                    return value
                value = func(*args, **kwargs)
                remember(key, value)
                return value

        def cache_clear() -> None:
            store.clear()
            order.clear()

        wrapper.cache_clear = cache_clear
        wrapper.cache_info = lambda: {
            "size": len(store),
            "maxsize": maxsize,
            "ttl": ttl,
        }
        return wrapper

    return decorator


_MISS = object()  # sentinel: distinguishes "no entry" from a cached ``None``
