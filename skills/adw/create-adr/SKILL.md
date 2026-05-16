---
name: adw-create-adr
description: Use when an ADW change introduces or modifies architectural direction and needs an Architecture Decision Record.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, architecture, adr, documentation]
    related_skills: [adw-core, adw-plan-feature, adw-do-impl]
---

# ADW Create ADR

## Overview

Use this skill when a delivery task changes architectural direction and needs a decision record.

## When to Use

- Introducing a new framework or major dependency.
- Changing deployment topology.
- Modifying authentication, persistence, or security boundaries.
- Introducing an external service.

## Required Context

Load `adw-core` before using this skill. It contains the shared delivery gates, templates, playbooks, ADRs, and workflow diagram. Resolve shared artifacts from the `adw-core` skill package, not from repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` directories.

## Workflow

1. Identify the decision and why it is needed now.
2. Capture context, considered options, decision, and consequences.
3. Create `adr/NNNN-short-title.md`.
4. Link the ADR from issue/PR.
5. Ensure implementation follows the accepted decision.

## Output

- ADR file path
- Status
- Decision summary
- Links to issue/PR

## Common Pitfalls

1. Writing implementation notes instead of a decision record.
2. Omitting rejected alternatives.
3. Creating ADRs for trivial code organization details.

## Verification Checklist

- [ ] ADR has status, context, decision, consequences
- [ ] ADR is linked from delivery artifacts
- [ ] Decision affects architecture, not just local code style


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
