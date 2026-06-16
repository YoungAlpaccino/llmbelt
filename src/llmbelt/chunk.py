"""Split text into overlapping chunks for RAG / embedding pipelines."""

from __future__ import annotations

from llmbelt.tokens import _CHARS_PER_TOKEN, _get_encoding


def chunk_text(
    text: str, chunk_size: int = 1000, overlap: int | None = None
) -> list[str]:
    """Split ``text`` into chunks of ``chunk_size`` characters.

    Consecutive chunks share ``overlap`` characters so that information sitting
    on a boundary isn't split in half (a common RAG failure mode).

    Args:
        text: the text to split.
        chunk_size: max characters per chunk (must be > 0).
        overlap: characters shared between consecutive chunks
            (0 <= overlap < chunk_size). Defaults to ~10% of ``chunk_size``,
            so it stays valid for any chunk size.

    Returns:
        A list of chunks. Empty input returns an empty list.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap is None:
        overlap = min(100, chunk_size // 10)
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must satisfy 0 <= overlap < chunk_size")
    if not text:
        return []

    chunks: list[str] = []
    step = chunk_size - overlap
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += step
    return chunks


def chunk_by_tokens(
    text: str,
    chunk_size: int = 500,
    overlap: int | None = None,
    model: str | None = None,
) -> list[str]:
    """Split ``text`` into chunks of at most ``chunk_size`` *tokens*.

    Like :func:`chunk_text`, but the budget is tokens rather than characters —
    which is what an embedding model or context window actually limits. With
    ``tiktoken`` installed this is exact (token slices are decoded back to text);
    otherwise it approximates using ~4 characters per token, so the library keeps
    zero *required* dependencies.

    Args:
        text: the text to split.
        chunk_size: max tokens per chunk (must be > 0).
        overlap: tokens shared between consecutive chunks
            (0 <= overlap < chunk_size). Defaults to ~10% of ``chunk_size``.
        model: optional model name to pick the tiktoken encoding.

    Returns:
        A list of chunks. Empty input returns an empty list.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap is None:
        overlap = min(50, chunk_size // 10)
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must satisfy 0 <= overlap < chunk_size")
    if not text:
        return []

    try:
        enc = _get_encoding(model)
    except ImportError:
        # No tiktoken — approximate token budgets as character budgets.
        return chunk_text(
            text, chunk_size * _CHARS_PER_TOKEN, overlap * _CHARS_PER_TOKEN
        )

    ids = enc.encode(text)
    chunks: list[str] = []
    step = chunk_size - overlap
    start = 0
    while start < len(ids):
        chunks.append(enc.decode(ids[start : start + chunk_size]))
        start += step
    return chunks
