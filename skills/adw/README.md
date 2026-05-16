# ADW Hermes Skills

This directory contains Hermes-compatible skills for the Agentic Delivery Workflow (ADW).

The skills are intentionally packaged together under `skills/adw/` because they form one PR-centric delivery pipeline:

```text
Plan → Branch → Issue → Implementation → PR → Review → Preview → Validation → Merge → Deployment
```

## Package Source of Truth

`adw-core` is the source of truth for shared installable artifacts. Shared playbooks, templates, ADRs, and diagrams live inside the `adw-core` skill directory so they travel with the skillset when installed into another Hermes profile.

Do not create repo-root shared artifact directories for new ADW materials. Add or update shared content under:

- `adw-core/references/playbooks/`
- `adw-core/templates/`
- `adw-core/references/adr/`
- `adw-core/assets/diagrams/`

## Skill Index

- `adw-core` — shared gates, playbooks, templates, ADRs, and diagrams. Load before any other ADW skill.
- `adw-plan-feature` — plan a new feature and create traceability artifacts.
- `adw-plan-bugfix` — plan a bugfix from symptoms and suspected root cause.
- `adw-do-impl` — implement a planned change directly and open a PR.
- `adw-do-impl-delegate` — delegate implementation to a sandboxed/remote agent and review the returned PR.
- `adw-test-feature` — review, preview deploy, and validate a PR before merge.
- `adw-merge-feature` — merge a validated PR and deploy the destination branch.
- `adw-rollback-deployment` — roll back a failed deployment and create follow-up work.
- `adw-promote-release` — promote a validated artifact across environments.
- `adw-validate-regression` — run targeted/broad regression validation.
- `adw-create-adr` — create architecture decision records.
- `adw-audit-dependencies` — audit dependency/build-tool risk.
- `adw-analyze-production` — inspect production feedback and route incidents.

## Usage

Always load `adw-core` with the operational skill:

```text
Use adw-core and adw-plan-feature for <feature>.
Use adw-core and adw-do-impl for <linked issue>.
Use adw-core and adw-test-feature for <PR>.
```
