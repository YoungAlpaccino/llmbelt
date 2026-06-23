"""Work with a group of environment variables that share a common prefix.

Apps often namespace their config (``MYAPP_HOST``, ``MYAPP_PORT``, …). These let
you treat that group as a single object or collect it into a dict, instead of
repeating the prefix at every lookup.
"""

from __future__ import annotations

import os
from collections.abc import Mapping


def collect_prefixed(
    prefix: str,
    strip: bool = True,
    lower: bool = True,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Collect every variable whose name starts with ``prefix`` into a dict.

    Args:
        prefix: the prefix to match (e.g. ``"MYAPP_"``).
        strip: remove the prefix from the resulting keys.
        lower: lower-case the resulting keys.
        environ: source mapping (defaults to ``os.environ``).
    """
    environ = os.environ if environ is None else environ
    result: dict[str, str] = {}
    for name, value in environ.items():
        if name.startswith(prefix):
            key = name[len(prefix) :] if strip else name
            if lower:
                key = key.lower()
            result[key] = value
    return result


class EnvNamespace:
    """A view over environment variables sharing ``prefix``.

    Example::

        db = EnvNamespace("DB_")
        db.host            # reads DB_HOST   (attribute access)
        db.get("port")     # reads DB_PORT
        db.as_dict()       # {"host": ..., "port": ...}
    """

    def __init__(self, prefix: str, environ: Mapping[str, str] | None = None):
        # set via __dict__ to avoid triggering __getattr__/__setattr__ recursion
        object.__setattr__(self, "prefix", prefix)
        object.__setattr__(self, "_environ", environ)

    def _source(self) -> Mapping[str, str]:
        return os.environ if self._environ is None else self._environ

    def get(self, name: str, default: str | None = None) -> str | None:
        return self._source().get(self.prefix + name.upper(), default)

    def __getattr__(self, name: str) -> str | None:
        if name.startswith("_"):
            raise AttributeError(name)
        return self._source().get(self.prefix + name.upper())

    def as_dict(self) -> dict[str, str]:
        return collect_prefixed(self.prefix, environ=self._source())

    def __repr__(self) -> str:
        return f"EnvNamespace(prefix={self.prefix!r}, keys={sorted(self.as_dict())})"
