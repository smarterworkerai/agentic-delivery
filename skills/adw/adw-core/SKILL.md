---
name: adw-core
description: >-
  Loads ADW delivery rules, project adapter resolution, shared playbooks, and the fail-closed mise task contract. Use before another ADW skill, when adopting ADW in a repository, or when working with .adw/adw-task-manifest.json or the legacy .hermes project directory.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: none
  hermes-tags: "adw core delivery-workflow playbooks task-contract"
  hermes-related-skills: "adw-plan adw-do-impl adw-test-feature adw-merge-feature adw-chain"
  human-gate: "—"
---
# ADW Core

## When to use / when not

Load this skill before any ADW workflow and when adopting the task contract in a repository. Use it for shared policy, project/context resolution, deterministic task rules, and adapter generation. Do not use it as permission to merge, deploy, roll back, handle secrets, destroy resources, or rewrite history.

## Project and context resolution

1. Inspect the repository and current Git/issue/PR state.
2. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` in an existing project.
3. Load any context helper named by that adapter.
4. Resolve remaining safe facts from the repository; ask when more than one candidate exists or the consequence is unsafe.

The ADW project directory is `.adw/`, or `.hermes/` for existing projects. If both exist, stop with `contract-error`; never choose one silently. New generic projects use `.adw/`. A selected context may require `.hermes/` until that context adopts `.adw/`.

## Deterministic operations

1. Require `<project-dir>/adw-task-manifest.json` and run `mise run adw:check` before any build, verification, deployment, health, readiness, E2E, hotfix, cleanup, or context task.
2. Run `mise run adw:describe` to discover declared capabilities, environments, and effective sources.
3. Invoke only the canonical `adw:*` task required by the active skill. Treat environment and target names as opaque manifest values.
4. Trust the task's exit code and redacted evidence under `<project-dir>/evidence/<run-id>/`; never upgrade `skipped`, `unsupported`, `blocked`, or `contract-error` to success.

If the manifest is absent, stop deterministic execution as `blocked`. There is no ad-hoc fallback to package-manager commands, provider CLIs, provider APIs, or inferred scripts.

## Parameter resolution

Resolve missing inputs in this order: repository state → project adapter → context helper → explicit human question. State safe inferences before continuing. Inference never authorizes a risky action.

## Status format

```markdown
### Status
<current stage>

### Completed
- <artifact/result>

### Risks / Blockers
- <risk or "None">

### Next
- <recommended next action>
```

## Adapter generation

Use `assets/mise/v2/generation-guide.md` and `assets/project_adw_adapter.md` to create a reviewable adapter diff. Generation may automatically run only `mise run adw:check`; it must not run install, quality, deployment, E2E, hotfix, cleanup, or context-sync tasks.

Shared operational detail is in `references/`; the stable contract snapshot remains at `assets/mise/v2/`.

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
