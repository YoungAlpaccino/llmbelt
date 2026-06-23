import pytest

from llmbelt import EnvError, env_report, mask_secret, require_env


def test_require_env_ok(monkeypatch):
    monkeypatch.setenv("A", "1")
    monkeypatch.setenv("B", "2")
    assert require_env("A", "B") == {"A": "1", "B": "2"}


def test_require_env_lists_all_missing(monkeypatch):
    monkeypatch.setenv("A", "1")
    monkeypatch.delenv("B", raising=False)
    monkeypatch.delenv("C", raising=False)
    with pytest.raises(EnvError) as exc:
        require_env("A", "B", "C")
    msg = str(exc.value)
    assert "B" in msg and "C" in msg
    assert "A" not in msg.split(":", 1)[1]


def test_mask_secret():
    assert mask_secret("sk-supersecret") == "sk-s**********"
    assert mask_secret("ab") == "**"
    assert mask_secret("") == ""
    assert mask_secret(None) == ""


def test_mask_secret_custom():
    assert mask_secret("abcdef", show=2, mask_char="x") == "abxxxx"


def test_env_report_masks(monkeypatch):
    monkeypatch.setenv("KEY", "sk-abcdef123456")
    monkeypatch.delenv("MISSING", raising=False)
    report = env_report(["KEY", "MISSING"])
    assert "KEY=sk-a" in report
    assert "sk-abcdef123456" not in report
    assert "MISSING=(unset)" in report


def test_env_report_unmasked(monkeypatch):
    monkeypatch.setenv("KEY", "plain")
    assert "KEY=plain" in env_report(["KEY"], mask=False)
