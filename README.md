# llmbelt 🧰

> A tiny, **zero-dependency** tool belt for working with LLMs. The small utilities you end up re-writing on every project — token counting, cost estimation, retries, prompt templates, and text chunking — in one clean import.

[![CI](https://github.com/YoungAlpaccino/llmbelt/actions/workflows/ci.yml/badge.svg)](https://github.com/YoungAlpaccino/llmbelt/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/llmbelt.svg)](https://pypi.org/project/llmbelt/)
[![Python](https://img.shields.io/pypi/pyversions/llmbelt.svg)](https://pypi.org/project/llmbelt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

- 🪶 **Zero required dependencies** — pure standard library.
- 🔌 **Provider-agnostic** — works with Anthropic, OpenAI, Gemini, or anything else.
- 🧪 **Fully tested** across Python 3.9–3.12.

---

## Install

```bash
pip install llmbelt

# Optional: exact token counts for OpenAI-family models
pip install "llmbelt[tiktoken]"
```

---

## Usage

### Count tokens

```python
from llmbelt import count_tokens, truncate_to_tokens

count_tokens("Hello, world!")              # exact if tiktoken installed, else estimated
count_tokens("Hello", model="gpt-4o")      # use a model-specific encoding

# Trim text to fit a budget (great before sending context to an API)
truncate_to_tokens(long_document, max_tokens=4000)
```

### Estimate cost

```python
from llmbelt import estimate_cost, Price

estimate_cost(input_tokens=1_500, output_tokens=800, model="gpt-4o-mini")   # -> USD

# Bring your own prices (the built-in table is approximate — always verify):
my_prices = {"my-model": Price(input_per_1m=2.0, output_per_1m=6.0)}
estimate_cost(1000, 500, "my-model", pricing=my_prices)
```

### Retry with backoff

```python
from llmbelt import retry

@retry(attempts=5, exceptions=(ConnectionError, TimeoutError))
def call_api():
    ...   # retried with exponential backoff + jitter on failure

# Works on async functions too — awaited, with non-blocking asyncio.sleep backoff
@retry(attempts=5, exceptions=(ConnectionError, TimeoutError))
async def call_api_async():
    ...
```

### Extract JSON from a model reply

```python
from llmbelt import extract_json

extract_json('Sure!\n```json\n{"ok": true}\n```')   # -> {"ok": True}
extract_json('The score is {"value": 0.9}.')         # -> {"value": 0.9}
extract_json("no json here", default=None)           # -> None (else raises ValueError)
```

### Prompt templates

```python
from llmbelt import PromptTemplate

t = PromptTemplate("Translate {text} into {language}.")
t.render(text="hello", language="French")   # "Translate hello into French."
t.render(text="hello")                      # KeyError: Missing template variables: ['language']
```

### Fit a conversation into the context window

```python
from llmbelt import count_message_tokens, trim_messages

messages = [
    {"role": "system", "content": "You are concise."},
    {"role": "user", "content": "..."},
    # ... a long history ...
]

count_message_tokens(messages)                      # total tokens of the chat
trim_messages(messages, max_tokens=8000)            # drop oldest turns, keep the system prompt
```

### Cache calls so you don't pay twice

```python
from llmbelt import cached

@cached(ttl=3600)            # remember results for an hour; unhashable args are fine
def ask(prompt: str):
    ...                      # identical prompt -> served from cache, no API call

# works on async functions too
@cached()
async def ask_async(prompt): ...
```

### Stay under rate limits

```python
from llmbelt import RateLimiter

limiter = RateLimiter(rate=60, per=60)   # 60 requests per minute

@limiter                                  # decorator
def call_api(): ...

with limiter:                             # or a context manager
    call_api()
```

### Chunk text for RAG

```python
from llmbelt import chunk_text, chunk_by_tokens

chunks = chunk_text(document, chunk_size=1000, overlap=100)
# overlapping chunks so answers aren't split across a boundary

# Budget by tokens instead of characters (exact with tiktoken installed):
chunks = chunk_by_tokens(document, chunk_size=500, overlap=50)
```

---

## API reference

| Function | Description |
|---|---|
| `count_tokens(text, model=None)` | Exact (tiktoken) or estimated token count |
| `estimate_tokens(text)` | Dependency-free heuristic count |
| `truncate_to_tokens(text, max_tokens, model=None)` | Trim text to a token budget |
| `estimate_cost(input_tokens, output_tokens, model, pricing=None)` | USD cost estimate |
| `retry(attempts, base_delay, backoff, jitter, exceptions, ...)` | Backoff retry decorator (sync **and** async) |
| `PromptTemplate(template)` | Templating with missing-variable validation |
| `chunk_text(text, chunk_size, overlap)` | Overlapping text chunks (by character) |
| `chunk_by_tokens(text, chunk_size, overlap, model=None)` | Overlapping text chunks (by token budget) |
| `extract_json(text, default=...)` | Parse the first JSON value out of an LLM reply |
| `count_message_tokens(messages, model=None)` | Token count of a chat-format message list |
| `trim_messages(messages, max_tokens, model=None, keep_system=True)` | Trim a conversation to a token budget |
| `cached(maxsize, ttl)` | Memoize calls on an args hash (sync + async) |
| `RateLimiter(rate, per, capacity=None)` | Token-bucket throttle (gate / context manager / decorator) |

---

## Development

```bash
git clone https://github.com/YoungAlpaccino/llmbelt
cd llmbelt
pip install -e ".[dev]"
pytest          # run tests
ruff check .    # lint
```

### Publishing to PyPI (maintainer notes)

```bash
python -m build
twine upload dist/*
```

> **Before first publish:** confirm the name `llmbelt` is free on [PyPI](https://pypi.org/project/llmbelt/).
> If taken, rename in `pyproject.toml`, the `src/` folder, and imports (a single find-and-replace).

---

## License

MIT — see [LICENSE](./LICENSE). Use it anywhere, including commercially.

