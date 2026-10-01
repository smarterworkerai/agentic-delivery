# Security policy

## Reporting

Report vulnerabilities privately through GitHub Security Advisories for `smarterworkerai/agentic-delivery`. Do not open a public issue containing an exploit, credential, private endpoint, or affected installation detail.

## Installer threat model

The Hermes installer accepts only an immutable lowercase 40-character commit SHA and requires the caller to supply the SHA-256 of GitHub's codeload archive. Branches and tags are refused because they can move. The archive is verified before extraction or target mutation.

Installed skills and plugin directories carry `.agentic-delivery-owner` markers. Upgrades and uninstall remove or replace only marker-owned paths unless the operator explicitly opts into reviewed unmanaged replacement. Payloads are staged and validated first; a failed activation or post-install Doctor check restores the previous paths and plugin state.

Release notes contain a ready-to-paste pinned installer command. Verify that the referenced release, commit, checksum, and repository are expected before running it. Agent skills and plugins run with the user's privileges, so review changes before upgrading.

Manifests, project adapters, evidence, reports, and issue bodies must contain secret environment-variable names only—never secret values, credentials, private keys, or raw private endpoints.
