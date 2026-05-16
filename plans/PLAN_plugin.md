# PLAN: Installable Hermes ADW Plugin + Skill Package

> **Decision:** ADW stays in a single repository. `smarterworkerai/agentic-delivery` must become both a Hermes skill source and a Hermes plugin repository.

## Purpose

Define how the `agentic-delivery` repository will expose the Agentic Delivery Workflow (ADW) in two installable forms:

1. **Skills:** the ADW workflow knowledge and delivery gates under `skills/adw/`.
2. **Plugin:** a thin `/adw <workflow> <payload>` Hermes command router installable from the repository root.

The plugin must not reimplement delivery workflows. It only parses, normalizes, and routes commands into the ADW skills so Hermes executes the existing workflow contracts consistently across CLI and gateway platforms.

## Final Packaging Decision

Use the single-repository root-plugin model:

```text
agentic-delivery/
  plugin.yaml
  __init__.py
  adw_plugin/
    __init__.py
    router.py
    prompts.py
    registry.py

  skills/
    adw/
      README.md
      adw-core/
        SKILL.md
        references/
        templates/
        assets/
      plan-feature/
        SKILL.md
      plan-bugfix/
        SKILL.md
      do-impl/
        SKILL.md
      do-impl-delegate/
        SKILL.md
      test-feature/
        SKILL.md
      merge-feature/
        SKILL.md
      promote-release/
        SKILL.md
      rollback-deployment/
        SKILL.md
      validate-regression/
        SKILL.md
      create-adr/
        SKILL.md
      audit-dependencies/
        SKILL.md
      analyze-production/
        SKILL.md

  scripts/
    install_adw.sh

  tools/
    validate_adw_skills.py
    validate_adw_plugin_package.py

  plans/
    PLAN.md
    PLAN_plugin.md

  README.md
  SOUL.md
```

Consequences:

- `hermes plugins install smarterworkerai/agentic-delivery --enable` should install the plugin from this repository root.
- `hermes skills tap add smarterworkerai/agentic-delivery` should make the ADW skills installable from the same repository.
- No separate `hermes-plugin-adw` repository is required for now.
- The repository root intentionally becomes a combined Hermes package: documentation source, skill source, and plugin package.
- Workflow rules stay in `skills/adw/*`; root plugin code stays thin.

## Current ADW Package Assumptions

- Target branch: `feature/initial-skills`.
- Shared ADW context is packaged as `skills/adw/adw-core/`.
- Operational workflow skills live under `skills/adw/<workflow>/`.
- Operational skills reference `adw-core` as the source of truth for shared playbooks, templates, ADRs, and diagrams.
- The root `SOUL.md` is an adoption/profile identity document, not a deterministic command router.
- Repository artifacts are written in English.

## Target User Experience

Canonical command form:

```text
/adw <workflow> <payload>
```

Examples:

```text
/adw plan-feature invoice CSV export
/adw plan-bugfix login timeout after OAuth callback
/adw do-impl issue #42
/adw do-impl-delegate issue #42
/adw test-feature PR #43
/adw merge-feature main PR #43
/adw promote-release demo to production PR #43
/adw rollback-deployment production login regression
```

The command should work from:

- Hermes CLI interactive sessions
- Telegram gateway messages
- Discord gateway slash commands, subject to platform command constraints
- other Hermes gateway platforms that pass slash commands into the shared gateway dispatcher

## Telegram Command Discoverability

Telegram can show bot-level slash command suggestions only for registered bot commands such as `/adw`. Standard Telegram bot command suggestions do **not** provide native autocomplete for sub-arguments after the command text, so Telegram cannot automatically offer `plan-feature`, `plan-bugfix`, `do-impl`, etc. as selectable arguments when the user types `/adw `.

Planned behavior:

- Keep `/adw <workflow> <payload>` as the canonical cross-platform command.
- If `/adw` is sent without a workflow, return concise usage help listing the supported workflow tokens and aliases.
- Optionally add a Telegram-friendly helper response with inline buttons for workflow selection, if the Hermes gateway/plugin API exposes a safe way to send platform-specific reply markup. This is a convenience path, not true compose-time argument autocomplete.
- Do not split ADW into many top-level Telegram commands by default (`/adw_plan_feature`, `/adw_test_feature`, etc.) because that weakens the single-router UX and is less portable across Hermes CLI and gateway platforms. Reconsider only if command-level Telegram suggestions become a higher priority than cross-platform consistency.

