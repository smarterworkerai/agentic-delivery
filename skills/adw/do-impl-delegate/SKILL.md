---
name: adw-do-impl-delegate
description: Use when delegating ADW implementation to a backend-selected agent. Defines a portable handoff/result contract, resolves the delegation target, reviews returned work, and requests correction when output is weak.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, delegation, implementation, review]
    related_skills: [adw-core, adw-do-impl, adw-test-feature]
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

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories.

For delegation, also resolve templates from `skills/adw/adw-core/templates/delegation/`:

- `task_brief.md`
- `environment.md`
- `constraints.md`
- `acceptance_criteria.md`
- `input_artifacts.md`
- `output_summary.md`
- `status.schema.json`

## Backend Resolution

Resolve the delegation backend in this order:

1. Use the backend or target explicitly named by the human.
2. Use the backend or target clearly implied by the current project/profile context.
3. Use a project/profile-specific delegation convention only when it is unambiguous.
4. Otherwise ask the human which delegation target/backend to use before launching.

Do not introduce or require a mandatory `adw-delegation-adapter` skill. The selected backend may be a sandbox worker, local worktree agent, MCP worker, `delegate_task`, Claude Code, Codex, or another mechanism.

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
- required deliverable;
- expected tests/checks;
- secret handling policy;
- instruction not to merge or deploy unless the human explicitly requested it.

`01-environment.md` should name the selected backend and summarize only the execution assumptions the worker needs. Backend-specific paths or commands may appear in the backend-produced bundle, but should not be copied into this portable ADW skill.

`02-constraints.md`, `03-acceptance-criteria.md`, and `04-input-artifacts.md` should make the work reviewable without dumping large raw context.

### Required result content for code changes

The worker result must include, at minimum:

- PR/MR URL;
- implementation branch;
- commit SHA;
- changed-file summary;
- verification commands and results;
- blockers / remaining risks;
- explicit statement that no merge/deploy was performed.

If a PR/MR is impossible, the worker must explain why and provide patches or artifacts under `result/`.

### Correction rounds

A correction round is required when output is weak, incomplete, self-reported only, missing a PR/diff/test artifact, or violates scope/non-scope. Correction rounds should preserve traceability through `status.json.correction_rounds`, a correction note artifact, and an updated `12-output-summary.md`.

## Workflow

1. Load `adw-core` and the relevant delegation templates.
2. Inspect current repository, branch, issue, PR, and plan state.
3. Resolve the delegation backend using the backend resolution order above.
4. Create the portable handoff bundle from the templates.
5. Launch the selected backend using that backend's documented mechanism.
6. Receive a verifiable result: PR/MR URL, branch, commit SHA, test evidence, and summary.
7. Inspect the returned diff and test evidence.
8. Verify scope, non-scope, traceability, and secret hygiene in tracked files/docs/examples.
9. Confirm no merge/deploy happened unless explicitly authorized.
10. Request a correction round when output is weak, missing, or self-reported only.
11. Comment on the PR or summarize the review result for the human.

## Orchestrator Completion Gate

Do not report delegation success until the orchestrator has verified:

- PR/MR exists or patches/artifacts are supplied with a clear blocker explanation.
- Returned branch and commit SHA match the PR/MR or artifact set.
- Diff matches the requested scope and avoids explicit non-scope.
- Test/check evidence is present and credible.
- Tracked files and docs/examples do not contain real-looking secrets.
- No merge or deployment happened unless the human explicitly authorized it.
- Remaining risks and blockers are documented.

## Output

Final user-facing output should include:

- Delegated task summary.
- Selected backend/target, if safe to disclose.
- PR/MR link or artifact location.
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
6. Treating a completed backend process as complete delivery when PR/test artifacts are missing.

## Verification Checklist

- [ ] `adw-core` was loaded first.
- [ ] Delegation backend/target was explicit, unambiguous, or confirmed by the human.
- [ ] Handoff bundle includes task brief, environment, constraints, acceptance criteria, and input artifacts.
- [ ] Worker returned PR/MR URL or patches/artifacts with a blocker explanation.
- [ ] Worker returned branch, commit SHA, changed-file summary, and verification evidence.
- [ ] PR diff or patches were reviewed by the orchestrator.
- [ ] Secret hygiene was checked in tracked files and docs/examples.
- [ ] No merge/deploy happened during delegation unless explicitly authorized.
- [ ] Correction round was requested for weak or incomplete output.

## ADW Shared Operating Contract

All ADW skills belong to one pipeline and share installable supporting material through `adw-core`.

Shared artifacts are package-owned by `adw-core`:

- Root `SOUL.md` — identity, tone, hard boundaries, and assumption policy for profiles that adopt ADW.
- `adw-core/references/playbooks/` — reusable operational procedures.
- `adw-core/templates/` — canonical issue, PR, report, plan, and delegation formats.
- `adw-core/references/adr/` — architecture decisions for the workflow itself.
- `adw-core/assets/diagrams/` — PlantUML sources and pre-rendered local SVGs.

Load `adw-core` before executing this skill. Do not copy shared playbooks/templates into individual workflow skills; update the central `adw-core` artifact instead.

## Parameter Resolution

Human prompts may be minimal. Resolve missing parameters in this order:

1. Inspect current repository, branch, issue, PR, and deployment metadata.
2. Check `adw-core` artifacts, playbooks, templates, ADRs, and the root `SOUL.md` if available.
3. If exactly one safe candidate exists, state the inferred assumption and ask the human to confirm before proceeding.
4. If multiple candidates exist or the consequence is unsafe, ask for explicit human input.
5. Never treat inference as approval for merge, production deployment, rollback, secret handling, destructive infrastructure changes, history rewrite, or an unspecified delegation backend.

## Standard Status Report

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
