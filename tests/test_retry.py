import asyncio

import pytest

from llmbelt import retry

_no_sleep = lambda _: None  # noqa: E731 — avoid real waits in tests


async def _no_async_sleep(_):  # avoid real waits in async tests
    return None


def test_succeeds_first_try():
    calls = []

    @retry(attempts=3, sleep=_no_sleep)
    def f():
        calls.append(1)
        return "ok"

    assert f() == "ok"
    assert len(calls) == 1


def test_retries_then_succeeds():
    calls = []

    @retry(attempts=3, sleep=_no_sleep)
    def f():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("transient")
        return "ok"

    assert f() == "ok"
    assert len(calls) == 3


def test_exhausts_and_raises():
    @retry(attempts=2, sleep=_no_sleep)
    def f():
        raise ValueError("always")

    with pytest.raises(ValueError):
        f()


def test_only_catches_listed_exceptions():
    @retry(attempts=3, exceptions=(KeyError,), sleep=_no_sleep)
    def f():
        raise ValueError("not retried")

    with pytest.raises(ValueError):
        f()


def test_preserves_function_metadata():
    @retry(sleep=_no_sleep)
    def my_func():
        """docstring."""
        return 1

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "docstring."


def test_async_retries_then_succeeds():
    calls = []

    @retry(attempts=3, async_sleep=_no_async_sleep)
    async def f():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("transient")
        return "ok"

    assert asyncio.iscoroutinefunction(f)
    assert asyncio.run(f()) == "ok"
    assert len(calls) == 3


def test_async_exhausts_and_raises():
    @retry(attempts=2, async_sleep=_no_async_sleep)
    async def f():
        raise ValueError("always")

    with pytest.raises(ValueError):
        asyncio.run(f())


def test_async_only_catches_listed_exceptions():
    @retry(attempts=3, exceptions=(KeyError,), async_sleep=_no_async_sleep)
    async def f():
        raise ValueError("not retried")

    with pytest.raises(ValueError):
        asyncio.run(f())