## Workflow Registry

The plugin should maintain an explicit workflow registry mapping command tokens to skill names.

Canonical workflow tokens:

- `plan-feature` -> `adw-plan-feature`
- `plan-bugfix` -> `adw-plan-bugfix`
- `do-impl` -> `adw-do-impl`
- `do-impl-delegate` -> `adw-do-impl-delegate`
- `test-feature` -> `adw-test-feature`
- `merge-feature` -> `adw-merge-feature`
- `promote-release` -> `adw-promote-release`
- `rollback-deployment` -> `adw-rollback-deployment`
- `validate-regression` -> `adw-validate-regression`
- `create-adr` -> `adw-create-adr`
- `audit-dependencies` -> `adw-audit-dependencies`
- `analyze-production` -> `adw-analyze-production`

Recommended aliases:

- `plan` -> `plan-feature`
- `feature` -> `plan-feature`
- `bug` -> `plan-bugfix`
- `bugfix` -> `plan-bugfix`
- `fix` -> `plan-bugfix`
- `impl` -> `do-impl`
- `implement` -> `do-impl`
- `delegate` -> `do-impl-delegate`
- `test` -> `test-feature`
- `validate` -> `test-feature`
- `merge` -> `merge-feature`
- `promote` -> `promote-release`
- `rollback` -> `rollback-deployment`
- `regress` -> `validate-regression`
- `regression` -> `validate-regression`
- `adr` -> `create-adr`
- `deps` -> `audit-dependencies`
- `dependencies` -> `audit-dependencies`
- `prod` -> `analyze-production`
- `production` -> `analyze-production`

## Plugin Responsibilities

The plugin should:

1. Register a single slash command named `adw`.
2. Parse the first argument as the workflow selector.
3. Normalize aliases to canonical workflow names.
4. Treat the remaining text as the workflow payload.
5. Build a deterministic invocation prompt that includes:
   - the selected workflow token;
   - the selected operational skill name;
   - the user payload;
   - instructions to preserve ADW gates, traceability, reviewability, and deployment safety.
6. In CLI mode, queue the generated invocation into the active conversation using `ctx.inject_message(...)` when available.
7. In gateway mode, rewrite valid `/adw ...` messages through the verified `pre_gateway_dispatch` hook using `{"action": "rewrite", "text": "..."}` before plugin command dispatch consumes them as direct responses.
8. Reject unknown or incomplete workflows with concise usage output.
9. Keep all business workflow rules in skills, not plugin code.

The plugin must not:

- create branches directly;
- create issues directly;
- create PRs directly;
- merge or deploy directly;
- bypass review, preview, validation, or production safety gates;
- duplicate ADW workflow policy except for minimal routing metadata.

## Hermes Source Findings

Hermes source inspected under:

```text
/home/pupz/.hermes/hermes-agent
```

### Plugin Discovery

Hermes discovers plugins from:

1. bundled plugins: `<hermes repo>/plugins/<name>/`;
2. user plugins: `$HERMES_HOME/plugins/<name>/`;
3. project-local plugins: `./.hermes/plugins/<name>/`, only when `HERMES_ENABLE_PROJECT_PLUGINS=1`;
4. Python entry points in the `hermes_agent.plugins` group.

A directory plugin requires:

- `plugin.yaml`;
- `__init__.py`;
- `register(ctx)`.

### Plugin Installation

`hermes plugins install <identifier>` is repository-root based:

- accepts `owner/repo`, HTTPS URLs, SSH URLs, and `file://...`;
- clones the whole Git repository into `$HERMES_HOME/plugins/`;
- expects `plugin.yaml` and/or `__init__.py` at the cloned repository root;
- does not currently provide source evidence for installing a plugin from a subdirectory such as `owner/repo/path/to/plugin`;
- plugins must be enabled with `hermes plugins enable <name>` or installed with `--enable`;
- gateway restart is required after plugin installation or update.

