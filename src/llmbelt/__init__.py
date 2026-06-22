"""llmbelt — a tiny, dependency-free tool belt for working with LLMs.

Token counting, cost estimation & tracking, retries with backoff, prompt
templating, smart text chunking, JSON extraction, conversation budgeting,
caching, and rate limiting — the small utilities you re-write on every LLM
project, in one import with zero required dependencies.
"""

from llmbelt.cache import cached
from llmbelt.chunk import chunk_by_tokens, chunk_text, split_text
from llmbelt.cost import PRICING, CostTracker, Price, estimate_cost
from llmbelt.extract import extract_json
from llmbelt.messages import count_message_tokens, trim_messages
from llmbelt.prompt import PromptTemplate
from llmbelt.ratelimit import RateLimiter
from llmbelt.retry import retry
from llmbelt.tokens import count_tokens, estimate_tokens, truncate_to_tokens

__version__ = "0.4.0"

__all__ = [
    "cached",
    "chunk_text",
    "chunk_by_tokens",
    "split_text",
    "PRICING",
    "CostTracker",
    "Price",
    "estimate_cost",
    "extract_json",
    "count_message_tokens",
    "trim_messages",
    "PromptTemplate",
    "RateLimiter",
    "retry",
    "count_tokens",
    "estimate_tokens",
    "truncate_to_tokens",
]
