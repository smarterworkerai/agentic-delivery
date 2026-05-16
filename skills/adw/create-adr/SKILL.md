---
name: adw-create-adr
description: Use when an ADW change introduces or modifies architectural direction and needs an Architecture Decision Record.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, architecture, adr, documentation]
    related_skills: [adw-plan-feature, adw-do-impl]
---

# ADW Create ADR

## Overview

Use this skill when a delivery task changes architectural direction and needs a decision record.

## When to Use

- Introducing a new framework or major dependency.
- Changing deployment topology.
- Modifying authentication, persistence, or security boundaries.
- Introducing an external service.

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
