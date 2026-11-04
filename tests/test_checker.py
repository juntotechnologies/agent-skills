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
import check  # noqa: E402
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


class PythonProcessRuleTests(unittest.TestCase):
    def test_running_python_outside_uv_from_python_code_is_a_fault(self):
        for source in ("subprocess.run(['python3', 'x.py'])", "subprocess.run([sys.executable, 'x'])",
                       "os.system('pip install x')", "subprocess.run(f'python3 {x}', shell=True)",
                       "os.execv('/usr/bin/python3', ['python3'])", "subprocess.check_output(('python', '-c', '1'))"):
            with self.subTest(source=source):
                self.assertIn('uv-only', rules_of(source + '\n'))

    def test_uv_and_unrelated_commands_pass(self):
        for source in ("subprocess.run(['uv', 'run', 'python', 'x'])", "subprocess.run(['git', 'status'])",
                       "print(sys.executable)", "subprocess.run(['uv', 'python', 'install', '3.14'])",
                       "run(['python3'])"):
            with self.subTest(source=source):
                self.assertNotIn('uv-only', rules_of(source + '\n'))


class ScopeTests(unittest.TestCase):
    def test_only_changed_lines_count(self):
        changed = scope.parse_diff('+++ b/a.py\n@@ -1,0 +5,2 @@\n+x\n+y\n@@ -9 +12 @@\n-z\n+z\n')
        self.assertEqual(changed, {'a.py': {5, 6, 12}})
        self.assertTrue(scope.touched(model.Fault('a.py', 1, 5, 'r', 'm'), changed))
        self.assertFalse(scope.touched(model.Fault('a.py', 1, 4, 'r', 'm'), changed))


class FailClosedTests(unittest.TestCase):
    def test_crashed_tool_is_a_fault_even_outside_changed_lines(self):
        done = subprocess.CompletedProcess([], 2, '', 'boom')
        faults = check.tool_failed('eslint', done)
        self.assertEqual(faults[0].rule, 'tool-failed')
        self.assertTrue(check.counts(faults[0], {}))
        self.assertEqual(check.tool_failed('eslint', subprocess.CompletedProcess([], 1, '[]', '')), [])


ESLINT = ROOT / 'checker/js/node_modules/.bin/eslint'
FIX_INPUT = """/** top stays */
export const a = 1 // goes
// goes
export const b = <div>
  {/* goes */}
</div>
// why: stays
"""
FIX_OUTPUT = """/** top stays */
export const a = 1
export const b = <div>
</div>
// why: stays
"""


@unittest.skipUnless(ESLINT.exists(), 'needs checker/js npm install')
class CommentFixerTests(unittest.TestCase):
    def test_fix_removes_only_disallowed_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'a.tsx'
            target.write_text(FIX_INPUT)
            config = ROOT / 'checker/js/eslint.config.mjs'
            command = [ESLINT, '--no-config-lookup', '-c', config, '--fix', 'a.tsx']
            subprocess.run(command, cwd=tmp, check=True, capture_output=True)
            self.assertEqual(target.read_text(), FIX_OUTPUT)


