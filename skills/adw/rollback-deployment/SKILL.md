---
name: adw-rollback-deployment
description: Use when rolling back a failed ADW deployment to the last known-good version, reporting impact, and creating follow-up bug work when needed.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, rollback, incident, deployment]
    related_skills: [adw-analyze-production, adw-plan-bugfix]
---

# ADW Rollback Deployment

## Overview

Use this skill when a deployment fails or post-deploy validation identifies a critical regression.

## When to Use

- Production deployment fails.
- Post-deploy validation fails.
- Monitoring indicates severe regression.
- User requests rollback.

## Workflow

1. Confirm rollback target and environment with the human.
2. Identify last known-good artifact, commit, image tag, or deployment.
3. Assess stateful risks: migrations, data changes, volumes, external services.
4. Execute the safest rollback path.
5. Verify deployment health and user-facing behavior.
6. Report impact and current status using `templates/rollback_report.md`.
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

All ADW skills belong to one pipeline and share repository artifacts rather than duplicating supporting material inside each skill directory.

Shared artifacts:

- `SOUL.md` — identity, tone, hard boundaries, and assumption policy.
- `playbooks/` — reusable operational procedures.
- `templates/` — canonical issue, PR, report, and plan formats.
- `adr/` — architecture decisions for the workflow itself.
- `docs/diagrams/` — PlantUML sources and pre-rendered local SVGs.

Use shared artifacts by path. Do not copy shared playbooks/templates into individual skills unless a future packaging target explicitly requires standalone skill bundles.

## Parameter Resolution

Human prompts may be minimal. Resolve missing parameters in this order:

1. Inspect current repository, branch, issue, PR, and deployment metadata.
2. Check linked ADW artifacts and shared playbooks/templates.
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
