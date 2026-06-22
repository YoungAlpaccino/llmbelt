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


# Tried in order: paragraph, line, sentence, word, then raw characters as a
# last resort. The first separator actually present in the text is used.
_DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def split_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int | None = None,
    separators: list[str] | None = None,
) -> list[str]:
    """Split ``text`` on natural boundaries, keeping chunks near ``chunk_size``.

    Unlike :func:`chunk_text` (which cuts at fixed character offsets, often
    mid-word), this recursively prefers to break on paragraph, then line, then
    sentence, then word boundaries — so chunks stay semantically clean, which
    improves retrieval quality. Falls back to a hard character cut only when a
    single token is longer than ``chunk_size``.

    Args:
        text: the text to split.
        chunk_size: target max characters per chunk.
        overlap: characters of trailing context repeated at the start of the
            next chunk (0 <= overlap < chunk_size).
        separators: boundary markers to try, most-preferred first. Defaults to
            paragraph/line/sentence/word/character.

    Returns:
        A list of chunks. Empty input returns an empty list. ``chunk_size`` is a
        target, not a hard cap — a chunk may exceed it by up to ``overlap``.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap is None:
        overlap = min(100, chunk_size // 10)
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must satisfy 0 <= overlap < chunk_size")
    if not text:
        return []

    seps = separators if separators is not None else _DEFAULT_SEPARATORS
    pieces = _recursive_split(text, seps, chunk_size)
    return _merge_pieces(pieces, chunk_size, overlap)


def _split_keep(text: str, sep: str) -> list[str]:
    """Split on ``sep`` but keep it attached, so pieces still reconstruct ``text``."""
    if sep == "":
        return list(text)
    parts = text.split(sep)
    if len(parts) == 1:
        return parts
    return [p + sep for p in parts[:-1]] + [parts[-1]]


def _recursive_split(text: str, separators: list[str], chunk_size: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text] if text else []

    sep = separators[-1]
    remaining: list[str] = []
    for i, candidate in enumerate(separators):
        if candidate == "" or candidate in text:
            sep = candidate
            remaining = separators[i + 1 :]
            break

    result: list[str] = []
    for piece in _split_keep(text, sep):
        if not piece:
            continue
        if len(piece) <= chunk_size:
            result.append(piece)
        elif remaining:
            result.extend(_recursive_split(piece, remaining, chunk_size))
        else:  # no finer separator left — hard slice
            result.extend(
                piece[j : j + chunk_size] for j in range(0, len(piece), chunk_size)
            )
    return result


def _merge_pieces(pieces: list[str], chunk_size: int, overlap: int) -> list[str]:
    """Greedily pack small pieces up to ``chunk_size``, carrying ``overlap`` tail."""
    chunks: list[str] = []
    current = ""
    for piece in pieces:
        if current and len(current) + len(piece) > chunk_size:
            chunks.append(current)
            current = current[-overlap:] if overlap else ""
        current += piece
    if current:
        chunks.append(current)
    return chunks
