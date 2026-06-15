import pytest

from llmbelt import chunk_text


def test_empty():
    assert chunk_text("") == []


def test_single_chunk():
    assert chunk_text("hello", chunk_size=100) == ["hello"]


def test_multiple_chunks_with_overlap():
    text = "abcdefghij"  # 10 chars
    # chunk_size=4, overlap=1 -> step=3
    assert chunk_text(text, chunk_size=4, overlap=1) == ["abcd", "defg", "ghij", "j"]


def test_no_overlap():
    assert chunk_text("abcdef", chunk_size=2, overlap=0) == ["ab", "cd", "ef"]


def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("x", chunk_size=0)


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("x", chunk_size=4, overlap=4)
