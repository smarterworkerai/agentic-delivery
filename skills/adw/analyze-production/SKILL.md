---
name: adw-analyze-production
description: Use when inspecting production or post-deployment feedback to classify incidents, regressions, rollback need, or follow-up ADW bugfix work.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, production, incident, analysis]
    related_skills: [adw-rollback-deployment, adw-plan-bugfix]
---

# ADW Analyze Production

## Overview

Use this skill to inspect production feedback after deployment and decide whether to continue, rollback, or open follow-up work.

## When to Use

- Post-deploy smoke checks fail.
- Users report a regression.
- Monitoring, logs, or Sentry indicate errors.
- Deployment health is uncertain.

## Workflow

1. Identify environment, deployment, commit/image, time window, and reported symptom.
2. Collect non-sensitive logs, metrics, traces, and endpoint evidence.
3. Classify severity and user impact.
4. Recommend continue, fix-forward, rollback, or deeper investigation.
5. If bugfix is needed, hand off to `adw-plan-bugfix`.
6. If rollback is needed, hand off to `adw-rollback-deployment`.

## Output

- Production feedback summary
- Evidence and impact
- Severity
- Recommended next action
- Follow-up artifact links

## Common Pitfalls

1. Pasting secrets from logs or environment output.
2. Treating one endpoint result as full health.
3. Delaying rollback recommendation for severe regressions.

## Verification Checklist

- [ ] Environment and artifact identity recorded
- [ ] Evidence is redacted and meaningful
- [ ] Severity and recommendation are explicit
- [ ] Follow-up skill/artifact is identified


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
