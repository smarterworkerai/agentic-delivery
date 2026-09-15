# ADW mise task contract v1

## Purpose

This contract defines the stable boundary between Agentic Delivery Workflow orchestration and deterministic project operations. ADW, CI, and humans invoke the same canonical mise tasks. Projects and optional context layers implement those tasks without exposing tool- or provider-specific decisions to generic ADW.

The contract version is `1.0.0`. Breaking task, manifest, evidence, status, or behavioral changes require a major version bump.

## Ownership boundary

Generic ADW owns task semantics, orchestration policy, review and approval gates, and interpretation of evidence. A project owns commands, components, routes, deployment-provider calls, health semantics, and E2E behavior. An optional context layer may supply shared task implementations and non-secret defaults.

Mise covers deterministic executable operations only. Human approval, subagent review, PR state, branch protection, merge policy, and hosted-CI orchestration are not mise tasks.

CI calls mise tasks directly. CI does not invoke ADW stages, and ADW does not invoke CI as a project command.

## Project files

The machine source of truth is `.hermes/adw-task-manifest.json`. `.hermes/ADW.md` is narrative and references the manifest instead of duplicating structured capability or environment data.

New ADW/mise-specific helper code and its tests belong under project-root `mise-helper/`. Existing project scripts may remain in their established locations and be called by tasks.

Evidence defaults to `.hermes/evidence/<run-id>/` and must be Git-ignored.

The project config declares a hard minimum mise version. This contract snapshot was tested with `2026.9.5`; newer compatible mise releases are allowed. Exact reproducibility applies to project tools through explicit versions and `mise.lock`, not by locking the mise executable itself.

## Fixed task ABI

Every canonical capability is declared as `supported` or `unsupported`, and every canonical task name exists. `adw:describe` and `adw:check` are always supported.

### Core

```text
adw:describe
adw:check
```

`adw:describe` returns the project identity, contract, environment enum, capability declarations, and effective source provenance.

`adw:check` is side-effect-free. It validates the manifest, task catalog, verification graphs, effective task source paths, source SHA-256 checksums, source metadata, and evidence contract. It may invoke only `adw:describe` and unsupported stubs. It must not execute build, test, network, deployment, or E2E operations.

Each source record contains `layer`, `ref`, `checksum`, and project-relative `path`. Generic and context `ref` values are immutable 40-character Git commit SHAs; project-local sources use the review commit's `HEAD`. Every capability source must exactly match an entry in the top-level source registry. `adw:check` compares resolved mise task sources to those paths and hashes the local snapshots. A later include may override an earlier layer only when the manifest records that effective source.

### Canonical side-effect classes

The side-effect class is fixed by task name and is validated even when the capability is declared `unsupported` (the unsupported stub itself remains non-mutating):

- `read-only`: `adw:describe`, `adw:check`, `adw:deploy:config:plan`, `adw:deploy:status`, `adw:health`, `adw:readiness`, `adw:context:check`;
- `local-write`: `adw:install`, `adw:build`, `adw:lint`, `adw:static-analysis`, `adw:test:unit`, `adw:test:integration`, `adw:verify:minimal`, `adw:verify:full`, `adw:deploy:config:pull`, `adw:context:sync`;
- `remote-write`: `adw:deploy:config:apply`, `adw:deploy:apply`, `adw:e2e`, `adw:validate-deployment`, `adw:hotfix:apply`;
- `destructive`: no v1 public task.

### Local preparation and quality

```text
adw:install
adw:build
adw:lint
adw:static-analysis
adw:test:unit
adw:test:integration
adw:verify:minimal
adw:verify:full
```

`mise install` installs the pinned toolchain. `adw:install` prepares project dependencies.

`adw:verify:minimal` runs a manifest-declared fast allowlist. It includes a fast build/compile or targeted smoke when applicable, but does not automatically add lint, static analysis, or the full test suite.

`adw:verify:full` runs every supported local quality capability required by the project, including build, lint, static analysis, unit/integration tests, and project verification. It does not launch hosted CI or subagent review.

Both verification graphs contain only supported local-quality leaf tasks (`adw:build`, `adw:lint`, `adw:static-analysis`, `adw:test:unit`, and `adw:test:integration`). They cannot contain deployment, remote-write, aggregate, or self-referential tasks.

ADW defaults inner feature/bugfix integration to minimal validation. Release-line integration requires full validation plus the external ADW review/approval gates.

### Deployment

All environment arguments are opaque values from the manifest enum. Generic ADW never invents or hardcodes environment names. Environment-scoped tasks also accept an optional `--target <logical-target>`. When omitted, the project chooses its declared active target; when present, the project validates it against its own inventory. A target is a bounded logical identifier only—not a provider, namespace, host, remote ID, endpoint, credential, or child-command argument.

```text
adw:deploy:config:pull <environment>
adw:deploy:config:plan <environment>
adw:deploy:config:apply <environment>
adw:deploy:apply <environment>
adw:deploy:status <environment>
adw:health <environment>
adw:readiness <environment>
adw:e2e <environment>
adw:validate-deployment <environment>
```

