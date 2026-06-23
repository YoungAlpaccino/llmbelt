import pytest

from llmbelt import (
    EnvError,
    env_bool,
    env_float,
    env_int,
    env_list,
    env_str,
    get_env,
)


def test_get_env_default(monkeypatch):
    monkeypatch.delenv("LB_X", raising=False)
    assert get_env("LB_X", "fallback") == "fallback"
    assert get_env("LB_X") is None


def test_get_env_reads_value(monkeypatch):
    monkeypatch.setenv("LB_X", "hello")
    assert get_env("LB_X") == "hello"


def test_get_env_required_raises(monkeypatch):
    monkeypatch.delenv("LB_X", raising=False)
    with pytest.raises(EnvError):
        get_env("LB_X", required=True)


def test_get_env_cast_failure_raises(monkeypatch):
    monkeypatch.setenv("LB_X", "notanint")
    with pytest.raises(EnvError):
        get_env("LB_X", cast=int)


def test_env_int_float(monkeypatch):
    monkeypatch.setenv("LB_I", "42")
    monkeypatch.setenv("LB_F", "3.5")
    assert env_int("LB_I") == 42
    assert env_float("LB_F") == 3.5


def test_env_str_default(monkeypatch):
    monkeypatch.delenv("LB_S", raising=False)
    assert env_str("LB_S", "d") == "d"


@pytest.mark.parametrize("raw,expected", [
    ("1", True), ("true", True), ("YES", True), ("on", True),
    ("0", False), ("false", False), ("no", False), ("off", False),
])
def test_env_bool_values(monkeypatch, raw, expected):
    monkeypatch.setenv("LB_B", raw)
    assert env_bool("LB_B") is expected


def test_env_bool_default_and_invalid(monkeypatch):
    monkeypatch.delenv("LB_B", raising=False)
    assert env_bool("LB_B", default=True) is True
    monkeypatch.setenv("LB_B", "maybe")
    with pytest.raises(EnvError):
        env_bool("LB_B")


def test_env_list(monkeypatch):
    monkeypatch.setenv("LB_L", "a, b ,c,")
    assert env_list("LB_L") == ["a", "b", "c"]
    monkeypatch.delenv("LB_L", raising=False)
    assert env_list("LB_L") == []
    assert env_list("LB_L", default=["x"]) == ["x"]
