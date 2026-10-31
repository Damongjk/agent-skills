---
name: skill-maintenance
description: Maintain the user's own dedicated skills in CC Switch and the private Damongjk/agent-skills repository. Third-party skills stay linked to their authors through CC Switch and are excluded from this repository.
---

# Personal Skill Maintenance

Use CC Switch's skill folder as the local installed master. The private GitHub repository stores published versions of the user's own dedicated skills only. CC Switch 4.0.20's native repository downloader does not provide the private-repository authorization used here; the helper uses Git with the computer's existing credential manager. Never put credentials in this skill, a command argument, or a remote URL.

The checkout normally lives at `~/Documents/Codex/agent-skills`. Its helper is `tools/skill_sync.py`. Use the available Python interpreter; do not install a new environment automatically. If the checkout is absent or Git cannot authenticate, report what remains local and ask the user to restore the checkout or finish Git login. Never describe an unpushed change as synchronized.

## Ownership boundary

- Publish only skills authored for the user's personal conventions, business workflows, or private maintenance needs.
- Keep third-party skills associated with their original author repositories in CC Switch. The user manages their repository bindings and updates there; do not copy, vendor, adopt, checkpoint, or mirror them into `Damongjk/agent-skills`.
- Installation, use, or local adaptation of a third-party skill does not make it eligible for personal-repository publication. Keep personal preferences in separate user-owned skills instead of maintaining a fork by default.
- Before adopting a skill, inspect its attribution, upstream metadata, and CC Switch source. If ownership is genuinely unclear, resolve it before publishing.
- When removing a third-party skill from personal-repository maintenance, remove its repository package, catalog entry, and personal sync-state entry while preserving the installed package, application links, and existing upstream registration unless the user requests uninstalling it.

## Create or adopt

For a completed user-owned skill, choose `common`, `codex`, or `workbuddy`. Common skills may have conditional runtime notes for both agents. A skill requiring only one agent's exclusive tools belongs to that agent's scope. Do not silently classify an ambiguous dependency as common.

Run:

```text
python <checkout>/tools/skill_sync.py adopt <skill-folder> --scope common
python <checkout>/tools/skill_sync.py checkpoint <skill-name> --message "Describe this skill change"
```

`adopt` validates the package, preserves replaced data, registers a local CC Switch skill, and creates links. Common links go to `.agents/skills` (Codex/AStudio) and `.workbuddy/skills`. Dedicated links go only to the matching agent's skill folder. The helper does not change global application switches or revive Claude/Hermes.

## Iterate

Read and edit the actual CC Switch master at `~/.cc-switch/skills/<name>`, or a verified link to it. Do not update an independent application copy without first checking conflicts. After meaningful validation, run `checkpoint` for only the changed user-owned skill. This standing publication authorization covers this user's requested personal skill creation/iteration to the named private repository; it does not authorize publishing third-party skills, unrelated files, client projects, credentials, or internal resource lists.

Before publishing, inspect the complete diff and supporting files. The helper checks credential-shaped text and internal resource identifiers, but its check is not proof that content is safe. Do not migrate the existing business skill collection until its content review is confirmed.

## Receive changes

Use `status` to inspect differences. Use `pull` before editing on another device; this receives the user's personal repository, not updates from third-party authors. If both the repository and installed master changed since the last checkpoint, preserve both and resolve the content deliberately. Never force-push, use modification time to pick a winner, or overwrite uncommitted work.

The helper's CC Switch registration adapter is schema-checked and backed up. If CC Switch changes its database schema, stop instead of guessing. Mac setup must be tested separately; do not claim cross-device verification from Windows tests alone.
