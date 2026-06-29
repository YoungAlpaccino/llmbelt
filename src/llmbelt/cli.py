"""Command-line interface for llmbelt.

Run via ``python -m llmbelt`` or the installed ``llmbelt`` command. Exposes the
most useful helpers — token counting, cost estimation, redaction, and
environment inspection — for quick terminal use and shell scripts.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from llmbelt import (
    __version__,
    available_providers,
    count_tokens,
    env_report,
    estimate_cost,
    redact,
    require_env,
)
from llmbelt.env import EnvError


def _read_text(arg: str | None) -> str:
    """Return ``arg``, or read stdin when it's missing or ``-``."""
    if arg is None or arg == "-":
        return sys.stdin.read()
    return arg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llmbelt",
        description="A tiny tool belt for LLMs — tokens, cost, redaction, env.",
    )
    parser.add_argument(
        "--version", action="version", version=f"llmbelt {__version__}"
    )
    sub = parser.add_subparsers(dest="command")

    p_tokens = sub.add_parser("tokens", help="count tokens in text or stdin")
    p_tokens.add_argument("text", nargs="?", help="text (omit or '-' for stdin)")
    p_tokens.add_argument("-m", "--model", default=None, help="model for encoding")

    p_cost = sub.add_parser("cost", help="estimate USD cost for a call")
    p_cost.add_argument("--in", dest="input_tokens", type=int, required=True)
    p_cost.add_argument("--out", dest="output_tokens", type=int, required=True)
    p_cost.add_argument("-m", "--model", required=True)

    p_redact = sub.add_parser("redact", help="mask PII/secrets in text or stdin")
    p_redact.add_argument("text", nargs="?", help="text (omit or '-' for stdin)")

    p_env = sub.add_parser("env", help="inspect environment configuration")
    env_sub = p_env.add_subparsers(dest="env_command")
    p_report = env_sub.add_parser("report", help="masked report of variables")
    p_report.add_argument("names", nargs="+")
    p_report.add_argument("--no-mask", action="store_true", help="show raw values")
    p_check = env_sub.add_parser("check", help="exit non-zero if any are unset")
    p_check.add_argument("names", nargs="+")
    env_sub.add_parser("keys", help="list providers with an API key set")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "tokens":
        print(count_tokens(_read_text(args.text), args.model))
        return 0

    if args.command == "cost":
        try:
            usd = estimate_cost(args.input_tokens, args.output_tokens, args.model)
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"${usd:.6f}")
        return 0

    if args.command == "redact":
        print(redact(_read_text(args.text)))
        return 0

    if args.command == "env":
        if args.env_command == "report":
            print(env_report(args.names, mask=not args.no_mask))
            return 0
        if args.env_command == "check":
            try:
                require_env(*args.names)
            except EnvError as exc:
                print(str(exc), file=sys.stderr)
                return 1
            print("OK")
            return 0
        if args.env_command == "keys":
            providers = available_providers()
            print("\n".join(providers) if providers else "(no provider keys set)")
            return 0
        parser.parse_args(["env", "--help"])
        return 1

    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