class TextRuleTests(unittest.TestCase):
    def test_uv_only(self):
        self.assertTrue(textrules.line_breaks_uv('python3 run.py'))
        self.assertTrue(textrules.line_breaks_uv('cd x && pip install y'))
        self.assertTrue(textrules.line_breaks_uv('uses: actions/setup-python@v5'))
        self.assertFalse(textrules.line_breaks_uv('uv run python x.py'))
        self.assertFalse(textrules.line_breaks_uv('uv run --with a python x.py && uvx ruff check'))

    def test_uv_only_catches_every_other_way_to_run_or_install_python(self):
        download = 'curl -L https://github.com/astral-sh/python-build-standalone/releases/download/x/cpython-3.14.tar.gz'
        for line in ('/usr/bin/python3 a.py', './venv/bin/python -m x', 'PYTHON=python3 make',
                     'brew install python@3.14', 'sudo apt-get install -y python3-pip', 'pyenv install 3.14',
                     'conda create -n x', 'pipx install ruff', 'poetry run pytest',
                     'uses: conda-incubator/setup-miniconda@v3', download, 'tar xzf cpython-3.14.10.tar.gz'):
            with self.subTest(line=line):
                self.assertTrue(textrules.line_breaks_uv(line))

    def test_uv_only_leaves_uv_and_plain_words_alone(self):
        for line in ('uv python install 3.14.10', 'uv sync --python /x/python3.14', 'uvx ruff check', 'brew install uv',
                     '"python": "3.14.10"', 'requires-python = ">=3.11"', 'echo see python.org', 'name: Python tests'):
            with self.subTest(line=line):
                self.assertFalse(textrules.line_breaks_uv(line))

    def test_uv_only_catches_an_interpreter_quoted_in_data_files(self):
        for line in ('"command": ["/usr/bin/python3", "x.py"]', '["python3", "-m", "x"]', "- 'python' x.py",
                     '<string>/usr/bin/python3</string>', 'ProgramArguments: [/opt/homebrew/bin/python3.14, a.py]'):
            with self.subTest(line=line):
                self.assertTrue(textrules.line_breaks_uv(line))
        for line in ('"python": "3.14.10"', '"python" : "3.14.10"', '"command": ["uv", "run", "x.py"]',
                     '<key>python_version</key>'):
            with self.subTest(line=line):
                self.assertFalse(textrules.line_breaks_uv(line))

    def test_the_shebang_rule_runs_in_the_text_pass_for_any_file_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            bare = Path(tmp) / 'tool'
            bare.write_text('#!/usr/bin/env python3\nprint(1)\n')
            uv = Path(tmp) / 'tool2'
            uv.write_text('#!/usr/bin/env -S uv run --script\nprint(1)\n')
            faults = check.text_faults({str(bare): {1}, str(uv): {1}}, LIMITS)
        self.assertEqual([(Path(fault.path).name, fault.rule) for fault in faults], [('tool', 'uv-only')])

    def test_a_python_shebang_is_a_fault_and_a_uv_shebang_is_not(self):
        self.assertEqual(textrules.shebang_faults('a.py', '#!/usr/bin/env python3\nx = 1\n', {1})[0].rule, 'uv-only')
        self.assertEqual(textrules.shebang_faults('a.py', '#!/usr/bin/env -S uv run --script\n', {1}), [])
        self.assertEqual(textrules.shebang_faults('a.sh', '#!/bin/sh\n', {1}), [])
        self.assertEqual(textrules.shebang_faults('a.py', '#!/usr/bin/env python3\n', {2}), [])

    def test_the_uv_only_patterns_are_one_data_file(self):
        patterns = json.loads((ROOT / 'checker/uv_only.json').read_text())
        self.assertEqual(sorted(patterns), ['alternatives', 'ci_actions', 'installs', 'interpreters', 'shebang'])

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


def run_checker(tmp, *flags):
    command = ['uv', 'run', '--no-project', 'python', str(ROOT / 'checker/check.py'), *flags, '--lint-only']
    done = subprocess.run(command, cwd=tmp, capture_output=True, text=True, env=os.environ)
    return done, [json.loads(line) for line in done.stdout.splitlines()]


class WorktreeModeTests(unittest.TestCase):
    def test_unstaged_edits_and_untracked_files_are_checked_before_any_git_add(self):
        with tempfile.TemporaryDirectory() as tmp:
            git('init', '-q', '-b', 'main', cwd=tmp)
            git('config', 'user.email', 't@t', cwd=tmp)
            git('config', 'user.name', 't', cwd=tmp)
            (Path(tmp) / 'a.py').write_text('x = 1  # old comment\n')
            git('add', '.', cwd=tmp)
            git('commit', '-qm', 'old', cwd=tmp)
            (Path(tmp) / 'a.py').write_text('x = 1  # old comment\ny = 2  # new comment\n')
            (Path(tmp) / 'b.py').write_text('z = 3  # fresh file\n')
            done, rows = run_checker(tmp, '--worktree')
            self.assertEqual(done.returncode, 1, done.stderr)
            self.assertEqual(sorted((row['path'], row['line'], row['rule']) for row in rows),
                             [('a.py', 2, 'comment-why-only'), ('b.py', 1, 'comment-why-only')])

    def test_a_clean_worktree_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            git('init', '-q', '-b', 'main', cwd=tmp)
            git('config', 'user.email', 't@t', cwd=tmp)
            git('config', 'user.name', 't', cwd=tmp)
            (Path(tmp) / 'a.py').write_text('x = 1  # old comment\n')
            git('add', '.', cwd=tmp)
            git('commit', '-qm', 'old', cwd=tmp)
            done, rows = run_checker(tmp, '--worktree')
            self.assertEqual((done.returncode, rows), (0, []), done.stderr)


if __name__ == '__main__':
    unittest.main()
