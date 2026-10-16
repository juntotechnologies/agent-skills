from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'skills/setup-project-repo/assets'


class ReviewWorkflowTests(unittest.TestCase):
    def test_github_templates_preserve_review_and_safety_checks(self):
        required = (
            '## Scope', '## Code Quality', '## Required Checks',
            '## Conditional Checks', '## Merge Readiness',
            'one named home', 'typed objects', 'no live credentials',
            'rollback', 'fresh agent review', 'computer-use',
            'generated PR body', 'human merge approval',
        )
        for base in (ROOT, ASSETS):
            text = (base / '.github/pull_request_template.md').read_text()
            for requirement in required:
                with self.subTest(base=base, requirement=requirement):
                    self.assertIn(requirement, text)

    def test_repository_template_uses_the_actual_local_checks(self):
        text = (ROOT / '.github/pull_request_template.md').read_text()
        self.assertIn('uv run python -m unittest discover -s tests -v', text)
        self.assertIn('bash tests/test_install.sh', text)
        self.assertIn('scripts/install.sh', text)

    def test_instructions_assign_walkthroughs_to_agents(self):
        for base in (ROOT, ASSETS):
            with self.subTest(base=base):
                text = (base / 'AGENTS.md').read_text()
                self.assertIn('Run applicable smoke tests and user-task walkthroughs yourself through computer use', text)
                self.assertNotIn('Smoke tests are things I confirm manually', text)

    def test_scope_has_a_user_outcome_and_refactor_boundary(self):
        for base in (ROOT, ASSETS):
            with self.subTest(base=base):
                text = (base / 'AGENTS.md').read_text()
                self.assertIn('one user outcome or one closely connected workflow', text)
                self.assertIn('independent cleanup or additional outcomes', text)

    def test_templates_retain_repeatable_walks_and_review_evidence(self):
        for base in (ROOT, ASSETS):
            with self.subTest(base=base):
                text = (base / 'docs/pr-docs/template.md').read_text()
                self.assertIn('## Acceptance Coverage', text)
                self.assertIn('## Agent Review', text)
                self.assertIn('Keep completed walk steps and pass criteria', text)
                self.assertNotIn('a done walk collapses', text)
                self.assertNotIn('checks the user performs', text)
                self.assertIn('Mocked tests do not replace real browser persistence checks.', text)

    def test_reusable_workflow_sections_stay_consistent(self):
        source = (ASSETS / 'AGENTS.md').read_text()
        own = (ROOT / 'AGENTS.md').read_text()
        heading = '## 8. Verification and Diagnostics Stay With You'
        self.assertEqual(own.split(heading)[1].split('\n## ')[0], source.split(heading)[1].split('\n## ')[0])

    def test_readiness_requires_observation_and_classifies_feedback(self):
        for base in (ROOT, ASSETS):
            with self.subTest(base=base):
                text = (base / 'AGENTS.md').read_text()
                self.assertIn('A screenshot proves layout; it does not prove persistence', text)
                self.assertIn('defect, missed requirement, new decision, or preference', text)
                self.assertIn('fresh review agent', text)
