---
name: adw-plan
description: >-
  Plans a feature or bugfix as a reviewable delivery unit with branch, issue, acceptance criteria, verification, and rollback notes. Use when scoping a new capability, investigating a defect, or preparing non-trivial ADW work.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: adw-core
  router-tokens: "plan-feature plan-bugfix"
  router-presets: "plan-feature=feature plan-bugfix=bugfix"
  hermes-tags: "adw planning feature bugfix github"
  hermes-related-skills: "adw-core adw-do-impl adw-test-feature"
  human-gate: "Plan approval when repository policy requires it"
---
# ADW Plan

## Overview

Use this skill to start a new feature safely. It prepares the delivery artifacts that implementation depends on: branch, implementation plan, GitHub issue, acceptance criteria, risks, rollback notes, and traceability links.

## When to Use

- A user asks for a new feature.
- A feature idea needs to become implementable work.
- A branch or issue is missing before implementation.

Classify the request as `feature` or `bugfix`; do not erase bugfix reproduction and regression requirements.

## Required Context

Load `adw-core` first. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` for an existing project, and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults. Shared playbooks are named from the `adw-core` skill; this skill's own templates are under `assets/`.

## Workflow

1. Inspect repository state: root, current branch, remotes, default branch, and working tree.
2. Determine or confirm the base branch from repository metadata and the project adapter; do not assume a branch name.
3. Create or confirm an adapter-compatible descriptive implementation branch; do not invent a prefix absent from repository policy.
4. For a feature, draft `assets/implementation_plan.md`; for a bugfix, reproduce or document the symptom, record root-cause confidence, and draft `assets/bugfix_plan.md`.
5. Read `references/github_traceability.md` from the `adw-core` skill, especially Markdown and Newline Hygiene, before creating or updating GitHub issue text.
6. Create an `enhancement` issue from `assets/github_issue_feature.md` or a `bug` issue from `assets/github_issue_bugfix.md`; prefer a Markdown body file and verify the posted issue renders without visible literal `\n` sequences.
7. Link branch, issue, plan, and expected PR target.
8. Stop before implementation and report ready-for-implementation status.

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

## Bugfix-specific content

For `type=bugfix`, include reproduction steps or evidence, expected and actual behavior, suspected root cause with confidence, affected components, tight fix scope, regression tests, safety/rollback considerations, and acceptance criteria. If the symptom cannot be reproduced, record the blocker rather than presenting a guess as fact.

## Output

- Branch: `<adapter-compatible implementation branch>`
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
- [ ] Issue body was posted from a Markdown body file or otherwise verified to render without visible literal `\n` sequences
- [ ] Plan includes acceptance criteria and test strategy
- [ ] Branch ↔ issue linkage is recorded
- [ ] Next skill is clearly identified

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
