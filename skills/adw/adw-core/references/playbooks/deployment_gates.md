# Deployment Gates Playbook

## Purpose

Verify deployments before declaring delivery complete.

## Gates

1. Deployment target and environment are explicit.
2. Build/image/artifact exists for the intended commit.
3. Environment/config parity has been applied to the target before deployment. For Dokploy targets, update the target environment's compose file and environment variables/settings before starting the deployment; the preview/feature deployment state is not sufficient evidence that production/demo/staging targets are current.
4. Deployment platform reports success.
5. Public/internal endpoint responds with correct semantics.
6. Target-environment smoke/E2E/regression checks have run according to the project adapter, or an explicit blocker/waiver is recorded.
7. Logs do not show startup failures.
8. Rollback path is known.
9. Deployment status is reported with artifact identity.

## Production Rule

Production deployment requires explicit human approval even when the target can be inferred.
