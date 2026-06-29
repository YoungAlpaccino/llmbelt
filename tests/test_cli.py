import pytest

from llmbelt.cli import main


def test_tokens(capsys):
    rc = main(["tokens", "hello world"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert int(out) > 0


def test_tokens_from_stdin(monkeypatch, capsys):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO("hello from stdin"))
    rc = main(["tokens", "-"])
    assert rc == 0
    assert int(capsys.readouterr().out.strip()) > 0


def test_cost(capsys):
    rc = main(["cost", "--in", "1000000", "--out", "0", "-m", "gpt-4o-mini"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "$0.150000"


def test_cost_unknown_model(capsys):
    rc = main(["cost", "--in", "1", "--out", "1", "-m", "nope"])
    assert rc == 1
    assert "Unknown model" in capsys.readouterr().err


def test_redact(capsys):
    rc = main(["redact", "email me at a@b.com"])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == "email me at [EMAIL]"


def test_env_report(monkeypatch, capsys):
    monkeypatch.setenv("LB_KEY", "sk-abcdef123456")
    rc = main(["env", "report", "LB_KEY"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "LB_KEY=sk-a" in out
    assert "sk-abcdef123456" not in out


def test_env_report_no_mask(monkeypatch, capsys):
    monkeypatch.setenv("LB_KEY", "plain")
    main(["env", "report", "LB_KEY", "--no-mask"])
    assert "LB_KEY=plain" in capsys.readouterr().out


def test_env_check_ok(monkeypatch, capsys):
    monkeypatch.setenv("LB_A", "1")
    rc = main(["env", "check", "LB_A"])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "OK"


def test_env_check_missing(monkeypatch, capsys):
    monkeypatch.delenv("LB_MISSING", raising=False)
    rc = main(["env", "check", "LB_MISSING"])
    assert rc == 1
    assert "LB_MISSING" in capsys.readouterr().err


def test_env_keys(monkeypatch, capsys):
    for n in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "CLAUDE_API_KEY"]:
        monkeypatch.delenv(n, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    rc = main(["env", "keys"])
    assert rc == 0
    assert "openai" in capsys.readouterr().out


def test_no_command_prints_help(capsys):
    rc = main([])
    assert rc == 1
    assert "usage" in capsys.readouterr().out.lower()


def test_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert "llmbelt" in capsys.readouterr().out
