"""Expand ``${VAR}`` references in values, and resolve layered config.

Config files often reference other variables (``URL=https://${HOST}:${PORT}``).
These expand those references and merge layered sources (defaults < .env <
process environment) into one resolved mapping.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping

# ${VAR} or $VAR
_REF = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def expand(
    value: str,
    environ: Mapping[str, str] | None = None,
    max_depth: int = 10,
) -> str:
    """Replace ``${VAR}`` / ``$VAR`` in ``value`` with values from ``environ``.

    Resolves repeatedly (so references-to-references work), stopping after
    ``max_depth`` passes to avoid infinite loops. Unknown references expand to
    an empty string.
    """
    environ = os.environ if environ is None else environ

    def replace(match: re.Match) -> str:
        name = match.group(1) or match.group(2)
        return environ.get(name, "")

    previous = None
    current = value
    depth = 0
    while current != previous and depth < max_depth:
        previous = current
        current = _REF.sub(replace, current)
        depth += 1
    return current


def resolve_layers(*layers: Mapping[str, str] | None) -> dict[str, str]:
    """Merge mappings left-to-right (later overrides), then expand ``${refs}``.

    Example::

        resolve_layers(defaults, dotenv_values, os.environ)
    """
    merged: dict[str, str] = {}
    for layer in layers:
        if layer:
            merged.update(layer)
    return {
        key: expand(value, merged) if isinstance(value, str) else value
        for key, value in merged.items()
    }
