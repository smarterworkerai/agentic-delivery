# Release Promotion Playbook

## Purpose

Move a validated artifact across environments while preserving traceability.

## Procedure

1. Identify source environment, target environment, commit SHA, image tag, and validation evidence.
2. Confirm target environment with the human.
3. Verify artifact identity is immutable or auditable.
4. Apply target environment configuration without changing artifact identity.
5. Deploy and verify health, logs, TLS, and smoke tests.
6. Record promotion status and rollback path.
