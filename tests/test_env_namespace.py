from llmbelt import EnvNamespace, collect_prefixed


def test_collect_prefixed(monkeypatch):
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("OTHER", "x")
    out = collect_prefixed("DB_")
    assert out == {"host": "localhost", "port": "5432"}


def test_collect_prefixed_no_strip_no_lower(monkeypatch):
    monkeypatch.setenv("DB_HOST", "h")
    out = collect_prefixed("DB_", strip=False, lower=False)
    assert out["DB_HOST"] == "h"


def test_namespace_get_and_attr(monkeypatch):
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")
    ns = EnvNamespace("DB_")
    assert ns.get("host") == "localhost"
    assert ns.host == "localhost"
    assert ns.port == "5432"


def test_namespace_missing_attr_is_none(monkeypatch):
    monkeypatch.delenv("DB_MISSING", raising=False)
    ns = EnvNamespace("DB_")
    assert ns.missing is None
    assert ns.get("missing", "fallback") == "fallback"


def test_namespace_as_dict():
    ns = EnvNamespace("APP_", environ={"APP_A": "1", "APP_B": "2", "X": "y"})
    assert ns.as_dict() == {"a": "1", "b": "2"}


def test_namespace_custom_environ():
    ns = EnvNamespace("Q_", environ={"Q_NAME": "value"})
    assert ns.name == "value"
