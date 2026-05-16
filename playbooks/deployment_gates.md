# Deployment Gates Playbook

## Purpose

Verify deployments before declaring delivery complete.

## Gates

1. Deployment target and environment are explicit.
2. Build/image/artifact exists for the intended commit.
3. Deployment platform reports success.
4. Public/internal endpoint responds with correct semantics.
5. Logs do not show startup failures.
6. Rollback path is known.
7. Deployment status is reported with artifact identity.

## Production Rule

Production deployment requires explicit human approval even when the target can be inferred.
