# PLAN: Hermes ADW Plugin

## Purpose

Define a thin Hermes plugin that turns the Agentic Delivery Workflow (ADW) skill package into a deterministic command surface:

```text
/adw <workflow> <payload>
```

The plugin must not reimplement the delivery workflows. Its job is to route, normalize, and inject the correct skill context so Hermes executes the existing ADW skills consistently across CLI and gateway platforms.

## Current ADW Package Assumptions

- The repository branch is `feature/initial-skills`.
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
/adw do-impl issue #42
/adw test-feature PR #43
/adw merge-feature main PR #43
/adw rollback-deployment production login regression
```

The command should work the same way from:

- Hermes CLI interactive sessions
- Telegram gateway messages
- Discord gateway slash commands, subject to platform naming and argument rules
- Other Hermes gateway platforms that pass slash commands into the shared gateway dispatcher

## Workflow Registry

The plugin should maintain an explicit registry mapping workflow tokens to skill names.

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
- `bugfix` -> `plan-bugfix`
- `impl` -> `do-impl`
- `delegate` -> `do-impl-delegate`
- `test` -> `test-feature`
- `merge` -> `merge-feature`
- `promote` -> `promote-release`
- `rollback` -> `rollback-deployment`
- `regress` -> `validate-regression`
- `adr` -> `create-adr`
- `deps` -> `audit-dependencies`
- `prod` -> `analyze-production`

## Plugin Responsibilities

The plugin should:

1. Register a single slash command named `adw`.
2. Parse the first argument as the workflow selector.
3. Normalize aliases to canonical workflow names.
4. Treat the remaining text as the workflow payload.
5. Build a deterministic prompt that loads or injects:
   - `adw-core`
   - the selected operational skill
6. In CLI mode, queue the generated skill invocation message into the active conversation rather than merely printing it.
7. In gateway mode, rewrite `/adw ...` into the selected operational skill slash command, or otherwise inject a real agent message before the normal agent runner starts.
8. Reject unknown workflows with a concise usage message.
9. Refuse unsafe ambiguity only when the missing information affects safety or workflow gates.
10. Keep all business workflow rules in skills, not plugin code.

The plugin should not:

- create branches directly
- create issues directly
- create PRs directly
- merge or deploy directly
- bypass review, preview, or validation gates
- duplicate the content of ADW skills or playbooks

## Hermes Source Findings

This section records findings from the Hermes source tree inspected under:

```text
/home/pupz/.hermes/hermes-agent
```

### Plugin API

Hermes discovers plugins from four sources in `hermes_cli/plugins.py`:

1. bundled plugins: `<hermes repo>/plugins/<name>/`
2. user plugins: `~/.hermes/plugins/<name>/`
3. project plugins: `./.hermes/plugins/<name>/`, gated by `HERMES_ENABLE_PROJECT_PLUGINS`
4. pip plugins exposing the `hermes_agent.plugins` entry point group

A directory plugin must contain:

- `plugin.yaml`
- `__init__.py`
- a `register(ctx)` function

The plugin context supports these relevant APIs:

- `ctx.register_command(name, handler, description='', args_hint='')`
- `ctx.register_cli_command(...)`
- `ctx.register_tool(...)`
- `ctx.register_hook(...)`
- `ctx.register_skill(name, path, description='')`
- `ctx.dispatch_tool(...)`
- `ctx.inject_message(...)` for CLI mode only; it logs that it is not available in gateway mode when no CLI reference exists

For ADW, the important API is `ctx.register_command()`.

### Command Registration

`ctx.register_command()` registers an in-session slash command, not a terminal subcommand.

Behavior observed in source:

- Command names are normalized to lowercase, stripped of a leading `/`, and spaces become hyphens.
- Conflicts with built-in commands are rejected.
- Handlers use this shape:

```python
def handler(raw_args: str) -> str | None:
    ...
```

- Async handlers are also supported.
- Registered plugin commands appear in the shared plugin command registry used by CLI, help/autocomplete, and gateways.

Minimal plugin skeleton:

```python
# plugin.yaml
manifest_version: 1
name: adw
description: Agentic Delivery Workflow command router
version: 0.1.0
```

```python
# __init__.py
from __future__ import annotations

WORKFLOWS = {
    "plan-feature": "adw-plan-feature",
    "plan-bugfix": "adw-plan-bugfix",
    "do-impl": "adw-do-impl",
    "do-impl-delegate": "adw-do-impl-delegate",
    "test-feature": "adw-test-feature",
    "merge-feature": "adw-merge-feature",
    "promote-release": "adw-promote-release",
    "rollback-deployment": "adw-rollback-deployment",
    "validate-regression": "adw-validate-regression",
    "create-adr": "adw-create-adr",
    "audit-dependencies": "adw-audit-dependencies",
    "analyze-production": "adw-analyze-production",
}

