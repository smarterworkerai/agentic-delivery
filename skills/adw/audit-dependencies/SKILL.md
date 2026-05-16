---
name: adw-audit-dependencies
description: Use when auditing ADW dependency, build, or tooling changes for security and maintenance risk before implementation, validation, or release.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [adw, dependencies, security, audit]
    related_skills: [adw-plan-feature, adw-test-feature]
---

# ADW Audit Dependencies

## Overview

Use this skill to assess dependency and build-tool risk.

## When to Use

- Dependency updates are requested.
- CVEs are reported.
- Build tooling changes.
- Production security posture is under review.

## Workflow

1. Inventory affected dependency files and package managers.
2. Identify direct and transitive risk where tooling supports it.
3. Check licenses, maintenance status, and breaking-change notes when relevant.
4. Recommend update, pin, replacement, or no-action.
5. Attach audit result to issue/PR/validation report.

## Output

- Dependency scope
- Risk findings
- Recommended action
- Required tests/checks

## Common Pitfalls

1. Treating version bump as risk-free.
2. Ignoring runtime image/package dependencies.
3. Reporting vulnerabilities without exploitability or scope.

## Verification Checklist

- [ ] Dependency files inspected
- [ ] CVE/security findings summarized without secrets
- [ ] Required tests/checks are identified
- [ ] Recommendation is actionable


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
