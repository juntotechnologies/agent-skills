"""One check for every repo: shared lint on changed lines, then the repo's tests. Same command in hook, CI + ops ship.

Run in a repo: check.py [--base origin/main] [--staged] [--all] [--lint-only] [--setup]. Repo settings: ops-check.json
(`test`, `setup` commands; `exempt`: rule -> path patterns).
Prints 1 JSON line per fault. Exit 1 on any fault.
"""
import argparse
import fnmatch
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import pyrules
import scope
import textrules
from model import Fault

HERE = Path(__file__).resolve().parent
SETTINGS_FILE = 'ops-check.json'


def parse(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--base', default='origin/main', help='compare HEAD with its merge base on this ref')
    parser.add_argument('--staged', action='store_true', help='check the staged change; for the pre-commit hook')
    parser.add_argument('--all', action='store_true', help='every line of every tracked file, not only changed lines')
    parser.add_argument('--lint-only', action='store_true', help='skip the repo test command')
    parser.add_argument('--setup', action='store_true', help='run the repo setup command first; for CI')
    return parser.parse_args(argv)


def git(*args):
    return subprocess.run(['git', *args], capture_output=True, text=True, check=True).stdout


def changed_lines(args):
    diff_args = ['--cached'] if args.staged else [f'{args.base}...HEAD']
    return scope.parse_diff(git('diff', '-U0', '--diff-filter=AM', *diff_args))


def whole_files():
    paths = [path for path in git('ls-files').splitlines() if Path(path).is_file()]
    return {path: set(range(1, 1 + len(read_text(path).splitlines()))) for path in paths}


def read_text(path):
    return Path(path).read_text(errors='ignore')


def load_settings():
    file = Path(SETTINGS_FILE)
    return json.loads(file.read_text()) if file.exists() else {}


def with_suffix(changed, suffixes):
    return [path for path in changed if Path(path).suffix in suffixes and Path(path).is_file()]


def run_tool(command):
    return subprocess.run(command, capture_output=True, text=True, check=False)


def tool_failed(name, done):
    if done.returncode in (0, 1):
        return []
    return [Fault(name, 1, 1, 'tool-failed', f'exit {done.returncode}: {done.stderr.strip()[:200]}')]


def ruff_fault(row, spans):
    path = str(Path(row['filename']).resolve().relative_to(Path.cwd()))
    line = row['location']['row']
    return Fault(path, line, spans.get(path, {}).get(line, line), 'ruff', f'{row["code"]}: {row["message"]}')


def spans_of(path):
    try:
        return pyrules.function_spans(read_text(path))
    except SyntaxError:
        return {}


def ruff_faults(paths, limits):
    if not paths:
        return []
    done = run_tool(['uvx', limits['ruff'], 'check', '--config', str(HERE / 'ruff.toml'), '--output-format', 'json', *paths])
    spans = {path: spans_of(path) for path in paths}
    return [*tool_failed('ruff', done), *(ruff_fault(row, spans) for row in json.loads(done.stdout or '[]'))]


def python_faults(paths, limits):
    own = [fault for path in paths for fault in pyrules.faults_for(path, read_text(path), limits)]
    return [*own, *ruff_faults(paths, limits)]


def install_js():
    if not (HERE / 'js/node_modules').exists():
        subprocess.run(['npm', 'ci', '--silent', '--prefix', str(HERE / 'js')], capture_output=True, check=True)


def eslint_row_faults(result):
    path = str(Path(result['filePath']).resolve().relative_to(Path.cwd()))
    return [Fault(path, row.get('line', 1), row.get('endLine', row.get('line', 1)), 'eslint', f'{row["ruleId"]}: {row["message"]}')
            for row in result['messages']]


def js_faults(paths):
    if not paths:
        return []
    install_js()
    config = str(HERE / 'js/eslint.config.mjs')
    eslint = str(HERE / 'js/node_modules/.bin/eslint')
    done = run_tool([eslint, '--no-inline-config', '--no-config-lookup', '-c', config, '--format', 'json', *paths])
    rows = [fault for result in json.loads(done.stdout or '[]') for fault in eslint_row_faults(result)]
    return [*tool_failed('eslint', done), *rows]


def text_faults(changed, limits):
    faults = []
    for path, lines in changed.items():
        faults += textrules.claude_md_faults(path, lines)
        faults += textrules.uv_faults(path, read_text(path), lines, limits) if Path(path).is_file() else []
    return faults


def exempt(fault, settings):
    patterns = [*settings.get('exempt', {}).get(fault.rule, []), *settings.get('exempt', {}).get('*', [])]
    return any(fnmatch.fnmatch(fault.path, pattern) for pattern in patterns)


def counts(fault, changed):
    return fault.rule == 'tool-failed' or scope.touched(fault, changed)


def lint(changed, settings, limits):
    python = with_suffix(changed, limits['python_suffixes'])
    javascript = with_suffix(changed, limits['js_suffixes'])
    found = [*python_faults(python, limits), *js_faults(javascript), *text_faults(changed, limits)]
    return [fault for fault in found if counts(fault, changed) and not exempt(fault, settings)]


def test_faults(settings):
    command = settings.get('test')
    if not command or subprocess.run(command, shell=True, check=False).returncode == 0:
        return []
    return [Fault(SETTINGS_FILE, 1, 1, 'repo-tests', f'failed: {command}')]


def run_setup(settings):
    if settings.get('setup'):
        subprocess.run(settings['setup'], shell=True, check=True)


def main(argv):
    args = parse(argv)
    limits = json.loads((HERE / 'limits.json').read_text())
    settings = load_settings()
    if args.setup:
        run_setup(settings)
    changed = whole_files() if args.all else changed_lines(args)
    faults = lint(changed, settings, limits)
    faults += [] if args.lint_only else test_faults(settings)
    for fault in faults:
        print(json.dumps(asdict(fault)))
    return 1 if faults else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
