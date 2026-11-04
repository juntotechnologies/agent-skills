# PR 55: Python only through uv, enforced

Status: done

Branch: `feature/uv-only-everywhere`

## Goal

Shaun, 2026-11-03: Python runs and installs only through `uv`; never a hand-extracted binary; "enforced at the linter level and a pre-commit hook, never pushed". Before: rule `uv-only` read only shell-like files and 2 words (`python`, `pip`).

Now `uv-only` also flags, on changed lines of any file:

| Where | What |
|---|---|
| shell, yml, json, plist, tmpl, Dockerfile, Makefile | bare or absolute `python*` / `pip*`; `pyenv`, `conda`, `mamba`, `pipx`, `pipenv`, `poetry`, `pdm`, `virtualenv`, `ensurepip`, `get-pip`; `brew`/`apt`/... installing python; `curl`/`wget`/`tar` of a Python build; `actions/setup-python`, `setup-miniconda` |
| any file, line 1 | python shebang (use `#!/usr/bin/env -S uv run --script`) |
| Python code | `subprocess.*`, `os.system/exec*/spawn*`, `asyncio.create_subprocess_*` whose command is a bare interpreter or `sys.executable` |

`uv ...` and `uvx ...` segments are never flagged. One data file, `checker/uv_only.json`, holds the patterns; `ops guard` (PreToolUse) reads the same file.

Gates that carry it: write hook, pre-commit, pre-push, `ops ship` + CI (all run this checker).

## Implementation Checklist

- [x] Tests first: text, shebang, Python-code and data-file tests (`tests/test_checker.py`)
- [x] `checker/uv_only.json`; `textrules` and `pyrules` read it
- [x] `limits.json` `shell_paths` covers json, plist, tmpl, Dockerfile, bash, zsh, Justfile
- [x] Registry rule `python-through-uv` states the whole policy
- [x] Own lint clean; suite OK
- [x] Exempt only `checker/uv_only.json` (the patterns) and `rules/rules.json` (policy prose names the tools). CI found the second one: local `ops check` ran the installed checker, CI runs the branch's own. Parity fix in personal-config.

## Known Limits

- Changed lines only: old code passes until touched. Backlog tracked in the system roadmap.
- `sh -c 'python3 x'` inside a Python list is not parsed; the guard sees the shell text.

## Smoke Tests

Not applicable: no UI.

## Related Docs

- personal-config: `ops guard` reads `checker/uv_only.json`
