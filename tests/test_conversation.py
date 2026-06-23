from llmbelt import Conversation


def test_system_prompt_seeded():
    chat = Conversation(system="You are concise.")
    assert len(chat) == 1
    assert chat.messages[0] == {"role": "system", "content": "You are concise."}


def test_add_user_and_assistant():
    chat = Conversation()
    chat.user("hi").assistant("hello")
    roles = [m["role"] for m in chat.messages]
    assert roles == ["user", "assistant"]


def test_chaining_returns_self():
    chat = Conversation()
    assert chat.user("a") is chat


def test_messages_returns_copy():
    chat = Conversation()
    chat.user("hi")
    snapshot = chat.messages
    snapshot.append({"role": "user", "content": "tampered"})
    assert len(chat) == 1  # internal list untouched


def test_token_count_grows():
    chat = Conversation()
    chat.user("hello there")
    before = chat.token_count()
    chat.assistant("general kenobi, you are a bold one")
    assert chat.token_count() > before


def test_auto_trims_to_budget_keeping_system():
    chat = Conversation(system="SYSTEM PROMPT", max_tokens=30)
    for i in range(20):
        chat.user(f"message number {i} with some filler content")
    # system survives, history was trimmed below the cap
    assert chat.messages[0]["role"] == "system"
    assert chat.token_count() <= 30 or len(chat) <= 2


def test_clear_keeps_system_by_default():
    chat = Conversation(system="S")
    chat.user("a")
    chat.clear()
    assert [m["role"] for m in chat.messages] == ["system"]


def test_clear_all():
    chat = Conversation(system="S")
    chat.user("a")
    chat.clear(keep_system=False)
    assert len(chat) == 0


def test_iterable():
    chat = Conversation()
    chat.user("a").assistant("b")
    assert [m["content"] for m in chat] == ["a", "b"]
