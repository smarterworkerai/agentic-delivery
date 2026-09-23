---
name: adw-chain
description: Use when coordinating an approved multi-stage ADW flow.
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
3. Classify the work as feature, bugfix, regression validation, adapter-declared release, rollback, or incident analysis.
4. Build a chain plan that lists each stage, the ADW skill that will own it, expected side effects, required confirmations, and blockers.
5. Stop and ask the human to approve the chain plan before creating branches, issues, commits, PRs, deployments, merges, or persistent changes. For a full-rollout opt-in, the first confirmation must explicitly authorize every listed release stage and target; the initial confirmation is never skipped.
6. After approval, execute one stage at a time using the existing ADW operational skill for that stage. Do not ask again at each successful gate when the upfront authorization covers the exact action.
7. Send a concise phase-boundary status report after each completed stage.
8. Re-check gates before each side-effecting stage; if prerequisites changed outside the approved scope, pause and report the new blocker. A failed or unresolved gate is never converted into approval.
9. Finish with a final traceability report: issue, branch, PR, commits, checks, preview/validation, merge/deploy status, and remaining risks.

## Chain Planning Report

Before any side effect, report:

```markdown
### ADW Chain Proposal

Requested stages: <parsed sequence>
Work classification: <feature|bugfix|validation|release|incident|unknown>
Repository context: <current repo/branch/adapter status>

### Planned Stage Owners
n. <stage> -> <adw-* skill> -> <side effects after approval>

### Required Lower-Layer Decisions
- Branch/issue/PR naming: <known|adapter|needs confirmation>
- Test/validation matrix: <known|adapter|needs confirmation>
- Merge/deploy target: <known|adapter|needs confirmation>
- Continuation mode: <stage-by-stage decisions|full rollout through exact approved route>
- Ordered targets and consequences: <exact branch/environment/deployment map or blocker>
- Required gate evidence and stop conditions: <quality/review/preview/runtime/identity>

### Blockers / Risks
- <blocker or None>

Approve this chain before I start side-effecting work. Explicitly choose full rollout here if you want all listed merge/deployment decisions authorized by this one confirmation.
```

## Full-Rollout Opt-In (One Initial Confirmation)

A full-rollout opt-in is available only when the first chain proposal resolves an exact release route from the repository adapter and context helper. No authorization is inherited from a generic chain request, a manifest, an earlier feature, or a previous conversation. The first confirmation remains mandatory: show the plan, then ask whether to stop at normal decision boundaries or **carry the entire specified feature through rollout**. A vague `implement` request is not a full-rollout opt-in.

Before that single upfront authorization, the proposal must identify the repository and feature/issue, PR base and approved review/preview path, ordered promotion branches (for example adapter-declared `demo` then `main`), exact deployment environments/targets, immutable artifact strategy, required quality/review/preview and deployment parity checks, and any write-path or provider-cost consequences. The operator must explicitly choose full rollout for this exact route, including both merges and both deployments. If a target, route, credential impact, or consequence cannot be resolved safely, ask at the initial confirmation rather than treating later inference as approval. Do not hard-code these branch names or environments as generic defaults.

After confirmation, execute each stage and its owning skill in order. Recheck the live PR-attached required quality/proof check on the exact tested tree, independent review, preview/runtime validation, immutable artifact identity, branch topology and destination state before each merge. Recheck config plan and secret-preservation constraints before each deployment; prove image/revision parity, health/readiness, project-required write-path smoke and destination-specific checks after each deployment. Successful gates authorize continuation under the same bounded grant, not automatic gate bypass; record phase evidence and proceed through the approved demo and main route without a new confirmation at each successful decision boundary. Optional full integration/E2E remains optional and remote-write E2E still needs its own explicit per-run authorization unless its exact run, target and provider-cost implications were included in the initial grant.

On rejection, failed/pending/stale quality, unresolved review, unknown target, secret or configuration drift, deployment failure, or any unapproved change in scope, **stop and request renewed authorization** after reporting the evidence. Expected implementation commits within the approved feature scope do not alone invalidate the initial grant; they must pass the ordinary new-tree quality, review and preview gates before promotion. A change to an already reviewed or validated tree invalidates its old proof: pause the promotion, rerun the gates on the new tree, and continue under the original grant only if the feature scope and route are unchanged. A changed target or release route requires renewed authorization. Never silently waive a gate, rewrite history, rollback, change secrets, run a destructive operation, or substitute a different target under this grant. The grant expires at completion, interruption with lost/ambiguous approval context, or a material route/plan change. On resume, reconstruct the exact approved scope and current evidence; if the grant cannot be verified, ask again. Production merge and deployment are high-risk actions covered only by the explicit first confirmation naming them, never by inference.

## Stage Mapping

Use these generic mappings unless a project adapter declares stricter routing:

- `plan` -> `adw-plan-feature` or `adw-plan-bugfix` after classification.
- `impl` / `implement` -> `adw-do-impl` or `adw-do-impl-delegate` depending on explicit delegation policy.
- `test` / `validate` -> `adw-test-feature` or `adw-validate-regression`.
- `merge` -> `adw-merge-feature` after review and validation gates pass.
- `deploy` -> the deployment phase owned by `adw-merge-feature` or the project adapter's release flow.
- `promote` -> treat as an adapter-declared release request and route to the repository's explicit release workflow; do not infer a branch or environment mapping.
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

Only proceed after the human confirms the chain proposal. A single upfront authorization to complete the exact full rollout includes the enumerated demo/main (or adapter-declared equivalent) merges and deployments, so do not re-ask after each passing gate. It does not waive any gate or authorize a changed route. If the user approves only implementation or the plan without explicitly selecting full rollout, keep the ordinary per-stage merge/production confirmation requirements.

## Output

- Chain proposal before side effects.
- Phase-boundary status reports during execution.
- Final traceability report with links and validation evidence.
- Any blocked or skipped stage with the reason.

## Common Pitfalls

1. Treating a compact chain command as approval to merge or deploy. The first chain proposal still requires explicit confirmation; only a bounded full-rollout opt-in at that confirmation can cover later merge/deployment decisions.
2. Re-implementing stage logic inside this skill instead of loading the specific ADW operational skill.
3. Hard-coding branch, environment, deployment, or organization defaults that belong in a context helper or project adapter.
4. Continuing the chain after a gate fails instead of pausing and reporting the blocker; full rollout automates successful transitions, not acceptance of failures.
5. Hiding weak implementation or validation results instead of returning them for correction.

## Verification Checklist

- [ ] `adw-core` was loaded first.
- [ ] The chain proposal listed all requested stages and side effects.
- [ ] The first proposal identified the exact route and the human explicitly selected full rollout before any merge or deployment, when that mode was requested.
- [ ] All quality/review/preview/deployment gates were rechecked at each stage; no passing gate was mistaken for a new approval requirement, and no failed gate was bypassed.
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
- `adw-core/assets/diagrams/` — reviewable PlantUML workflow source.

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
