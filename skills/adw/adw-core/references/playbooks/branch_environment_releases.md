# Branch-Environment Release Playbook

## Purpose

Keep each long-lived branch as the source of truth for its matching environment. ADW does not use a separate artifact transfer workflow: merge or update the branch that owns the target environment, then deploy and validate that exact branch state.

## Branch to Environment Mapping

- Feature/bugfix branches -> preview only when explicitly selected for review.
- `demo` -> demo environment.
- `main` -> production environment.

Project adapters may add repository-specific branch names or release lines, but they must keep the same invariant: the deployed environment must be traceable to the Git branch that owns it.

## Procedure

1. Identify the source branch/PR, destination branch, target environment, intended commit SHA, image tags, and validation evidence.
2. Confirm the destination branch and deployment consequence with the human before merge or deployment.
3. Merge or update the destination branch through `adw-merge-feature`; do not use a separate artifact transfer stage to bypass the branch/environment contract.
4. Wait for the destination branch CI/image publication to complete, then verify mutable environment tags and immutable `sha-<short-sha>` tags point to the intended commit.
5. Apply target environment configuration before deployment. For Dokploy, update raw compose and environment variables/settings for the target environment while preserving live secrets.
6. Deploy the target environment that corresponds to the destination branch.
7. Verify deployment status, artifact/revision parity, endpoint semantics, logs, TLS/domains, rollback path, and target-environment smoke/E2E/regression checks.
8. Close or update linked issues according to `github_traceability.md`.
9. Record final status with branch, commit SHA, image/artifact identity, deployment target, validation evidence, and rollback notes.

## Rollback / Restore Procedure

Rollback preserves the same branch-to-environment invariant. Do not restore an environment only by moving a runtime tag or redeploying an old image while the owning branch still points at the failed state.

1. Identify the failed environment, owning branch, failed SHA/deployment/image, and last known-good SHA.
2. Before changing the owning branch, preserve a fix-forward path for the failed state. If no equivalent issue/branch exists, create a bug issue and a bugfix branch from the failed branch head.
3. Assess stateful risk: migrations, persistent volumes, credentials, external services, and compose/env contract differences between failed and good states.
4. Restore the owning branch to the last known-good tree. For long-lived branches, prefer an auditable restore commit over force-push unless the human explicitly approves history rewrite.
5. Wait for the restored branch CI/image publication and verify mutable environment tags plus immutable `sha-<short-sha>` tags point to the restore commit.
6. Re-apply target raw compose/env from the restored commit while preserving live secrets, then deploy the matching environment.
7. Verify deployment status, artifact/revision parity, endpoint semantics, logs or compensated evidence, TLS/domains, and target smoke/E2E/regression checks.
8. Update the bug issue and rollback report with failed SHA, good SHA, restore commit, deployment evidence, and next fix-forward path.

## Prohibited Shortcuts

Do not claim demo-to-production completion by moving only a mutable image tag or copying preview/demo runtime state into production. Production reflects `main`; demo reflects `demo`; preview reflects the explicitly selected feature/bugfix branch.

Do not claim rollback completion by deploying an old image while the environment branch and Dokploy raw compose/env still describe the failed release.