ALIASES = {
    "plan": "plan-feature",
    "feature": "plan-feature",
    "bugfix": "plan-bugfix",
    "impl": "do-impl",
    "delegate": "do-impl-delegate",
    "test": "test-feature",
    "merge": "merge-feature",
    "promote": "promote-release",
    "rollback": "rollback-deployment",
    "regress": "validate-regression",
    "adr": "create-adr",
    "deps": "audit-dependencies",
    "prod": "analyze-production",
}


def register(ctx):
    ctx.register_command(
        "adw",
        handle_adw,
        description="Run an Agentic Delivery Workflow",
        args_hint="<workflow> <payload>",
    )


def handle_adw(raw_args: str) -> str:
    args = (raw_args or "").strip()
    if not args:
        return usage()

    workflow_token, _, payload = args.partition(" ")
    workflow = ALIASES.get(workflow_token, workflow_token)
    skill = WORKFLOWS.get(workflow)
    if not skill:
        return usage(f"Unknown ADW workflow: {workflow_token}")

    return build_prompt(workflow, skill, payload.strip())


def build_prompt(workflow: str, skill: str, payload: str) -> str:
    return f"""ADW command invocation.

Load and follow these skills in order:
1. adw-core
2. {skill}

Workflow: {workflow}
User intent: {payload or "(none provided)"}

Execute the workflow according to the ADW skill contract. Preserve ADW gates, traceability, reviewability, and deployment safety.
""".strip()


def usage(prefix: str | None = None) -> str:
    workflows = ", ".join(sorted(WORKFLOWS))
    body = f"Usage: /adw <workflow> <payload>\nWorkflows: {workflows}"
    return f"{prefix}\n\n{body}" if prefix else body
```

### Skill Preload and Prompt Injection

Hermes already has a skill slash command system in `agent/skill_commands.py`.

Relevant behavior:

- Installed skills under `~/.hermes/skills/` and configured external skill dirs are scanned for `SKILL.md`.
- A skill named `adw-plan-feature` becomes callable as `/adw-plan-feature`.
- `build_skill_invocation_message()` formats the skill content into a prompt-like message.
- The generated message includes:
  - skill content
  - absolute skill directory
  - linked supporting files
  - optional skill config values
  - the user's instruction alongside the invocation

However, plugin commands do not automatically call `build_skill_invocation_message()` for multiple skills. A plugin command handler returns a string, and that string becomes the next message/response path depending on the surface.

Recommended initial implementation:

A plain plugin command return value is not enough to start an ADW agent turn:

- In CLI mode, `cli.py` prints the plugin command result.
- In gateway mode, `gateway/run.py` returns the plugin command result as a direct reply.

Therefore the plugin should not rely on returning a normalized prompt as the final runtime mechanism.

Recommended implementation:

- For CLI, close over `ctx` in the `/adw` handler and call `ctx.inject_message(...)` with a generated skill invocation message. `ctx.inject_message()` is explicitly CLI-oriented and queues into the active conversation when `_cli_ref` exists.
- For gateway, use the command hook/rewrite path or a pre-dispatch rewrite so `/adw <workflow> <payload>` becomes `/<selected-operational-skill> <payload>` before skill command dispatch. Operational skills already know to use `adw-core`.
- For both surfaces, build the injected or rewritten content with `agent.skill_commands.build_skill_invocation_message()` where stable, and keep a fallback usage/error response for failed internal imports.

This should be validated with both CLI and gateway because `build_skill_invocation_message()` is an internal helper rather than a plugin public API.

### Gateway Command Compatibility

The gateway dispatcher in `gateway/run.py` checks plugin-registered slash commands before skill slash commands.

Relevant behavior:

- Incoming slash command names are normalized by replacing underscores with hyphens.
- `get_plugin_command_handler(command.replace("_", "-"))` is used.
- If a plugin command handler exists, the gateway passes `event.get_command_args().strip()` as `raw_args`.
- Coroutine handlers are awaited.
- The returned result is sent back as text if present.

This means `/adw ...` should pass through Telegram and the shared gateway dispatcher as a plugin command.

Discord has additional native slash registration support in `gateway/platforms/discord.py`:

- Discord imports `_iter_plugin_command_entries()` from `hermes_cli.commands`.
- Plugin commands are automatically added to Discord's native slash picker.
- The code comment states plugin commands are platform-agnostic and no per-platform plugin API is needed.
- `args_hint` is used to expose an argument field where possible.

Caveats:

- Telegram Bot API command names do not support hyphens in the native command menu, so Hermes normalizes underscores to hyphens when dispatching. The canonical plugin command `/adw` avoids this issue.
- Discord command names have length and character limits. `/adw` is safe.
- Subcommand-like syntax (`/adw plan-feature ...`) is plain text arguments to Hermes, not a native Discord subcommand tree unless a future plugin implements a Discord-specific command group.
- Returning a normal string from a plugin command is direct output, not automatic prompt injection.
- `ctx.inject_message()` is available for CLI mode but logs that no CLI reference is available in gateway mode.
- The safest gateway design is to rewrite `/adw <workflow> <payload>` to `/<operational-skill> <payload>` before the skill command dispatcher runs.
- The command hook path in `gateway/run.py` supports `decision: rewrite` with `command_name` and `raw_args` for recognized commands, but this should be validated with plugin-registered `command:adw` hooks before finalizing the implementation.

### Plugin Installation Model

Hermes plugin install support is Git-repository based.

`hermes_cli/plugins_cmd.py` shows:

- `hermes plugins install <identifier>` clones a Git repo into `~/.hermes/plugins/`.
- Accepted identifiers:
  - `https://github.com/owner/repo.git`
  - `git@github.com:owner/repo.git`
  - `ssh://git@github.com/owner/repo.git`
  - `owner/repo`, resolved to GitHub HTTPS
  - `file://...` is accepted but warned as insecure/local