Tasks ending in `:apply` mutate state. They do not implement approval flags or interactive confirmation. ADW/human policy authorizes invocation; manifest side-effect metadata lets every caller distinguish inspection from mutation.

Projects encode provider methods, routes, payloads, redaction, live-ID lookup, polling, readback, and idempotency in project-owned tasks/helpers.

### Temporary hotfix

```text
adw:hotfix:apply <environment>
```

This is one public aggregate. Hidden tasks and helper functions may implement its internal build, transfer, apply, and identity checks.

The capability lists its supported environments. Only those environments are disposable hotfix targets. A supported hotfix requires a clean working tree and a local HEAD that exactly equals its remote-tracking branch after readback.

The artifact uses a unique non-release identity tied to the commit. Transfer transport is project/context owned. The desired artifact identity must be proven on the target and in the running deployment.

If running identity is proven, `adw:hotfix:apply` returns exit code 0. A failed health/readiness check remains a prominent separate finding and does not trigger automatic rollback. No automatic rollback is required; latest hotfix wins, and restore is optional.

### Context snapshots

```text
adw:context:check
adw:context:sync
```

`adw:context:check` is read-only and only operates when the manifest declares the trusted `smarterworkerai/agentic-delivery` `main` branch plus a safe release-index path. It retrieves that upstream index over HTTPS, records the consumer generic pin and selected latest compatible immutable ref/version, and returns one of `current`, `update-available`, `update-required`, `incompatible-major`, or `lookup-unavailable`. `require-current-compatible` blocks stale pins and unavailable lookup in CI. Moving branches and tags are never final resolved refs.

`adw:context:sync` is an explicit local-write maintenance task. It copies the selected local/approved immutable snapshot, verifies the checksum, and updates only the vendor snapshot and manifest pins for review; it never commits, opens a PR, or runs automatically from `check` or normal CI.

## Include precedence and offline operation

Effective task precedence is:

```text
generic agentic-delivery snapshot
→ optional context snapshot
→ project-local override
```

Shared layers may define canonical `adw:*` tasks directly. Projects record effective task source/ref/checksum.

Normal execution uses exact vendored snapshots under `mise-helper/vendor/agentic-delivery/` and `mise-helper/vendor/<context>/`. Remote Git retrieval is restricted to explicit sync, uses an immutable 40-character commit SHA plus checksum, and must not be required for offline task execution.

Each project records an exact consumed ref/checksum and an accepted SemVer range. An incompatible major version is a contract error.

## Capability behavior

Unsupported task stubs exit 0 and emit `status=unsupported`. This means the task invocation itself behaved as declared. When an aggregate or requested ADW goal requires that capability, the aggregate/orchestrator returns non-zero `blocked`.

Canonical statuses:

```text
passed
failed
skipped
unsupported
blocked
contract-error
```

Exit classes:

- `0`: declared operation completed, including a direct unsupported stub;
- `1`: supported operation failed;
- `20`: required precondition/capability blocked execution;
- `21`: manifest, task catalog, schema, or compatibility contract error.

Skipped and unsupported work must never be represented as passed.

## Evidence

Tasks print concise human-readable progress and write separate redacted JSON evidence conforming to `schemas/adw-task-evidence.schema.json`.

Project and context task implementations should invoke `adw_contract.py run --task <task> [--environment <value>] [--child <canonical-task>]... -- <command>`. The adapter validates the complete manifest and source checksums before execution. A nonzero child exit becomes the public `failed` exit class `1`; the raw child exit remains in the evidence finding. The adapter persists only the selected target environment name and declared canonical child task names, and does not persist child command arguments or environment-variable values. Only aggregate tasks may declare unique, non-self-referential children. Unsupported generic stubs use `adw_contract.py unsupported`, return zero only when the manifest declares that canonical task unsupported, and record `unsupported`.

An aggregate may report `passed` only after every declared child evidence file exists under the same run ID and its run ID, task name, status, and exit class validate. `adw:verify:minimal` and `adw:verify:full` must declare exactly the corresponding manifest verification graph.

The JSON Schemas enforce closed structure and directly expressible constraints. The dependency-free Python validator is normative for cross-object invariants that Draft 2020-12 cannot compare dynamically, including supported-capability verification coverage and source-registry/file containment checks.

`ADW_RUN_ID` is inherited when supplied and generated otherwise. It must match `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$`; invalid values are rejected before task execution and cannot escape the evidence root. The resolved value is exported to child processes, so aggregate and child records share the run ID and identify relationships. Evidence records contract/schema version, task, status, exit code, source revision, effective task source/ref/checksum, arguments, timestamps, children, and findings.

Writes are atomic. Secret values, credentials, raw private endpoints, and private-key paths are forbidden. A manifest may list required secret environment-variable names, never their values.

## Manifest absence

If `.hermes/adw-task-manifest.json` is absent, ADW returns `blocked` and offers generation of a reviewable adapter diff. It does not infer and execute ad-hoc project commands.

## Context neutrality

This specification defines interfaces and observable behavior. It does not prescribe a programming language, build system, image format, transfer transport, deployment provider, CI provider, project name, organization, or concrete environment name.
