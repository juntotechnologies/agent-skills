#!/usr/bin/env python3

import importlib.util
import json
import threading
import unittest
import io
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from contextlib import redirect_stderr
from urllib.request import ProxyHandler, HTTPRedirectHandler
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

    def test_cloud_command_is_rejected_before_execution(self):
        with patch("subprocess.run") as run, redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                self.helper.run_cli(["claude", "--prompt", "do not transmit"])
        self.assertEqual(error.exception.code, 2)
        run.assert_not_called()

    def test_rejects_external_urls_before_transport(self):
        for url in ("https://api.anthropic.com/v1", "http://8.8.8.8/v1",
                    "http://private.example/v1", "http://user:pass@127.0.0.1/v1",
                    "http://169.254.169.254/v1", "file:///tmp/model"):
            with self.subTest(url=url), patch.object(self.helper, "default_urlopen") as request:
                with self.assertRaises(self.helper.DelegationError):
                    self.helper.request_completion(self.helper.Endpoint(url, "m"), "private")
                request.assert_not_called()

    def test_accepts_local_private_and_tailnet_addresses(self):
        for host in ("127.0.0.1", "10.1.2.3", "192.168.1.2", "172.16.0.1",
                     "100.96.198.21", "[::1]", "[fd7a:115c:a1e0::1]"):
            self.helper.validate_endpoint_url(f"http://{host}:8080/v1")

    def test_transport_disables_proxies_and_redirects(self):
        with patch.dict(os.environ, {"http_proxy": "http://external.example:8080",
                                     "https_proxy": "http://external.example:8080"}):
            opener = self.helper.local_opener()
        proxy = [h for h in opener.handlers if isinstance(h, ProxyHandler)]
        self.assertTrue(all(h.proxies == {} for h in proxy))
        redirect = next(h for h in opener.handlers if isinstance(h, HTTPRedirectHandler))
        with self.assertRaises(self.helper.DelegationError):
            redirect.redirect_request(None, None, 302, "redirect", {}, "https://external.example")

    def test_real_transport_does_not_follow_redirect(self):
        paths = []

        class RedirectServer(BaseHTTPRequestHandler):
            def do_POST(self):
                paths.append(self.path)
                self.send_response(302)
                self.send_header("Location", "/must-not-receive")
                self.end_headers()

            def do_GET(self):
                paths.append(self.path)
                self.send_response(200)
                self.end_headers()

            def log_message(self, *_args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), RedirectServer)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            endpoint = self.helper.Endpoint(f"http://127.0.0.1:{server.server_port}/v1", "m")
            with self.assertRaisesRegex(self.helper.DelegationError, "redirect"):
                self.helper.request_completion(endpoint, "fixture", timeout_seconds=2)
            self.assertEqual(paths, ["/v1/chat/completions"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_failed_local_cli_never_invokes_cloud_or_fallback(self):
        routes = {"mac": self.helper.Endpoint("http://127.0.0.1/v1", "m")}
        with patch.object(self.helper, "load_routing_config", return_value=routes), patch.object(
            self.helper, "request_completion", side_effect=self.helper.DelegationError("unavailable")
        ) as request, patch("subprocess.run") as cloud:
            status, output = self.helper.run_cli(["ask", "--prompt", "private"])
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(output)["status"], "error")
        self.assertNotIn("result", json.loads(output))
        request.assert_called_once()
        cloud.assert_not_called()

    def test_extracts_content_and_rejects_malformed_responses(self):
        payload = {"choices": [{"message": {"content": "result"}}]}
        self.assertEqual(self.helper.extract_content(payload), "result")

        with self.assertRaisesRegex(self.helper.DelegationError, "model response"):
            self.helper.extract_content({"choices": []})

    def test_request_wraps_unavailable_endpoint_without_fabricating_result(self):
        endpoint = self.helper.Endpoint("http://127.0.0.1/v1", "model-a")

        def unavailable(*_args, **_kwargs):
            raise URLError("offline")

        with self.assertRaisesRegex(self.helper.DelegationError, "127.0.0.1"):
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
