---
name: adw-promote-release
description: Use when promoting a validated artifact across ADW environments such as preview to demo or demo to production while preserving artifact identity and release gates.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, promotion, release, deployment]
    related_skills: [adw-test-feature, adw-merge-feature]
---

# ADW Promote Release

## Overview

Use this skill to promote the same tested artifact across environments.

## When to Use

- A tested version should move from preview to demo or production.
- The same commit/image/artifact must be preserved across environments.
- Promotion needs a controlled gate and report.

## Workflow

1. Identify source environment, target environment, artifact identity, and validation evidence.
2. Confirm promotion target and impact with the human.
3. Verify artifact identity is immutable or traceable.
4. Apply environment-specific configuration without changing the artifact.
5. Deploy target environment.
6. Verify target environment using `playbooks/deployment_gates.md`.
7. Report promotion result using `templates/deployment_report.md`.

## Output

- Source and target environments
- Artifact identity: commit/image/tag
- Deployment status
- Validation evidence
- Rollback path

## Common Pitfalls

1. Rebuilding instead of promoting the validated artifact.
2. Confusing branch promotion with artifact promotion.
3. Skipping target environment config audit.
4. Claiming promotion before deployment verification.

## Verification Checklist

- [ ] Artifact identity is recorded
- [ ] Human approved target environment
- [ ] Target deployment verified
- [ ] Rollback path known


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
