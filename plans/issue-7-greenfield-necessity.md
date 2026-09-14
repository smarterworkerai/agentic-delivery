# Issue #7 greenfield necessity log

Branch: `spike/mise-adw-contract-greenfield`
Base: orphan/empty tree
Target: `main` through an explicitly approved replacement PR
Parent: smarterworkerai/mwcal2#37
Issue: smarterworkerai/agentic-delivery#7

## Greenfield rule

This branch is the delivery source, not only a disposable proof. It starts from an empty tree. Existing `main` artifacts are present only when a runtime, delivery, documentation, or validation dependency below justifies them.

The repository intentionally separates three layers:

1. **Agentic ADW workflows** plan work, edit code, delegate implementation, manage issues/PRs, review, approve, merge, and orchestrate releases. These are Hermes skills, not mise tasks.
2. **Deterministic project operations** use the versioned canonical `adw:*` mise ABI for check, build, test, deployment, health, readiness, E2E, context synchronization, and temporary hotfix execution.
3. **Policy gates** authorize review, merge, production deployment, rollback, and destructive actions outside mise.

## Included top-level artifacts

### `skills/adw/`

Necessary because the repository delivers the Agentic Delivery Workflow itself. The retained skills preserve planning and implementation as agentic methods while changing only deterministic project-operation boundaries to canonical mise tasks.

Required groups:

- `plan-feature` and `plan-bugfix`: create branches, plans, issues, acceptance criteria, and traceability; they do not invoke mise.
- `do-impl` and `do-impl-delegate`: edit or delegate code, then invoke `adw:check` and `adw:verify:minimal` at the deterministic validation boundary.
- `test-feature`, `merge-feature`, `validate-regression`, `rollback-deployment`, and `analyze-production`: orchestrate policy and call manifest-declared canonical tasks instead of provider/package-manager commands.
- `create-adr`, `audit-dependencies`, `chain`, and `self-improve`: retained workflow capabilities referenced by the plugin registry.
- `adw-core`: shared policy, project/context resolution, templates, playbooks, ADRs, diagrams, and the installable mise contract package.

### `skills/adw/adw-core/assets/mise/v1/`

Necessary as the single canonical contract distribution. It contains the normative contract, dependency-free validator/runner, task snapshot, JSON Schemas, adapter-generation guide, project/context templates, and library/service conformance fixtures.

There is no duplicate top-level `contracts/` copy. The installer distributes `adw-core`, so this location makes the contract available to installed profiles and vendoring workflows.

### `adw_plugin/`, `__init__.py`, and `plugin.yaml`

Necessary to register `/adw`, route workflow names to the retained skills, inject the resolved invocation prompt, and support Hermes plugin discovery. These files are runtime code, not historical documentation.

### `scripts/install_adw.sh`

Necessary to install the complete ADW skill package and verify installed skill identities. The contract travels through the installed `adw-core` directory.

### `tools/`

Necessary for model-free repository validation:

- `validate_adw_skills.py` proves skill metadata, required shared artifacts, installer coverage, and package layout.
- `validate_adw_plugin_package.py` proves root plugin metadata, registry consistency, routing, gateway integration, and Hermes discovery.

### `tests/`

Necessary to prove contract behavior and distribution completeness. Tests cover fail-closed manifest handling, canonical capabilities, source provenance/checksums, task signatures, side-effect classes, verification graphs, safe run IDs, evidence correlation/redaction, schemas, fixtures, hard mise minimum, variable ownership, operational skill boundaries, and transactional installer safety.

### `README.md` and `skills/adw/README.md`

Necessary user-facing repository and installable-package documentation. They describe the ADW workflow layer separately from the deterministic mise facade.

### `SOUL.md`

Necessary because installed ADW profiles use it as the workflow identity, safety, approval, and delivery contract.

### `LICENSE`

Necessary to preserve the legal terms of redistributed plugin, skill, template, and contract files.

### `.gitignore`

Necessary to exclude Python caches and generated `.hermes/evidence/` records at any fixture or project depth.

