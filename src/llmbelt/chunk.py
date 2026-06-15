"""Split text into overlapping chunks for RAG / embedding pipelines."""

from __future__ import annotations


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
