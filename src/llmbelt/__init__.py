"""llmbelt — a tiny, dependency-free tool belt for working with LLMs.

Token counting, cost estimation & tracking, retries with backoff, prompt
templating, smart text chunking, JSON extraction, conversation management, PII
redaction, caching, rate limiting, and first-class environment-variable config —
the small utilities you re-write on every LLM project, in one import with zero
required dependencies.
"""

from llmbelt.cache import cached
from llmbelt.chunk import chunk_by_tokens, chunk_text, split_text
from llmbelt.conversation import Conversation
from llmbelt.cost import PRICING, CostTracker, Price, estimate_cost
from llmbelt.dotenv import find_dotenv, load_dotenv, parse_dotenv
from llmbelt.env import (
    EnvError,
    env_bool,
    env_float,
    env_int,
    env_list,
    env_str,
    get_env,
)
from llmbelt.env_config import EnvConfig
from llmbelt.env_interpolate import expand, resolve_layers
from llmbelt.env_keys import (
    PROVIDER_ENV_VARS,
    available_providers,
    get_api_key,
    has_api_key,
)
from llmbelt.env_llm import llm_settings_from_env
from llmbelt.env_namespace import EnvNamespace, collect_prefixed
from llmbelt.env_require import env_report, mask_secret, require_env
from llmbelt.env_snapshot import FrozenEnv, diff_env, freeze_env, snapshot_env
from llmbelt.env_template import env_template, env_template_from_config
from llmbelt.extract import extract_json
from llmbelt.messages import count_message_tokens, trim_messages
from llmbelt.prompt import PromptTemplate
from llmbelt.ratelimit import RateLimiter
from llmbelt.redact import DEFAULT_PII_PATTERNS, find_pii, redact
from llmbelt.retry import retry
from llmbelt.tokens import count_tokens, estimate_tokens, truncate_to_tokens

__version__ = "0.6.0"

__all__ = [
    "cached",
    "chunk_text",
    "chunk_by_tokens",
    "split_text",
    "Conversation",
    "PRICING",
    "CostTracker",
    "Price",
    "estimate_cost",
    "load_dotenv",
    "parse_dotenv",
    "find_dotenv",
    "EnvError",
    "get_env",
    "env_str",
    "env_int",
    "env_float",
    "env_bool",
    "env_list",
    "EnvConfig",
    "EnvNamespace",
    "collect_prefixed",
    "expand",
    "resolve_layers",
    "llm_settings_from_env",
    "env_template",
    "env_template_from_config",
    "snapshot_env",
    "diff_env",
    "freeze_env",
    "FrozenEnv",
    "PROVIDER_ENV_VARS",
    "get_api_key",
    "has_api_key",
    "available_providers",
    "require_env",
    "mask_secret",
    "env_report",
    "extract_json",
    "count_message_tokens",
    "trim_messages",
    "PromptTemplate",
    "RateLimiter",
    "DEFAULT_PII_PATTERNS",
    "find_pii",
    "redact",
    "retry",
    "count_tokens",
    "estimate_tokens",
    "truncate_to_tokens",
]
