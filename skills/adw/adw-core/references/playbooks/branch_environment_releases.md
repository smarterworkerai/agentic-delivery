# Branch-Environment Release Playbook

## Purpose

Keep each long-lived branch as the source of truth for its matching environment. ADW does not use a separate artifact transfer workflow: merge or update the branch that owns the target environment, then deploy and validate that exact branch state.

## Branch to Environment Mapping

Read the mapping from the repository adapter and validate each environment against `.hermes/adw-task-manifest.json`. Generic ADW defines no branch or environment names. The invariant is that each deployed environment remains traceable to its adapter-declared owning Git branch and exact revision.

## Procedure

1. Identify the source branch/PR, destination branch, target environment, intended commit SHA, artifact identity, and validation evidence.
2. Confirm the destination branch and deployment consequence with the human before merge or deployment.
3. Merge or update the destination branch through `adw-merge-feature`; do not use a separate artifact transfer stage to bypass the branch/environment contract.
4. Wait for destination-branch artifact publication when applicable, then verify its immutable identity against the intended commit.
5. Apply target environment configuration through `adw:deploy:config:pull`, `adw:deploy:config:plan`, and the externally approved `adw:deploy:config:apply` task.
6. Deploy with `adw:deploy:apply` and inspect `adw:deploy:status` evidence for the explicit environment.
7. Verify with the manifest-supported `adw:health`, `adw:readiness`, `adw:e2e`, and `adw:validate-deployment` tasks.
8. Close or update linked issues according to `github_traceability.md`.
9. Record final status with branch, commit SHA, image/artifact identity, deployment target, validation evidence, and rollback notes.

## Rollback / Restore Procedure

Rollback preserves the same branch-to-environment invariant. Do not restore an environment only by moving a runtime pointer or redeploying an old artifact while the owning branch still points at the failed state.

1. Identify the failed environment, owning branch, failed SHA/deployment/artifact, and last known-good SHA.
2. Before changing the owning branch, preserve a fix-forward path for the failed state. If no equivalent issue/branch exists, create a bug issue and a bugfix branch from the failed branch head.
3. Assess stateful risk: migrations, persistent storage, credentials, external services, and runtime configuration differences between failed and good states.
4. Restore the owning branch to the last known-good tree. For long-lived branches, prefer an auditable restore commit over force-push unless the human explicitly approves history rewrite.
5. Wait for restored-branch artifact publication when applicable and verify its immutable identity against the restore commit.
6. Run the configuration pull/plan/apply tasks for the restored revision, then deploy with `adw:deploy:apply`.
7. Verify the rollback through deployment status, health, readiness, E2E, and deployment-validation task evidence.
8. Update the bug issue and rollback report with failed SHA, good SHA, restore commit, deployment evidence, and next fix-forward path.

## Prohibited Shortcuts

Do not claim cross-environment promotion by moving only a mutable artifact pointer or copying runtime state between environments. Each environment reflects its adapter-declared owning branch and exact revision.

Do not claim rollback completion by deploying an old artifact while the environment branch or provider-owned deployment configuration still describes the failed release. Require restored config plan/apply evidence.
