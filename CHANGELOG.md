# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.6.0] - 2026-06-23

### Added — first-class environment-variable configuration
- `get_env` + `env_str` / `env_int` / `env_float` / `env_bool` / `env_list` — typed environment readers with defaults, `required`, and casting, raising a descriptive `EnvError`.
- `get_api_key(provider)`, `has_api_key`, `available_providers`, `PROVIDER_ENV_VARS` — resolve LLM provider API keys from the conventional env vars.
- `load_dotenv`, `parse_dotenv`, `find_dotenv` — a zero-dependency `.env` loader.
- `require_env`, `mask_secret`, `env_report` — fail-fast validation and secret-safe reporting.
- `EnvConfig` — declarative, typed config loaded from the environment (prefix + annotated fields).
- `EnvNamespace`, `collect_prefixed` — work with a group of prefixed variables as one object.
- `expand`, `resolve_layers` — `${VAR}` interpolation and layered (defaults < .env < environ) resolution.
- `llm_settings_from_env` — assemble an LLM client config (api_key/model/base_url/temperature/…) in one call.
- `env_template`, `env_template_from_config` — generate a `.env.example`, optionally from an `EnvConfig`.
- `snapshot_env`, `diff_env`, `freeze_env`, `FrozenEnv` — snapshot, diff, and immutably freeze environment config.

## [0.5.0] - 2026-06-22

### Added
- `redact` / `find_pii` — best-effort scrubbing of PII and secrets (email, phone, credit card, SSN, IP, API keys, AWS keys) before text is sent to a third-party LLM; customizable patterns and mask. `DEFAULT_PII_PATTERNS` is exported for inspection/extension.
- `Conversation` — a stateful chat-history container that appends `user`/`assistant` turns and auto-trims to a token budget (keeping the system prompt), with `messages`, `token_count()`, and `clear()`.

## [0.4.0] - 2026-06-22

### Added
- `split_text` — recursive, boundary-aware text splitter that prefers to break on paragraph → line → sentence → word boundaries (falling back to a hard cut only when a single token exceeds `chunk_size`), with character overlap. Produces cleaner RAG chunks than the fixed-offset `chunk_text`.
- `CostTracker` — accumulate calls, input/output tokens, and USD cost across many requests; `.add()`, `.summary()`, `.reset()`, `total_tokens`, and a readable `str()`.

## [0.3.0] - 2026-06-18

### Added
- `count_message_tokens` / `trim_messages` — measure a chat-format conversation and trim it to fit a context window, always keeping the system prompt and preserving order.
- `cached` — decorator that memoizes a function on a hash of its arguments (unhashable args OK), with optional `ttl` and `maxsize`; works on sync and `async def` functions. Stops you re-paying for identical LLM calls.
- `RateLimiter` — thread-safe token-bucket throttle to stay under provider requests-per-minute limits; usable as a gate, context manager, or decorator.

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
