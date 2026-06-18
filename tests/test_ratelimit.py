import pytest

from llmbelt import RateLimiter


class FakeClock:
    """Controllable monotonic clock; sleeping just advances the clock."""

    def __init__(self):
        self.now = 0.0
        self.slept = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds
        self.slept += seconds


def _limiter(clock, **kw):
    return RateLimiter(sleep=clock.sleep, monotonic=clock.monotonic, **kw)


def test_invalid_rate():
    with pytest.raises(ValueError):
        RateLimiter(rate=0)


def test_invalid_per():
    with pytest.raises(ValueError):
        RateLimiter(rate=1, per=0)


def test_full_bucket_does_not_wait():
    clock = FakeClock()
    limiter = _limiter(clock, rate=5, per=1)  # capacity 5, starts full
    for _ in range(5):
        limiter.acquire()
    assert clock.slept == 0


def test_throttles_when_empty():
    clock = FakeClock()
    limiter = _limiter(clock, rate=1, per=1, capacity=1)  # 1 token/sec
    limiter.acquire()  # consumes the initial token, no wait
    limiter.acquire()  # bucket empty -> must wait ~1s for a refill
    assert clock.slept == pytest.approx(1.0)


def test_acquire_more_than_capacity_raises():
    clock = FakeClock()
    limiter = _limiter(clock, rate=5, per=1, capacity=5)
    with pytest.raises(ValueError):
        limiter.acquire(6)


def test_decorator_gates_calls():
    clock = FakeClock()
    limiter = _limiter(clock, rate=1, per=1, capacity=1)

    @limiter
    def f():
        return "ok"

    assert f() == "ok"
    assert f() == "ok"
    assert clock.slept == pytest.approx(1.0)  # second call waited


def test_context_manager():
    clock = FakeClock()
    limiter = _limiter(clock, rate=2, per=1)
    with limiter:
        pass
    assert clock.slept == 0
