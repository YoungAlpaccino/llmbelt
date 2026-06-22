import pytest

from llmbelt import CostTracker, Price, estimate_cost


def test_known_model():
    cost = estimate_cost(1_000_000, 1_000_000, "gpt-4o-mini")
    assert cost == pytest.approx(0.15 + 0.60)


def test_input_only():
    assert estimate_cost(1_000_000, 0, "gpt-4o-mini") == pytest.approx(0.15)


def test_unknown_model_raises():
    with pytest.raises(KeyError):
        estimate_cost(1, 1, "no-such-model")


def test_custom_pricing():
    table = {"x": Price(10.0, 20.0)}
    assert estimate_cost(1_000_000, 0, "x", pricing=table) == pytest.approx(10.0)


def test_tracker_accumulates():
    t = CostTracker()
    c1 = t.add(1_000_000, 0, "gpt-4o-mini")
    c2 = t.add(0, 1_000_000, "gpt-4o-mini")
    assert c1 == pytest.approx(0.15)
    assert c2 == pytest.approx(0.60)
    assert t.calls == 2
    assert t.input_tokens == 1_000_000
    assert t.output_tokens == 1_000_000
    assert t.total_tokens == 2_000_000
    assert t.cost == pytest.approx(0.75)


def test_tracker_summary_and_str():
    t = CostTracker()
    t.add(1_000_000, 0, "gpt-4o-mini")
    summary = t.summary()
    assert summary["calls"] == 1
    assert summary["total_tokens"] == 1_000_000
    assert summary["cost_usd"] == pytest.approx(0.15)
    assert "1 calls" in str(t)
    assert "$0.15" in str(t)


def test_tracker_reset():
    t = CostTracker()
    t.add(1_000_000, 0, "gpt-4o-mini")
    t.reset()
    assert t.calls == 0
    assert t.cost == 0.0
    assert t.total_tokens == 0


def test_tracker_uses_custom_pricing():
    t = CostTracker(pricing={"x": Price(10.0, 20.0)})
    assert t.add(1_000_000, 0, "x") == pytest.approx(10.0)


def test_tracker_unknown_model_raises():
    t = CostTracker()
    with pytest.raises(KeyError):
        t.add(1, 1, "no-such-model")
