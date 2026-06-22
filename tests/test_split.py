import pytest

from llmbelt import split_text


def test_empty():
    assert split_text("") == []


def test_short_text_single_chunk():
    assert split_text("hello world", chunk_size=100) == ["hello world"]


def test_no_overlap_reconstructs_text():
    text = "Para one.\n\nPara two is a bit longer.\n\nPara three here."
    chunks = split_text(text, chunk_size=20, overlap=0)
    assert "".join(chunks) == text


def test_prefers_paragraph_boundary():
    text = "AAAA\n\nBBBB"  # fits two paragraphs; chunk_size forces a split
    chunks = split_text(text, chunk_size=6, overlap=0)
    # split happens on the blank line, not mid-word
    assert chunks[0].strip() == "AAAA"
    assert chunks[-1].strip() == "BBBB"


def test_overlap_repeats_tail():
    text = "abcdefghij klmnopqrst uvwxyz"
    chunks = split_text(text, chunk_size=12, overlap=4)
    assert len(chunks) > 1
    # consecutive chunks share trailing/leading characters
    assert chunks[1].startswith(chunks[0][-4:])


def test_hard_split_when_no_separator():
    text = "x" * 25  # no whitespace at all
    chunks = split_text(text, chunk_size=10, overlap=0)
    assert chunks == ["xxxxxxxxxx", "xxxxxxxxxx", "xxxxx"]


def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        split_text("x", chunk_size=0)


def test_invalid_overlap():
    with pytest.raises(ValueError):
        split_text("x", chunk_size=4, overlap=4)
