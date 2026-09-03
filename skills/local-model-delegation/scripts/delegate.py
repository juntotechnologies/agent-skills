#!/usr/bin/env python3
"""Route read-only inference across Hermes's configured local model servers."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, NamedTuple, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen as default_urlopen


DEFAULT_CONFIG_PATH = Path.home() / ".hermes" / "config.yaml"
DEFAULT_MAX_OUTPUT_CHARS = 6_000
DEFAULT_MAX_TOKENS = 2_048
DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_MAX_WORKERS = 10
TRUNCATION_MARKER = "\n[local-model output truncated]"
SYSTEM_PROMPT = (
    "You are a read-only analysis worker assisting another coding agent. "
    "Return concise evidence and reasoning only. You have no tools and must not "
    "claim to have read, changed, executed, sent, or verified anything that is "
    "not present in the prompt."
)


class Endpoint(NamedTuple):
    base_url: str
    model: str


class DelegationError(RuntimeError):
    pass


CompletionFn = Callable[..., str]


def _yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _top_level_sections(text: str) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current_section: str | None = None

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indentation = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()

        if indentation == 0 and stripped.endswith(":"):
            current_section = stripped[:-1]
            sections.setdefault(current_section, {})
            continue
        if indentation != 2 or current_section is None or ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        sections[current_section][key.strip()] = _yaml_scalar(value)

    return sections


def parse_routing_config(text: str) -> dict[str, Endpoint]:
    sections = _top_level_sections(text)
    required = {
        "model.default": sections.get("model", {}).get("default", ""),
        "model.base_url": sections.get("model", {}).get("base_url", ""),
        "delegation.model": sections.get("delegation", {}).get("model", ""),
        "delegation.base_url": sections.get("delegation", {}).get("base_url", ""),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise DelegationError(
            "Hermes routing config is missing: " + ", ".join(missing)
        )

    return {
        "mac": Endpoint(required["model.base_url"], required["model.default"]),
        "spark": Endpoint(
            required["delegation.base_url"], required["delegation.model"]
        ),
    }


def load_routing_config(path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Endpoint]:
    try:
        return parse_routing_config(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise DelegationError(f"Cannot read Hermes config at {path}: {error}") from error


def route_for_task_count(task_count: int) -> str:
    if task_count < 1:
        raise DelegationError("At least one task is required")
    return "mac" if task_count <= 2 else "hybrid"


def build_chat_request(model: str, prompt: str, max_tokens: int) -> dict:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "stream": False,
    }


def extract_content(payload: dict) -> str:
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise DelegationError("Malformed local model response") from error
    if not isinstance(content, str) or not content.strip():
        raise DelegationError("Malformed local model response: missing content")
    return content.strip()


def _completion_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/chat/completions"


def request_completion(
    endpoint: Endpoint,
    prompt: str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    urlopen=None,
) -> str:
    body = json.dumps(
        build_chat_request(endpoint.model, prompt, max_tokens)
    ).encode("utf-8")
    request = Request(
        _completion_url(endpoint.base_url),
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    open_request = urlopen or default_urlopen

    try:
        with open_request(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as error:
        host = urlparse(endpoint.base_url).netloc or endpoint.base_url
        raise DelegationError(f"Local model endpoint {host} failed: {error}") from error

    return extract_content(payload)


def bound_output(text: str, max_chars: int) -> str:
    if max_chars < 1:
        raise DelegationError("Output limit must be positive")
    if len(text) <= max_chars:
        return text
    if max_chars <= len(TRUNCATION_MARKER):
        return text[:max_chars]
    content_limit = max_chars - len(TRUNCATION_MARKER)
    return text[:content_limit] + TRUNCATION_MARKER


def run_parallel(
    endpoint: Endpoint,
    tasks: Sequence[str],
    *,
    completion_fn: CompletionFn = request_completion,
    max_workers: int = DEFAULT_MAX_WORKERS,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> list[str]:
    if not tasks:
        raise DelegationError("At least one task is required")
    worker_count = min(len(tasks), max_workers)

    def complete(task: str) -> str:
        return completion_fn(
            endpoint,
            task,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
        )

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(executor.map(complete, tasks))


def _synthesis_prompt(tasks: Sequence[str], findings: Sequence[str]) -> str:
    sections = []
    for index, (task, finding) in enumerate(zip(tasks, findings), start=1):
        sections.append(f"Task {index}: {task}\nFinding {index}: {finding}")
    joined = "\n\n".join(sections)
    return (
        "Condense the independent findings below into one concise, internally "
        "consistent report for the supervising coding agent. Preserve concrete "
        "evidence, disagreements, and uncertainty. Do not add unsupported facts.\n\n"
        + joined
    )


def run_hybrid(
    routes: dict[str, Endpoint],
    tasks: Sequence[str],
    *,
    completion_fn: CompletionFn = request_completion,
    max_workers: int = DEFAULT_MAX_WORKERS,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    findings = run_parallel(
        routes["spark"],
        tasks,
        completion_fn=completion_fn,
        max_workers=max_workers,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
    )
    bounded_findings = [bound_output(finding, 4_000) for finding in findings]
    return completion_fn(
        routes["mac"],
        _synthesis_prompt(tasks, bounded_findings),
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Delegate read-only analysis to Hermes-configured model servers."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_options(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
        command_parser.add_argument(
            "--max-output-chars", type=int, default=DEFAULT_MAX_OUTPUT_CHARS
        )
        command_parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
        command_parser.add_argument(
            "--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS
        )

    ask_parser = subparsers.add_parser("ask", help="Run one serial task on the Mac")
    ask_parser.add_argument("--prompt", required=True)
    add_common_options(ask_parser)

    fanout_parser = subparsers.add_parser(
        "fanout", help="Run independent tasks on Spark and synthesize on the Mac"
    )
    fanout_parser.add_argument("--task", action="append", required=True)
    fanout_parser.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS)
    add_common_options(fanout_parser)

    return parser


def run_cli(argv: Sequence[str] | None = None) -> tuple[int, str]:
    try:
        args = _parser().parse_args(argv)
        routes = load_routing_config(args.config)
        if args.command == "ask":
            route = "mac"
            result = request_completion(
                routes["mac"],
                args.prompt,
                max_tokens=args.max_tokens,
                timeout_seconds=args.timeout,
            )
        else:
            if route_for_task_count(len(args.task)) != "hybrid":
                raise DelegationError("Fan-out requires at least three independent tasks")
            route = "spark-to-mac"
            result = run_hybrid(
                routes,
                args.task,
                max_workers=args.max_workers,
                max_tokens=args.max_tokens,
                timeout_seconds=args.timeout,
            )
        payload = {
            "status": "ok",
            "route": route,
            "result": bound_output(result, args.max_output_chars),
        }
        return 0, json.dumps(payload, ensure_ascii=False)
    except (DelegationError, ValueError) as error:
        return 1, json.dumps({"status": "error", "error": str(error)})


def main() -> int:
    status, output = run_cli()
    print(output)
    return status


if __name__ == "__main__":
    sys.exit(main())
