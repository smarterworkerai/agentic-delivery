# Release Target Playbook

## Purpose

Deliver an approved revision to an adapter-declared environment without imposing a generic branch, artifact, or provider topology.

## Target Resolution

Read the destination branch, release target, and opaque environment value from the repository adapter and `.hermes/adw-task-manifest.json`. A project may map long-lived branches to environments, promote immutable artifacts, or use another reviewable strategy. Generic ADW defines none of those names or mappings.

## Procedure

1. Identify the source PR/revision, destination branch when applicable, target environment, intended commit, and validation evidence.
2. Confirm the destination and deployment consequence with the human before merge or deployment.
3. Complete the repository's reviewed integration or promotion policy; do not bypass branch protection or artifact provenance.
4. Verify the deployable artifact or revision has immutable identity tied to the intended commit when applicable.
5. Run `adw:check` and `adw:describe`, then use `adw:deploy:config:pull`, `adw:deploy:config:plan`, and externally approved `adw:deploy:config:apply` for the explicit environment.
6. Deploy with `adw:deploy:apply` and inspect `adw:deploy:status` evidence.
7. Verify with the manifest-supported `adw:health`, `adw:readiness`, and `adw:validate-deployment` tasks. Optional E2E suites require separate per-run authorization and never gate promotion merely by their absence.
8. Close or update linked issues according to `github_traceability.md`.
9. Record the integrated revision, immutable artifact identity when applicable, deployment target, canonical task evidence, and rollback notes.

## Rollback

The adapter defines the rollback strategy and source of truth. It may require an auditable Git restore/revert, immutable artifact selection, configuration restoration, or a combination. Preserve the failed state and require explicit approval before any high-impact change.

After preparing the approved last-known-good state:

1. run the configuration pull/plan/apply tasks for the restored state;
2. deploy through `adw:deploy:apply`;
3. verify status, health, readiness, E2E, deployment validation, and intended revision identity;
4. update the incident/bug issue and rollback report with failed and restored identities.

## Prohibited Shortcuts

- Do not infer branch/environment mappings.
- Do not move only a mutable artifact pointer and call that verified promotion or rollback.
- Do not bypass manifest-declared configuration tasks.
- Do not report completion until source, configuration, deployment, and runtime evidence agree.
