"""Validate required environment variables up front, and mask secrets for logs.

Fail fast: check everything you need at startup and get one error listing all the
gaps, instead of discovering a missing key mid-request. And when you *do* log
config, mask the secret values so keys don't leak into your logs.
"""

from __future__ import annotations

import os
from collections.abc import Iterable

from llmbelt.env import EnvError


def require_env(*names: str) -> dict[str, str]:
    """Ensure every variable in ``names`` is set and non-empty.

    Returns a dict of the values on success. Raises ``EnvError`` naming *all*
    missing variables (not just the first) so one run surfaces every gap.
    """
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        raise EnvError(
            "Missing required environment variables: " + ", ".join(missing)
        )
    return {name: os.environ[name] for name in names}


def mask_secret(value: str | None, show: int = 4, mask_char: str = "*") -> str:
    """Mask a secret, revealing only the first ``show`` characters.

    ``"sk-supersecret"`` -> ``"sk-s**********"``. Short values are fully masked.
    """
    if not value:
        return ""
    if len(value) <= show:
        return mask_char * len(value)
    return value[:show] + mask_char * (len(value) - show)


def env_report(names: Iterable[str], mask: bool = True) -> str:
    """Build a ``NAME=value`` report for ``names`` (secrets masked by default)."""
    lines: list[str] = []
    for name in names:
        raw = os.environ.get(name)
        if raw is None:
            shown = "(unset)"
        else:
            shown = mask_secret(raw) if mask else raw
        lines.append(f"{name}={shown}")
    return "\n".join(lines)
