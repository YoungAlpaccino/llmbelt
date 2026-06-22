"""Estimate API cost from token counts.

Prices are USD per 1M tokens and are **approximate** — providers change them
often. Treat the built-in table as a convenience, update it, or pass your own
``pricing`` dict. Always confirm against the provider's current pricing page.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """Price per 1M tokens, in USD."""

    input_per_1m: float
    output_per_1m: float


# Indicative prices (USD per 1M tokens). VERIFY before relying on these.
PRICING: dict[str, Price] = {
    "claude-opus": Price(15.0, 75.0),
    "claude-sonnet": Price(3.0, 15.0),
    "claude-haiku": Price(0.80, 4.0),
    "gpt-4o": Price(2.50, 10.0),
    "gpt-4o-mini": Price(0.15, 0.60),
    "gemini-flash": Price(0.10, 0.40),
}


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str,
    pricing: dict[str, Price] | None = None,
) -> float:
    """Return the estimated USD cost for a call.

    Raises ``KeyError`` if ``model`` isn't in the pricing table — pass a custom
    ``pricing`` dict for models not listed here.
    """
    table = pricing or PRICING
    if model not in table:
        raise KeyError(
            f"Unknown model {model!r}. Known: {sorted(table)}. "
            "Pass a custom `pricing` dict for other models."
        )
    p = table[model]
    return (
        input_tokens / 1_000_000 * p.input_per_1m
        + output_tokens / 1_000_000 * p.output_per_1m
    )


@dataclass
class CostTracker:
    """Accumulate token usage and USD cost across many calls.

    Drop one in your app and call :meth:`add` after each LLM response to keep a
    running total — handy for budgeting an agent loop, a batch job, or an eval.

    Example::

        tracker = CostTracker()
        tracker.add(1_500, 800, "gpt-4o-mini")
        tracker.add(2_000, 1_200, "gpt-4o-mini")
        print(tracker)            # "2 calls, 5,500 tokens, $0.0019"
        tracker.summary()         # dict with the breakdown
    """

    pricing: dict[str, Price] | None = None
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0

    def add(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Record one call and return its cost (also added to the running total)."""
        call_cost = estimate_cost(input_tokens, output_tokens, model, self.pricing)
        self.calls += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.cost += call_cost
        return call_cost

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def reset(self) -> None:
        """Zero the running totals (keeps the configured ``pricing``)."""
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cost = 0.0

    def summary(self) -> dict[str, float | int]:
        return {
            "calls": self.calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost,
        }

    def __str__(self) -> str:
        return f"{self.calls} calls, {self.total_tokens:,} tokens, ${self.cost:.4f}"
