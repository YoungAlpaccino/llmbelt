"""Resolve LLM provider API keys from the conventional environment variables.

Every provider documents its own key variable (and some have aliases). This
looks them up so you don't hard-code variable names all over your app, and gives
a single clear error listing what to set when a key is missing.
"""

from __future__ import annotations

import os

from llmbelt.env import EnvError

# provider -> ordered list of env vars to try (first non-empty wins)
PROVIDER_ENV_VARS: dict[str, list[str]] = {
    "openai": ["OPENAI_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"],
    "google": ["GOOGLE_API_KEY", "GEMINI_API_KEY"],
    "groq": ["GROQ_API_KEY"],
    "mistral": ["MISTRAL_API_KEY"],
    "cohere": ["COHERE_API_KEY"],
    "deepseek": ["DEEPSEEK_API_KEY"],
    "together": ["TOGETHER_API_KEY"],
    "openrouter": ["OPENROUTER_API_KEY"],
    "azure": ["AZURE_OPENAI_API_KEY"],
}


def _candidate_vars(provider: str) -> list[str]:
    return PROVIDER_ENV_VARS.get(provider.lower(), [f"{provider.upper()}_API_KEY"])


def get_api_key(provider: str, required: bool = True) -> str | None:
    """Return the API key for ``provider`` from the environment.

    Tries each known variable for the provider in order. Raises ``EnvError`` if
    none is set and ``required`` is true; otherwise returns ``None``.
    """
    for name in _candidate_vars(provider):
        value = os.environ.get(name)
        if value:
            return value
    if required:
        names = ", ".join(_candidate_vars(provider))
        raise EnvError(
            f"No API key found for provider {provider!r}. Set one of: {names}."
        )
    return None


def has_api_key(provider: str) -> bool:
    """True if an API key for ``provider`` is present in the environment."""
    return get_api_key(provider, required=False) is not None


def available_providers() -> list[str]:
    """Sorted list of known providers that currently have a key set."""
    return sorted(p for p in PROVIDER_ENV_VARS if has_api_key(p))
