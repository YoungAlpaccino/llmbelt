"""Token counting and budgeting for chat-format message lists.

A "message" here is a mapping like ``{"role": "user", "content": "..."}`` — the
shape every chat completion API uses. These helpers let you measure a whole
conversation and trim it to fit a context window without dropping the system
prompt.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from llmbelt.tokens import count_tokens

# Each message carries a little framing (role markers, separators) on top of its
# content. ~4 tokens/message is the commonly-used approximation for OpenAI chat.
_PER_MESSAGE_OVERHEAD = 4
# A couple of tokens prime the assistant's reply at the end of the list.
_REPLY_PRIMING = 2

Message = Mapping[str, object]


def _content_text(content: object) -> str:
    """Flatten a message's ``content`` to plain text for counting.

    Handles a plain string, or a list of content blocks (multimodal format),
    pulling the text out of each block.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, Sequence):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, Mapping):
                text = block.get("text") or block.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts)
    return str(content)


def count_message_tokens(
    messages: Sequence[Message], model: str | None = None
) -> int:
    """Estimate the token count of a list of chat messages.

    Counts each message's role and content plus a small per-message framing
    overhead, mirroring how chat APIs bill the conversation. Exact-ish with
    ``tiktoken`` installed, heuristic otherwise (see :func:`count_tokens`).
    """
    total = 0
    for message in messages:
        total += _PER_MESSAGE_OVERHEAD
        role = message.get("role")
        if isinstance(role, str):
            total += count_tokens(role, model)
        total += count_tokens(_content_text(message.get("content")), model)
    return total + _REPLY_PRIMING


def trim_messages(
    messages: Sequence[Message],
    max_tokens: int,
    model: str | None = None,
    keep_system: bool = True,
) -> list[Message]:
    """Drop the oldest messages until the conversation fits ``max_tokens``.

    The most recent messages are preserved (they matter most), and the oldest
    droppable messages are removed first. ``system`` messages are protected by
    default — they hold the instructions you don't want to lose. Original order
    is preserved.

    If even the protected messages exceed ``max_tokens``, they're returned
    as-is (this function never drops a protected message).

    Returns a new list; the input is not modified.
    """
    messages = list(messages)
    if count_message_tokens(messages, model) <= max_tokens:
        return messages

    def protected(message: Message) -> bool:
        return keep_system and message.get("role") == "system"

    dropped: set[int] = set()
    for i, message in enumerate(messages):
        current = [m for j, m in enumerate(messages) if j not in dropped]
        if count_message_tokens(current, model) <= max_tokens:
            return current
        if not protected(message):
            dropped.add(i)
    return [m for j, m in enumerate(messages) if j not in dropped]
