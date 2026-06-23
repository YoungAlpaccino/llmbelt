from llmbelt import expand, resolve_layers


def test_expand_braced():
    env = {"HOST": "localhost", "PORT": "5432"}
    assert expand("https://${HOST}:${PORT}/db", env) == "https://localhost:5432/db"


def test_expand_bare():
    assert expand("$USER home", {"USER": "jane"}) == "jane home"


def test_expand_unknown_is_empty():
    assert expand("a${MISSING}b", {}) == "ab"


def test_expand_recursive():
    env = {"A": "${B}", "B": "deep"}
    assert expand("${A}", env) == "deep"


def test_expand_depth_cap_no_infinite_loop():
    env = {"A": "${B}", "B": "${A}"}
    # must terminate (cycle) rather than hang
    assert isinstance(expand("${A}", env), str)


def test_resolve_layers_precedence():
    defaults = {"HOST": "default-host", "PORT": "80"}
    dotenv = {"HOST": "file-host"}
    osenv = {"PORT": "443"}
    out = resolve_layers(defaults, dotenv, osenv)
    assert out["HOST"] == "file-host"   # dotenv overrode default
    assert out["PORT"] == "443"         # osenv overrode default


def test_resolve_layers_expands_refs():
    out = resolve_layers({"HOST": "h", "URL": "http://${HOST}"})
    assert out["URL"] == "http://h"


def test_resolve_layers_ignores_none():
    out = resolve_layers(None, {"A": "1"}, None)
    assert out == {"A": "1"}
