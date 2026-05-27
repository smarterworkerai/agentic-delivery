---
name: adw-rollback-deployment
description: Use when rolling back a failed ADW deployment to the last known-good version, reporting impact, and creating follow-up bug work when needed.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, rollback, incident, deployment]
    related_skills: [adw-core, adw-analyze-production, adw-plan-bugfix]
---

# ADW Rollback Deployment

## Overview

Use this skill when a deployment fails or post-deploy validation identifies a critical regression.

## When to Use

- Production deployment fails.
- Post-deploy validation fails.
- Monitoring indicates severe regression.
- User requests rollback.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. If the current repository contains `.hermes/ADW.md`, read it before acting and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults.

## Workflow

1. Confirm rollback target and environment with the human.
2. Identify last known-good artifact, commit, image tag, or deployment.
3. Assess stateful risks: migrations, data changes, volumes, external services.
4. Execute the safest rollback path.
5. Verify deployment health and user-facing behavior.
6. Report impact and current status using `adw-core/templates/rollback_report.md`.
7. Create a follow-up bug issue if needed with `adw-plan-bugfix`.

## Safety Boundary

Rollback is destructive or high-impact. Never infer approval. Always ask for explicit confirmation of environment and rollback target.

## Output

- Rolled-back environment
- Previous and current artifact identity
- Verification result
- User impact
- Follow-up issue link, if created

## Common Pitfalls

1. Rolling back code without checking data compatibility.
2. Assuming Git revert updates deployment platform raw compose/env state.
3. Losing evidence needed for root-cause analysis.
4. Not creating follow-up work after emergency recovery.

## Verification Checklist

- [ ] Explicit rollback approval recorded
- [ ] Last known-good artifact identified
- [ ] Stateful risks checked
- [ ] Rollback verified through deployment and endpoint checks
- [ ] Follow-up bug issue created when needed


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
