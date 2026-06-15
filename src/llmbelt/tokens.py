"""Token counting and budgeting.

Uses ``tiktoken`` if it's installed (accurate for OpenAI-family models),
otherwise falls back to a fast character-based heuristic — so the library keeps
zero *required* dependencies.
"""

from __future__ import annotations

_CHARS_PER_TOKEN = 4  # rough English average (~4 chars per token)


def estimate_tokens(text: str) -> int:
    """Heuristic token count with no dependencies (~4 chars per token)."""
    if not text:
        return 0
    return max(1, round(len(text) / _CHARS_PER_TOKEN))


def count_tokens(text: str, model: str | None = None) -> int:
    """Count tokens in ``text``.

    If ``tiktoken`` is installed, returns an exact count (using the encoding for
    ``model`` when known, else ``cl100k_base``). Otherwise estimates.
    """
    if not text:
        return 0
    try:
        import tiktoken
    except ImportError:
        return estimate_tokens(text)

    try:
        enc = (
            tiktoken.encoding_for_model(model)
            if model
            else tiktoken.get_encoding("cl100k_base")
        )
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def truncate_to_tokens(text: str, max_tokens: int, model: str | None = None) -> str:
    """Truncate ``text`` so it fits within ``max_tokens`` (best-effort).

    Uses a binary search on character length, so it works with both the exact
    and the heuristic token counters.
    """
    if max_tokens <= 0:
        return ""
    if count_tokens(text, model) <= max_tokens:
        return text

    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if count_tokens(text[:mid], model) <= max_tokens:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo]
