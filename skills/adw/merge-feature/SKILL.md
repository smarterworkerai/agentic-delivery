---
name: adw-merge-feature
description: Use when merging a validated ADW PR into a destination branch and deploying the resulting branch only after review, preview, and merge gates are satisfied.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, merge, deployment, release]
    related_skills: [adw-test-feature, adw-promote-release, adw-analyze-production]
---

# ADW Merge Feature

## Overview

Use this skill to merge a validated PR and deploy the destination branch.

## When to Use

- A PR passed review and preview validation.
- The human explicitly requests merge/deploy.
- The destination branch and deployment target are known.

## Workflow

1. Inspect PR state, checks, review status, linked issue, and validation report.
2. Confirm destination branch and deployment consequence with the human.
3. Stop if PR is rejected, checks are unresolved, or target is ambiguous.
4. Merge PR using the repository's merge policy.
5. Verify destination branch SHA.
6. Deploy the destination branch using `playbooks/deployment_gates.md`.
7. Verify deployment status, logs, endpoint, and rollback path.
8. Close or update linked issue if appropriate.
9. Report final delivery status.

## Merge Gate

Before merge, confirm:

- destination branch is correct
- PR is not rejected
- required checks passed or failures are explicitly accepted
- preview validation is complete when applicable
- deployment consequences are understood

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
- [ ] Merge completed and destination SHA is recorded
- [ ] Deployment status verified
- [ ] Rollback path is documented


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
