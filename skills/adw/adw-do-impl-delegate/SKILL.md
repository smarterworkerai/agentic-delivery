---
name: adw-do-impl-delegate
description: >-
  Delegates an approved implementation through a backend-neutral brief and independently verifies the returned change. Use when another agent or worker should implement an ADW plan while the orchestrator retains delivery gates.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: adw-core
  router-tokens: "do-impl-delegate"
  hermes-tags: "adw delegation implementation review"
  hermes-related-skills: "adw-core adw-do-impl adw-test-feature"
  human-gate: "Exact PR source and target route"
---
# ADW Do Implementation Delegate

## Overview

Use this skill when implementation should be delegated to another agent or worker while preserving ADW traceability, PR-centric delivery, and review gates.

This skill defines the portable ADW delegation contract: what the orchestrator hands off, what the worker must return, and how the orchestrator verifies the result. It does not prescribe a concrete execution backend. Backend-specific mechanics belong to the selected backend's documentation or skill.

Companion backend conformance issue: https://github.com/smarterworkerai/sandbox-delegation/issues/1

## When to Use

- Work is complex enough to benefit from an isolated worker.
- The user explicitly requests delegation.
- A project/profile convention requires an external implementation worker.
- The primary deliverable should still be a PR/MR reviewed by the ADW orchestrator.

Use `adw-do-impl` instead when the current agent should implement directly in the local worktree.

## Required Context

