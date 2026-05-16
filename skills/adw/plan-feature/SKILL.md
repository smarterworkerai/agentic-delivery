---
name: adw-plan-feature
description: Use when planning a new feature through the Agentic Delivery Workflow. Creates or confirms plan, branch, issue, acceptance criteria, and traceability before implementation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, planning, feature, github]
    related_skills: [adw-do-impl, adw-test-feature]
---

# ADW Plan Feature

## Overview

Use this skill to start a new feature safely. It prepares the delivery artifacts that implementation depends on: branch, implementation plan, GitHub issue, acceptance criteria, risks, rollback notes, and traceability links.

## When to Use

- A user asks for a new feature.
- A feature idea needs to become implementable work.
- A branch or issue is missing before implementation.

Do not use for bug reports; use `adw-plan-bugfix` instead.

## Workflow

1. Inspect repository state: root, current branch, remotes, default branch, and working tree.
2. Determine or confirm base branch. Default to `main` when safe.
3. Create or confirm feature branch using `feature/<short-description>`.
4. Draft a plan from `templates/implementation_plan.md`.
5. Create a GitHub issue labeled `enhancement` using `templates/github_issue_feature.md`.
6. Link branch, issue, plan, and expected PR target.
7. Stop before implementation and report ready-for-implementation status.

## Required Plan Content

- goal
- scope and non-scope
- affected files/components
- implementation steps
- test strategy
- risks
- rollback considerations
- acceptance criteria
- branch and issue linkage

## Output

- Branch: `<feature/...>`
- Issue: `<GitHub issue URL>`
- Plan: attached to issue or committed plan artifact
- Acceptance criteria: listed
- Next: `adw-do-impl` or `adw-do-impl-delegate`

## Common Pitfalls

1. Starting implementation before issue/plan linkage exists.
2. Creating broad feature branches that mix unrelated work.
3. Treating inferred base branch as approved when multiple release branches exist.
4. Omitting rollback considerations because the feature seems small.

## Verification Checklist

- [ ] Branch exists and is isolated from unrelated work
- [ ] Issue exists and is labeled `enhancement`
- [ ] Plan includes acceptance criteria and test strategy
- [ ] Branch ↔ issue linkage is recorded
- [ ] Next skill is clearly identified


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
