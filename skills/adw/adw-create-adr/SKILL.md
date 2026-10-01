---
name: adw-create-adr
description: >-
  Creates a reviewable Architecture Decision Record with context, options, decision, and consequences. Use for architectural, security-boundary, platform, or long-lived delivery decisions that need durable rationale.
license: MIT
compatibility: Requires git and the GitHub CLI. Deterministic steps require mise and an ADW task manifest.
metadata:
  suite: agentic-delivery
  version: "2.2.0"
  author: smarterworkerai
  requires: adw-core
  router-tokens: "create-adr"
  hermes-tags: "adw architecture adr documentation"
  hermes-related-skills: "adw-core adw-plan adw-do-impl"
  human-gate: "—"
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

Load `adw-core` first. Read the project adapter from `.adw/ADW.md`, or `.hermes/ADW.md` for an existing project, and load any adapter-declared context helper before resolving branch, validation, deployment, or administration defaults. Shared playbooks are named from the `adw-core` skill; this skill's own templates are under `assets/`.

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

## Guardrails

<!-- adw:guardrails:start -->
- Never fake or upgrade results; `skipped` and `unsupported` are not `passed`.
- Run no deterministic operation without a valid manifest; report `blocked` and do not improvise commands.
- Require explicit human approval for merge, production-class deploy, rollback, secrets, destructive changes, and history rewrites.
- Inference is never approval.
- Resolve missing parameters through `adw-core`: repository → adapter → context → ask.
- Report status, completed work, risks/blockers, and the next action.
<!-- adw:guardrails:end -->
