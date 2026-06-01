# Preview Deployments Playbook

## Purpose

Validate feature or bugfix branches in an isolated preview environment before merge.

## Procedure

1. Confirm PR, branch, target base, review status, and whether preview deployment is explicitly requested or supported by the project adapter.
2. Stop if the PR was rejected.
3. Identify preview environment, URL convention, deployment platform, source type, service name, internal port, and HTTPS/TLS expectation from the project adapter or explicit human input.
4. Verify preview artifact availability before redeploy:
   - the build/publish workflow exists and can run for the selected ref;
   - the intended commit has a published artifact or image;
   - immutable identity is known, such as image digest, revision label, or `sha-<short-sha>` tag.
5. If a workflow was newly introduced on the PR branch, check whether the workflow file also exists on the default branch before relying on `workflow_dispatch`. If GitHub cannot see or dispatch the workflow from the default branch, report preview publish as blocked instead of redeploying an older artifact.
6. Deploy the feature branch or immutable preview artifact. For raw-compose platforms, verify the live source type, service/port/domain mapping, and environment contract before deployment. Preserve secrets and do not overwrite live values with examples, blanks, or masked placeholders.
7. Verify deployment status and logs, or record compensated runtime evidence when logs are unavailable.
8. Run smoke/E2E/manual QA checks. Validate response semantics, not only HTTP status.
9. For persistent services, health pages and GET-only checks are insufficient. If the app uses a database, filesystem storage, mounted volume, queue, or external write path, run at least one create/update/delete or artifact-generation path and inspect logs for storage/database failures.
10. Verify runtime artifact parity where the platform exposes it: running image digest, revision label, deployment metadata, or equivalent evidence must match the intended commit/artifact.
11. Record preview URL, artifact identity, deployment target, smoke/write-path evidence, logs/runtime evidence, and validation result in the PR using the GitHub traceability playbook.

## Safety Rules

- Never deploy preview branches to production.
- Never reuse production secrets unless explicitly approved and designed for preview.
- Treat preview as validation evidence, not merge approval by itself.
- Do not claim preview readiness from mutable tags alone. Record immutable artifact identity and running revision/digest evidence when available.
- Do not claim a persistent service is healthy from liveness-only checks; include write-path validation or explicitly document the blocker/waiver.
- For GitHub issue/PR bodies and validation comments, use file-backed Markdown and verify there are no visible backslash-n escape sequences.