- The installer expects `plugin.yaml` and/or `__init__.py` at the repository root after clone.
- There is no source evidence that `hermes plugins install owner/repo/path/to/plugin` installs a subdirectory directly.
- Plugins are opt-in after installation; they must be enabled via `hermes plugins enable <name>` or installed with `--enable`.
- Gateway restart is required for plugin changes to take effect.

Implications for this repository:

1. A plugin in `agentic-delivery/plugins/adw/` is useful for development, but it is not directly installable by the current plugin installer as a subdirectory of the repo.
2. A repo-local project plugin is possible at `./.hermes/plugins/adw/` when running Hermes from this repository with `HERMES_ENABLE_PROJECT_PLUGINS=1`, but this is a trust-gated development mode, not a portable package-manager install path.
3. For a clean user-facing plugin install, use one of these approaches:
   - put the plugin at the root of a dedicated repository, e.g. `smarterworkerai/hermes-plugin-adw`; or
   - make this repository itself plugin-installable by placing `plugin.yaml` and `__init__.py` at the root, but this would mix plugin runtime files with the ADW skill package and is not recommended.

Recommended packaging decision:

- Keep ADW skills in `smarterworkerai/agentic-delivery`.
- Create a separate thin plugin repository later, e.g. `smarterworkerai/hermes-plugin-adw`, if the plugin is meant to be installed via `hermes plugins install smarterworkerai/hermes-plugin-adw --enable`.
- During development, optionally mirror the plugin under `.hermes/plugins/adw/` for repo-local testing with `HERMES_ENABLE_PROJECT_PLUGINS=1`.

## Proposed Repository Additions

### Option A: Development Plugin Inside This Repository

Create:

```text
.hermes/plugins/adw/
  plugin.yaml
  __init__.py
  README.md
```

Pros:

- Can be tested from this repository without a second repo.
- Does not change the root package shape.
- Makes the plugin source colocated with the ADW skills during design.

Cons:

- Requires `HERMES_ENABLE_PROJECT_PLUGINS=1`.
- Not a normal `hermes plugins install owner/repo` package.
- Hidden under `.hermes/`, which may be less discoverable.

### Option B: Dedicated Plugin Repository

Create a separate repository:

```text
smarterworkerai/hermes-plugin-adw
  plugin.yaml
  __init__.py
  README.md
  tests/
```

Pros:

- Directly installable with Hermes plugin manager.
- Clear package boundary.
- Keeps ADW skills and plugin runtime independently versionable.

Cons:

- Requires keeping workflow registry in sync with the ADW skill repository.
- Needs release coordination between skill package and plugin package.

### Option C: Root-Level Plugin in This Repository

Create root-level plugin files:

```text
plugin.yaml
__init__.py
```

Pros:

- `hermes plugins install smarterworkerai/agentic-delivery` could work from this repository.

Cons:

- Mixes plugin runtime with skill package source.
- Makes the repository root ambiguous: skill package, documentation repo, and plugin package at once.
- Not recommended unless the repo is intentionally repositioned as a combined Hermes package.

Recommended path: Option A for local spike, Option B for user-facing installation.

