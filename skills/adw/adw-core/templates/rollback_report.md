# Rollback Report

## Environment

<environment and owning branch>

## Failed State

- Branch head: <failed branch SHA>
- Artifact/image: <failed artifact/image identity>
- Deployment: <failed deployment ID/status>
- Evidence: <non-sensitive symptoms, logs, endpoint or E2E failures>

## Bugfix Tracking

- Bug issue: <issue URL or ID>
- Bugfix branch: <branch created from failed state, or existing linked branch>

## Restored State

- Last known-good SHA/tree: <good SHA>
- Restore commit: <rollback/restore commit SHA>
- Artifact/image after restore: <restored artifact/image identity>

## Stateful Risk Review

<migrations, data, volumes, external services, compose/env contract, and decisions>

## Deployment Recovery

<Dokploy/raw compose/env sync, deployment ID/status, domain/route checked>

## Verification

<checks run: status, endpoint semantics, logs or compensated evidence, revision parity, smoke/E2E/regression>

## Impact

<user/system impact and recovery status>

## Follow-up

<fix-forward plan, bug issue status, owner/next action>