Implication:

```text
.hermes/plugins/adw/
```

is useful for a trusted local spike, but it is not the portable install target for `hermes plugins install smarterworkerai/agentic-delivery`. For portable install, this repository needs root-level plugin files.

### Command Registration

`ctx.register_command()` registers an in-session slash command. Behavior observed from source and spike validation:

- command names are normalized to lowercase;
- a leading `/` is stripped;
- spaces become hyphens;
- conflicts with built-in commands are rejected;
- handler shape is `handler(raw_args: str) -> str | None`;
- async handlers are supported;
- registered plugin commands flow into CLI, help/autocomplete, Discord command registration, and gateway dispatch.

### Prompt Injection and Gateway Rewrite

A plugin command handler return value is not enough to start an agent workflow:

- in CLI, the returned string is printed;
- in gateway, the returned string is sent as a direct reply.

Therefore ADW needs real injection/rewrite:

- CLI path: close over `ctx` and call `ctx.inject_message(prompt, role="user")`.
- Gateway path: register a `pre_gateway_dispatch` hook and return `{"action": "rewrite", "text": prompt}` for valid `/adw ...` commands.
- Invalid `/adw` inputs should not be rewritten; they should fall through to the direct command handler so users get usage output.

## Local Spike Results

A project-local plugin spike was created under:

```text
.hermes/plugins/adw/
  plugin.yaml
  __init__.py
  README.md
```

A model-free validation harness was created at:

```text
tools/validate_adw_plugin_spike.py
```

Validated behavior:

- `/adw` command registration through `ctx.register_command()`.
- Workflow parsing and alias normalization.
- Prompt construction with embedded `adw-core` and selected operational `SKILL.md` content.
- CLI injection through `ctx.inject_message(...)` with a fake context.
- Gateway rewrite through `pre_gateway_dispatch` returning `{"action": "rewrite", "text": ...}`.
- Hermes project-plugin discovery using:
  - temporary `HERMES_HOME`;
  - `plugins.enabled: [adw]`;
  - `HERMES_ENABLE_PROJECT_PLUGINS=1`;
  - the Hermes venv Python interpreter.

Validation command:

```bash
python3 tools/validate_adw_plugin_spike.py
```

Observed successful result:

```text
Direct plugin tests OK: parse, CLI injection, and gateway rewrite
Hermes discovery OK: /adw command registered and gateway rewrite hook works
ADW plugin spike validation OK
```

Design conclusions from the spike:

1. The `/adw` UX is viable.
2. Gateway support should use `pre_gateway_dispatch` rewrite, not plain handler returns.
3. CLI support should use `ctx.inject_message(...)` when available.
4. The packaged root plugin can reuse the spike logic, but should move reusable code into `adw_plugin/` modules.
5. The local `.hermes/plugins/adw/` copy and spike-only validation script must be removed after the root plugin package is implemented and tested.

## Target Repository Changes

### 1. Root Plugin Manifest

Create:

```text
plugin.yaml
```

Purpose:

- make the repository installable with `hermes plugins install smarterworkerai/agentic-delivery --enable`;
- define plugin name `adw`;
- describe the `/adw` router;
- identify this as a standalone Hermes plugin.

Expected fields:

```yaml
name: adw
version: 0.1.0
description: "Agentic Delivery Workflow slash command router."
author: smarterworkerai
kind: standalone
platforms:
  - linux
  - macos
  - windows
```

### 2. Root Plugin Entrypoint

Create:

```text
__init__.py
```

Purpose:

- expose `register(ctx)` from the implementation package;
- keep root entrypoint minimal.

Expected content shape:

```python
from adw_plugin.router import register

__all__ = ["register"]
```

### 3. Plugin Implementation Package

Create:

```text
adw_plugin/
  __init__.py
  registry.py
  prompts.py
  router.py
```

Responsibilities:

- `registry.py`
  - canonical workflow registry;
  - alias registry;
  - skill-directory mapping;
  - route dataclass;
  - parsing and validation helpers.
