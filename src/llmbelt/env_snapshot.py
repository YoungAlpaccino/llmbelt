"""Snapshot, diff, and freeze the environment for reproducible config.

Capture the variables your run depends on, compare two points in time (handy in
tests or to log what a ``.env`` load changed), and freeze a subset into an
immutable view so nothing mutates your config out from under you mid-run.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping


def snapshot_env(
    keys: Iterable[str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return a plain-dict copy of the environment (or just ``keys`` from it)."""
    environ = os.environ if environ is None else environ
    if keys is None:
        return dict(environ)
    return {key: environ[key] for key in keys if key in environ}


def diff_env(
    before: Mapping[str, str], after: Mapping[str, str]
) -> dict[str, dict]:
    """Compare two snapshots.

    Returns ``{"added": {...}, "removed": {...}, "changed": {k: (old, new)}}``.
    """
    added = {k: after[k] for k in after if k not in before}
    removed = {k: before[k] for k in before if k not in after}
    changed = {
        k: (before[k], after[k])
        for k in before
        if k in after and before[k] != after[k]
    }
    return {"added": added, "removed": removed, "changed": changed}


class FrozenEnv:
    """An immutable, read-only view of a set of environment values."""

    __slots__ = ("_data",)

    def __init__(self, data: Mapping[str, str]):
        object.__setattr__(self, "_data", dict(data))

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> str:
        return self._data[key]

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def as_dict(self) -> dict[str, str]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"FrozenEnv(keys={sorted(self._data)})"


def freeze_env(
    keys: Iterable[str] | None = None,
    environ: Mapping[str, str] | None = None,
) -> FrozenEnv:
    """Snapshot the environment (or ``keys``) into an immutable :class:`FrozenEnv`."""
    return FrozenEnv(snapshot_env(keys, environ))
