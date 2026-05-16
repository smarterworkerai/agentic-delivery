---
name: adw-test-feature
description: Use when validating an ADW PR through review, preview deployment, smoke or E2E checks, and go/no-go reporting before merge.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, review, preview, validation]
    related_skills: [adw-do-impl, adw-merge-feature, adw-validate-regression]
---

# ADW Test Feature

## Overview

Use this skill after a PR exists and before merge. It enforces review and preview gates.

## When to Use

- A feature or bugfix PR needs validation.
- Preview deployment is required before merge.
- The PR review status is unknown.

## Workflow

1. Inspect PR state, branch, target branch, linked issue, and checks.
2. Check whether a review already exists.
3. Review the PR if needed using `playbooks/pr_reviewing.md`.
4. Stop if rejected.
5. Deploy feature branch to preview when supported using `playbooks/preview_deployments.md`.
6. Run smoke/E2E/regression checks; invoke `adw-validate-regression` if deeper coverage is needed.
7. Write validation report using `templates/validation_report.md`.
8. Report go/no-go recommendation.

## Review Gate

Do not deploy or merge a rejected PR. Missing review must be resolved before preview validation proceeds unless the user explicitly defines a safe exception.

## Preview Gate

Preview branch deployments are for validation only. Do not use preview as production approval.

## Output

- PR review status
- Preview URL or reason preview is not applicable
- Test result
- Manual QA notes if applicable
- Go/no-go recommendation

## Common Pitfalls

1. Treating green CI as a human/code review.
2. Deploying rejected work to preview.
3. Reporting HTTP 200 as success without validating response semantics.
4. Skipping manual QA notes for user-visible changes.

## Verification Checklist

- [ ] PR state and checks inspected
- [ ] Review status known
- [ ] Rejection blocks further workflow
- [ ] Preview URL and deployment status recorded when applicable
- [ ] Smoke/E2E/manual validation result documented


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
