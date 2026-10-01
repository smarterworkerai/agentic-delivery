# Rollback Report

## Target

- Environment: `<opaque manifest value>`
- Release target: `<adapter-declared target>`

## Failed State

- Source revision: `<failed immutable revision>`
- Artifact identity: `<failed immutable artifact identity or not applicable>`
- Deployment identity/status: `<failed deployment reference>`
- Evidence: `<non-sensitive symptoms, logs, health/readiness/E2E findings>`

## Fix-Forward Traceability

- Bug issue: <URL>
- Implementation branch/commit or patch artifact: <reference>
- PR/MR: <approved URL or pending approval>

## Approved Restore State

- Restore strategy: `<Git revert/restore | artifact selection | configuration restoration | adapter-defined combination>`
- Last-known-good source revision: `<immutable revision>`
- Last-known-good artifact identity: `<immutable identity or not applicable>`
- Prepared restore revision/configuration: `<reference>`

## Stateful Risk Review

<migrations, data, volumes, external services, deployment/configuration contract, and decisions>

## Recovery Evidence

- `adw:check` / `adw:describe`: <evidence>
- Configuration pull/plan/apply: <evidence>
- Deployment apply/status: <evidence>
- Restored runtime identity: <evidence>
- Health/readiness/E2E/deployment validation: <evidence or unsupported/blocker>

## User Impact

<impact summary>

## Follow-up

<remaining risks, root-cause work, owner, and next action>