- `prompts.py`
  - invocation prompt builder;
  - installed-skill-first prompt shape;
  - fallback embedded-skill prompt shape when local repository skills are available.
- `router.py`
  - `register(ctx)`;
  - `/adw` command handler;
  - `pre_gateway_dispatch` hook;
  - event parsing helpers;
  - usage formatting.

### 4. Package Validation

Create:

```text
tools/validate_adw_plugin_package.py
```

This should validate the root-plugin package, not only the project-local spike:

- root `plugin.yaml` exists and has `name: adw`;
- root `__init__.py` exposes `register`;
- `adw_plugin.router.register()` registers `/adw` and `pre_gateway_dispatch`;
- every workflow registry entry maps to an existing skill directory;
- every operational ADW skill has a registry entry or explicit exclusion;
- aliases resolve to valid canonical workflows;
- gateway rewrite produces a normal agent prompt, not a direct slash command echo;
- install/discovery can be simulated with a temporary `HERMES_HOME` and `file://` or direct import path.

### 5. README Installation Documentation

Update:

```text
README.md
```

Add a dedicated section:

```markdown
## Installation
```

Document both install paths with Hermes commands.

Skill installation documentation should include:

```bash
hermes skills tap add smarterworkerai/agentic-delivery
hermes skills install smarterworkerai/agentic-delivery/skills/adw/adw-core
hermes skills install smarterworkerai/agentic-delivery/skills/adw/plan-feature
hermes skills install smarterworkerai/agentic-delivery/skills/adw/plan-bugfix
hermes skills install smarterworkerai/agentic-delivery/skills/adw/do-impl
hermes skills install smarterworkerai/agentic-delivery/skills/adw/do-impl-delegate
hermes skills install smarterworkerai/agentic-delivery/skills/adw/test-feature
hermes skills install smarterworkerai/agentic-delivery/skills/adw/merge-feature
hermes skills install smarterworkerai/agentic-delivery/skills/adw/promote-release
hermes skills install smarterworkerai/agentic-delivery/skills/adw/rollback-deployment
hermes skills install smarterworkerai/agentic-delivery/skills/adw/validate-regression
hermes skills install smarterworkerai/agentic-delivery/skills/adw/create-adr
hermes skills install smarterworkerai/agentic-delivery/skills/adw/audit-dependencies
hermes skills install smarterworkerai/agentic-delivery/skills/adw/analyze-production
```

If the exact tap install identifier differs after live verification, update README with the verified Hermes command form and record the reason in this plan.

Plugin installation documentation should include:

```bash
hermes plugins install smarterworkerai/agentic-delivery --enable
```

Gateway note:

```bash
hermes gateway restart
```

Profile note:

```bash
hermes --profile <profile> plugins list
hermes --profile <profile> skills list
```

Usage examples:

```text
/adw plan-feature invoice CSV export
/adw do-impl issue #42
/adw test-feature PR #42
/adw merge-feature main PR #42
```

Also document the skill-only fallback:

```text
Use adw-core and adw-plan-feature for invoice CSV export.
```

### 6. One-Liner Bootstrap Installer

Create:

```text
scripts/install_adw.sh
```

Purpose:

- provide a one-liner bootstrap path for installing both ADW skills and the ADW plugin;
- ask which Hermes profile should receive the install;
- make repeated runs safe for updates by removing old ADW installs first;
- install/update skills and plugin using Hermes commands;
- avoid storing credentials or secrets.

Desired one-liner after the script is merged to the default branch:

```bash
curl -fsSL https://raw.githubusercontent.com/smarterworkerai/agentic-delivery/main/scripts/install_adw.sh | bash
```

For branch testing before merge:

```bash
curl -fsSL https://raw.githubusercontent.com/smarterworkerai/agentic-delivery/feature/initial-skills/scripts/install_adw.sh | bash
```

Script behavior:

1. Verify `hermes` exists on `PATH`.
2. Print the active Hermes version if available.
3. Ask the user for a target profile:
   - default profile when empty;
   - explicit named profile when provided.
