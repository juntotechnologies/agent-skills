# agent-skills

Reusable user-wide skills and generic project bootstrap templates. Project
instructions and project-specific skills belong in the owning repositories.

## Install global skills

Requires `uv` and Python (resolved through `uv`):

```sh
scripts/install.sh
```

Installs real copies of `skills/*` into `~/.agents/skills`. It never searches or
writes project checkouts, and never manages Claude compatibility paths. Older
bootstrap callers may still pass `--workspace-root`; it is accepted but ignored.

`.agent-skills-manifest.json` in the install directory records owned skill file
hashes and modes. Re-running installs upstream updates and removes retired,
unmodified managed skills. Unmanaged paths, local edits, foreign symlinks, and
locally removed managed skills stop the whole preflight before any skill changes.
Only symlinks resolving to the corresponding source skill in this checkout are
converted to copies. Unrelated installed skills remain untouched.

Edit global skills in this repository, then run the installer. If an installed
copy was edited, preserve it and reconcile its changes with the source before
restoring the installed version recorded in the manifest. Do not delete a conflict
just to make installation pass. A concurrent run is refused; after an interrupted
process, inspect it before removing a stale `.agent-skills-install-lock` directory.

The installer stages each replacement and records completed changes incrementally.
It is not a transaction across the whole skill collection; an I/O failure can
require recovery from this source checkout and the manifest.

## Project ownership

Projects track real `AGENTS.md` files, scoped directory guidance, and project
skills under `.agents/skills`. The Setup Project Repo skill supplies starting
assets and can explicitly merge requested generic updates while preserving local
rules. There is no project registry or automatic propagation into projects.

The repository's own workflow/template files are ordinary files too. Generic
assets live under `skills/setup-project-repo/assets/`; update this repo's own
copies separately when a shared change applies.

## Verification

```sh
uv run python -m unittest discover -s tests -v
bash tests/test_install.sh
```

## Migration ordering

Before removing older `projects/` sources from any checkout, land the owning
projects' local copies: chem-inventory, personal-config, and swarm-infra. Existing
Claude aliases may remain if they resolve entirely inside their owning repo.
Update personal-config's bootstrap to call the global-only installer. Then update
agent-skills and install the global copies. No live services or databases change.
