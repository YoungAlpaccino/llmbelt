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
```

### Prompt templates

```python
from llmbelt import PromptTemplate

t = PromptTemplate("Translate {text} into {language}.")
t.render(text="hello", language="French")   # "Translate hello into French."
t.render(text="hello")                      # KeyError: Missing template variables: ['language']
```

### Chunk text for RAG

```python
from llmbelt import chunk_text

chunks = chunk_text(document, chunk_size=1000, overlap=100)
# overlapping chunks so answers aren't split across a boundary
```

---

## API reference

| Function | Description |
|---|---|
| `count_tokens(text, model=None)` | Exact (tiktoken) or estimated token count |
| `estimate_tokens(text)` | Dependency-free heuristic count |
| `truncate_to_tokens(text, max_tokens, model=None)` | Trim text to a token budget |
| `estimate_cost(input_tokens, output_tokens, model, pricing=None)` | USD cost estimate |
| `retry(attempts, base_delay, backoff, jitter, exceptions, ...)` | Backoff retry decorator |
| `PromptTemplate(template)` | Templating with missing-variable validation |
| `chunk_text(text, chunk_size, overlap)` | Overlapping text chunks |

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
