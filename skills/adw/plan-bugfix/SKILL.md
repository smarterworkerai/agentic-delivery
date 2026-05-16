---
name: adw-plan-bugfix
description: Use when planning a bugfix through the Agentic Delivery Workflow. Captures symptoms, suspected root cause, branch, issue, verification strategy, and rollback considerations.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, planning, bugfix, github]
    related_skills: [adw-do-impl, adw-test-feature]
---

# ADW Plan Bugfix

## Overview

Use this skill to convert a bug report or failed validation into a traceable bugfix plan.

## When to Use

- A user reports a defect or regression.
- Monitoring, logs, or validation indicate broken behavior.
- A PR or deployment needs a scoped fix plan.

## Workflow

1. Reproduce or document the symptom as far as possible.
2. Inspect current branch, target branch, recent commits, logs, tests, and related issues.
3. Identify suspected root cause and confidence level.
4. Create or confirm `bugfix/<short-description>` branch.
5. Draft a bugfix plan from `templates/bugfix_plan.md`.
6. Create a GitHub issue labeled `bug` using `templates/github_issue_bugfix.md`.
7. Attach repro notes, expected/actual behavior, and verification strategy.

## Required Bugfix Plan Content

- symptom summary
- reproduction steps or evidence
- suspected root cause
- affected components
- proposed fix scope
- regression tests
- rollback/safety considerations
- acceptance criteria

## Output

- Branch: `<bugfix/...>`
- Issue: `<GitHub issue URL>`
- Suspected root cause: `<summary>`
- Verification strategy: `<tests/smokes>`
- Next: `adw-do-impl` or `adw-do-impl-delegate`

## Common Pitfalls

1. Fixing symptoms without capturing reproduction evidence.
2. Expanding a bugfix into unrelated cleanup.
3. Failing to add regression verification.
4. Guessing production impact without checking logs or deployment metadata.

## Verification Checklist

- [ ] Bug issue exists and is labeled `bug`
- [ ] Repro/evidence is documented or blocker is explicit
- [ ] Suspected root cause is stated with confidence
- [ ] Regression strategy is defined
- [ ] Scope is tight and safe


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
