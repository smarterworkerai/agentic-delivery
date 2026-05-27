---
name: adw-self-improve
description: Use when the user asks ADW to persist a durable workflow, context, or project-adapter improvement through a confirm-first PR-based change.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, self-improvement, skill-maintenance, context, confirmation]
    related_skills: [adw-core, adw-plan-feature, adw-do-impl, adw-test-feature]
---

# ADW Self Improve

## Overview

Use this skill when a human explicitly asks ADW to remember, persist, or improve a delivery workflow rule, project context rule, template, validator, or project adapter. The skill is a confirm-first intake router: infer the durable correction, classify the right persistence layer, propose a safe change plan, and only then perform PR-based source-of-truth updates.

This skill is generic. It must not hard-code organization, repository, or project facts. Generic ADW receives reusable workflow mechanics; context helpers receive organization or environment policy; project adapters receive concrete repository/runtime facts.

## When to Use

Use this skill when the user says things like:

- "ADW should remember this rule";
- "make this workflow better next time";
- "persist this into the ADW/context/project adapter";
- "add this as a validator/template/pitfall";
- "self-improve the delivery workflow based on this finding".

Do not use this skill for:

- ordinary implementation work;
- one-off task progress or stale session outcomes;
- secrets or credentials;
- unverified mutable runtime facts;
- immediate live skill edits without a source-of-truth plan and explicit confirmation.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories.

If the improvement mentions a concrete repository, read its project adapter when available. If the adapter declares a context helper, load or inspect that helper before classifying the persistence target.

## Persistence Layers

Classify every proposed improvement into one or more of these layers:

1. **Generic ADW** — reusable workflow mechanics, gates, report formats, skill routing, plugin behavior, or package validators.
2. **Context helper** — organization, team, user, or environment policy that applies across compatible repositories.
3. **Project adapter** — concrete repository files, services, domains, deployment targets, tests, sidecars, and project-specific pitfalls.
4. **Live installed skill update** — optional temporary runtime update after source-of-truth scope is known; must report divergence risk.
5. **Memory-only** — rare; only durable user preference or environment fact that does not belong in a skill, context helper, project adapter, or repository document.
6. **Reject** — secrets, transient task progress, unverified facts, or stale outcomes.

## Workflow

1. Restate the improvement in durable, non-secret terms.
2. Inspect relevant source files, adapters, context helpers, and current repository state.
3. Classify the target layer(s), including rejected layers and why.
4. Produce a plan-only proposal with target repositories/files, validation commands, secret risk, and whether live installed skills should be updated.
5. Stop and wait for human confirmation before editing files, memory, live skills, branches, or PRs.
6. After approval, create/update a branch in the correct source-of-truth repository.
7. Make the smallest durable change that enforces the improvement.
8. Add or update validators/templates/tests where practical.
9. Run validation and record exact command output.
10. Commit, push, and open/update a PR.
11. If live skills were updated, report how to reconcile them with the PR merge.

## Proposal Format

```markdown
### ADW Self-Improvement Proposal

Improvement: <durable restatement>

### Layer Classification
- Generic ADW: <yes/no + reason>
- Context helper: <yes/no + reason>
- Project adapter: <yes/no + reason>
- Live installed skill update: <yes/no + divergence risk>
- Memory-only: <yes/no + reason>
- Rejected targets: <why>

### Planned Source-of-Truth Changes
- Repository/file: <path>
- Validation: <commands>

### Secret / Safety Review
- Secret risk: <none|possible + mitigation>
- Side effects before approval: none

Approve this plan before I persist anything.
```

## Confirmation Gate

Do not perform any persistent side effect before approval:

- no file writes;
- no branch creation;
- no commits;
- no PRs;
- no memory writes;
- no live installed skill edits;
- no deployment or merge actions.

If the requested improvement is clearly a secret, unsafe credential, or transient task result, reject it and explain the safe alternative.

## Output

- Proposal with layer classification and rejected layers.
- After approval: PR URL, changed files, validation results, and any live/source divergence.
- Clear statement of what future ADW run will do differently.

## Common Pitfalls

1. Writing to memory when the improvement belongs in a skill, context helper, project adapter, or validator.
2. Putting project-specific runtime facts into generic ADW skills.
3. Putting organization policy into a project adapter when it should be shared by a context helper.
4. Persisting unverified mutable facts as durable truth.
5. Updating live installed skills without a PR-backed source of truth and reconciliation plan.
6. Treating user correction as permission for immediate side effects; this skill still requires a proposal first.

## Verification Checklist

- [ ] `adw-core` was loaded first.
- [ ] The improvement was restated without secrets or transient task state.
- [ ] Target layer classification is explicit.
- [ ] Rejected layers are listed with reasons.
- [ ] No side effects occurred before confirmation.
- [ ] Source-of-truth changes were committed and pushed to a PR.
- [ ] Validation commands were run or blockers documented.
- [ ] Any optional live skill update reports divergence and reconciliation.

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
