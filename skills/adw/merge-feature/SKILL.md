---
name: adw-merge-feature
description: Use when merging a validated PR into an approved target.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, merge, deployment, release]
    related_skills: [adw-core, adw-test-feature, adw-validate-regression, adw-analyze-production]
---

# ADW Merge Feature

## Overview

Use this skill to merge a validated PR and, when requested, deploy through the adapter-declared release strategy. The repository adapter and task manifest define any branch, artifact, and environment relationship; generic ADW treats environment names as opaque.

## When to Use

- A PR passed review and preview validation.
- The human explicitly requests the merge and approves the exact destination branch.
- When deployment is separately requested, its exact opaque target and consequences are known and approved.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. If the current repository contains `.hermes/ADW.md`, read it before acting and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults.

## Workflow

1. Inspect PR state, checks, review status, linked issue, and validation report using `adw-core/references/playbooks/deployment_gates.md` and `adw-core/references/playbooks/release_targets.md`.
2. Confirm the exact destination branch and, when deployment is requested, the exact opaque environment and deployment consequence with the human.
3. Stop if PR is rejected, checks are unresolved, or target is ambiguous.
4. Merge PR using the repository's merge policy.
5. Verify destination branch SHA. If deployment was not explicitly requested, report the merge result and stop. Otherwise resolve the environment through the repository adapter and manifest, then run `mise run adw:check` and `mise run adw:describe`; do not infer an environment name.
6. Run `mise run adw:deploy:config:pull <environment>` and `mise run adw:deploy:config:plan <environment>`. Inspect the plan and, after the external deployment approval gate, apply it with `mise run adw:deploy:config:apply <environment>`.
7. Deploy with `mise run adw:deploy:apply <environment>` and inspect `mise run adw:deploy:status <environment>` evidence.
8. Verify artifact/revision identity and runtime behavior with `mise run adw:health <environment>`, `mise run adw:readiness <environment>`, and `mise run adw:validate-deployment <environment>` according to manifest support. Neither optional E2E suite is automatic; require explicit per-run authorization before executing either. Persistent services require write-path validation or an explicit blocker/waiver. Load `adw-validate-regression` for deeper coverage.
9. Close the linked issue only when repository policy and verified delivery state say its acceptance criteria are complete. Otherwise add an intermediate status comment. Link the merged PR, destination revision, validation/deployment evidence when applicable, final status, and follow-up or rollback note using `adw-core/references/playbooks/github_traceability.md` and file-backed Markdown.
10. Report final delivery status with `adw-core/templates/deployment_report.md` when deployment ran; otherwise report the verified merge-only result.

## Merge Gate

Before merge, confirm:

- destination branch is correct; when deployment is requested, the adapter/manifest resolve the intended target environment
- PR is not rejected
- the PR-attached required quality/proof check passed for the exact current head and tested tree; pending, failed, skipped, stale, or unrelated checks block merge
- preview validation is complete when applicable
- when deployment is requested, deployment configuration parity is proven by `adw:deploy:config:pull` and `adw:deploy:config:plan` evidence for every affected target environment
- when deployment is requested, the approved plan is applied with `adw:deploy:config:apply` before deployment
- when deployment is requested, its consequences are understood
- when deployment is requested, target-environment smoke/E2E/regression requirements are known from the project adapter or explicitly documented as unavailable
- when deployment is requested for a persistent service, write-path validation requirements are known for databases, filesystem storage, mounted volumes, queues, or external side effects

## Output

- Merge result
- Destination branch
- Deployment target or `not requested`
- Deployment status or `not requested`
- Linked issue status
- Rollback path when deployment is requested, otherwise `not applicable`

## Common Pitfalls

1. Treating inferred destination branch as approval.
2. Merging without preview validation when the app supports preview.
3. Deploying without proving immutable source and artifact identity.
4. Closing issues while deployment is still unverified.
5. Treating a green deploy plus HTTP 200 as sufficient when persistent write paths were not exercised.
6. Posting closing/deployment comments with visible backslash-n escape sequences instead of file-backed Markdown.

## Verification Checklist

- [ ] Human explicitly approved the exact merge target and, when requested, the exact deployment target
- [ ] Review and preview gates satisfied
- [ ] When deployment is requested, the configuration plan covers all changed runtime configuration for relevant target environments
- [ ] When deployment is requested, configuration pull/plan/apply evidence is recorded for all relevant environments
- [ ] Merge completed and destination SHA is recorded
- [ ] When deployment is requested, status, endpoint semantics, artifact/revision parity, and target-environment smoke/E2E/regression are verified
- [ ] When deployment is requested for a persistent service, write-path validation or a blocker/waiver is recorded
- [ ] Linked issue closed only when acceptance criteria are complete under repository policy; otherwise updated with intermediate status
- [ ] GitHub issue/PR comments use readable Markdown with real line breaks
- [ ] When deployment is requested, the rollback path is documented


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
3. If exactly one safe candidate exists, state the inferred assumption and ask the human to confirm before proceeding.
4. If multiple candidates exist or the consequence is unsafe, ask for explicit human input.
5. Never treat inference as approval for merge, production deployment, rollback, secret handling, destructive infrastructure changes, or history rewrite.

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
