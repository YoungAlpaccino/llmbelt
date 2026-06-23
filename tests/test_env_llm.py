from llmbelt import llm_settings_from_env


def _clear(monkeypatch):
    for name in [
        "OPENAI_API_KEY", "LLM_MODEL", "OPENAI_MODEL", "ANTHROPIC_MODEL", "MODEL",
        "LLM_BASE_URL", "OPENAI_BASE_URL", "OPENAI_API_BASE", "LLM_API_BASE",
        "LLM_TEMPERATURE", "LLM_MAX_TOKENS", "LLM_TIMEOUT",
    ]:
        monkeypatch.delenv(name, raising=False)


def test_defaults_all_none(monkeypatch):
    _clear(monkeypatch)
    s = llm_settings_from_env()
    assert s["provider"] == "openai"
    assert s["api_key"] is None
    assert s["model"] is None
    assert s["temperature"] is None


def test_reads_prefixed(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-x")
    monkeypatch.setenv("LLM_MODEL", "gpt-4o")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.2")
    monkeypatch.setenv("LLM_MAX_TOKENS", "1024")
    monkeypatch.setenv("LLM_TIMEOUT", "30")
    s = llm_settings_from_env()
    assert s["api_key"] == "sk-x"
    assert s["model"] == "gpt-4o"
    assert s["temperature"] == 0.2
    assert s["max_tokens"] == 1024
    assert s["timeout"] == 30.0


def test_model_fallback(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    assert llm_settings_from_env()["model"] == "gpt-4o-mini"


def test_base_url_fallback(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.example.com")
    assert llm_settings_from_env()["base_url"] == "https://api.example.com"


def test_provider_passthrough(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-a")
    s = llm_settings_from_env(provider="anthropic")
    assert s["provider"] == "anthropic"
    assert s["api_key"] == "sk-a"