### `plans/issue-7-greenfield-necessity.md` and `plans/issue-7-legacy-file-audit.md`

Necessary to make every retained group, each of the 58 legacy file decisions, and every deliberate deletion reviewable in the unrelated-history replacement PR.

## Obsolescence audit outcomes

The copied legacy candidates were reviewed as content, not accepted by filename alone.

- Replaced mandatory branch/environment ownership with adapter-declared release targets and opaque manifest environments.
- Renamed `branch_environment_releases.md` to `release_targets.md` and updated every reference.
- Rewrote rollback policy so Git branch restoration, artifact selection, and configuration restoration are adapter strategies rather than generic invariants.
- Rewrote preview and deployment gates to use canonical config/deploy/status/health/readiness/E2E evidence instead of raw-compose or provider operations.
- Rewrote `project_contexts.md` and `project_adw_adapter.md` so the manifest/mise adapter is machine-readable source of truth and `.hermes/ADW.md` is narrative policy.
- Removed automatic `main` base selection, `main → production`, `demo → demo`, owning-branch, branch-prefix issue-closure, and release-branch promotion assumptions.
- Replaced historical invoice CSV and branch-testing examples with generic payloads and explicit refs.
- Removed unused `templates/review_report.md`; review findings are owned by the review playbook/platform, while validation and deployment keep dedicated reports.
- Made direct, delegated, chained, and self-improvement PR creation conditional on explicit source/target/replacement route approval; local commit/patch output remains valid before approval.
- Rewrote the PlantUML workflow for the v1 boundary and deleted the stale pre-rendered SVG because no matching generated artifact was available.
- Removed the machine-local validator fallback; validation now finds the Hermes CLI through `HERMES_BIN`, `PATH`, or the active Hermes interpreter and runs Plugin Doctor directly.
- Raised the greenfield plugin package version from `0.1.0` to `1.0.0` for the breaking replacement and normalized every packaged skill to concise current trigger metadata at `1.0.0`.
- Replaced fixed feature/bugfix prefixes, mandatory image/tag fields, and unconditional `Closes` PR text with adapter-compatible branches, immutable optional artifact identity, and repository-policy issue closure.
- Replaced brittle full-repository plugin copying and `sys.path` mutation with a runtime-only plugin package, package-relative imports, and installed-skill loading prompts.
- Replaced mutable-ref/destructive installer behavior with exact commit SHA plus archive SHA-256 verification, full source preflight, same-filesystem staging, ownership markers, unmanaged collision refusal, file/config rollback, and marker-only uninstall.
- Declared the runtime hook in `plugin.yaml` and verified it with the current Hermes Plugin Doctor.
- Removed automatic cleanup of the former plugin alias; install and uninstall manage only marker-owned `adw` paths.

## Explicitly omitted legacy files and rejected integration candidates

- `plans/PLAN.md`: historical implementation plan; not a runtime, contract, install, or validation dependency.
- `plans/PLAN_plugin.md`: historical plugin plan; the resulting plugin code and validators are retained directly.
- Top-level `adw_plugin.py` and package-level `adw_plugin/plugin.py` compatibility shims: no consumer remains because the standalone package entrypoint imports the router directly.
- Any generated cache or evidence directory: runtime output, never source.
- A top-level `contracts/` copy: would duplicate the canonical installable package under `adw-core/assets/mise/v1/`.

## Delivery gate

Before opening the replacement PR:

1. validate all retained skill and plugin dependencies;
2. run the complete contract/distribution test suite and Python compilation;
3. validate all three schemas, both manifests, and generated evidence with a Draft 2020-12 engine;
4. run checksum-verified real-mise discovery, hard-minimum, required-environment, and aggregate evidence smoke tests;
5. inspect the complete empty-tree and `main...greenfield` diffs;
6. verify no secrets, provider-specific commands, generated evidence, or raw infrastructure identifiers are tracked;
7. commit and push the orphan branch;
8. open the explicitly approved replacement PR from `spike/mise-adw-contract-greenfield` to `main` without merging.
