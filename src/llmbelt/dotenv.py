"""A minimal, zero-dependency ``.env`` file loader.

Just enough to load local config in development without pulling in
``python-dotenv``: walk up to find a ``.env``, parse ``KEY=VALUE`` lines (with
``export`` prefixes, quotes, and ``#`` comments), and put them in
``os.environ`` — without clobbering values already set, by default.
"""

from __future__ import annotations

import os
from pathlib import Path


def parse_dotenv(text: str) -> dict[str, str]:
    """Parse ``.env``-style text into a dict. Does not touch ``os.environ``."""
    data: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # strip a single layer of matching quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            data[key] = value
    return data


def find_dotenv(filename: str = ".env", start: str | None = None) -> str | None:
    """Search ``start`` (or cwd) and its parents for ``filename``."""
    current = Path(start or os.getcwd()).resolve()
    for directory in (current, *current.parents):
        candidate = directory / filename
        if candidate.is_file():
            return str(candidate)
    return None


def load_dotenv(
    path: str | None = None, override: bool = False
) -> dict[str, str]:
    """Load a ``.env`` file into ``os.environ`` and return what was applied.

    Args:
        path: the file to load. If ``None``, searches up from the cwd.
        override: if true, overwrite variables already in the environment.

    Returns:
        The mapping of variables actually set (empty if no file was found).
    """
    if path is None:
        path = find_dotenv()
    if path is None or not Path(path).is_file():
        return {}
    parsed = parse_dotenv(Path(path).read_text(encoding="utf-8"))
    applied: dict[str, str] = {}
    for key, value in parsed.items():
        if override or key not in os.environ:
            os.environ[key] = value
            applied[key] = value
    return applied
