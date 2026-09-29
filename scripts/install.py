"""Install owned global skill copies without touching project repositories."""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile


class Conflict(Exception):
    pass


def snapshot(directory):
    if directory.is_symlink() or not directory.is_dir():
        raise Conflict(f'Expected a real directory: {directory}')
    result = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise Conflict(f'Symlinks are not installed or overwritten: {path}')
        key = path.relative_to(directory).as_posix()
        if path.is_file():
            result[key] = [hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mode & 0o777]
        elif path.is_dir():
            result[key] = ['directory']
        else:
            raise Conflict(f'Unsupported file: {path}')
    return result


@contextmanager
def install_lock(root):
    lock = root / '.agent-skills-install-lock'
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise Conflict(f'Another install is active, or a stale lock needs review: {lock}') from error
    try:
        yield
    finally:
        lock.rmdir()


def sync(source_root, destination):
    destination.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise Conflict(f'Install directory must not be a symlink: {destination}')
    with install_lock(destination):
        manifest = destination / '.agent-skills-manifest.json'
        if manifest.is_symlink():
            raise Conflict(f'Manifest must not be a symlink: {manifest}')
        previous = json.loads(manifest.read_text()) if manifest.exists() else {}
        if not isinstance(previous, dict):
            raise Conflict('Invalid installation manifest')
        sources = {p.name: p for p in source_root.iterdir() if (p / 'SKILL.md').is_file()}
        for name in set(sources) | set(previous):
            if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]*', name):
                raise Conflict(f'Invalid skill name: {name}')
        current = {name: snapshot(path) for name, path in sources.items()}
        # Preflight the complete install before changing any skill.
        for name in sorted(set(sources) | set(previous)):
            target = destination / name
            if target.is_symlink():
                if name not in sources or target.resolve() != sources[name].resolve():
                    raise Conflict(f'Unmanaged symlink: {target}')
            elif target.exists():
                actual = snapshot(target)
                if name not in previous or actual != previous[name]:
                    raise Conflict(f'Unmanaged or locally edited skill: {target}. Preserve/reconcile it before syncing.')
            elif name in previous:
                raise Conflict(f'Locally removed skill: {target}. Reconcile the manifest before syncing.')
        for name, source in sorted(sources.items()):
            target = destination / name
            if name in previous and previous[name] == current[name] and not target.is_symlink():
                continue
            with tempfile.TemporaryDirectory(prefix='.agent-skills-stage-', dir=destination) as staging:
                staged = Path(staging) / name
                shutil.copytree(source, staged)
                if snapshot(staged) != current[name]:
                    raise Conflict(f'Source changed during install: {source}')
                if target.is_symlink():
                    target.unlink()
                elif target.exists():
                    shutil.rmtree(target)
                staged.rename(target)
            # Save after each completed change so an interrupted run can resume.
            previous[name] = current[name]
            write_manifest(manifest, previous)
            print(f'Installed copy: {name}')
        for name in sorted(set(previous) - set(sources)):
            shutil.rmtree(destination / name)
            del previous[name]
            write_manifest(manifest, previous)
            print(f'Removed retired managed skill: {name}')
        write_manifest(manifest, current)
        print('Global skills synchronized; project repositories were not touched.')


def write_manifest(path, contents):
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as file:
        json.dump(contents, file, indent=2, sort_keys=True)
        file.write('\n')
        temporary = Path(file.name)
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace-root', help='Deprecated; accepted for older bootstrap callers, never scanned')
    parser.parse_args()
    try:
        sync(Path(__file__).resolve().parents[1] / 'skills', Path.home() / '.agents/skills')
    except (Conflict, OSError, ValueError) as error:
        print(f'Install stopped: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
