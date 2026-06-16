"""Pull structured JSON out of a free-form LLM response.

Models rarely return clean JSON: they wrap it in ```` ```json ```` fences, add a
"Sure, here you go:" preamble, or trail an explanation after the object. This
finds and parses the first JSON value in the text so you don't re-write the same
brittle regex on every project.
"""

from __future__ import annotations

import json
import re
from typing import Any

# Matches a fenced code block, optionally tagged ```json. Non-greedy so the
# first complete block wins.
_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)

_MISSING = object()  # sentinel so ``default=None`` is distinguishable from unset


def extract_json(text: str, default: Any = _MISSING) -> Any:
    """Extract and parse the first JSON value from ``text``.

    Handles the common LLM output shapes: a bare JSON value, a value wrapped in
    a ```` ```json ```` (or plain ```` ``` ````) fence, and a value embedded in
    surrounding prose.

    Args:
        text: the raw model response.
        default: value to return when no JSON is found. If omitted, a
            ``ValueError`` is raised instead.

    Returns:
        The parsed JSON value (``dict``, ``list``, ``str``, ``int``, etc.).

    Raises:
        ValueError: if no JSON value is found and no ``default`` was given.
    """
    if text:
        # Prefer fenced blocks (the model's explicit "this is the data" marker),
        # then fall back to scanning the whole string.
        candidates = [m.group(1).strip() for m in _FENCE_RE.finditer(text)]
        candidates.append(text.strip())
        for candidate in candidates:
            result = _parse_or_scan(candidate)
            if result is not _MISSING:
                return result

    if default is not _MISSING:
        return default
    raise ValueError("No JSON value found in text.")


def _parse_or_scan(candidate: str) -> Any:
    """Try to parse ``candidate`` whole, else scan for the first JSON value."""
    try:
        return json.loads(candidate)
    except ValueError:
        return _scan_balanced(candidate)


def _scan_balanced(s: str) -> Any:
    """Find the first balanced ``{...}`` or ``[...]`` and parse it.

    Walks the string tracking bracket depth, ignoring brackets inside string
    literals, and parses the first complete top-level value. Returns ``_MISSING``
    if none is found or it doesn't parse.
    """
    start = next((i for i, ch in enumerate(s) if ch in "{["), None)
    if start is None:
        return _MISSING

    open_ch = s[start]
    close_ch = "}" if open_ch == "{" else "]"
    depth = 0
    in_str = False
    escaped = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(s[start : i + 1])
                except ValueError:
                    return _MISSING
    return _MISSING
