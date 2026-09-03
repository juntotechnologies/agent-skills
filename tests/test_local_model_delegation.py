#!/usr/bin/env python3

import importlib.util
import json
import threading
import unittest
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
