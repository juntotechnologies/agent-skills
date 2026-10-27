"""Tests for the site-taste skill: data, rules, renderers and the site comparison."""
import json
import tempfile
import unittest
from pathlib import Path

import context_site_taste  # noqa: F401  puts the skill scripts on the path
from taste import HANDLERS, stale_outputs
from taste_model import Area, Principle, Site, Taste, load_taste
from taste_render import render_principles, render_sites, row
from taste_rules import problems, sentences
from taste_sites import DEFAULT_ROOTS, checkout_for, expected_files, failing, report_lines, report_site

PRINCIPLE = {
    "id": "sample-rule", "area": "layout", "scope": "all", "rule": "Keep it short.", "why": "Long is slow.",
    "fix": "Cut words.", "enforcement": "check", "checks": [{"site": "demo", "file": "tests/a.test.js"}],
    "evidence": [{"site": "demo", "pr": 1}],
}
SITE = {
    "id": "demo", "name": "Demo", "repo": "org/demo", "url": "https://example.test/", "kind": "public-site",
    "taste_docs": ["docs/design.md"], "commands": [{"run": "npm run check", "does": "Check it"}],
}
AREAS = ({"id": "layout", "title": "Layout", "summary": "Fit."},)


def make_taste(principle: dict | None = None, site: dict | None = None) -> Taste:
    principles = (Principle.from_json({**PRINCIPLE, **(principle or {})}),)
    sites = (Site.from_json({**SITE, **(site or {})}),)
    return Taste(Area.many(list(AREAS)), principles, sites)


def make_checkout(root: Path, files: list[str], scripts: dict, agents: str) -> Path:
    checkout = root / "demo"
    (checkout / ".git").mkdir(parents=True)
    for name in files:
        (checkout / name).parent.mkdir(parents=True, exist_ok=True)
        (checkout / name).write_text("x")
    (checkout / "package.json").write_text(json.dumps({"scripts": scripts}))
    (checkout / "AGENTS.md").write_text(agents)
    return checkout


class TestRealData(unittest.TestCase):
    def test_data_has_no_problems(self):
        self.assertEqual(problems(load_taste()), [])

    def test_references_are_up_to_date(self):
        self.assertEqual(stale_outputs(load_taste()), [])

    def test_every_area_holds_a_principle(self):
        taste = load_taste()
        used = {item.area for item in taste.principles}
        self.assertEqual(used, {area.id for area in taste.areas})


class TestLoader(unittest.TestCase):
    def test_unknown_key_fails(self):
        with self.assertRaises(TypeError):
            Principle.from_json({**PRINCIPLE, "colour": "red"})

    def test_missing_key_fails(self):
        with self.assertRaises(TypeError):
            Principle.from_json({key: value for key, value in PRINCIPLE.items() if key != "why"})

    def test_bad_enum_fails(self):
        with self.assertRaises(ValueError):
            Principle.from_json({**PRINCIPLE, "scope": "everywhere"})


class TestRules(unittest.TestCase):
    def test_sample_is_clean(self):
        self.assertEqual(problems(make_taste()), [])

    def test_long_rule_sentence_is_flagged(self):
        taste = make_taste({"rule": " ".join(["word"] * 21) + "."})
        self.assertIn("sample-rule rule: 21 words", problems(taste)[0])

    def test_two_short_sentences_pass(self):
        self.assertEqual(sentences("One two. Three four."), ["One two.", "Three four."])

    def test_unknown_area_is_flagged(self):
        self.assertEqual(problems(make_taste({"area": "nope"})), ["sample-rule: unknown area nope"])

    def test_unknown_site_is_flagged(self):
        taste = make_taste({"evidence": [{"site": "ghost", "pr": 2}]})
        self.assertEqual(problems(taste), ["sample-rule: unknown site ghost"])

    def test_check_without_file_is_flagged(self):
        self.assertIn("check enforcement with 0 check files", problems(make_taste({"checks": []}))[0])

    def test_manual_with_file_is_flagged(self):
        self.assertIn("manual enforcement with 1 check files", problems(make_taste({"enforcement": "manual"}))[0])

    def test_bad_slug_is_flagged(self):
        self.assertEqual(problems(make_taste({"id": "Bad_Id"})), ["bad principle id: Bad_Id"])

    def test_command_prefix_is_enforced(self):
        taste = make_taste(site={"commands": [{"run": "yarn test", "does": "x"}]})
        self.assertEqual(problems(taste), ["demo: command must start with npm run or make: yarn test"])

    def test_site_kind_all_is_flagged(self):
        self.assertEqual(problems(make_taste(site={"kind": "all"})), ["demo: kind must not be all"])


