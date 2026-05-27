---
name: adw-do-impl-delegate
description: Use when delegating ADW implementation to a sandboxed or remote agent. Prepares a complete handoff, receives a PR, reviews it, and reports acceptance or remediation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, delegation, implementation, review]
    related_skills: [adw-core, adw-do-impl, adw-test-feature]
---

# ADW Do Implementation Delegate

## Overview

Use this skill when implementation should be delegated to a remote or sandboxed agent while preserving ADW traceability and review gates.

## When to Use

- Work is complex enough to benefit from an isolated worker.
- The user explicitly requests delegation.
- A sandbox/launcher flow is required.

## Delegation Packet

Include:

- repository URL and branch
- base branch and target PR branch
- linked issue and plan
- exact scope and non-scope
- tests/checks to run
- secrets policy
- expected deliverable: PR URL and summary
- instruction to avoid merge/deploy

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories. If the current repository contains `.hermes/ADW.md`, read it before acting and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults.

## Workflow

1. Prepare delegation context from issue, plan, branch, and repo state.
2. Launch the approved sandbox/remote agent flow.
3. Receive result with verifiable artifact: PR URL, commit SHA, test output.
4. Inspect the PR diff and test evidence.
5. Perform an implicit review against plan and repository hygiene.
6. Comment on the PR with acceptance/rejection and remediation notes.
7. Report outcome to the human.

## Output

- Delegated task summary
- PR link
- Review comment or review summary
- Acceptance/rejection status
- Required remediation, if any

## Common Pitfalls

1. Sending vague delegation context.
2. Accepting a self-reported success without inspecting the PR.
3. Bypassing the sandbox/launcher flow.
4. Forgetting to return weak results for correction instead of hiding them.

## Verification Checklist

- [ ] Delegation packet includes issue, plan, branch, tests, and non-scope
- [ ] Worker returned PR URL and commit SHA
- [ ] PR diff was reviewed
- [ ] Review result was posted or summarized
- [ ] No merge/deploy happened during delegation


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
