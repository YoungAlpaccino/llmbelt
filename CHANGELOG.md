# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-06-15

### Added
- `extract_json` — pull and parse the first JSON value out of a free-form LLM response (handles ```` ```json ```` fences, prose around the value, and braces inside strings).
- `chunk_by_tokens` — token-budget chunking for RAG (exact with tiktoken, ~4-chars/token heuristic without it).
- `retry` now also decorates `async def` functions, awaiting them and using `asyncio.sleep` for backoff (new `async_sleep` argument, injectable for testing).
- `py.typed` marker so downstream type checkers (mypy/pyright) see the package's type hints.

## [0.1.0] - 2026-06-13

### Added
- `count_tokens`, `estimate_tokens`, `truncate_to_tokens` — token counting with optional tiktoken.
- `estimate_cost`, `Price`, `PRICING` — cost estimation from token counts.
- `retry` — decorator with exponential backoff + jitter.
- `PromptTemplate` — prompt templating with required-variable validation.
- `chunk_text` — overlapping text chunking for RAG.
- Full test suite and CI across Python 3.9–3.12.