class TestRender(unittest.TestCase):
    def test_principles_hold_rule_check_and_evidence(self):
        text = render_principles(make_taste())
        self.assertIn("`sample-rule`<br>all", text)
        self.assertIn("demo: `tests/a.test.js`", text)
        self.assertIn("demo #1", text)

    def test_manual_principle_says_manual_walk(self):
        text = render_principles(make_taste({"enforcement": "manual", "checks": []}))
        self.assertIn("Manual walk", text)

    def test_pipe_is_escaped(self):
        self.assertEqual(row(("a|b",)), "| a\\|b |")

    def test_sites_list_commands_and_pending_pr(self):
        text = render_sites(make_taste(site={"pending_pr": "org/demo#3"}))
        self.assertIn("`npm run check`: Check it", text)
        self.assertIn("Pending: org/demo#3", text)


class TestSites(unittest.TestCase):
    def test_complete_checkout_is_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_checkout(Path(tmp), ["docs/design.md", "tests/a.test.js"], {"check": "x"}, "Use site-taste.")
            report = report_site(make_taste(), make_taste().sites[0], (Path(tmp),))
        self.assertEqual(report.problems, ())
        self.assertEqual(report_lines(report), ["demo: ok"])

    def test_missing_file_command_and_pointer_are_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_checkout(Path(tmp), [], {}, "No pointer.")
            report = report_site(make_taste(), make_taste().sites[0], (Path(tmp),))
        self.assertEqual(len(report.problems), 4)
        self.assertEqual(len(failing([report])), 1)

    def test_pending_site_does_not_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_checkout(Path(tmp), [], {}, "")
            taste = make_taste(site={"pending_pr": "org/demo#3"})
            report = report_site(taste, taste.sites[0], (Path(tmp),))
        self.assertEqual(failing([report]), [])
        self.assertIn("(pending org/demo#3)", report_lines(report)[0])

    def test_make_target_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            checkout = make_checkout(Path(tmp), ["docs/design.md", "tests/a.test.js"], {}, "site-taste")
            (checkout / "Makefile").write_text("lint:\n\ttrue\n")
            taste = make_taste(site={"commands": [{"run": "make lint", "does": "x"}]})
            report = report_site(taste, taste.sites[0], (Path(tmp),))
        self.assertEqual(report.problems, ())

    def test_site_without_checkout_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(checkout_for(make_taste().sites[0], (Path(tmp),)))
            report = report_site(make_taste(), make_taste().sites[0], (Path(tmp),))
        self.assertEqual(report_lines(report), ["demo: no checkout here"])

    def test_expected_files_join_docs_and_checks(self):
        taste = make_taste()
        self.assertEqual(expected_files(taste, taste.sites[0]), ["docs/design.md", "tests/a.test.js"])


class TestSkillText(unittest.TestCase):
    def skill_text(self) -> str:
        return (context_site_taste.SCRIPTS.parent / "SKILL.md").read_text()

    def test_skill_names_each_command(self):
        for name in HANDLERS:
            self.assertIn(f"scripts/taste.py {name}", self.skill_text())

    def test_skill_names_each_default_root(self):
        for root in DEFAULT_ROOTS:
            self.assertIn("~/" + str(root.relative_to(Path.home())), self.skill_text())


if __name__ == "__main__":
    unittest.main()