4. Optionally list existing profiles if `hermes profile list` is available.
5. Build a profile-aware Hermes command prefix:
   - `hermes` for default profile;
   - `hermes --profile <name>` for named profile.
6. Uninstall previous ADW installation artifacts before reinstalling, so the script can be used as an update command:
   - discover installed skills with `hermes skills list`;
   - remove skills whose installed name starts with `adw-`;
   - remove the existing ADW plugin if `hermes plugins list` shows `adw` or `agentic-delivery`;
   - tolerate "not installed" / "not found" results, but fail on unexpected uninstall errors.
7. Add or update the skill tap:
   - `hermes skills tap add smarterworkerai/agentic-delivery`.
8. Install all ADW skills from `skills/adw/`.
9. Install and enable the plugin:
   - `hermes plugins install smarterworkerai/agentic-delivery --enable`.
10. Run post-install verification:
    - `hermes skills list` contains ADW skills;
    - `hermes plugins list` shows `adw` enabled.
11. Print next steps:
    - restart gateway if using Telegram/Discord/etc.;
    - try `/adw plan-feature <feature>`.

Safety requirements:

- Do not request or print secrets.
- Use `set -euo pipefail`.
- Quote all profile/user input.
- Make the script idempotent where Hermes commands allow it.
- Treat update as the primary path: uninstall old `adw-*` skills and the ADW plugin before reinstalling the current repo version.
- Scope uninstall strictly to ADW-owned artifacts; never remove non-ADW skills, plugins, taps, profiles, config, memory, sessions, credentials, or user data.
- Prefer dry, parseable Hermes CLI output where available; if Hermes lacks machine-readable output for a command, use conservative text parsing and re-verify after each uninstall/install step.
- Fail with actionable messages if tap/plugin install commands are unavailable in the user's Hermes version.

### 7. Local Spike Cleanup

After the root plugin package is implemented and validated, remove the spike artifacts instead of preserving them:

```text
.hermes/plugins/adw/
tools/validate_adw_plugin_spike.py
```

Required final state:

- delete the project-local plugin copy to avoid duplicate source of truth;
- delete spike-only helper scripts once their assertions are covered by `tools/validate_adw_plugin_package.py`;
- ensure README and validation instructions reference only the root plugin package and package-level validator;
- keep historical spike findings documented in this plan, but do not keep executable spike artifacts in the final repository tree.

## Implementation Plan

### Phase 1: Commit Research and Decision

Update `plans/PLAN_plugin.md` with:

- single-repository root-plugin decision;
- Hermes source findings;
- local spike validation results;
- target root package structure;
- README documentation requirements;
- bootstrap installer requirements.

Validation:

```bash
python3 tools/validate_adw_skills.py
git diff --check
```

During the already-completed local spike, `python3 tools/validate_adw_plugin_spike.py` was used as temporary evidence. Do not keep that script after root package validation replaces it.

### Phase 2: Convert Spike to Root Plugin Package

Create root plugin files and implementation package:

```text
plugin.yaml
__init__.py
adw_plugin/
```

Move reusable logic from:

```text
.hermes/plugins/adw/__init__.py
```

into:

```text
adw_plugin/registry.py
adw_plugin/prompts.py
adw_plugin/router.py
```

Acceptance criteria:

- `from adw_plugin.router import register` works;
- root `__init__.py` exposes `register`;
- no workflow policy is moved out of skills;
- the root package can be discovered as a Hermes plugin.

### Phase 3: Package-Level Validation

Add and run:

```bash
python3 tools/validate_adw_plugin_package.py
```

Acceptance criteria:

- root plugin manifest and entrypoint are valid;
- `/adw` command registers;
- CLI injection is model-free testable with fake context;
- gateway rewrite is model-free testable with fake event;
- registry and skill directories are consistent.

### Phase 4: README Installation Documentation

Update `README.md` with:

- skill tap installation commands;
- per-skill installation commands;
- plugin installation command;
- gateway restart note;
- profile-specific examples;
- `/adw` usage examples;
- skill-only fallback examples;
- bootstrap one-liner.

Acceptance criteria:

- README commands are copy-pasteable;
- README clearly separates skills from plugin;
- README states that the plugin is only a router and the skills contain workflow policy;
- README warns to restart the gateway after plugin install/update.

