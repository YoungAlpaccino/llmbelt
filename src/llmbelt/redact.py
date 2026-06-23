"""Scrub PII and secrets from text before sending it to a third-party LLM.

Best-effort regex redaction for the most common sensitive data: email
addresses, phone numbers, credit-card and social-security numbers, IP
addresses, and API-key-shaped tokens. This is a guardrail, **not** a compliance
guarantee — pattern matching can miss things and occasionally over-match. Review
``DEFAULT_PII_PATTERNS`` and supply your own for anything important.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping

# Order matters: more specific / structured patterns run before greedier ones so
# they win on overlapping text.
DEFAULT_PII_PATTERNS: dict[str, re.Pattern] = {
    "EMAIL": re.compile(r"\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    "AWS_KEY": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "API_KEY": re.compile(
        r"\b(?:sk|pk|rk|api|key|token)[-_][A-Za-z0-9]{16,}\b", re.IGNORECASE
    ),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "CREDIT_CARD": re.compile(r"\b\d{4}(?:[ -]?\d{4}){3}\b"),
    "PHONE": re.compile(
        r"\b(?:\+?\d{1,2}[\s-]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    ),
    "IP": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}


def redact(
    text: str,
    patterns: Mapping[str, re.Pattern] | None = None,
    mask: str | Callable[[str], str] = "[{label}]",
) -> str:
    """Replace detected PII/secrets in ``text`` with a placeholder.

    Args:
        text: the text to scrub.
        patterns: label -> compiled regex map (defaults to
            :data:`DEFAULT_PII_PATTERNS`). Applied in iteration order.
        mask: a format string using ``{label}`` (default ``"[{label}]"``), or a
            callable taking the label and returning the replacement.

    Returns:
        The text with every match replaced.
    """
    if not text:
        return text
    patterns = patterns if patterns is not None else DEFAULT_PII_PATTERNS

    for label, pattern in patterns.items():
        replacement = mask(label) if callable(mask) else mask.format(label=label)
        # Pass a function so the replacement is treated literally (no \g / \1
        # backreference interpretation by re.sub).
        text = pattern.sub(lambda _m, r=replacement: r, text)
    return text


def find_pii(
    text: str, patterns: Mapping[str, re.Pattern] | None = None
) -> list[tuple[str, str]]:
    """Return a list of ``(label, matched_text)`` for every detection in ``text``."""
    patterns = patterns if patterns is not None else DEFAULT_PII_PATTERNS
    found: list[tuple[str, str]] = []
    for label, pattern in patterns.items():
        found.extend((label, m.group(0)) for m in pattern.finditer(text))
    return found
