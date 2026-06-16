import pytest

from llmbelt import chunk_by_tokens

# Plain ASCII so the assertions hold on both the tiktoken (exact) and the
# heuristic (no-tiktoken) code paths.
_TEXT = "the quick brown fox jumps over the lazy dog " * 50


def test_empty():
    assert chunk_by_tokens("") == []


def test_single_chunk_fits():
    assert chunk_by_tokens("hello world", chunk_size=1000) == ["hello world"]


def test_multiple_chunks():
    chunks = chunk_by_tokens(_TEXT, chunk_size=20)
    assert len(chunks) > 1
    assert all(isinstance(c, str) and c for c in chunks)


def test_no_overlap_reconstructs_text():
    chunks = chunk_by_tokens(_TEXT, chunk_size=20, overlap=0)
    assert "".join(chunks) == _TEXT


def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_by_tokens("x", chunk_size=0)


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_by_tokens("x", chunk_size=4, overlap=4)
