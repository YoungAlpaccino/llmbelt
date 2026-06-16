"""llmbelt — a tiny, dependency-free tool belt for working with LLMs.

Token counting, cost estimation, retries with backoff, prompt templating, text
chunking, and JSON extraction — the small utilities you re-write on every LLM
project, in one import with zero required dependencies.
"""

from llmbelt.chunk import chunk_by_tokens, chunk_text
from llmbelt.cost import PRICING, Price, estimate_cost
from llmbelt.extract import extract_json
from llmbelt.prompt import PromptTemplate
from llmbelt.retry import retry
from llmbelt.tokens import count_tokens, estimate_tokens, truncate_to_tokens

__version__ = "0.2.0"

__all__ = [
    "chunk_text",
    "chunk_by_tokens",
    "PRICING",
    "Price",
    "estimate_cost",
    "extract_json",
    "PromptTemplate",
    "retry",
    "count_tokens",
    "estimate_tokens",
    "truncate_to_tokens",
]
