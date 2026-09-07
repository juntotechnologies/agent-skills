#!/usr/bin/env python3

import importlib.util
import json
import threading
import unittest
import subprocess
from unittest.mock import patch
from pathlib import Path
from urllib.error import URLError


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = (
    REPO_ROOT / "skills" / "local-model-delegation" / "scripts" / "delegate.py"
)


def load_helper():
    spec = importlib.util.spec_from_file_location("local_model_delegate", HELPER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LocalModelDelegationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helper = load_helper()

    def test_discovers_mac_and_spark_routes_from_hermes_config(self):
        config = """
model:
  default: mac-model
  provider: custom
  base_url: http://mac.example/v1
delegation:
  model: spark-model
  provider: custom
  base_url: http://spark.example/v1
  max_concurrent_children: 10
"""

        routes = self.helper.parse_routing_config(config)

        self.assertEqual(
            routes["mac"],
            self.helper.Endpoint("http://mac.example/v1", "mac-model"),
        )
        self.assertEqual(
            routes["spark"],
            self.helper.Endpoint("http://spark.example/v1", "spark-model"),
        )

    def test_discovery_rejects_missing_required_route_fields(self):
        with self.assertRaisesRegex(self.helper.DelegationError, "delegation.model"):
            self.helper.parse_routing_config(
                "model:\n  default: mac\n  base_url: http://mac/v1\n"
                "delegation:\n  base_url: http://spark/v1\n"
            )

    def test_routes_one_or_two_tasks_to_mac_and_three_or_more_to_hybrid(self):
        self.assertEqual(self.helper.route_for_task_count(1), "mac")
        self.assertEqual(self.helper.route_for_task_count(2), "mac")
        self.assertEqual(self.helper.route_for_task_count(3), "hybrid")

    def test_builds_model_only_openai_compatible_request(self):
        body = self.helper.build_chat_request("model-a", "analyze this", 321)

        self.assertEqual(body["model"], "model-a")
        self.assertEqual(body["max_tokens"], 321)
        self.assertFalse(body["stream"])
        self.assertNotIn("tools", body)
        self.assertEqual(body["messages"][-1]["content"], "analyze this")

    def test_fanout_defaults_to_two_workers_for_context_first_serving(self):
        args = self.helper._parser().parse_args(["fanout", "--task", "a"])
        self.assertEqual(args.max_workers, 2)

    def test_bounded_local_analysis_reserves_output_for_the_answer(self):
        body = self.helper.build_chat_request("model-a", "summarize", 450)
        self.assertEqual(body.get("reasoning_effort"), "none")

    def test_claude_receives_prompt_as_stdin_with_no_tools_or_customizations(self):
        with patch.object(self.helper.subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, "finding", "")
            result = self.helper.request_claude("literal $(do-not-run)", timeout_seconds=12)
        args, kwargs = run.call_args
        self.assertEqual(result, "finding")
        self.assertEqual(args[0][0], "claude")
        self.assertIn("--safe-mode", args[0])
        self.assertIn("--strict-mcp-config", args[0])
        self.assertIn("--no-session-persistence", args[0])
        self.assertEqual(args[0][args[0].index("--tools") + 1], "")
        self.assertEqual(kwargs["input"], "literal $(do-not-run)")
        self.assertEqual(kwargs["timeout"], 12)
        self.assertFalse(kwargs.get("shell", False))

    def test_claude_failures_are_explicit_and_do_not_echo_sensitive_output(self):
        for failure in (FileNotFoundError(), subprocess.TimeoutExpired("claude", 1)):
            with patch.object(self.helper.subprocess, "run", side_effect=failure):
                with self.assertRaises(self.helper.DelegationError):
                    self.helper.request_claude("review")
        for code, output in ((1, "secret diagnostic"), (0, "")):
            with patch.object(self.helper.subprocess, "run") as run:
                run.return_value = subprocess.CompletedProcess([], code, output, "secret")
                with self.assertRaises(self.helper.DelegationError) as error:
                    self.helper.request_claude("review")
                self.assertNotIn("secret", str(error.exception))

    def test_claude_cli_does_not_require_hermes_config_and_bounds_output(self):
        with patch.object(self.helper, "request_claude", return_value="abcdef"), patch.object(
            self.helper, "load_routing_config", side_effect=AssertionError("not needed")
        ):
            status, output = self.helper.run_cli(
                ["claude", "--prompt", "review", "--max-output-chars", "3"]
            )
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output), {"status": "ok", "route": "claude", "result": "abc"})

    def test_extracts_content_and_rejects_malformed_responses(self):
        payload = {"choices": [{"message": {"content": "result"}}]}
        self.assertEqual(self.helper.extract_content(payload), "result")

        with self.assertRaisesRegex(self.helper.DelegationError, "model response"):
            self.helper.extract_content({"choices": []})

    def test_request_wraps_unavailable_endpoint_without_fabricating_result(self):
        endpoint = self.helper.Endpoint("http://offline.example/v1", "model-a")

        def unavailable(*_args, **_kwargs):
            raise URLError("offline")

        with self.assertRaisesRegex(self.helper.DelegationError, "offline.example"):
            self.helper.request_completion(
                endpoint,
                "prompt",
                timeout_seconds=1,
                urlopen=unavailable,
            )

    def test_parallel_requests_execute_concurrently_and_preserve_order(self):
        endpoint = self.helper.Endpoint("http://spark.example/v1", "spark-model")
        barrier = threading.Barrier(3, timeout=2)

        def complete(_endpoint, task, **_kwargs):
            barrier.wait()
            return f"done:{task}"

        results = self.helper.run_parallel(
            endpoint,
            ["one", "two", "three"],
            completion_fn=complete,
            max_workers=3,
        )

        self.assertEqual(results, ["done:one", "done:two", "done:three"])

    def test_hybrid_fans_out_on_spark_then_synthesizes_on_mac(self):
        routes = {
            "mac": self.helper.Endpoint("http://mac.example/v1", "mac-model"),
            "spark": self.helper.Endpoint(
                "http://spark.example/v1", "spark-model"
            ),
        }
        calls = []

        def complete(endpoint, prompt, **_kwargs):
            calls.append((endpoint, prompt))
            if endpoint == routes["mac"]:
                return "condensed"
            return f"finding:{prompt}"

        result = self.helper.run_hybrid(
            routes,
            ["one", "two", "three"],
            completion_fn=complete,
            max_workers=3,
        )

        self.assertEqual(result, "condensed")
        self.assertEqual(sum(endpoint == routes["spark"] for endpoint, _ in calls), 3)
        self.assertEqual(sum(endpoint == routes["mac"] for endpoint, _ in calls), 1)
        synthesis_prompt = next(
            prompt for endpoint, prompt in calls if endpoint == routes["mac"]
        )
        self.assertIn("finding:one", synthesis_prompt)
        self.assertIn("finding:three", synthesis_prompt)

    def test_output_is_bounded_before_returning_to_codex(self):
        self.assertEqual(self.helper.bound_output("abcdef", 40), "abcdef")

        output = self.helper.bound_output("x" * 100, 40)

        self.assertLessEqual(len(output), 40)
        self.assertTrue(output.endswith(self.helper.TRUNCATION_MARKER))

    def test_cli_emits_structured_error_and_nonzero_status(self):
        status, output = self.helper.run_cli(
            ["ask", "--prompt", "hello", "--config", "/missing/config.yaml"]
        )

        self.assertEqual(status, 1)
        payload = json.loads(output)
        self.assertEqual(payload["status"], "error")
        self.assertNotIn("result", payload)


if __name__ == "__main__":
    unittest.main()
