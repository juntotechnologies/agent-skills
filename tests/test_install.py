import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'repo'
        shutil.copytree(ROOT / 'scripts', self.repo / 'scripts')
        self.source = self.repo / 'skills/example'
        self.source.mkdir(parents=True)
        (self.source / 'SKILL.md').write_text('original')
        self.home = self.base / 'home'
        self.home.mkdir()
        self.target = self.home / '.agents/skills/example'

    def run_install(self, expected=0, *args):
        result = subprocess.run(['bash', str(self.repo / 'scripts/install.sh'), *args],
            env={**os.environ, 'HOME': str(self.home)}, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_copy_update_remove_and_idempotence(self):
        self.run_install()
        self.assertFalse(self.target.is_symlink())
        self.assertEqual((self.target / 'SKILL.md').read_text(), 'original')
        self.run_install()
        (self.source / 'extra.txt').write_text('new')
        self.run_install()
        self.assertTrue((self.target / 'extra.txt').exists())
        (self.source / 'extra.txt').unlink()
        self.run_install()
        self.assertFalse((self.target / 'extra.txt').exists())
        shutil.rmtree(self.source)
        self.run_install()
        self.assertFalse(self.target.exists())

    def test_local_edits_block_all_updates(self):
        self.run_install()
        (self.target / 'SKILL.md').write_text('local')
        (self.source / 'SKILL.md').write_text('upstream')
        self.run_install(1)
        self.assertEqual((self.target / 'SKILL.md').read_text(), 'local')

    def test_unmanaged_content_preserved(self):
        self.target.mkdir(parents=True)
        (self.target / 'mine').write_text('keep')
        self.run_install(1)
        self.assertEqual((self.target / 'mine').read_text(), 'keep')
        self.assertFalse((self.target / 'SKILL.md').exists())

    def test_owned_symlink_migrates_but_foreign_link_does_not(self):
        self.target.parent.mkdir(parents=True)
        self.target.symlink_to(self.source, target_is_directory=True)
        self.run_install()
        self.assertFalse(self.target.is_symlink())
        shutil.rmtree(self.target)
        self.target.symlink_to(self.home, target_is_directory=True)
        self.run_install(1)
        self.assertTrue(self.target.is_symlink())

    def test_projects_and_other_skills_untouched(self):
        project = self.home / 'Documents/GitHub/projects/chem-inventory'
        project.mkdir(parents=True)
        (project / 'AGENTS.md').write_text('local instructions')
        unrelated = self.home / '.agents/skills/other'
        unrelated.mkdir(parents=True)
        (unrelated / 'SKILL.md').write_text('other')
        self.run_install(0, '--workspace-root', str(project.parent))
        self.assertEqual((project / 'AGENTS.md').read_text(), 'local instructions')
        self.assertEqual((unrelated / 'SKILL.md').read_text(), 'other')
        self.assertFalse((project / '.agents').exists())

    def test_source_link_refused(self):
        (self.source / 'outside').symlink_to(self.home)
        self.run_install(1)
        self.assertFalse(self.target.exists())

    def test_removed_modified_skill_preserved(self):
        self.run_install()
        (self.target / 'SKILL.md').write_text('local')
        shutil.rmtree(self.source)
        self.run_install(1)
        self.assertTrue(self.target.exists())

    def test_unknown_flag(self):
        self.run_install(2, '--claude-compat')
        self.assertFalse((self.home / '.agents').exists())

if __name__ == '__main__':
    unittest.main()
