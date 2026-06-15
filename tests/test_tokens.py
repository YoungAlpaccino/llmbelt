from llmbelt import count_tokens, estimate_tokens, truncate_to_tokens


def test_estimate_tokens_empty():
    assert estimate_tokens("") == 0


def test_estimate_tokens_rough():
    assert estimate_tokens("a" * 40) == 10


def test_count_tokens_empty():
    assert count_tokens("") == 0


def test_count_tokens_nonzero():
    assert count_tokens("hello world") > 0


def test_truncate_already_fits():
    text = "short text"
    assert truncate_to_tokens(text, 100) == text


def test_truncate_shrinks_to_budget():
    text = "a" * 400
    out = truncate_to_tokens(text, 10)
    assert count_tokens(out) <= 10
    assert len(out) < len(text)


def test_truncate_zero_budget():
    assert truncate_to_tokens("anything", 0) == ""
