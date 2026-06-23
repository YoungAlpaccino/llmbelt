from llmbelt import EnvConfig, env_template, env_template_from_config


def test_template_from_name_list():
    out = env_template(["A", "B"])
    assert "A=" in out
    assert "B=" in out
    assert out.startswith("#")


def test_template_from_tuples():
    out = env_template([("API_KEY", "", "your key"), ("PORT", 8080, "the port")])
    assert "# your key" in out
    assert "API_KEY=" in out
    assert "PORT=8080" in out


def test_template_from_mapping():
    out = env_template({"HOST": "the hostname"})
    assert "# the hostname" in out
    assert "HOST=" in out


class Settings(EnvConfig):
    __prefix__ = "APP_"
    api_key: str
    timeout: float = 30.0
    debug: bool = False


def test_template_from_config():
    out = env_template_from_config(Settings)
    assert "APP_API_KEY=" in out
    assert "required" in out
    assert "APP_TIMEOUT=30.0" in out
    assert "APP_DEBUG=" in out
    assert "optional" in out


def test_template_ends_with_newline():
    assert env_template(["X"]).endswith("\n")
