---
name: adw-do-impl
description: >-
  Implements an approved plan, runs manifest-declared minimal verification, and prepares a reviewable commit or pull request. Use when coding a planned ADW change directly in a repository with an ADW task manifest.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: adw-core
  router-tokens: "do-impl"
  hermes-tags: "adw implementation github pull-request"
  hermes-related-skills: "adw-core adw-plan adw-test-feature"
  human-gate: "Exact PR source and target route"
---
# ADW Do Implementation

## Overview

Use this skill to implement the current ADW plan directly in the repository.

## When to Use

- A feature or bugfix plan exists.
- The branch and issue are known or can be inferred safely.
- The user wants implementation by the current agent.

Use `adw-do-impl-delegate` when implementation should run through a selected delegation backend with a portable handoff/result contract.

## Required Context

Load `adw-core` first. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` for an existing project, and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults. Shared playbooks are named from the `adw-core` skill; this skill's own templates are under `assets/`.

## Workflow

1. Load the linked plan and GitHub issue.
2. Verify branch, working tree, and PR target.
3. Confirm no secrets or unrelated changes are present.
4. Implement only planned scope.
5. Run `mise run adw:check`, then `mise run adw:verify:minimal`; record task evidence and exact results. If the project manifest is absent, stop as blocked and offer the `adw-core` adapter generator. Do not substitute package-manager or inferred project commands.
6. Commit the validated changes with scoped messages.
7. Review the complete diff and report the proposed source branch, destination branch, replacement/deletion effect, and delivery route.
8. Push and open/update a PR with `assets/pull_request.md` only when that exact route is explicitly approved. Otherwise stop with a validated local commit ready for approval.
9. Report changed files, validation status, branch/commit/PR state, and remaining risks.

## Implementation Gate

Before PR creation, confirm:

- code compiles/builds where applicable, proven by `adw:verify:minimal` evidence
- obvious lint/type errors required by the manifest's minimal graph are handled
- implementation matches plan
- no unrelated changes were introduced
- secrets are not committed
- exact source branch, destination branch, replacement/deletion effect, and delivery route are explicitly approved

## Output

- Implementation summary
- Changed files summary
- Test/check results
- Branch
- Commit and PR URL, or the exact approval still required
- Remaining risks or limitations

## Common Pitfalls

1. Implementing opportunistic refactors outside the plan.
2. Pushing or opening a PR without exact route approval and test evidence.
3. Forgetting to link the issue in the PR body.
4. Claiming tests passed without exact command output.

## Verification Checklist

- [ ] Linked issue and plan were read
- [ ] Diff matches planned scope
- [ ] Tests/checks were run or blockers documented
- [ ] Push/PR route was explicitly approved, or work stopped at a validated local commit
- [ ] Any created PR links the issue
- [ ] Next step is `adw-test-feature`

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
