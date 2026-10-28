"""Install the global AGENTS.md copies listed in global/targets.json."""
import hashlib
import json
from pathlib import Path
import shutil

MANIFEST = '.agents/.agent-skills-global-manifest.json'


class GlobalConflict(Exception):
    pass


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_plan(repo_root):
    plan = json.loads((repo_root / 'global/targets.json').read_text())
    return repo_root / plan['source'], plan['targets']


def check_target(target, owned_hash, source_hash):
    if target.is_symlink():
        raise GlobalConflict(f'Unmanaged symlink: {target}')
    if target.exists() and digest(target) not in (owned_hash, source_hash):
        raise GlobalConflict(f'Unmanaged or locally edited file: {target}. Reconcile it with the source first.')


def install_global(repo_root, home):
    source, targets = load_plan(repo_root)
    manifest = home / MANIFEST
    previous = json.loads(manifest.read_text()) if manifest.exists() else {}
    source_hash = digest(source)
    for name in targets:
        check_target(home / name, previous.get(name), source_hash)
    for name in targets:
        (home / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, home / name)
        print(f'Installed global instructions: ~/{name}')
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({name: source_hash for name in targets}, indent=2, sort_keys=True) + '\n')
