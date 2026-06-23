"""Read environment variables with types, defaults, and clear errors.

``os.environ.get`` gives you a string or ``None`` and leaves casting, validation,
and "this is required" handling to you. These helpers do that consistently and
raise a single, descriptive :class:`EnvError` when something's wrong — so a
misconfigured deployment fails loudly at startup instead of deep in a request.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

_UNSET = object()  # sentinel: distinguishes "no default given" from ``default=None``


class EnvError(RuntimeError):
    """Raised when a required environment variable is missing or won't cast."""


def get_env(
    name: str,
    default: Any = _UNSET,
    cast: Callable[[str], Any] | None = None,
    required: bool = False,
) -> Any:
    """Read ``name`` from the environment, optionally casting it.

    Args:
        name: the variable name.
        default: value returned when unset/empty. If omitted and not
            ``required``, returns ``None``.
        cast: a callable applied to the raw string (e.g. ``int``).
        required: if true and the variable is unset/empty, raise ``EnvError``.

    Raises:
        EnvError: if required and missing, or if ``cast`` fails.
    """
    raw = os.environ.get(name)
    if raw is None or raw == "":
        if required:
            raise EnvError(f"Required environment variable {name!r} is not set.")
        return None if default is _UNSET else default
    if cast is None:
        return raw
    try:
        return cast(raw)
    except (ValueError, TypeError) as exc:
        cast_name = getattr(cast, "__name__", repr(cast))
        raise EnvError(
            f"Environment variable {name!r}={raw!r} could not be cast "
            f"via {cast_name}: {exc}"
        ) from exc


def env_str(name: str, default: str | None = None) -> str | None:
    """Read a string environment variable."""
    return get_env(name, default)


def env_int(name: str, default: int | None = None) -> int | None:
    """Read an integer environment variable."""
    return get_env(name, default, cast=int)


def env_float(name: str, default: float | None = None) -> float | None:
    """Read a float environment variable."""
    return get_env(name, default, cast=float)


_TRUE = {"1", "true", "yes", "on", "y", "t"}
_FALSE = {"0", "false", "no", "off", "n", "f"}


def env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean environment variable (``true/1/yes/on`` → True)."""
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    value = raw.strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise EnvError(
        f"Environment variable {name!r}={raw!r} is not a valid boolean."
    )


def env_list(
    name: str, default: list[str] | None = None, sep: str = ","
) -> list[str]:
    """Read a delimited environment variable into a list (empty items dropped)."""
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return list(default) if default is not None else []
    return [part.strip() for part in raw.split(sep) if part.strip()]
