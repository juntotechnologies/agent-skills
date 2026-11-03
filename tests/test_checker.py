import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'checker'))
sys.path.insert(0, str(ROOT / 'scripts'))
import gen_rules  # noqa: E402
import model  # noqa: E402
import pyrules  # noqa: E402
import scope  # noqa: E402
import textrules  # noqa: E402

LIMITS = json.loads((ROOT / 'checker/limits.json').read_text())


def rules_of(source, path='a.py'):
    return {fault.rule for fault in pyrules.faults_for(path, source, LIMITS)}


class PythonRuleTests(unittest.TestCase):
    def test_comment_needs_why(self):
        self.assertIn('comment-why-only', rules_of('x = 1  # sets x\n'))
        self.assertEqual(rules_of('x = 1  # why: API needs it\n# noqa: E501\n'), set())

    def test_function_docstring_needs_why_module_may_have_one(self):
        self.assertEqual(rules_of('"""Module."""\n'), set())
        self.assertIn('docstring-why-only', rules_of('def f():\n    """Does f."""\n'))
        self.assertEqual(rules_of('def f():\n    """why: slow path."""\n'), set())

    def test_nested_function_and_lambda(self):
        self.assertIn('no-nested-function', rules_of('def f():\n    def g():\n        pass\n'))
        self.assertIn('no-lambda', rules_of('f = lambda x: x\n'))

    def test_inline_sql(self):
        self.assertIn('inline-sql', rules_of('q = "SELECT a FROM t"\n'))
        self.assertEqual(rules_of('q = "select a person"\n'), set())

    def test_length_limit_skips_tests(self):
        body = ''.join(f'    a{index} = 1\n' for index in range(20))
        source = f'def f():\n{body}'
        self.assertIn('function-length', rules_of(source))
        self.assertNotIn('function-length', rules_of(source, 'tests/test_a.py'))

    def test_syntax_error_is_a_fault(self):
        self.assertEqual(rules_of('def\n'), {'syntax'})


class ScopeTests(unittest.TestCase):
    def test_only_changed_lines_count(self):
        changed = scope.parse_diff('+++ b/a.py\n@@ -1,0 +5,2 @@\n+x\n+y\n@@ -9 +12 @@\n-z\n+z\n')
        self.assertEqual(changed, {'a.py': {5, 6, 12}})
        self.assertTrue(scope.touched(model.Fault('a.py', 1, 5, 'r', 'm'), changed))
        self.assertFalse(scope.touched(model.Fault('a.py', 1, 4, 'r', 'm'), changed))


class TextRuleTests(unittest.TestCase):
    def test_uv_only(self):
        self.assertTrue(textrules.line_breaks_uv('python3 run.py'))
        self.assertTrue(textrules.line_breaks_uv('cd x && pip install y'))
        self.assertTrue(textrules.line_breaks_uv('uses: actions/setup-python@v5'))
        self.assertFalse(textrules.line_breaks_uv('uv run python x.py'))
        self.assertFalse(textrules.line_breaks_uv('uv run --with a python x.py && uvx ruff check'))

    def test_claude_md(self):
        self.assertEqual(textrules.claude_md_faults('x/CLAUDE.md', {1})[0].rule, 'no-claude-md')
        self.assertEqual(textrules.claude_md_faults('AGENTS.md', {1}), [])


class RegistryTests(unittest.TestCase):
    def test_agents_md_is_generated(self):
        self.assertEqual((ROOT / 'global/AGENTS.md').read_text(), gen_rules.render(gen_rules.load_registry()))

    def test_ids_unique_and_enforcers_exist(self):
        rows = gen_rules.load_registry()['rules']
        self.assertEqual(len({row['id'] for row in rows}), len(rows))
        named = [rule for row in rows if row['enforcer'] for rule in row['enforcer'].get('rules', [])]
        self.assertEqual(sorted(set(named) - set(model.RULES)), [])

    def test_enforced_rule_leaves_prose(self):
        registry = {'title': 'T', 'footer': 'F', 'sections': ['S'], 'rules': [
            {'id': 'a', 'section': 'S', 'text': '- keep', 'enforcer': None},
            {'id': 'b', 'section': 'S', 'text': '- drop', 'enforcer': {'kind': 'lint', 'rules': ['no-lambda']}}]}
        self.assertEqual(gen_rules.render(registry), '# T\n\n## S\n- keep\n\nF\n')


def git(*args, cwd):
    subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', *args], cwd=cwd, check=True, capture_output=True)


class EndToEndTests(unittest.TestCase):
    def test_old_lines_pass_new_lines_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            git('init', '-q', '-b', 'main', cwd=tmp)
            git('config', 'user.email', 't@t', cwd=tmp)
            git('config', 'user.name', 't', cwd=tmp)
            (Path(tmp) / 'a.py').write_text('x = 1  # old comment\n')
            git('add', '.', cwd=tmp)
            git('commit', '-qm', 'old', cwd=tmp)
            (Path(tmp) / 'a.py').write_text('x = 1  # old comment\ny = 2  # new comment\n')
            git('add', '.', cwd=tmp)
            done = subprocess.run(['uv', 'run', '--no-project', 'python', str(ROOT / 'checker/check.py'), '--staged', '--lint-only'],
                                  cwd=tmp, capture_output=True, text=True, env=os.environ)
            rows = [json.loads(line) for line in done.stdout.splitlines()]
            self.assertEqual(done.returncode, 1, done.stderr)
            self.assertEqual([(row['line'], row['rule']) for row in rows], [(2, 'comment-why-only')])


if __name__ == '__main__':
    unittest.main()
