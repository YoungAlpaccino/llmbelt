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

### Configure from the environment

```python
from llmbelt import get_api_key, load_dotenv, EnvConfig, llm_settings_from_env

load_dotenv()                          # zero-dep .env loader (no override by default)
key = get_api_key("openai")            # reads OPENAI_API_KEY (+ known aliases)
settings = llm_settings_from_env()     # {api_key, model, base_url, temperature, ...}

# Declarative, typed config straight from the environment:
class Settings(EnvConfig):
    __prefix__ = "APP_"
    api_key: str                       # required (no default) -> clear EnvError if unset
    timeout: float = 30.0
    debug: bool = False

cfg = Settings.from_env()              # reads APP_API_KEY, APP_TIMEOUT, APP_DEBUG
```

Also included: `env_str/int/float/bool/list`, `require_env`, `mask_secret`,
`EnvNamespace`, `expand`/`resolve_layers` (`${VAR}` interpolation),
`env_template` (generate a `.env.example`), and `snapshot_env`/`freeze_env`.

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

### Manage a chat with a self-trimming history

```python
from llmbelt import Conversation

chat = Conversation(system="You are concise.", max_tokens=8000)
chat.user("Hello!")
chat.assistant("Hi — how can I help?")

response = client.chat(messages=chat.messages)   # plug into any SDK; auto-trims as it grows
```

### Redact PII before sending to an LLM

```python
from llmbelt import redact, find_pii

redact("email jane@acme.com or call 555-123-4567")
# -> "email [EMAIL] or call [PHONE]"

find_pii("card 4111 1111 1111 1111")   # -> [("CREDIT_CARD", "4111 1111 1111 1111")]
```

> Best-effort regex redaction — a guardrail, not a compliance guarantee. Extend `DEFAULT_PII_PATTERNS` for your own data.

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
from llmbelt import chunk_text, chunk_by_tokens, split_text

chunks = chunk_text(document, chunk_size=1000, overlap=100)
# overlapping chunks so answers aren't split across a boundary

# Budget by tokens instead of characters (exact with tiktoken installed):
chunks = chunk_by_tokens(document, chunk_size=500, overlap=50)

# Smarter: break on paragraph/sentence/word boundaries instead of mid-word
chunks = split_text(document, chunk_size=1000, overlap=100)
```

### Track spend across calls

```python
from llmbelt import CostTracker

tracker = CostTracker()
tracker.add(input_tokens=1_500, output_tokens=800, model="gpt-4o-mini")
tracker.add(2_000, 1_200, "gpt-4o-mini")

print(tracker)          # "2 calls, 5,500 tokens, $0.0019"
tracker.summary()       # {"calls": 2, "input_tokens": ..., "cost_usd": ...}
```

---

## API reference

| Function | Description |
|---|---|
| `get_env / env_str / env_int / env_float / env_bool / env_list` | Typed environment readers (defaults, `required`, casting) |
| `get_api_key(provider)` / `has_api_key` / `available_providers` | Resolve LLM provider API keys from env |
| `load_dotenv / parse_dotenv / find_dotenv` | Zero-dependency `.env` loader |
| `require_env` / `mask_secret` / `env_report` | Fail-fast validation + secret-safe reporting |
| `EnvConfig` | Declarative typed config from the environment |
| `EnvNamespace` / `collect_prefixed` | Group prefixed variables into one object/dict |
| `expand` / `resolve_layers` | `${VAR}` interpolation + layered resolution |
| `llm_settings_from_env(provider)` | Assemble an LLM client config from env |
| `env_template` / `env_template_from_config` | Generate a `.env.example` |
| `snapshot_env` / `diff_env` / `freeze_env` / `FrozenEnv` | Snapshot, diff, freeze env config |
| `count_tokens(text, model=None)` | Exact (tiktoken) or estimated token count |
| `estimate_tokens(text)` | Dependency-free heuristic count |
| `truncate_to_tokens(text, max_tokens, model=None)` | Trim text to a token budget |
| `estimate_cost(input_tokens, output_tokens, model, pricing=None)` | USD cost estimate |
| `CostTracker(pricing=None)` | Accumulate tokens + USD cost across many calls |
| `retry(attempts, base_delay, backoff, jitter, exceptions, ...)` | Backoff retry decorator (sync **and** async) |
| `PromptTemplate(template)` | Templating with missing-variable validation |
| `chunk_text(text, chunk_size, overlap)` | Overlapping text chunks (by character) |
| `chunk_by_tokens(text, chunk_size, overlap, model=None)` | Overlapping text chunks (by token budget) |
| `split_text(text, chunk_size, overlap, separators=None)` | Boundary-aware chunks (paragraph/sentence/word) |
| `extract_json(text, default=...)` | Parse the first JSON value out of an LLM reply |
| `count_message_tokens(messages, model=None)` | Token count of a chat-format message list |
| `trim_messages(messages, max_tokens, model=None, keep_system=True)` | Trim a conversation to a token budget |
| `Conversation(system=None, max_tokens=None, model=None)` | Stateful chat history that self-trims to a budget |
| `redact(text, patterns=None, mask="[{label}]")` | Mask PII/secrets in text |
| `find_pii(text, patterns=None)` | List `(label, match)` PII detections |
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




<!-- pair touch -->
