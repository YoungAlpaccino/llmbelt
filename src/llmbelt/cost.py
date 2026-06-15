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
