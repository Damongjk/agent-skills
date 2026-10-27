import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('skill_sync', ROOT / 'tools/skill_sync.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class SkillHubTests(unittest.TestCase):
    def setUp(self):
        self.home = ROOT / 'test-runs' / uuid.uuid4().hex / 'home'
        self.repo = self.home / 'Documents/Codex/agent-skills'
        self.repo.mkdir(parents=True)
        self.cc = self.home / '.cc-switch'
        self.cc.mkdir()
        c = sqlite3.connect(self.cc / 'cc-switch.db')
        c.execute('create table skills(id text primary key,name text not null,description text,directory text not null,repo_owner text,content_hash text,installed_at integer default 0,updated_at integer default 0,enabled_codex boolean default 0,enabled_claude boolean default 0,enabled_hermes boolean default 0)')
        c.close()
        self.source = self.repo / 'skills/common/probe'
        self.make_skill(self.source, 'probe')
        self.catalog = {'schema': 1, 'repository': 'https://github.com/Damongjk/agent-skills.git', 'branch': 'main', 'skills': {'probe': {'scope': 'common', 'path': 'skills/common/probe'}}}
        self.write_catalog()

    def make_skill(self, where, name):
        where.mkdir(parents=True)
        (where / 'SKILL.md').write_text('---\nname: '+name+'\ndescription: Test synchronization only.\n---\nRead version.txt.\n', encoding='utf-8')
        (where / 'version.txt').write_text('v1', encoding='utf-8')

    def write_catalog(self):
        (self.repo / 'catalog.json').write_text(json.dumps(self.catalog), encoding='utf-8')

    def hub(self):
        return mod.Hub(self.repo, self.home)

    def test_common_links_and_registration(self):
        h = self.hub(); h.install('probe')
        master = self.cc / 'skills/probe'
        self.assertEqual((self.home / '.agents/skills/probe').resolve(), master.resolve())
        self.assertEqual((self.home / '.workbuddy/skills/probe').resolve(), master.resolve())
        c = sqlite3.connect(self.cc / 'cc-switch.db')
        self.assertEqual(c.execute('select id from skills').fetchone()[0], 'local:probe'); c.close()

    def test_edit_through_workbuddy_returns_to_master(self):
        h = self.hub(); h.install('probe')
        (self.home / '.workbuddy/skills/probe/version.txt').write_text('v2', encoding='utf-8')
        self.assertEqual((self.cc / 'skills/probe/version.txt').read_text(), 'v2')

    def test_both_sides_changed_blocks_overwrite(self):
        h = self.hub(); h.install('probe')
        (self.cc / 'skills/probe/version.txt').write_text('local')
        (self.source / 'version.txt').write_text('remote')
        with self.assertRaises(mod.SyncError): h.install('probe')
        self.assertEqual((self.cc / 'skills/probe/version.txt').read_text(), 'local')
        self.assertEqual((self.source / 'version.txt').read_text(), 'remote')

    def test_remote_only_update_keeps_live_links(self):
        h = self.hub(); h.install('probe')
        (self.source / 'version.txt').write_text('v2')
        h.install('probe')
        self.assertEqual((self.home / '.workbuddy/skills/probe/version.txt').read_text(), 'v2')

    def test_codex_dedicated_does_not_leak_to_shared_or_workbuddy(self):
        self.catalog['skills']['probe']['scope'] = 'codex'; self.write_catalog()
        h = self.hub(); h.install('probe')
        self.assertTrue((self.home / '.codex/skills/probe').is_symlink())
        self.assertFalse((self.home / '.agents/skills/probe').exists())
        self.assertFalse((self.home / '.workbuddy/skills/probe').exists())

    def test_workbuddy_dedicated_does_not_leak_to_shared_or_codex(self):
        self.catalog['skills']['probe']['scope'] = 'workbuddy'; self.write_catalog()
        h = self.hub(); h.install('probe')
        self.assertTrue((self.home / '.workbuddy/skills/probe').is_symlink())
        self.assertFalse((self.home / '.agents/skills/probe').exists())
        self.assertFalse((self.home / '.codex/skills/probe').exists())

    def test_nested_link_cannot_publish_external_data(self):
        outside = self.home / 'unrelated'; outside.mkdir()
        (outside / 'private.txt').write_text('Do not publish this unrelated file')
        (self.source / 'outside').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(mod.SyncError): self.hub().install('probe')
        self.assertFalse((self.cc / 'skills/probe').exists())

    def test_new_workbuddy_skill_adopted_into_common_master(self):
        source = self.home / '.workbuddy/skills/new-probe'; self.make_skill(source, 'new-probe')
        h = self.hub(); h.adopt(source, 'common')
        self.assertTrue(source.is_symlink())
        self.assertTrue((self.cc / 'skills/new-probe/SKILL.md').exists())
        self.assertTrue((self.repo / 'skills/common/new-probe/SKILL.md').exists())

    def test_dedicated_adoption_removes_source_from_wrong_agent(self):
        source = self.home / '.workbuddy/skills/codex-only'; self.make_skill(source, 'codex-only')
        h = self.hub(); h.adopt(source, 'codex')
        self.assertFalse(source.exists())
        self.assertTrue((self.home / '.codex/skills/codex-only').is_symlink())

    def test_secret_is_blocked_before_registration(self):
        (self.source / 'private.txt').write_text('sk-' + 'x' * 40)
        with self.assertRaises(mod.SyncError): self.hub().install('probe')
        self.assertFalse((self.cc / 'skills/probe').exists())

    def test_existing_repository_source_not_silently_reassigned(self):
        c = sqlite3.connect(self.cc / 'cc-switch.db')
        c.execute('insert into skills(id,name,directory,repo_owner) values(?,?,?,?)', ('upstream:probe','probe','probe','upstream'))
        c.commit(); c.close()
        with self.assertRaises(mod.SyncError): self.hub().install('probe')
        self.assertFalse((self.cc / 'skills/probe').exists())

if __name__ == '__main__':
    unittest.main()
