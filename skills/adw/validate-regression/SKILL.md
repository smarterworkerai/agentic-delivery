---
name: adw-validate-regression
description: Use when running targeted or broad regression validation against an ADW PR, branch, deployment, or release candidate.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, testing, regression, validation]
    related_skills: [adw-core, adw-test-feature]
---

# ADW Validate Regression

## Overview

Use this skill to run regression checks beyond the basic PR validation flow.

## When to Use

- A change touches critical behavior.
- A bugfix needs regression proof.
- A release candidate needs broader smoke/API/E2E validation.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. If the current repository contains `.hermes/ADW.md`, read it before acting and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults.

## Workflow

1. Identify validation target: PR, branch, deployment URL, or artifact.
2. Select checks based on risk: unit, integration, E2E, API contract, visual, performance baseline.
3. Run exact commands or manual steps. For persistent services, include write-path validation when deployment/runtime behavior is in scope.
4. Capture evidence, artifact identity, runtime environment, and failures.
5. Report pass/fail with remediation recommendations using `adw-core/references/playbooks/github_traceability.md` for file-backed Markdown when posting to GitHub.

## Output

- Target under test
- Artifact/deployment identity when runtime validation is in scope
- Check list and command evidence
- Write-path evidence for persistent services, or a documented blocker/waiver
- Pass/fail result
- Risks and recommended next action

## Common Pitfalls

1. Running generic tests that do not cover the changed behavior.
2. Hiding flaky or inconclusive results.
3. Forgetting to document environment and artifact identity.
4. Treating liveness or HTTP 200 checks as enough for database/filesystem-backed services.
5. Posting multiline validation results with visible backslash-n escape sequences.

## Verification Checklist

- [ ] Target identity recorded
- [ ] Checks are risk-based
- [ ] Runtime/artifact identity recorded when applicable
- [ ] Persistent write-path checks run or blocker/waiver documented
- [ ] Evidence is concrete
- [ ] Failures produce a bugfix or remediation path
- [ ] GitHub-facing reports use readable Markdown with real line breaks


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
