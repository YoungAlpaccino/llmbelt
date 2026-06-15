import pytest

from llmbelt import Price, estimate_cost


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
