import pytest

from llmbelt import EnvConfig, EnvError


class Settings(EnvConfig):
    __prefix__ = "APP_"
    api_key: str
    timeout: float = 30.0
    retries: int = 3
    debug: bool = False
    hosts: list = []


def test_reads_with_prefix_and_defaults(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "sk-1")
    for k in ["APP_TIMEOUT", "APP_RETRIES", "APP_DEBUG", "APP_HOSTS"]:
        monkeypatch.delenv(k, raising=False)
    cfg = Settings.from_env()
    assert cfg.api_key == "sk-1"
    assert cfg.timeout == 30.0
    assert cfg.retries == 3
    assert cfg.debug is False
    assert cfg.hosts == []


def test_coerces_types(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "k")
    monkeypatch.setenv("APP_TIMEOUT", "12.5")
    monkeypatch.setenv("APP_RETRIES", "5")
    monkeypatch.setenv("APP_DEBUG", "true")
    monkeypatch.setenv("APP_HOSTS", "a, b ,c")
    cfg = Settings.from_env()
    assert cfg.timeout == 12.5
    assert cfg.retries == 5
    assert cfg.debug is True
    assert cfg.hosts == ["a", "b", "c"]


def test_missing_required_raises(monkeypatch):
    monkeypatch.delenv("APP_API_KEY", raising=False)
    with pytest.raises(EnvError):
        Settings.from_env()


def test_bad_int_raises(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "k")
    monkeypatch.setenv("APP_RETRIES", "notnum")
    with pytest.raises(EnvError):
        Settings.from_env()


def test_custom_environ_mapping():
    cfg = Settings.from_env(environ={"APP_API_KEY": "z", "APP_DEBUG": "yes"})
    assert cfg.api_key == "z"
    assert cfg.debug is True


def test_as_dict_and_repr(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "k")
    cfg = Settings.from_env()
    d = cfg.as_dict()
    assert d["api_key"] == "k" and "timeout" in d
    assert "Settings(" in repr(cfg)
