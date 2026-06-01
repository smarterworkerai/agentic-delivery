---
name: adw-test-feature
description: Use when validating an ADW PR through review, preview deployment, smoke or E2E checks, and go/no-go reporting before merge.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, review, preview, validation]
    related_skills: [adw-core, adw-do-impl, adw-merge-feature, adw-validate-regression]
---

# ADW Test Feature

## Overview

Use this skill after a PR exists and before merge. It enforces review and preview gates.

## When to Use

- A feature or bugfix PR needs validation.
- Preview deployment is required before merge.
- The PR review status is unknown.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. If the current repository contains `.hermes/ADW.md`, read it before acting and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults.

## Workflow

1. Inspect PR state, branch, target branch, linked issue, and checks.
2. Check whether a review already exists.
3. Review the PR if needed using `adw-core/references/playbooks/pr_reviewing.md`.
4. Stop if rejected.
5. Deploy feature branch to preview when supported using `adw-core/references/playbooks/preview_deployments.md`.
6. Run smoke/E2E/regression checks; invoke `adw-validate-regression` if deeper coverage is needed. For persistent services, include a write-path smoke or document why it is blocked/unavailable.
7. Write validation report using `adw-core/templates/validation_report.md` and the Markdown/newline hygiene rules from `adw-core/references/playbooks/github_traceability.md`.
8. Report go/no-go recommendation.

## Review Gate

Do not deploy or merge a rejected PR. Missing review must be resolved before preview validation proceeds unless the user explicitly defines a safe exception.

## Preview Gate

Preview branch deployments are for validation only. Do not use preview as production approval.

## Output

- PR review status
- Preview URL or reason preview is not applicable
- Artifact identity and runtime revision/digest parity when preview is deployed
- Test result
- Write-path smoke result for persistent services, or documented blocker/waiver
- Manual QA notes if applicable
- Go/no-go recommendation

## Common Pitfalls

1. Treating green CI as a human/code review.
2. Deploying rejected work to preview.
3. Reporting HTTP 200 as success without validating response semantics.
4. Skipping manual QA notes for user-visible changes.
5. Redeploying a stale preview image because a newly added workflow is not yet visible on the default branch.
6. Posting structured PR comments with visible backslash-n escape sequences instead of real Markdown line breaks.

## Verification Checklist

- [ ] PR state and checks inspected
- [ ] Review status known
- [ ] Rejection blocks further workflow
- [ ] Preview URL and deployment status recorded when applicable
- [ ] Artifact identity and runtime revision/digest parity recorded when applicable
- [ ] Smoke/E2E/manual validation result documented, including write-path checks for persistent services
- [ ] Validation report/comment follows GitHub traceability Markdown hygiene


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
