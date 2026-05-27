---
name: adw-analyze-production
description: Use when inspecting production or post-deployment feedback to classify incidents, regressions, rollback need, or follow-up ADW bugfix work.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, production, incident, analysis]
    related_skills: [adw-core, adw-rollback-deployment, adw-plan-bugfix]
---

# ADW Analyze Production

## Overview

Use this skill to inspect production feedback after deployment and decide whether to continue, rollback, or open follow-up work.

## When to Use

- Post-deploy smoke checks fail.
- Users report a regression.
- Monitoring, logs, or Sentry indicate errors.
- Deployment health is uncertain.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. If the current repository contains `.hermes/ADW.md`, read it before acting and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults.

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
