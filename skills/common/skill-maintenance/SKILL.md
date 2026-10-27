---
name: skill-maintenance
description: Maintain the user's personal skills when creating, installing, or iterating a skill. Register the local CC Switch master, project common or agent-specific links, and checkpoint approved skill changes to the private Damongjk/agent-skills repository. Not for ordinary document, application, or project edits.
---

# Personal Skill Maintenance

Use CC Switch's skill folder as the local installed master. The private GitHub repository stores published versions. CC Switch 4.0.20's native repository downloader does not provide the private-repository authorization used here; the helper uses Git with the computer's existing credential manager. Never put credentials in this skill, a command argument, or a remote URL.

The checkout normally lives at `~/Documents/Codex/agent-skills`. Its helper is `tools/skill_sync.py`. Use the available Python interpreter; do not install a new environment automatically. If the checkout is absent or Git cannot authenticate, report what remains local and ask the user to restore the checkout or finish Git login. Never describe an unpushed change as synchronized.

## Create or adopt

For a completed skill, choose `common`, `codex`, or `workbuddy`. Common skills may have conditional runtime notes for both agents. A skill requiring only one agent's exclusive tools belongs to that agent's scope. Do not silently classify an ambiguous dependency as common.

Run:

```text
python <checkout>/tools/skill_sync.py adopt <skill-folder> --scope common
python <checkout>/tools/skill_sync.py checkpoint <skill-name> --message "Describe this skill change"
```

`adopt` validates the package, preserves replaced data, registers a local CC Switch skill, and creates links. Common links go to `.agents/skills` (Codex/AStudio) and `.workbuddy/skills`. Dedicated links go only to the matching agent's skill folder. The helper does not change global application switches or revive Claude/Hermes.

## Iterate

Read and edit the actual CC Switch master at `~/.cc-switch/skills/<name>`, or a verified link to it. Do not update an independent application copy without first checking conflicts. After meaningful validation, run `checkpoint` for only the changed skill. This standing publication authorization covers this user's requested skill creation/iteration to the named private repository; it does not authorize uploading unrelated files, client projects, credentials, or internal resource lists.

Before publishing, inspect the complete diff and supporting files. The helper checks credential-shaped text and internal resource identifiers, but its check is not proof that content is safe. Do not migrate the existing business skill collection until its content review is confirmed.

## Receive changes

Use `status` to inspect differences. Use `pull` before editing on another device. If both the repository and installed master changed since the last checkpoint, preserve both and resolve the content deliberately. Never force-push, use modification time to pick a winner, or overwrite uncommitted work.

The helper's CC Switch registration adapter is schema-checked and backed up. If CC Switch changes its database schema, stop instead of guessing. Mac setup must be tested separately; do not claim cross-device verification from Windows tests alone.
