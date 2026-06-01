# Deployment Gates Playbook

## Purpose

Verify deployments before declaring delivery complete.

## Gates

1. Deployment target and environment are explicit.
2. Build/image/artifact exists for the intended commit. Prefer immutable artifact identity such as image digest, revision label, release version, or `sha-<short-sha>` tag.
3. Environment/config parity has been applied to the target before deployment. For Dokploy/raw-compose targets, update the target environment's compose file and environment variables/settings before starting the deployment; the preview/feature deployment state is not sufficient evidence that production/demo/staging targets are current.
4. Deployment platform reports success.
5. Public/internal endpoint responds with correct semantics. Validate body/content-type/business behavior, not only HTTP 200.
6. Target-environment smoke/E2E/regression checks have run according to the project adapter, or an explicit blocker/waiver is recorded.
7. Persistent services include write-path validation. If the deployment uses a database, filesystem storage, mounted volume, queue, or external write side effect, run at least one create/update/delete/artifact path and inspect logs for storage/database failures.
8. Logs do not show startup or write-path failures, or log access limitations are clearly stated and compensated with container state, endpoint semantics, and runtime artifact evidence.
9. Running artifact parity is verified where possible. Mutable environment tags are not sufficient; compare running image digest/revision metadata with the intended commit/artifact.
10. HTTPS/TLS/domain expectations are verified when a routed domain is part of the target. Record certificate type/issuer when relevant.
11. Rollback path is known.
12. Deployment status is reported with artifact identity and verification evidence.

## Production Rule

Production deployment requires explicit human approval even when the target can be inferred.
