# ADW Hermes Skills

This directory contains Hermes-compatible skills for the Agentic Delivery Workflow (ADW).

The skills are intentionally packaged together under `skills/adw/` because they form one PR-centric delivery pipeline:

```text
Plan → Branch → Issue → Implementation → PR → Review → Preview → Validation → Merge → Deployment
```

Shared playbooks and templates are kept as repository-level artifacts instead of being duplicated into each skill directory.

## Skill Index

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

## Shared Artifacts

- `SOUL.md`
- `playbooks/`
- `templates/`
- `adr/`
- `docs/diagrams/`

Do not duplicate shared templates/playbooks into individual skills unless a future distribution target requires standalone skill bundles.
