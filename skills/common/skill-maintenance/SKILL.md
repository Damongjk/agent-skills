---
name: skill-maintenance
description: Maintain the user's own dedicated skills in CC Switch and the private Damongjk/agent-skills repository. Third-party skills stay linked to their authors through CC Switch and are excluded from this repository.
---

# Personal Skill Maintenance

Use CC Switch's skill folder as the local installed master. The private GitHub repository stores published versions of the user's own dedicated skills only. CC Switch 4.0.20's native repository downloader does not provide the private-repository authorization used here; the helper uses Git with the computer's existing credential manager. Never put credentials in this skill, a command argument, or a remote URL.

The checkout normally lives at `~/Documents/Codex/agent-skills`. Its helper is `tools/skill_sync.py`. Use the available Python interpreter; do not install a new environment automatically. If the checkout is absent, report what remains local and ask the user to restore it. For GitHub authentication errors, follow the diagnosis below before requesting login. Never describe an unpushed change as synchronized.

## GitHub authentication diagnosis

A failed push or an authentication error in a restricted agent environment does not establish that the user's GitHub login expired. Diagnose before asking the user to log in again:

1. Identify the actual Git executable used by the helper. Compare its effective GitHub credential configuration with the system Git, including configuration origins. Bundled Git and system Git may inherit different helpers. Use `git config --show-origin --get-all credential.helper` and `git config --show-origin --get-all credential.https://github.com.helper`; an empty entry can reset inherited helpers.
2. Check the existing account with `gh auth status --hostname github.com`. If that check fails in a restricted context, repeat the status check in an appropriately authorized host/user context that can access the system credential store and network. Compare the active account and host state, not just the process exit code; JSON status may report a failed host while exiting successfully. Do not show tokens or dump credential files.
3. Classify the result before changing anything:
   - Host login works, restricted-context login fails: treat it as an execution-permission or credential-store access issue. Use the normal approval path for authorized host execution; do not request a fresh login or weaken isolation.
   - Host login works, the Git executable has no working GitHub helper: configure Git to use the existing GitHub CLI login with `gh auth setup-git --hostname github.com` when authorized. Verify that the actual Git executable sees the new configuration.
   - Network, proxy or certificate errors: diagnose connectivity; do not assume the credential is invalid. Repository access errors can instead mean the wrong account, missing repository permission or organization authorization.
   - Only after a reachable GitHub host confirms the saved login is missing or invalid in the correct user context should the user complete `gh auth login --hostname github.com --web`. Reuse existing credentials first; do not repeatedly request login after an unchanged failure.
4. Validate read access to the intended private repository, then perform the already-authorized scoped checkpoint/push. Confirm the pushed revision before reporting synchronization. A public-repository read or a local commit does not prove private push access.

Keep credentials in the existing system credential store. Never print tokens, store them in skill files or remote URLs, or export them to bypass credential-store restrictions. GitHub CLI configuration does not remove the agent's execution-permission requirements.

Treat the helper's “managed by another repository” error as a source-registration issue, not an authentication failure. Inspect CC Switch ownership, catalog mapping and the configured Git origin; never clear ownership or adopt third-party packages to make a checkpoint pass. If the verified source is this same personal repository and the adapter still rejects its metadata, a reviewed Git checkpoint may publish only the intended skill files while preserving CC Switch registration; otherwise stop and report the source conflict.

Official references: [GitHub CLI credential helper](https://cli.github.com/manual/gh_auth_setup-git), [GitHub CLI login](https://cli.github.com/manual/gh_auth_login).

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
