---
name: adw-validate-regression
description: Use when running targeted or broad regression validation against an ADW PR, branch, deployment, or release candidate.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, testing, regression, validation]
    related_skills: [adw-test-feature]
---

# ADW Validate Regression

## Overview

Use this skill to run regression checks beyond the basic PR validation flow.

## When to Use

- A change touches critical behavior.
- A bugfix needs regression proof.
- A release candidate needs broader smoke/API/E2E validation.

## Workflow

1. Identify validation target: PR, branch, deployment URL, or artifact.
2. Select checks based on risk: unit, integration, E2E, API contract, visual, performance baseline.
3. Run exact commands or manual steps.
4. Capture evidence and failures.
5. Report pass/fail with remediation recommendations.

## Output

- Target under test
- Check list and command evidence
- Pass/fail result
- Risks and recommended next action

## Common Pitfalls

1. Running generic tests that do not cover the changed behavior.
2. Hiding flaky or inconclusive results.
3. Forgetting to document environment and artifact identity.

## Verification Checklist

- [ ] Target identity recorded
- [ ] Checks are risk-based
- [ ] Evidence is concrete
- [ ] Failures produce a bugfix or remediation path


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
