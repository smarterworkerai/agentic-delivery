---
name: adw-plan-feature
description: Use when planning a new feature through the Agentic Delivery Workflow. Creates or confirms plan, branch, issue, acceptance criteria, and traceability before implementation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, planning, feature, github]
    related_skills: [adw-core, adw-do-impl, adw-test-feature]
---

# ADW Plan Feature

## Overview

Use this skill to start a new feature safely. It prepares the delivery artifacts that implementation depends on: branch, implementation plan, GitHub issue, acceptance criteria, risks, rollback notes, and traceability links.

## When to Use

- A user asks for a new feature.
- A feature idea needs to become implementable work.
- A branch or issue is missing before implementation.

Do not use for bug reports; use `adw-plan-bugfix` instead.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories.

## Workflow

1. Inspect repository state: root, current branch, remotes, default branch, and working tree.
2. Determine or confirm base branch. Default to `main` when safe.
3. Create or confirm feature branch using `feature/<short-description>`.
4. Draft a plan from `adw-core/templates/implementation_plan.md`.
5. Create a GitHub issue labeled `enhancement` using `adw-core/templates/github_issue_feature.md`.
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
