---
name: adw-self-improve
description: >-
  Persists an explicitly requested workflow improvement in the correct ADW, context, or project layer through a reviewable pull request. Use when the user asks the delivery system to learn, improve, or codify a recurring lesson.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: adw-core
  router-tokens: "self-improve"
  hermes-tags: "adw self-improvement skill-maintenance context confirmation"
  hermes-related-skills: "adw-core adw-plan adw-do-impl adw-test-feature"
  human-gate: "Confirm the improvement proposal"
---
# ADW Self Improve

## Overview

Use this skill when a human explicitly asks ADW to remember, persist, or improve a delivery workflow rule, project context rule, template, validator, or project adapter. The skill is a confirm-first intake router: infer the durable correction, classify the right persistence layer, propose a safe change plan, and only then perform PR-based source-of-truth updates.

This skill is generic. It must not hard-code organization, repository, or project facts. Generic ADW receives reusable workflow mechanics; context helpers receive organization or environment policy; project adapters receive concrete repository/runtime facts.

## When to Use

Use this skill when the user says things like:

- "ADW should remember this rule";
- "make this workflow better next time";
- "persist this into the ADW/context/project adapter";
- "add this as a validator/template/pitfall";
- "self-improve the delivery workflow based on this finding".

Do not use this skill for:

- ordinary implementation work;
- one-off task progress or stale session outcomes;
- secrets or credentials;
- unverified mutable runtime facts;
- immediate live skill edits without a source-of-truth plan and explicit confirmation.

## Required Context

Load `adw-core` first. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` for an existing project, and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults. Shared playbooks are named from the `adw-core` skill; this skill's own templates are under `assets/`.

## Persistence Layers

Classify every proposed improvement into one or more of these layers:

1. **Generic ADW** — reusable workflow mechanics, gates, report formats, skill routing, plugin behavior, or package validators.
2. **Context helper** — organization, team, user, or environment policy that applies across compatible repositories.
3. **Project adapter** — concrete repository files, services, domains, deployment targets, tests, sidecars, and project-specific pitfalls.
4. **Live installed skill update** — optional temporary runtime update after source-of-truth scope is known; must report divergence risk.
5. **Memory-only** — rare; only durable user preference or environment fact that does not belong in a skill, context helper, project adapter, or repository document.
6. **Reject** — secrets, transient task progress, unverified facts, or stale outcomes.

## Workflow

1. Restate the improvement in durable, non-secret terms.
2. Inspect relevant source files, adapters, context helpers, and current repository state.
3. Classify the target layer(s), including rejected layers and why.
4. Produce a plan-only proposal with target repositories/files, validation commands, secret risk, and whether live installed skills should be updated.
5. Stop and wait for human confirmation before editing files, memory, live skills, branches, or PRs.
6. After approval, create/update a branch in the correct source-of-truth repository.
7. Make the smallest durable change that enforces the improvement.
8. Add or update validators/templates/tests where practical.
9. Run validation and record exact command output.
10. Commit the validated change. Push and open/update a PR only after explicit approval of the exact source branch, destination branch, and replacement/deletion effect; otherwise stop with the local commit ready for review.
11. If live skills were updated, report how to reconcile them with the PR merge.

## Proposal Format

```markdown
### ADW Self-Improvement Proposal

Improvement: <durable restatement>

### Layer Classification
- Generic ADW: <yes/no + reason>
- Context helper: <yes/no + reason>
- Project adapter: <yes/no + reason>
- Live installed skill update: <yes/no + divergence risk>
- Memory-only: <yes/no + reason>
- Rejected targets: <why>

### Planned Source-of-Truth Changes
- Repository/file: <path>
- Validation: <commands>

### Secret / Safety Review
- Secret risk: <none|possible + mitigation>
- Side effects before approval: none

Approve this plan before I persist anything.
```

## Confirmation Gate

Do not perform any persistent side effect before approval:

- no file writes;
- no branch creation;
- no commits;
- no PRs;
- no memory writes;
- no live installed skill edits;
- no deployment or merge actions.

If the requested improvement is clearly a secret, unsafe credential, or transient task result, reject it and explain the safe alternative.

## Output

- Proposal with layer classification and rejected layers.
- After approval: PR URL, changed files, validation results, and any live/source divergence.
- Clear statement of what future ADW run will do differently.

## Common Pitfalls

1. Writing to memory when the improvement belongs in a skill, context helper, project adapter, or validator.
2. Putting project-specific runtime facts into generic ADW skills.
3. Putting organization policy into a project adapter when it should be shared by a context helper.
4. Persisting unverified mutable facts as durable truth.
5. Updating live installed skills without a PR-backed source of truth and reconciliation plan.
6. Treating user correction as permission for immediate side effects; this skill still requires a proposal first.

## Verification Checklist

- [ ] `adw-core` was loaded first.
- [ ] The improvement was restated without secrets or transient task state.
- [ ] Target layer classification is explicit.
- [ ] Rejected layers are listed with reasons.
- [ ] No side effects occurred before confirmation.
- [ ] Source-of-truth changes were committed; push/PR used an explicitly approved exact route or remains pending approval.
- [ ] Validation commands were run or blockers documented.
- [ ] Any optional live skill update reports divergence and reconciliation.

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
