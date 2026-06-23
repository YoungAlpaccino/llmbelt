import pytest

from llmbelt import (
    EnvError,
    available_providers,
    get_api_key,
    has_api_key,
)


def _clear_keys(monkeypatch):
    for name in [
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "CLAUDE_API_KEY",
        "GOOGLE_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY",
        "MISTRAL_API_KEY", "COHERE_API_KEY", "DEEPSEEK_API_KEY",
        "TOGETHER_API_KEY", "OPENROUTER_API_KEY", "AZURE_OPENAI_API_KEY",
    ]:
        monkeypatch.delenv(name, raising=False)


def test_get_api_key_reads_primary(monkeypatch):
    _clear_keys(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-123")
    assert get_api_key("openai") == "sk-123"


def test_get_api_key_alias(monkeypatch):
    _clear_keys(monkeypatch)
    monkeypatch.setenv("CLAUDE_API_KEY", "sk-claude")
    assert get_api_key("anthropic") == "sk-claude"


def test_get_api_key_case_insensitive_provider(monkeypatch):
    _clear_keys(monkeypatch)
    monkeypatch.setenv("GROQ_API_KEY", "gk")
    assert get_api_key("GROQ") == "gk"


def test_missing_raises(monkeypatch):
    _clear_keys(monkeypatch)
    with pytest.raises(EnvError):
        get_api_key("openai")


def test_missing_optional_returns_none(monkeypatch):
    _clear_keys(monkeypatch)
    assert get_api_key("openai", required=False) is None
    assert has_api_key("openai") is False


def test_unknown_provider_uses_convention(monkeypatch):
    _clear_keys(monkeypatch)
    monkeypatch.setenv("FOOBAR_API_KEY", "fb")
    assert get_api_key("foobar") == "fb"


def test_available_providers(monkeypatch):
    _clear_keys(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("MISTRAL_API_KEY", "y")
    assert available_providers() == ["mistral", "openai"]
