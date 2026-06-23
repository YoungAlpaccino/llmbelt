from llmbelt import find_dotenv, load_dotenv, parse_dotenv


def test_parse_basic():
    text = "A=1\nB=hello\n"
    assert parse_dotenv(text) == {"A": "1", "B": "hello"}


def test_parse_comments_and_blanks():
    text = "# a comment\n\nA=1\n   # indented comment\nB=2\n"
    assert parse_dotenv(text) == {"A": "1", "B": "2"}


def test_parse_export_and_quotes():
    text = "export A=\"quoted value\"\nB='single'\n"
    assert parse_dotenv(text) == {"A": "quoted value", "B": "single"}


def test_parse_value_with_equals():
    assert parse_dotenv("URL=postgres://u:p@h/db?x=1") == {
        "URL": "postgres://u:p@h/db?x=1"
    }


def test_find_dotenv(tmp_path):
    env = tmp_path / ".env"
    env.write_text("X=1")
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert find_dotenv(start=str(nested)) == str(env)


def test_find_dotenv_missing(tmp_path):
    assert find_dotenv(filename=".nope", start=str(tmp_path)) is None


def test_load_dotenv_sets_and_respects_existing(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("NEW_VAR=fromfile\nEXISTING=fromfile\n")
    monkeypatch.delenv("NEW_VAR", raising=False)
    monkeypatch.setenv("EXISTING", "preset")

    applied = load_dotenv(str(env))
    assert applied == {"NEW_VAR": "fromfile"}  # EXISTING not overridden
    import os
    assert os.environ["NEW_VAR"] == "fromfile"
    assert os.environ["EXISTING"] == "preset"


def test_load_dotenv_override(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("EXISTING=fromfile\n")
    monkeypatch.setenv("EXISTING", "preset")
    load_dotenv(str(env), override=True)
    import os
    assert os.environ["EXISTING"] == "fromfile"


def test_load_dotenv_missing_file_returns_empty(tmp_path):
    assert load_dotenv(str(tmp_path / "nope.env")) == {}