Load `adw-core` first. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` for an existing project, and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults. Shared playbooks are named from the `adw-core` skill; this skill's own templates are under `assets/`.

## Backend Resolution

Resolve the delegation backend only after loading the project context. Read the repository's ADW project adapter when present and load any adapter-declared context helper before choosing defaults. A context helper may provide the delegation backend skill and target alias; do not require the the repository's ADW project adapter adapter to repeat backend defaults when the loaded context helper owns them. Then resolve the backend in this order:

1. Use the backend or target explicitly named by the human.
2. Use the backend or target declared by the ADW project adapter or its context helper.
3. Use the backend or target clearly implied by the current project/profile context.
4. Use a project/profile-specific delegation convention only when it is unambiguous.
5. Otherwise ask the human which delegation target/backend to use before launching.

Do not introduce or require a mandatory `adw-delegation-adapter` skill. The selected backend may be a sandbox worker, local worktree agent, MCP worker, `delegate_task`, Claude Code, Codex, or another mechanism. If the loaded context helper selects a backend skill, load that backend skill before creating the handoff bundle or launching the worker.

## Portable Delegation Contract

The orchestrator must prepare a run bundle with these backend-neutral names and semantics:

```text
<delegation-run-root>/<run-id>/
├── 00-task-brief.md
├── 01-environment.md
├── 02-constraints.md
├── 03-acceptance-criteria.md
├── 04-input-artifacts.md
├── 10-worker-log.md
├── 11-commands.md
├── 12-output-summary.md
├── result/
│   ├── patches/
│   ├── notes/
│   └── artifacts/
└── status.json
```

The concrete run root is backend-specific. ADW skills may require the file names and meanings above, but must not require a particular worker host, user, filesystem layout, launcher command, runtime, token mount, permission model, or cache directory.

### Required handoff content

`00-task-brief.md` should include:

- repository URL;
- base branch;
- target implementation branch;
- linked issue and/or approved plan artifact;
- exact scope;
- explicit non-scope;
- required deliverable, including whether an exact PR/MR route is approved or patch/local-commit output is required;
- expected tests/checks;
- secret handling policy;
- instruction not to open a PR/MR without approved source/target/replacement scope, and not to merge or deploy unless the human explicitly requested it.

`01-environment.md` should name the selected backend and summarize only the execution assumptions the worker needs. Backend-specific paths or commands may appear in the backend-produced bundle, but should not be copied into this portable ADW skill.

`02-constraints.md`, `03-acceptance-criteria.md`, and `04-input-artifacts.md` should make the work reviewable without dumping large raw context.

### Required result content for code changes

The worker result must include, at minimum:

- PR/MR URL when the exact route was approved, otherwise a local commit or patch/artifact reference;
- implementation branch;
- commit SHA;
- changed-file summary;
- verification commands and results;
- blockers / remaining risks;
- explicit statement that no merge/deploy was performed.

When PR/MR creation is not approved or is technically impossible, the worker must provide a local commit or patches/artifacts under `result/` and state why no PR/MR exists.

### Correction rounds

A correction round is required when output is weak, incomplete, self-reported only, missing an approved PR or reviewable diff/test artifact, or violates scope/non-scope. Correction rounds should preserve traceability through `status.json.correction_rounds`, a correction note artifact, and an updated `12-output-summary.md`.

## Workflow

1. Load `adw-core` and the relevant delegation templates.
2. Inspect current repository, branch, issue, PR, and plan state.
3. Read the ADW project adapter when present and load any adapter-declared context helper before resolving branch, validation, deployment, administration, or delegation defaults.
4. Resolve the delegation backend using the backend resolution order above.
5. Create the portable handoff bundle from the templates. Include an exact approved PR/MR source/target/replacement route, or explicitly require local-commit/patch output without PR creation.
6. Load the selected backend's skill or documentation before launching (for example, load `sandbox-delegation` when the project adapter, the context helper, or the human selects the sandbox backend); if no backend docs/skill are available, stop and ask instead of inventing launcher commands.
7. Launch the selected backend using that backend's documented mechanism.
8. Receive a verifiable result: approved PR/MR URL or local commit/patch reference, branch when applicable, commit SHA, test evidence, and summary.
9. Inspect the returned diff and evidence, then independently run `mise run adw:check` and `mise run adw:verify:minimal` in the returned revision when accessible. If the manifest is absent, return the work for an adapter-generation correction instead of substituting ad-hoc commands.
10. Verify scope, non-scope, traceability, and secret hygiene in tracked files/docs/examples.
11. Confirm no merge/deploy happened unless explicitly authorized.
12. Request a correction round when output is weak, missing, or self-reported only.
13. Comment on the PR only when one was approved and created; otherwise summarize the reviewed commit/patch result for the human.

## Orchestrator Completion Gate

Do not report delegation success until the orchestrator has verified:

- An approved PR/MR exists, or local commit/patch artifacts are supplied with the explicit no-PR reason.
- Returned branch and commit SHA match the approved PR/MR or artifact set.
- Diff matches the requested scope and avoids explicit non-scope.
- Test/check evidence is present and credible.
- Tracked files and docs/examples do not contain real-looking secrets.
- No merge or deployment happened unless the human explicitly authorized it.
- Remaining risks and blockers are documented.
- Any GitHub issue/PR body/comment text uses real Markdown newlines, not visible literal `\n` sequences.

## Output

Final user-facing output should include:

- Delegated task summary.
- Selected backend/target, if safe to disclose.
- Approved PR/MR link, or local commit/patch artifact location and pending route approval.
- Implementation branch and commit SHA.
- Checks/tests reviewed.
- Correction rounds performed.
- Acceptance/rejection status.
- Required remediation, if any.

## Common Pitfalls

1. Sending vague delegation context.
2. Accepting a self-reported success without inspecting the PR/diff.
3. Assuming a backend target when context is ambiguous instead of asking the human.
4. Hard-coding backend-specific launcher mechanics into the portable ADW contract.
5. Forgetting to return weak results for correction instead of hiding them.
6. Treating a completed backend process as complete delivery when the approved PR or required diff/test artifacts are missing.

## Verification Checklist

- [ ] `adw-core` was loaded first.
- [ ] Repository-local the ADW project adapter and any adapter-declared context helper were checked before backend/default resolution.
- [ ] Delegation backend/target was explicit, unambiguous, or confirmed by the human.
- [ ] Selected backend skill/documentation was loaded before launcher-specific commands were used.
- [ ] Handoff bundle includes task brief, environment, constraints, acceptance criteria, input artifacts, and approved PR route or explicit no-PR instruction.
- [ ] Worker returned an approved PR/MR URL or local commit/patch artifacts with the no-PR reason.
- [ ] Worker returned branch, commit SHA, changed-file summary, and verification evidence.
- [ ] PR diff or patches were reviewed by the orchestrator.
- [ ] Secret hygiene was checked in tracked files and docs/examples.
- [ ] No merge/deploy happened during delegation unless explicitly authorized.
- [ ] Correction round was requested for weak or incomplete output.
- [ ] GitHub issue/PR/comment markdown uses real newlines rather than escaped `\n` sequences.

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
