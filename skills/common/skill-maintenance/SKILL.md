---
name: skill-maintenance
description: Maintain the user's own dedicated skills in CC Switch and the private Damongjk/agent-skills repository. Third-party skills stay linked to their authors through CC Switch and are excluded from this repository.
---

# Personal Skill Maintenance

Use CC Switch's skill folder as the local installed master. `Damongjk/agent-skills` is private. Preserve its visibility unless the user asks to change it. It stores reviewed versions of the user's own dedicated skills only; private visibility does not authorize uploading customer data, credentials or internal resource indexes. The helper coordinates the installed master with Git; both reads and pushes use the computer's existing credential manager and repository permissions. Never put credentials in this skill, a command argument, or a remote URL.

The checkout normally lives at `~/Documents/Codex/agent-skills`. Its helper is `tools/skill_sync.py`. Use the available Python interpreter; do not install a new environment automatically. If the checkout is absent, report what remains local and ask the user to restore it. Before network synchronization, follow the connection checks below; diagnose authentication only when evidence points to it. Never describe an unpushed change as synchronized.

## Private-repository access routes

Use the connected GitHub plugin for repository inspection when its tools fit the task. Its GitHub App authorization is separate from the host Git login used by this helper; verify each route independently when diagnosing access. Do not transfer tokens between them.

