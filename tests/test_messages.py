from llmbelt import count_message_tokens, trim_messages

CONV = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello there, how are you?"},
    {"role": "assistant", "content": "I'm doing well, thanks for asking!"},
    {"role": "user", "content": "Great. Tell me a joke."},
]


def test_count_is_positive_and_grows():
    one = count_message_tokens(CONV[:1])
    two = count_message_tokens(CONV[:2])
    assert one > 0
    assert two > one  # more messages -> more tokens


def test_count_handles_multimodal_content():
    msgs = [{"role": "user", "content": [{"type": "text", "text": "hi"}, "there"]}]
    assert count_message_tokens(msgs) > 0


def test_count_handles_missing_content():
    assert count_message_tokens([{"role": "user"}]) > 0


def test_trim_noop_when_under_budget():
    assert trim_messages(CONV, max_tokens=10_000) == CONV


def test_trim_drops_oldest_first_and_keeps_system():
    trimmed = trim_messages(CONV, max_tokens=count_message_tokens(CONV) - 1)
    assert len(trimmed) < len(CONV)
    # system survives
    assert trimmed[0]["role"] == "system"
    # the most recent user turn survives
    assert trimmed[-1]["content"] == "Great. Tell me a joke."
    # the oldest non-system message was the first dropped
    assert {"role": "user", "content": "Hello there, how are you?"} not in trimmed


def test_trim_preserves_order():
    trimmed = trim_messages(CONV, max_tokens=count_message_tokens(CONV) - 1)
    indices = [CONV.index(m) for m in trimmed]
    assert indices == sorted(indices)


def test_trim_can_drop_system_when_disabled():
    only_system = [{"role": "system", "content": "x " * 200}]
    trimmed = trim_messages(only_system, max_tokens=1, keep_system=False)
    assert trimmed == []


def test_trim_does_not_mutate_input():
    original = list(CONV)
    trim_messages(CONV, max_tokens=5)
    assert CONV == original