## Implementation Plan

### Phase 1: Plugin Spike

Create a repo-local development plugin under:

```text
.hermes/plugins/adw/
```

Files:

- `plugin.yaml`
  - manifest version
  - plugin name: `adw`
  - description
  - version
- `__init__.py`
  - workflow registry
  - alias registry
  - `/adw` command registration
  - usage/error formatting
  - prompt builder
- `README.md`
  - setup instructions
  - command examples
  - known gateway caveats

### Phase 2: Prompt Injection Validation

Test in CLI:

```text
/adw plan-feature invoice CSV export
```

Acceptance criteria:

- `/adw` is recognized as a plugin command.
- Unknown workflow returns usage.
- Valid workflow queues a real agent turn through `ctx.inject_message(...)` or an equivalent verified mechanism.
- The queued turn loads/follows `adw-core` and the selected operational skill.
- The plugin does not bypass ADW gates.

Test in Telegram gateway:

```text
/adw plan-feature invoice CSV export
```

Acceptance criteria:

- Gateway recognizes `/adw`.
- Command arguments arrive intact.
- Result produces a real ADW agent turn, not merely a prompt string echoed to the user.

If gateway only echoes the returned prompt, do not treat that as acceptable behavior. The expected gateway implementation is a rewrite/injection path that causes the normal skill command dispatcher and agent runner to execute.

### Phase 3: Skill Composition Helper

If Phase 2 shows that a plain returned prompt is too weak, add internal helper use:

```python
from agent.skill_commands import build_skill_invocation_message
```

Compose:

```text
build_skill_invocation_message('/adw-core', '')
build_skill_invocation_message('/adw-plan-feature', normalized_payload)
```

Then return the combined message. Validate this in CLI and gateway.

### Phase 4: Documentation Updates

Update:

- `README.md`
- `skills/adw/README.md`
- relevant operational skill usage examples

Document:

- canonical `/adw <workflow> <payload>` usage
- skill-only fallback
- local development plugin setup
- future dedicated plugin package install path

### Phase 5: Validation Tooling

Extend `tools/validate_adw_skills.py` or add a new validator to check:

- every workflow in plugin registry has a corresponding operational skill
- every operational workflow skill has a registry entry or an explicit exclusion
- aliases resolve to valid canonical workflows
- README examples reference valid workflows
- `adw-core` remains present

### Phase 6: Dedicated Plugin Repository

If the spike succeeds, create `smarterworkerai/hermes-plugin-adw` with:

- plugin root files
- tests
- release notes
- install docs

Install command:

```bash
hermes plugins install smarterworkerai/hermes-plugin-adw --enable
hermes gateway restart
```

The dedicated plugin should depend on the ADW skills being installed separately until Hermes supports bundled skill installation from plugin packages as a stable public workflow.

## Test Strategy

Minimum checks:

```bash
python3 tools/validate_adw_skills.py
git diff --check
```

Plugin smoke tests:

```bash
HERMES_ENABLE_PROJECT_PLUGINS=1 hermes plugins list
HERMES_ENABLE_PROJECT_PLUGINS=1 hermes chat -q '/adw plan-feature invoice CSV export'
```

Gateway smoke tests:

```bash
HERMES_ENABLE_PROJECT_PLUGINS=1 hermes gateway restart
```

Then from Telegram:

```text
/adw plan-feature invoice CSV export
```

Expected behavior:

- no unknown-command message
- no direct echo-only behavior
- ADW workflow begins with plan/branch/issue gate behavior

## Risks and Open Questions

- Plugin command handlers returning strings may be treated as direct responses in gateway mode. This must be verified before relying on return-string prompt injection as the final design.
- Direct use of `agent.skill_commands.build_skill_invocation_message()` is internal API. It is practical but should be guarded with fallback behavior.
- Plugin-provided skills registered via `ctx.register_skill()` are explicit `plugin:skill` loads and do not appear in the normal system prompt skill index. ADW should continue to package skills as regular installed skills unless a future plugin bundle model is intentionally adopted.
- Hermes plugin installer does not currently appear to install a plugin from a repository subdirectory. A separate plugin repository is the clean package-manager path.
- Discord native slash UX for `/adw` is likely fine, but true nested native subcommands are not part of the generic Hermes plugin command API.

## Recommended Next Step

Implement Option A as a local spike:

```text
.hermes/plugins/adw/
```

Then validate `/adw plan-feature ...` in CLI and Telegram. If the command only echoes a prompt instead of starting an agent turn, switch the implementation to a `pre_gateway_dispatch` rewrite hook or a composed skill invocation message approach.