CC Switch 4.0.33 downloads skill ZIP files without repository authentication. Its built-in discovery/update buttons cannot replace authenticated `pull` / `checkpoint` for this private repository. Keep CC Switch as the installed master and retain repository ownership metadata; keep third-party skills connected to their authors. Do not patch the application binary, clear ownership, or make the repository public to suppress an update error. Recheck this limitation against the installed version when CC Switch changes. Source: [v4.0.33 download implementation](https://github.com/farion1231/cc-switch/blob/v4.0.33/src-tauri/src/services/skill.rs#L4200).

For personal skills, use this helper rather than a separate installer that would create an independent copy. If a separate GitHub installer is needed for another authorized task, prefer its authenticated Git mode and reuse a verified process-scoped proxy route; do not embed or export credentials to make anonymous archive downloads work.

## Automatic GitHub connection and proxy checks

Before each `checkpoint` or `pull`, the helper verifies access to the configured repository with a bounded `git ls-remote` probe. It respects explicit Git and process proxy settings. Otherwise it detects enabled system proxies with Python's standard proxy discovery, including macOS System Configuration, honors proxy bypass rules, and tries the available system HTTPS/SOCKS routes before the current connection. A working route is reused for that synchronization through process-scoped Git configuration; no proxy port is hard-coded or persisted. Local-only commands do not run this network check.

Use the current helper so this happens automatically, rather than repeatedly attempting a slow direct push. If an older helper is in use, inspect the actual Git proxy configuration, proxy environment variables, and enabled OS proxy settings first. On macOS, `scutil --proxy` provides the enabled hosts, ports and bypass list; do not assume that command-line Git inherits the proxy used by browsers. Use only an already configured proxy, validate the intended repository through it, then pass it to that Git process with `-c http.proxy=...` or append a `GIT_CONFIG_COUNT` runtime entry. Preserve existing runtime entries. Do not change global Git settings, OS proxy settings, certificates or credentials merely to complete a synchronization.

The observed failure was a valid GitHub login and working host DNS, but direct HTTPS to GitHub timed out while the enabled local proxy worked. This is a connection-route failure, not evidence of expired credentials. Re-read current settings each time; the previously working port is not a permanent default. A DNS failure only inside a restricted execution context also does not establish that the host cannot resolve GitHub: repeat the read-only check in the normally authorized host context, without bypassing execution permissions.

Stop after the bounded available-route probes fail. Distinguish DNS/connectivity, proxy authentication, TLS validation, GitHub authentication, and repository permission errors; do not loop identical pushes, request a new login for a network failure, disable TLS verification, or print proxy passwords/tokens. Explicit configured proxy failures require diagnosis before overriding the user's route. A successful public-page or repository read alone does not prove write permission: complete the authorized push, then compare the local revision with the live remote branch before reporting synchronization. If the environment blocks host execution or no valid route works, keep local work and report the exact remaining gap.

References: [Git runtime configuration and HTTP proxy](https://git-scm.com/docs/git-config), [Python system proxy discovery](https://docs.python.org/3/library/urllib.request.html#urllib.request.getproxies).

## GitHub authentication diagnosis

A failed push or an authentication error in a restricted agent environment does not establish that the user's GitHub login expired. Diagnose before asking the user to log in again:

1. Identify the actual Git executable used by the helper. Compare its effective GitHub credential configuration with the system Git, including configuration origins. Bundled Git and system Git may inherit different helpers. Use `git config --show-origin --get-all credential.helper` and `git config --show-origin --get-all credential.https://github.com.helper`; an empty entry can reset inherited helpers.
2. Check the existing account with `gh auth status --hostname github.com`. If that check fails in a restricted context, repeat the status check in an appropriately authorized host/user context that can access the system credential store and network. Compare the active account and host state, not just the process exit code; JSON status may report a failed host while exiting successfully. Do not show tokens or dump credential files.
3. Classify the result before changing anything:
   - Host login works, restricted-context login fails: treat it as an execution-permission or credential-store access issue. Use the normal approval path for authorized host execution; do not request a fresh login or weaken isolation.
   - Host login works, the Git executable has no working GitHub helper: configure Git to use the existing GitHub CLI login with `gh auth setup-git --hostname github.com` when authorized. Verify that the actual Git executable sees the new configuration.
   - Network, proxy or certificate errors: diagnose connectivity; do not assume the credential is invalid. Repository access errors can instead mean the wrong account, missing repository permission or organization authorization.
   - Only after a reachable GitHub host confirms the saved login is missing or invalid in the correct user context should the user complete `gh auth login --hostname github.com --web`. Reuse existing credentials first; do not repeatedly request login after an unchanged failure.
4. Validate read access to the intended repository, then perform the already-authorized scoped checkpoint/push. Confirm the pushed revision before reporting synchronization. A repository read or a local commit does not prove push access.

Keep credentials in the existing system credential store. Never print tokens, store them in skill files or remote URLs, or export them to bypass credential-store restrictions. GitHub CLI configuration does not remove the agent's execution-permission requirements.

The registration adapter accepts existing entries whose `repo_owner` and `repo_name` identify this same repository (case-insensitive). It preserves their source, branch, document URL and existing application switches. Different or incomplete repository identities are blocked. Treat a source-registration error as distinct from authentication; inspect CC Switch ownership, catalog mapping and Git origin, and never clear ownership or adopt third-party packages to bypass the check.

Official references: [GitHub CLI credential helper](https://cli.github.com/manual/gh_auth_setup-git), [GitHub CLI login](https://cli.github.com/manual/gh_auth_login).

## Ownership boundary

- Publish only skills authored for the user's personal conventions, reusable business workflows, or personal maintenance needs, after reviewing their contents for repository synchronization.
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

Read and edit the actual CC Switch master at `~/.cc-switch/skills/<name>`, or a verified link to it. Do not update an independent application copy without first checking conflicts. After meaningful validation, run `checkpoint` for only the changed user-owned skill. The user's standing authorization covers requested personal skill creation/iteration in the private `Damongjk/agent-skills` repository. Do not request a visibility change or repeat authorization for those scoped updates. This does not authorize publishing third-party skills, unrelated files, client projects, credentials, or internal resource lists. Review only the intended changes and exclude nonpublic business content before pushing.

Before publishing, inspect the complete diff and supporting files. The helper checks credential-shaped text and internal resource identifiers, but its check is not proof that content is safe. Do not migrate the existing business skill collection until its content review is confirmed.

## Receive changes

Use `status` to inspect differences. Use `pull` before editing on another device; this receives the user's personal repository, not updates from third-party authors. If both the repository and installed master changed since the last checkpoint, preserve both and resolve the content deliberately. Never force-push, use modification time to pick a winner, or overwrite uncommitted work.

The helper's CC Switch registration adapter is schema-checked and backed up. If CC Switch changes its database schema, stop instead of guessing. Mac setup must be tested separately; do not claim cross-device verification from Windows tests alone.
