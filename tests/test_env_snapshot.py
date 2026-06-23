import pytest

from llmbelt import FrozenEnv, diff_env, freeze_env, snapshot_env


def test_snapshot_all(monkeypatch):
    monkeypatch.setenv("SNAP_X", "1")
    snap = snapshot_env()
    assert snap["SNAP_X"] == "1"
    assert isinstance(snap, dict)


def test_snapshot_subset(monkeypatch):
    monkeypatch.setenv("SNAP_A", "1")
    monkeypatch.setenv("SNAP_B", "2")
    monkeypatch.delenv("SNAP_MISSING", raising=False)
    snap = snapshot_env(["SNAP_A", "SNAP_MISSING"])
    assert snap == {"SNAP_A": "1"}


def test_diff_env():
    before = {"A": "1", "B": "2", "C": "3"}
    after = {"A": "1", "B": "changed", "D": "4"}
    d = diff_env(before, after)
    assert d["added"] == {"D": "4"}
    assert d["removed"] == {"C": "3"}
    assert d["changed"] == {"B": ("2", "changed")}


def test_freeze_env_readonly():
    fe = freeze_env(environ={"A": "1", "B": "2"})
    assert isinstance(fe, FrozenEnv)
    assert fe["A"] == "1"
    assert fe.get("missing", "d") == "d"
    assert "A" in fe
    assert len(fe) == 2
    assert sorted(fe) == ["A", "B"]
    with pytest.raises(AttributeError):
        fe.something = "x"  # __slots__ + immutable


def test_freeze_env_as_dict_is_copy():
    fe = freeze_env(environ={"A": "1"})
    d = fe.as_dict()
    d["A"] = "tampered"
    assert fe["A"] == "1"
