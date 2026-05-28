---
name: adw-chain
description: Use when the user asks for a confirmed multi-stage ADW sequence such as plan, implement, test, merge, or deploy from one free-text request.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, orchestration, chain, confirmation, delivery-workflow]
    related_skills: [adw-core, adw-plan-feature, adw-plan-bugfix, adw-do-impl, adw-test-feature, adw-merge-feature]
---

# ADW Chain

## Overview

Use this skill to orchestrate a human-requested sequence of ADW stages from a compact command such as `plan impl test merge <work description>`. The chain skill is a generic coordinator: it resolves the requested stages, produces a confirmation plan, and then runs existing ADW operational skills in order after explicit human approval.

This skill must not encode organization, repository, deployment, branch, environment, or project-specific defaults. Resolve those through the current repository, declared project adapter, and optional context helper described by `adw-core`.

## When to Use

Use this skill when:

- the user asks for multiple ADW stages in one request;
- the request includes stage words such as `plan`, `impl`, `test`, `merge`, `deploy`, or `rollback`;
- the user expects phase-boundary status updates and one coordinated delivery path;
- the underlying work still belongs in the normal PR-centric ADW pipeline.

Do not use this skill for:

- a single stage that maps directly to another `adw-*` skill;
- side-effecting work before the user has approved the chain plan;
- project-specific command shortcuts that should live in a project adapter or context helper.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. If the current repository contains `.hermes/ADW.md`, read it before acting and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults.

Also load any project context helper explicitly declared by the repository adapter. If no adapter exists, inspect the repository and ask for missing unsafe decisions instead of inventing defaults.

## Workflow

1. Parse the requested stage sequence and free-text work description.
2. Inspect the repository, current branch, existing issue/PR state, and any project adapter such as `.hermes/ADW.md`.
3. Classify the work as feature, bugfix, regression validation, release-branch merge/deploy, rollback, or incident analysis.
4. Build a chain plan that lists each stage, the ADW skill that will own it, expected side effects, required confirmations, and blockers.
5. Stop and ask the human to approve the chain plan before creating branches, issues, commits, PRs, deployments, merges, or persistent changes.
6. After approval, execute one stage at a time using the existing ADW operational skill for that stage.
7. Send a concise phase-boundary status report after each completed stage.
8. Re-check gates before each side-effecting stage; if prerequisites changed, pause and report the new blocker.
9. Finish with a final traceability report: issue, branch, PR, commits, checks, preview/validation, merge/deploy status, and remaining risks.

## Chain Planning Report

Before any side effect, report:

```markdown
### ADW Chain Proposal

Requested stages: <parsed sequence>
Work classification: <feature|bugfix|validation|release-branch-merge|incident|unknown>
Repository context: <current repo/branch/adapter status>

### Planned Stage Owners
n. <stage> -> <adw-* skill> -> <side effects after approval>

### Required Lower-Layer Decisions
- Branch/issue/PR naming: <known|adapter|needs confirmation>
- Test/validation matrix: <known|adapter|needs confirmation>
- Merge/deploy target: <known|adapter|needs confirmation>

### Blockers / Risks
- <blocker or None>

Approve this chain before I start side-effecting work.
```

## Stage Mapping

Use these generic mappings unless a project adapter declares stricter routing:

- `plan` -> `adw-plan-feature` or `adw-plan-bugfix` after classification.
- `impl` / `implement` -> `adw-do-impl` or `adw-do-impl-delegate` depending on explicit delegation policy.
- `test` / `validate` -> `adw-test-feature` or `adw-validate-regression`.
- `merge` -> `adw-merge-feature` after review and validation gates pass.
- `deploy` -> the deployment phase owned by `adw-merge-feature` or the project adapter's release flow.
- `promote` -> treat as a release-branch merge/deploy request and route to `adw-merge-feature` unless the project adapter defines a different explicit workflow.
- `rollback` -> `adw-rollback-deployment`.

If a word is ambiguous, report the ambiguity in the proposal and ask for confirmation before acting.

## Approval Gate

The first response for a side-effecting chain must be plan-only. Do not create or update:

- branches;
- issues;
- commits;
- pull requests;
- deployments;
- merges;
- live skills or persistent memory.

Only proceed after the human confirms the chain proposal.

## Output

- Chain proposal before side effects.
- Phase-boundary status reports during execution.
- Final traceability report with links and validation evidence.
- Any blocked or skipped stage with the reason.

## Common Pitfalls

1. Treating a compact chain command as approval to merge or deploy. The chain proposal still requires explicit confirmation.
2. Re-implementing stage logic inside this skill instead of loading the specific ADW operational skill.
3. Hard-coding branch, environment, deployment, or organization defaults that belong in a context helper or project adapter.
4. Continuing the chain after a gate fails instead of pausing and reporting the blocker.
5. Hiding weak implementation or validation results instead of returning them for correction.

## Verification Checklist

- [ ] `adw-core` was loaded first.
- [ ] The chain proposal listed all requested stages and side effects.
- [ ] No side effects happened before explicit approval.
- [ ] Each executed stage used the owning `adw-*` skill.
- [ ] Project-specific defaults came only from repository inspection, context helper, or project adapter.
- [ ] Final report includes issue/branch/PR/check/deploy traceability as applicable.

## ADW Shared Operating Contract

All ADW skills belong to one pipeline and share installable supporting material through `adw-core`.

Shared artifacts are package-owned by `adw-core`:

- Root `SOUL.md` — identity, tone, hard boundaries, and assumption policy for profiles that adopt ADW.
- `adw-core/references/playbooks/` — reusable operational procedures.
- `adw-core/templates/` — canonical issue, PR, report, and plan formats.
- `adw-core/references/adr/` — architecture decisions for the workflow itself.
- `adw-core/assets/diagrams/` — PlantUML sources and pre-rendered local SVGs.

Load `adw-core` before executing this skill. Do not copy shared playbooks/templates into individual workflow skills; update the central `adw-core` artifact instead.

## Parameter Resolution

Human prompts may be minimal. Resolve missing parameters in this order:

1. Inspect current repository, branch, issue, PR, and deployment metadata.
2. Check `adw-core` artifacts, playbooks, templates, ADRs, and the root `SOUL.md` if available.
3. Read the project adapter and declared context helper when present.
4. If exactly one safe candidate exists, state the inferred assumption and ask the human to confirm before proceeding.
5. If multiple candidates exist or the consequence is unsafe, ask for explicit human input.
6. Never treat inference as approval for merge, production deployment, rollback, secret handling, destructive infrastructure changes, or history rewrite.

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
