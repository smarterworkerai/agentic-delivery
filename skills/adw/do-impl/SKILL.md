---
name: adw-do-impl
description: Use when implementing an approved ADW plan directly.
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, implementation, github, pull-request]
    related_skills: [adw-core, adw-plan-feature, adw-plan-bugfix, adw-test-feature]
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

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. If the current repository contains `.hermes/ADW.md`, read it before acting and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults.

## Workflow

1. Load the linked plan and GitHub issue.
2. Verify branch, working tree, and PR target.
3. Confirm no secrets or unrelated changes are present.
4. Implement only planned scope.
5. Run `mise run adw:check`, then `mise run adw:verify:minimal`; record task evidence and exact results. If the project manifest is absent, stop as blocked and offer the `adw-core` adapter generator. Do not substitute package-manager or inferred project commands.
6. Commit the validated changes with scoped messages.
7. Review the complete diff and report the proposed source branch, destination branch, replacement/deletion effect, and delivery route.
8. Push and open/update a PR with `adw-core/templates/pull_request.md` only when that exact route is explicitly approved. Otherwise stop with a validated local commit ready for approval.
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


## ADW Shared Operating Contract

All ADW skills belong to one pipeline and share installable supporting material through `adw-core`.

Shared artifacts are package-owned by `adw-core`:

- Root `SOUL.md` — identity, tone, hard boundaries, and assumption policy for profiles that adopt ADW.
- `adw-core/references/playbooks/` — reusable operational procedures.
- `adw-core/templates/` — canonical issue, PR, report, and plan formats.
- `adw-core/references/adr/` — architecture decisions for the workflow itself.
- `adw-core/assets/diagrams/` — reviewable PlantUML workflow source.

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
