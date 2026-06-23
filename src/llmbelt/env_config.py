"""Declarative, typed configuration loaded from the environment.

Subclass :class:`EnvConfig`, annotate the fields you need (with optional
defaults and an optional ``__prefix__``), and call ``from_env()``. Each field is
read from ``PREFIX + FIELD_NAME.upper()``, coerced to its annotated type, and
missing-but-required fields raise a single clear :class:`EnvError`. One object,
fully typed, instead of ``os.environ.get`` scattered everywhere.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any, get_type_hints

from llmbelt.env import EnvError

_UNSET = object()
_TRUE = {"1", "true", "yes", "on", "y", "t"}
_FALSE = {"0", "false", "no", "off", "n", "f"}


def _coerce(raw: str, annotation: Any, env_name: str) -> Any:
    """Coerce a raw env string to the annotated Python type."""
    if annotation in (str, None, Any):
        return raw
    if annotation is bool:
        value = raw.strip().lower()
        if value in _TRUE:
            return True
        if value in _FALSE:
            return False
        raise EnvError(f"{env_name}={raw!r} is not a valid boolean.")
    if annotation is int:
        try:
            return int(raw)
        except ValueError as exc:
            raise EnvError(f"{env_name}={raw!r} is not an int: {exc}") from exc
    if annotation is float:
        try:
            return float(raw)
        except ValueError as exc:
            raise EnvError(f"{env_name}={raw!r} is not a float: {exc}") from exc
    if annotation in (list, list[str]):
        return [p.strip() for p in raw.split(",") if p.strip()]
    return raw


class EnvConfig:
    """Base class for environment-backed config objects.

    Example::

        class Settings(EnvConfig):
            __prefix__ = "APP_"
            api_key: str                 # required (no default)
            timeout: float = 30.0
            debug: bool = False
            hosts: list = []

        cfg = Settings.from_env()        # reads APP_API_KEY, APP_TIMEOUT, ...
    """

    __prefix__: str = ""

    @classmethod
    def _annotations(cls) -> dict[str, Any]:
        try:
            return get_type_hints(cls)
        except Exception:
            merged: dict[str, Any] = {}
            for klass in reversed(cls.__mro__):
                merged.update(getattr(klass, "__annotations__", {}))
            return merged

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> EnvConfig:
        """Build an instance by reading each annotated field from the environment."""
        environ = os.environ if environ is None else environ
        instance = cls()
        for field, annotation in cls._annotations().items():
            if field.startswith("_"):
                continue
            env_name = cls.__prefix__ + field.upper()
            default = getattr(cls, field, _UNSET)
            raw = environ.get(env_name)
            if raw is None or raw == "":
                if default is _UNSET:
                    raise EnvError(
                        f"Required environment variable {env_name!r} "
                        f"(for {cls.__name__}.{field}) is not set."
                    )
                setattr(instance, field, default)
            else:
                setattr(instance, field, _coerce(raw, annotation, env_name))
        return instance

    def as_dict(self) -> dict[str, Any]:
        return {
            field: getattr(self, field)
            for field in self._annotations()
            if not field.startswith("_")
        }

    def __repr__(self) -> str:
        items = ", ".join(f"{k}={v!r}" for k, v in self.as_dict().items())
        return f"{type(self).__name__}({items})"