### Phase 5: Bootstrap Installer

Create:

```text
scripts/install_adw.sh
```

Implement the interactive profile prompt and install flow described above.

Acceptance criteria:

- script passes `bash -n scripts/install_adw.sh`;
- script fails safely when `hermes` is missing;
- script prints the exact profile it will modify before installing;
- script installs skills and plugin using Hermes commands;
- script verifies installed artifacts after completion;
- README contains the one-liner curl command.

### Phase 6: End-to-End Install Smoke

Use a temporary or disposable Hermes profile for smoke testing.

Suggested commands:

```bash
hermes profile create adw-smoke
hermes --profile adw-smoke skills tap add smarterworkerai/agentic-delivery
hermes --profile adw-smoke skills install smarterworkerai/agentic-delivery/skills/adw/adw-core
hermes --profile adw-smoke plugins install smarterworkerai/agentic-delivery --enable
hermes --profile adw-smoke plugins list
hermes --profile adw-smoke skills list
```

Then test command routing in CLI:

```text
/adw plan-feature invoice CSV export
```

Gateway smoke after installation:

```bash
hermes --profile adw-smoke gateway restart
```

Then from Telegram or another gateway platform:

```text
/adw plan-feature invoice CSV export
```

Expected behavior:

- no unknown-command response;
- no direct echo-only behavior;
- ADW workflow begins as a normal agent turn;
- ADW response respects planning/branch/issue gates.

### Phase 7: Cleanup and Source of Truth

After root plugin validation succeeds:

- delete `.hermes/plugins/adw/`;
- delete `tools/validate_adw_plugin_spike.py` after its useful assertions are covered by `tools/validate_adw_plugin_package.py`;
- ensure only one plugin source of truth remains;
- update validators so CI/review depends only on the root plugin package;
- keep repository artifacts in English.

## Test Strategy

Minimum checks before committing plugin package work:

```bash
python3 tools/validate_adw_skills.py
python3 tools/validate_adw_plugin_package.py
bash -n scripts/install_adw.sh
git diff --check
```

If `tools/validate_adw_plugin_package.py` or `scripts/install_adw.sh` do not exist yet in an intermediate planning commit, run the available subset and document the missing checks as planned work.

## Risks and Mitigations

- **Root package ambiguity:** The repository root becomes documentation, skill source, and plugin package. Mitigation: keep root `__init__.py` minimal and all plugin logic under `adw_plugin/`.
- **Plugin command direct replies:** Returning strings does not start an agent turn. Mitigation: use `ctx.inject_message(...)` for CLI and `pre_gateway_dispatch` rewrite for gateway.
- **Internal Hermes API drift:** `ctx.inject_message` and gateway hook behavior may change. Mitigation: keep model-free validators that fail when behavior changes.
- **Skill install identifier uncertainty:** Tap install path syntax must be verified with the current Hermes version. Mitigation: README update task includes live command verification and correction.
- **Duplicate plugin sources:** Keeping both `.hermes/plugins/adw/` and root `adw_plugin/` can drift. Mitigation: delete the local spike and spike-only helper scripts after root plugin conversion.
- **Profile targeting mistakes:** Bootstrap installer could install into the wrong Hermes profile. Mitigation: prompt for profile, print target profile, and verify with profile-aware Hermes commands.
- **Gateway stale code:** Gateway may keep old plugin code loaded. Mitigation: README and installer output must tell users to restart the gateway after plugin changes.

## Definition of Done

The ADW package is complete when:

- `agentic-delivery` is installable as a Hermes plugin from the repository root;
- ADW skills are installable from the same repository as a Hermes skill tap;
- README documents both skill and plugin installation with Hermes commands;
- README documents profile-aware installation and gateway restart requirements;
- `scripts/install_adw.sh` provides a one-liner bootstrap installer that prompts for target profile;
- `/adw <workflow> <payload>` works in CLI and gateway smoke tests;
- validators confirm registry-to-skill consistency;
- workflow policy remains in skills, not in plugin code;
- no secrets or credentials are committed.
