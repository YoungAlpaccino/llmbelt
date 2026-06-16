import pytest

from llmbelt import extract_json


def test_bare_object():
    assert extract_json('{"a": 1, "b": [2, 3]}') == {"a": 1, "b": [2, 3]}


def test_bare_array():
    assert extract_json("[1, 2, 3]") == [1, 2, 3]


def test_json_fence():
    text = 'Sure, here you go:\n```json\n{"ok": true}\n```\nHope that helps!'
    assert extract_json(text) == {"ok": True}


def test_plain_fence():
    assert extract_json("```\n{\"x\": 1}\n```") == {"x": 1}


def test_embedded_in_prose():
    text = 'The result is {"score": 0.9} according to the model.'
    assert extract_json(text) == {"score": 0.9}


def test_ignores_braces_inside_strings():
    text = 'prefix {"note": "a } inside a string"} suffix'
    assert extract_json(text) == {"note": "a } inside a string"}


def test_first_value_wins():
    assert extract_json('{"first": 1} then {"second": 2}') == {"first": 1}


def test_no_json_raises():
    with pytest.raises(ValueError):
        extract_json("there is no json here")


def test_no_json_returns_default():
    assert extract_json("nope", default=None) is None
    assert extract_json("", default={}) == {}
