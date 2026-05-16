---
name: adw-do-impl
description: Use when implementing an approved ADW plan directly. Loads the linked issue and plan, changes only planned scope, runs checks, commits, and opens a PR.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, implementation, github, pull-request]
    related_skills: [adw-plan-feature, adw-plan-bugfix, adw-test-feature]
---

# ADW Do Implementation

## Overview

Use this skill to implement the current ADW plan directly in the repository.

## When to Use

- A feature or bugfix plan exists.
- The branch and issue are known or can be inferred safely.
- The user wants implementation by the current agent.

Use `adw-do-impl-delegate` when implementation should run in a sandbox or remote agent.

## Workflow

1. Load the linked plan and GitHub issue.
2. Verify branch, working tree, and PR target.
3. Confirm no secrets or unrelated changes are present.
4. Implement only planned scope.
5. Run relevant tests/checks and record exact commands/results.
6. Commit changes with scoped messages.
7. Open a PR using `templates/pull_request.md`.
8. Report changed files, validation status, PR link, and remaining risks.

## Implementation Gate

Before PR creation, confirm:

- code compiles/builds where applicable
- obvious lint/type errors are handled
- implementation matches plan
- no unrelated changes were introduced
- secrets are not committed

## Output

- Implementation summary
- Changed files summary
- Test/check results
- Branch
- PR URL
- Remaining risks or limitations

## Common Pitfalls

1. Implementing opportunistic refactors outside the plan.
2. Opening a PR without test evidence.
3. Forgetting to link the issue in the PR body.
4. Claiming tests passed without exact command output.

## Verification Checklist

- [ ] Linked issue and plan were read
- [ ] Diff matches planned scope
- [ ] Tests/checks were run or blockers documented
- [ ] PR exists and links the issue
- [ ] Next step is `adw-test-feature`


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
