import pytest

from llmbelt import PromptTemplate


def test_render():
    t = PromptTemplate("Hello {name}!")
    assert t.render(name="Ada") == "Hello Ada!"


def test_variables_detected():
    t = PromptTemplate("{a} and {b}")
    assert t.variables == {"a", "b"}


def test_no_variables():
    t = PromptTemplate("static text")
    assert t.variables == set()
    assert t.render() == "static text"


def test_missing_variable_raises():
    t = PromptTemplate("Hi {name}")
    with pytest.raises(KeyError):
        t.render()


def test_extra_kwargs_ignored():
    t = PromptTemplate("Hi {name}")
    assert t.render(name="X", extra="ignored") == "Hi X"
