import asyncio

from llmbelt import cached


def test_caches_result():
    calls = []

    @cached()
    def f(x):
        calls.append(x)
        return x * 2

    assert f(3) == 6
    assert f(3) == 6
    assert calls == [3]  # second call served from cache


def test_distinguishes_arguments():
    calls = []

    @cached()
    def f(x):
        calls.append(x)
        return x

    f(1)
    f(2)
    f(1)
    assert calls == [1, 2]


def test_handles_unhashable_arguments():
    @cached()
    def f(data):
        return sum(data["nums"])

    assert f({"nums": [1, 2, 3]}) == 6
    assert f({"nums": [1, 2, 3]}) == 6  # would TypeError under lru_cache


def test_caches_none():
    calls = []

    @cached()
    def f():
        calls.append(1)
        return None

    assert f() is None
    assert f() is None
    assert len(calls) == 1


def test_ttl_expiry_with_fake_clock():
    now = [1000.0]
    calls = []

    @cached(ttl=10, clock=lambda: now[0])
    def f():
        calls.append(1)
        return "v"

    f()
    now[0] += 5
    f()  # still fresh
    assert len(calls) == 1
    now[0] += 6  # now 11s elapsed -> expired
    f()
    assert len(calls) == 2


def test_maxsize_eviction():
    calls = []

    @cached(maxsize=2)
    def f(x):
        calls.append(x)
        return x

    f(1)
    f(2)
    f(3)  # evicts key for 1
    f(1)  # recomputed
    assert calls == [1, 2, 3, 1]


def test_cache_clear_and_info():
    @cached()
    def f(x):
        return x

    f(1)
    assert f.cache_info()["size"] == 1
    f.cache_clear()
    assert f.cache_info()["size"] == 0


def test_async_caches_result():
    calls = []

    @cached()
    async def f(x):
        calls.append(x)
        return x * 2

    async def run():
        return await f(4), await f(4)

    assert asyncio.run(run()) == (8, 8)
    assert calls == [4]
