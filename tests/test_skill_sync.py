import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import unittest
from unittest.mock import patch
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

    def test_named_secret_literals_are_blocked(self):
        for text in ['api_key = "' + 'x' * 40 + '"', '"access_token": "' + 'y' * 40 + '"', 'password: ' + 'z' * 40]:
            with self.subTest(text_type=text[:10]):
                (self.source / 'config.txt').write_text(text)
                with self.assertRaises(mod.SyncError): mod.package(self.source)

    def test_credential_reader_expression_is_not_a_secret_literal(self):
        (self.source / 'reader.py').write_text('api_key = backend_elevenlabs.read_elevenlabs_api_key(args.elevenlabs_api_key_env)\n')
        self.assertEqual(mod.package(self.source)[0], 'probe')

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

    def test_failed_remote_verification_does_not_advance_sync_state(self):
        h = self.hub(); h.install('probe')
        previous_hash = h.state['probe']['hash']
        (self.cc / 'skills/probe/version.txt').write_text('v2')
        def git(*args):
            if args[0] == 'remote': return self.catalog['repository']
            if args[0] == 'branch': return 'main'
            if args[0] == 'show': return json.dumps(self.catalog)
            if args[0] == 'rev-parse': return 'a' * 40
            if args[0] == 'ls-remote': return 'b' * 40 + '\trefs/heads/main'
            return ''
        with patch.object(h, 'git', side_effect=git), patch.object(h, 'prepare_github'):
            with self.assertRaisesRegex(mod.SyncError, 'live remote revision'):
                h.checkpoint(['probe'], 'Update probe')
        self.assertEqual(h.state['probe']['hash'], previous_hash)
        self.assertEqual((self.cc / 'skills/probe/version.txt').read_text(), 'v2')

class GitHubConnectionTests(unittest.TestCase):
    def hub(self):
        hub = mod.Hub.__new__(mod.Hub)
        hub.repo = Path('/tmp/test-skill-repository')
        hub.catalog = {'repository': 'https://github.com/Damongjk/agent-skills.git', 'branch': 'main'}
        hub.network_env = None
        return hub

    def run_connection(self, hub, outcomes, proxies=None, bypass=False, env=None,
                       configured=False):
        probes = []
        def run(args, **kwargs):
            if 'config' in args:
                return subprocess.CompletedProcess(args, 0 if configured else 1, '', '')
            probes.append((args, dict(kwargs['env'])))
            result = outcomes[len(probes) - 1]
            if isinstance(result, Exception): raise result
            code, error = result
            return subprocess.CompletedProcess(args, code, 'a' * 40 + '\trefs/heads/main', error)
        log = io.StringIO()
        with patch.dict(os.environ, env or {}, clear=True), \
             patch.object(mod.urllib.request, 'getproxies', return_value=proxies or {}), \
             patch.object(mod.urllib.request, 'proxy_bypass', return_value=bypass), \
             patch.object(mod.subprocess, 'run', side_effect=run), \
             contextlib.redirect_stderr(log):
            hub.prepare_github()
        return probes, log.getvalue()

    def test_system_proxy_is_selected_without_persistent_configuration(self):
        hub = self.hub()
        original = dict(os.environ)
        probes, log = self.run_connection(hub, [(0, '')],
                         {'https': 'http://proxy.invalid:9000'})
        self.assertEqual(len(probes), 1)
        self.assertIn('ls-remote', probes[0][0])
        self.assertEqual(hub.network_env['GIT_CONFIG_VALUE_0'], 'http://proxy.invalid:9000')
        self.assertEqual(dict(os.environ), original)
        self.assertIn('system HTTPS proxy', log)

    def test_unavailable_proxy_can_fall_back_to_a_working_connection(self):
        hub = self.hub()
        probes, _ = self.run_connection(hub, [(128, 'Failed to connect'), (0, '')],
                         {'https': 'http://proxy.invalid:9000'})
        self.assertEqual(len(probes), 2)
        self.assertNotIn('GIT_CONFIG_COUNT', hub.network_env)

    def test_proxy_bypass_does_not_force_the_system_proxy(self):
        hub = self.hub()
        probes, _ = self.run_connection(hub, [(0, '')],
                         {'https': 'http://proxy.invalid:9000'}, bypass=True)
        self.assertEqual(len(probes), 1)
        self.assertNotIn('GIT_CONFIG_COUNT', hub.network_env)

    def test_explicit_git_proxy_is_not_silently_overridden(self):
        hub = self.hub()
        probes, _ = self.run_connection(hub, [(0, '')],
                         {'https': 'http://proxy.invalid:9000'}, configured=True)
        self.assertEqual(len(probes), 1)
        self.assertNotIn('GIT_CONFIG_COUNT', hub.network_env)

    def test_existing_process_proxy_is_reused(self):
        hub = self.hub()
        probes, _ = self.run_connection(hub, [(0, '')],
                         env={'HTTPS_PROXY': 'http://proxy.invalid:9000'})
        self.assertEqual(len(probes), 1)
        self.assertEqual(hub.network_env['HTTPS_PROXY'], 'http://proxy.invalid:9000')

    def test_existing_runtime_config_entries_are_preserved(self):
        hub = self.hub()
        env = {'GIT_CONFIG_COUNT': '1', 'GIT_CONFIG_KEY_0': 'color.ui',
               'GIT_CONFIG_VALUE_0': 'false'}
        self.run_connection(hub, [(0, '')], {'https': 'http://proxy.invalid:9000'}, env=env)
        self.assertEqual(hub.network_env['GIT_CONFIG_COUNT'], '2')
        self.assertEqual(hub.network_env['GIT_CONFIG_KEY_0'], 'color.ui')
        self.assertEqual(hub.network_env['GIT_CONFIG_KEY_1'], 'http.proxy')

    def test_proxy_timeout_tries_the_remaining_route(self):
        hub = self.hub()
        probes, _ = self.run_connection(hub,
                         [subprocess.TimeoutExpired('git', 12), (0, '')],
                         {'https': 'http://proxy.invalid:9000'})
        self.assertEqual(len(probes), 2)

    def test_authentication_failure_is_not_retried_as_networking(self):
        with self.assertRaisesRegex(mod.SyncError, 'authentication or repository access'):
            self.run_connection(self.hub(), [(128, 'Authentication failed')],
                                {'https': 'http://proxy.invalid:9000'})

    def test_proxy_authentication_is_distinguished_from_github_login(self):
        with self.assertRaisesRegex(mod.SyncError, 'Proxy authentication failed'):
            self.run_connection(self.hub(), [(128, 'CONNECT tunnel failed, response 407')],
                                {'https': 'http://proxy.invalid:9000'})

    def test_failed_routes_do_not_expose_proxy_credentials(self):
        secret = 'http://test-user:private-value@proxy.invalid:9000'
        with self.assertRaises(mod.SyncError) as caught:
            self.run_connection(self.hub(), [(128, 'Failed to connect'), (128, 'DNS failed')],
                                {'https': secret})
        self.assertNotIn('test-user', str(caught.exception))
        self.assertNotIn('private-value', str(caught.exception))
        self.assertIn('Do not infer that the saved login expired', str(caught.exception))

    def test_certificate_errors_do_not_disable_tls_verification(self):
        with self.assertRaisesRegex(mod.SyncError, 'TLS certificate validation failed'):
            self.run_connection(self.hub(), [(128, 'SSL certificate problem')])

if __name__ == '__main__':
    unittest.main()
