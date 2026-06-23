"""Assemble an LLM client configuration from the environment in one call.

Every project re-reads the same handful of variables — API key, model, base
URL, temperature — to construct a client. This gathers them (with sensible
fallbacks) into a dict you can splat straight into a client constructor.
"""

from __future__ import annotations

import os

from llmbelt.env import env_float, env_int, env_str
from llmbelt.env_keys import get_api_key

# Provider-specific fallback variables for model and base URL, tried when the
# generic LLM_* variable isn't set.
_MODEL_FALLBACKS = ["OPENAI_MODEL", "ANTHROPIC_MODEL", "MODEL"]
_BASE_URL_FALLBACKS = ["OPENAI_BASE_URL", "OPENAI_API_BASE", "LLM_API_BASE"]


def _first_set(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def llm_settings_from_env(
    provider: str = "openai", prefix: str = "LLM_"
) -> dict[str, object]:
    """Build an LLM client config dict from the environment.

    Keys: ``provider``, ``api_key``, ``model``, ``base_url``, ``temperature``,
    ``max_tokens``, ``timeout``. Unset numeric/url/model values come back as
    ``None`` so you can filter them before constructing a client.

    Args:
        provider: provider name used to resolve the API key (see
            :func:`llmbelt.get_api_key`).
        prefix: prefix for the generic settings (defaults to ``"LLM_"``).
    """
    return {
        "provider": provider,
        "api_key": get_api_key(provider, required=False),
        "model": env_str(prefix + "MODEL") or _first_set(*_MODEL_FALLBACKS),
        "base_url": env_str(prefix + "BASE_URL") or _first_set(*_BASE_URL_FALLBACKS),
        "temperature": env_float(prefix + "TEMPERATURE"),
        "max_tokens": env_int(prefix + "MAX_TOKENS"),
        "timeout": env_float(prefix + "TIMEOUT"),
    }
