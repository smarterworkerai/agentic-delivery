---
name: adw-merge-feature
description: Use when merging a validated ADW PR into a destination branch and deploying the resulting branch only after review, preview, and merge gates are satisfied.
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

Use this skill to merge a validated PR and deploy the destination branch. The destination branch is the environment source of truth: feature/bugfix branches map to preview when explicitly selected, `demo` maps to demo, and `main` maps to production.

## When to Use

- A PR passed review and preview validation.
- The human explicitly requests merge/deploy.
- The destination branch and deployment target are known.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. If the current repository contains `.hermes/ADW.md`, read it before acting and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults.

## Workflow

1. Inspect PR state, checks, review status, linked issue, and validation report.
2. Confirm destination branch and deployment consequence with the human.
3. Stop if PR is rejected, checks are unresolved, or target is ambiguous.
4. Merge PR using the repository's merge policy.
5. Verify destination branch SHA and resolve the deployment environment from the branch (`main` -> production, `demo` -> demo, explicitly selected feature/bugfix branch -> preview).
6. Before deploying, update every affected deployment target with the merged configuration required by its environment. For Dokploy targets, update the target environment's compose file and environment variables/settings first; do not rely on the preview/feature deployment being current.
7. Deploy the destination branch using `adw-core/references/playbooks/deployment_gates.md`.
8. Verify deployment status, logs, endpoint semantics, artifact/revision parity, rollback path, and target-environment smoke/E2E/regression checks. Load `adw-validate-regression` when the adapter requires deeper or component-specific coverage.
9. If the PR was merged into a non-feature/non-bugfix destination branch, close the linked issue after deployment verification. Add a closing issue comment that links the merged PR, destination branch/SHA, validation/deployment evidence, final status, and any known follow-up or rollback note. If the PR was merged into another feature or bugfix branch, update the issue with an intermediate merge-status comment instead of closing it.
10. Report final delivery status.

## Merge Gate

Before merge, confirm:

- destination branch is correct and maps to the intended target environment
- PR is not rejected
- required checks passed or failures are explicitly accepted
- preview validation is complete when applicable
- environment/config parity is checked: relevant `.env.example`, compose, deployment, and environment-variable mappings are up to date for every affected target environment, not only the preview/feature deployment
- deployment target configuration is updated before deployment; for Dokploy targets, the target environment compose and environment variables/settings have been updated from the verified parity check
- deployment consequences are understood
- target-environment smoke/E2E/regression requirements are known from the project adapter or explicitly documented as unavailable

## Output

- Merge result
- Destination branch
- Deployment target
- Deployment status
- Linked issue status
- Rollback path

## Common Pitfalls

1. Treating inferred destination branch as approval.
2. Merging without preview validation when the app supports preview.
3. Deploying mutable tags before build/image publication completes.
4. Closing issues while deployment is still unverified.

## Verification Checklist

- [ ] Human explicitly approved merge/deploy target
- [ ] Review and preview gates satisfied
- [ ] `.env.example` / compose / deployment / environment-variable parity checked for all relevant target environments
- [ ] Target deployment configuration updated before deployment, including Dokploy compose and environment variables/settings when Dokploy is used
- [ ] Merge completed and destination SHA is recorded
- [ ] Deployment status, endpoint semantics, artifact/revision parity, and target-environment smoke/E2E/regression verified
- [ ] Linked issue closed with a final evidence comment when the PR merged into a non-feature/non-bugfix branch, or updated with intermediate merge status when merged into another work branch
- [ ] Rollback path is documented


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
