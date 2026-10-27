"""Explicit skill checkpoints. No background watcher, embedded credentials, or force push."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import uuid

SCOPES = {'common', 'codex', 'workbuddy'}
SKIP = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.DS_Store', '_meta.json', '_skillhub_meta.json'}
TEXT = {'.md', '.py', '.ps1', '.json', '.yaml', '.yml', '.toml', '.txt', '.js', '.ts', '.html', '.css', '.sh', '.xml'}

class SyncError(RuntimeError):
    pass

def fail(message):
    raise SyncError(message)

def is_link(path):
    # Windows directory junction support without requiring Python 3.12+.
    return path.is_symlink() or bool(getattr(path.lstat(), 'st_file_attributes', 0) & 0x400)

def data_files(root):
    root = Path(root)
    if not root.is_dir():
        return {}
    result = {}
    for dp, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [n for n in dirs if n not in SKIP]
        for n in dirs + names:
            p = Path(dp) / n
            if is_link(p):
                fail('Nested links are not published: ' + str(p))
        for n in names:
            if n in SKIP or n.endswith(('.pyc', '.pyo')):
                continue
            p = Path(dp) / n
            result[p.relative_to(root).as_posix()] = p.read_bytes()
    return result

def digest(files):
    return hashlib.sha256(json.dumps([(n, hashlib.sha256(v).hexdigest()) for n, v in sorted(files.items())]).encode()).hexdigest()

def package(root):
    files = data_files(root)
    if 'SKILL.md' not in files:
        fail('SKILL.md is required')
    text = files['SKILL.md'].decode('utf-8-sig')
    match = re.search(r'^name:\s*[\"\']?([a-z0-9][a-z0-9-]{0,63})[\"\']?\s*$', text, re.M)
    if not match or not re.search(r'^description:\s*\S', text, re.M):
        fail('Skill needs a valid lowercase name and a nonempty description')
    name = match.group(1)
    for n, raw in files.items():
        if Path(n).name.startswith('.env') or Path(n).name in {'auth.json', 'credentials.json'} or Path(n).suffix.lower() in {'.pem', '.key', '.p12'}:
            fail('Credential file blocked: ' + n)
        if Path(n).suffix.lower() in TEXT:
            t = raw.decode('utf-8', errors='replace')
            if re.search(r'(?i)(?:sk-[A-Za-z0-9_-]{20,}|ak_[A-Za-z0-9]{16,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:app[_ -]?secret|api[_ -]?key|access[_ -]?token|password)[^A-Za-z0-9\n]{0,16}[A-Za-z0-9_/+.-]{24,})', t):
                fail('Possible credential; inspect before publishing: ' + n)
            if re.search(r'\b(?:basrz|doxrz)[A-Za-z0-9]{12,}|\btbl[A-Za-z0-9]{10,}|\bou_[a-f0-9]{24,}', t):
                fail('Internal resource/person identifiers require content review: ' + n)
    description = re.search(r'^description:\s*(.+)$', text, re.M).group(1).strip().strip('\"\'')
    return name, description, files

class Hub:
    def __init__(self, repo, home=None):
        self.repo = Path(repo).resolve()
        self.home = Path(home or Path.home()).resolve()
        self.catalog_path = self.repo / 'catalog.json'
        self.catalog = json.loads(self.catalog_path.read_text(encoding='utf-8'))
        if self.catalog.get('repository') != 'https://github.com/Damongjk/agent-skills.git':
            fail('Unexpected publication destination')
        self.master = self.home / '.cc-switch/skills'
        self.db = self.home / '.cc-switch/cc-switch.db'
        self.state_path = self.home / '.cc-switch/skill-sync-state.json'
        self.state = json.loads(self.state_path.read_text(encoding='utf-8')) if self.state_path.exists() else {}
        settings = self.home / '.cc-switch/settings.json'
        if settings.exists() and json.loads(settings.read_text(encoding='utf-8-sig')).get('skillStorageLocation', 'cc_switch') != 'cc_switch':
            fail('CC Switch master storage changed; inspect before proceeding')
        if not self.db.exists():
            fail('Initialize CC Switch on this computer first')

    def save(self):
        self.catalog_path.write_text(json.dumps(self.catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def entry_path(self, entry):
        p = (self.repo / entry['path']).resolve()
        if not p.is_relative_to(self.repo / 'skills') or entry['scope'] not in SCOPES:
            fail('Unsafe catalog path or scope')
        return p

    def backup(self, path):
        path = Path(path)
        if not path.resolve().is_relative_to(self.home):
            fail('Refusing to move a path outside the user directory')
        target = self.home / '.cc-switch/skill-sync-backups' / (str(time.time_ns()) + '-' + uuid.uuid4().hex[:6]) / path.name
        target.parent.mkdir(parents=True)
        # Both absolute paths are checked before moving a directory.
        if not target.resolve().is_relative_to(self.home / '.cc-switch/skill-sync-backups'):
            fail('Unsafe backup target')
        path.rename(target)
        return target

    def write_tree(self, target, files):
        target = Path(target)
        if target.exists():
            self.backup(target)
        target.mkdir(parents=True)
        for rel, raw in files.items():
            p = target / rel
            if not p.resolve().is_relative_to(target.resolve()):
                fail('Unsafe package entry')
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)

    def projections(self, name, scope):
        choices = {
            'common': [self.home / '.agents/skills' / name, self.home / '.workbuddy/skills' / name],
            'codex': [self.home / '.codex/skills' / name],
            'workbuddy': [self.home / '.workbuddy/skills' / name],
        }
        return choices[scope]

    def forbidden_projections(self, name, scope):
        if scope == 'codex':
            return [self.home / '.agents/skills' / name, self.home / '.workbuddy/skills' / name]
        if scope == 'workbuddy':
            return [self.home / '.agents/skills' / name, self.home / '.codex/skills' / name]
        return []

    def register(self, name, description, scope):
        c = sqlite3.connect(self.db, timeout=10)
        c.row_factory = sqlite3.Row
        try:
            c.execute('BEGIN IMMEDIATE')
            columns = {r['name'] for r in c.execute('pragma table_info(skills)')}
            required = {'id', 'name', 'directory', 'description', 'installed_at', 'updated_at', 'repo_owner', 'content_hash', 'enabled_codex'}
            if not required.issubset(columns):
                fail('Unsupported CC Switch skill schema')
            old = c.execute('select * from skills where lower(directory)=lower(?)', (name,)).fetchone()
            if old and old['repo_owner']:
                fail('This directory is managed by another repository; resolve its source in CC Switch first')
            snapshot = self.home / '.cc-switch/skill-sync-backups' / ('metadata-' + str(time.time_ns()) + '.json')
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_text(json.dumps(dict(old) if old else {'new_skill': name}, ensure_ascii=False, indent=2), encoding='utf-8')
            if old:
                c.execute('update skills set name=?,description=?,content_hash=NULL,updated_at=? where id=?', (name, description, int(time.time()), old['id']))
            else:
                c.execute('insert into skills(id,name,description,directory,installed_at,updated_at) values(?,?,?,?,?,?)', ('local:' + name, name, description, name, int(time.time()), int(time.time())))
            for column in sorted(k for k in columns if k.startswith('enabled_')):
                c.execute('update skills set '+column+'=? where lower(directory)=lower(?)', (int(scope == 'codex' and column == 'enabled_codex'), name))
            c.commit()
        except:
            c.rollback()
            raise
        finally:
            c.close()

    def install(self, name):
        entry = self.catalog['skills'][name]
        source = self.entry_path(entry)
        actual, description, files = package(source)
        if actual != name:
            fail('Catalog name differs from SKILL.md')
        target = self.master / name
        current = digest(data_files(target)) if target.exists() else None
        wanted = digest(files)
        baseline = self.state.get(name, {}).get('hash')
        if current and current != wanted and current != baseline:
            fail('Local master has unpublished changes: ' + name)
        old_scope = self.state.get(name, {}).get('scope')
        if old_scope and old_scope != entry['scope']:
            fail('Scope changes require explicit projection review: ' + name)
        # Preflight foreign directories before changing the master.
        for p in self.projections(name, entry['scope']):
            if (p.exists() or p.is_symlink()) and p.resolve() != target.resolve() and digest(data_files(p)) != wanted:
                fail('Independent application copy differs: ' + str(p))
        for p in self.forbidden_projections(name, entry['scope']):
            if (p.exists() or p.is_symlink()) and p.resolve() != target.resolve() and digest(data_files(p)) != wanted:
                fail('A different copy exists outside the dedicated scope: ' + str(p))
        self.register(name, description, entry['scope'])
        if current != wanted:
            self.write_tree(target, files)
        for p in self.projections(name, entry['scope']):
            if (p.exists() or p.is_symlink()) and p.resolve() == target.resolve():
                continue
            if p.exists() or p.is_symlink():
                self.backup(p)
            p.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(target, p, target_is_directory=True)
        for p in self.forbidden_projections(name, entry['scope']):
            if p.exists() or p.is_symlink():
                self.backup(p)
        self.state[name] = {'hash': wanted, 'scope': entry['scope']}
        self.save()

    def adopt(self, source, scope):
        if scope not in SCOPES:
            fail('Unknown scope')
        source = Path(source).resolve()
        name, description, files = package(source)
        target = self.master / name
        if target.exists() and source != target.resolve() and digest(data_files(target)) != digest(files):
            fail('Master and application source differ; inspect before adopting')
        if name in self.catalog['skills']:
            fail('Already managed; edit the master and use checkpoint')
        c = sqlite3.connect(self.db)
        try:
            old = c.execute('select repo_owner from skills where lower(directory)=lower(?)', (name,)).fetchone()
            if old and old[0]:
                fail('Existing upstream ownership must be resolved in CC Switch before adoption')
        finally:
            c.close()
        rel = ('skills/common/' if scope == 'common' else 'skills/agents/' + scope + '/') + name
        repo_target = self.repo / rel
        if repo_target.exists():
            fail('Repository destination already exists')
        self.write_tree(repo_target, files)
        self.catalog['skills'][name] = {'scope': scope, 'path': rel}
        self.save()
        self.install(name)
        return name

    def git(self, *args):
        env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='Never')
        r = subprocess.run(['git', '-C', str(self.repo), *args], capture_output=True, text=True, env=env, timeout=90)
        if r.returncode:
            # Git credentials stay in the credential manager, not command arguments.
            fail('Git operation failed (' + args[0] + '); changes remain local. ' + r.stderr[-600:])
        return r.stdout.strip()

    def check_remote(self):
        if self.git('remote', 'get-url', 'origin').rstrip('/') != self.catalog['repository']:
            fail('Unexpected Git origin; publication stopped')
        if self.git('branch', '--show-current') != self.catalog['branch']:
            fail('Use the configured publication branch')

    def checkpoint(self, names, message):
        self.check_remote()
        if self.git('diff', '--cached', '--name-only'):
            fail('The Git index already contains staged work; leave it untouched')
        try:
            previous = json.loads(self.git('show', 'HEAD:catalog.json'))
        except SyncError:
            previous = {'skills': {}}
        others = (set(previous['skills']) | set(self.catalog['skills'])) - set(names)
        if any(previous['skills'].get(n) != self.catalog['skills'].get(n) for n in others):
            fail('Catalog also has changes for other skills; publish those deliberately')
        paths = ['catalog.json']
        for name in names:
            if name not in self.catalog['skills']:
                fail('Adopt this skill before checkpointing: ' + name)
            entry = self.catalog['skills'][name]
            _, description, files = package(self.master / name)
            repo_path = self.entry_path(entry)
            master_hash, repo_hash = digest(files), digest(data_files(repo_path))
            baseline = self.state.get(name, {}).get('hash')
            if repo_hash != master_hash and repo_hash != baseline:
                fail('Repository/master conflict; neither version was overwritten: ' + name)
            if repo_hash != master_hash:
                self.write_tree(repo_path, files)
            self.register(name, description, entry['scope'])
            paths.append(entry['path'])
        self.save()
        self.git('add', '--', *paths)
        if self.git('diff', '--cached', '--name-only'):
            self.git('commit', '-m', message)
        self.git('push', 'origin', 'HEAD:' + self.catalog['branch'])
        for name in names:
            self.state[name]['hash'] = digest(data_files(self.master / name))
        self.save()
        return self.git('rev-parse', 'HEAD')

    def pull(self):
        self.check_remote()
        if self.git('status', '--porcelain'):
            fail('Repository has uncommitted work; checkpoint it first')
        self.git('pull', '--ff-only')
        self.catalog = json.loads(self.catalog_path.read_text(encoding='utf-8'))
        for name, entry in self.catalog['skills'].items():
            current = digest(data_files(self.master / name)) if (self.master / name).exists() else None
            remote = digest(data_files(self.entry_path(entry)))
            baseline = self.state.get(name, {}).get('hash')
            if current and current != remote and current != baseline:
                fail('Unpublished local master preserved; resolve before applying: ' + name)
        for name in self.catalog['skills']:
            self.install(name)

    def status(self):
        rows = []
        for name, e in self.catalog['skills'].items():
            master = self.master / name
            rows.append({'name': name, 'scope': e['scope'], 'master_exists': master.exists(), 'master_matches_repository': master.exists() and digest(data_files(master)) == digest(data_files(self.entry_path(e))), 'links_ok': all(p.is_symlink() and p.resolve() == master.resolve() for p in self.projections(name, e['scope']))})
        return rows

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--home', type=Path, help='Isolated test home; omit for real operation')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    p = sub.add_parser('install'); p.add_argument('names', nargs='+')
    p = sub.add_parser('adopt'); p.add_argument('source', type=Path); p.add_argument('--scope', choices=sorted(SCOPES), required=True)
    p = sub.add_parser('checkpoint'); p.add_argument('names', nargs='+'); p.add_argument('--message', required=True)
    sub.add_parser('pull')
    args = parser.parse_args()
    try:
        h = Hub(args.repo, args.home)
        if args.command == 'status': result = h.status()
        elif args.command == 'install':
            for name in args.names: h.install(name)
            result = {'installed': args.names}
        elif args.command == 'adopt': result = {'adopted': h.adopt(args.source, args.scope)}
        elif args.command == 'checkpoint': result = {'commit': h.checkpoint(args.names, args.message)}
        else: h.pull(); result = {'updated': list(h.catalog['skills'])}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (SyncError, OSError, sqlite3.Error, ValueError) as e:
        print(json.dumps({'ok': False, 'error': str(e), 'note': 'No automatic force overwrite or force push.'}, ensure_ascii=False))
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
