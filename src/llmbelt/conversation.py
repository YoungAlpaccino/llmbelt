"""A small stateful chat-history container with automatic token budgeting.

Wraps the plain ``[{"role", "content"}, ...]`` list every chat API expects, and
keeps it within a token budget as you go (oldest turns drop, the system prompt
stays) so an agent loop never blows the context window.
"""

from __future__ import annotations

from collections.abc import Iterator

from llmbelt.messages import Message, count_message_tokens, trim_messages


class Conversation:
    """Append-only chat history that self-trims to ``max_tokens``.

    Example::

        chat = Conversation(system="You are concise.", max_tokens=8000)
        chat.user("Hello!")
        chat.assistant("Hi — how can I help?")
        response = client.chat(messages=chat.messages)   # plug into any SDK
    """

    def __init__(
        self,
        system: str | None = None,
        max_tokens: int | None = None,
        model: str | None = None,
    ):
        self.max_tokens = max_tokens
        self.model = model
        self._messages: list[Message] = []
        if system:
            self._messages.append({"role": "system", "content": system})

    def add(self, role: str, content: object) -> Conversation:
        """Append a message and re-apply the token budget. Returns ``self``."""
        self._messages.append({"role": role, "content": content})
        if self.max_tokens is not None:
            self._messages = trim_messages(
                self._messages, self.max_tokens, self.model
            )
        return self

    def user(self, content: object) -> Conversation:
        return self.add("user", content)

    def assistant(self, content: object) -> Conversation:
        return self.add("assistant", content)

    @property
    def messages(self) -> list[Message]:
        """A copy of the current message list, ready to pass to an API."""
        return list(self._messages)

    def token_count(self) -> int:
        return count_message_tokens(self._messages, self.model)

    def clear(self, keep_system: bool = True) -> None:
        """Drop the history (optionally keeping the system prompt)."""
        if keep_system:
            self._messages = [
                m for m in self._messages if m.get("role") == "system"
            ]
        else:
            self._messages = []

    def __len__(self) -> int:
        return len(self._messages)

    def __iter__(self) -> Iterator[Message]:
        return iter(self._messages)

    def __repr__(self) -> str:
        return (
            f"Conversation(messages={len(self._messages)}, "
            f"tokens={self.token_count()})"
        )
