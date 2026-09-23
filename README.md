# agentic-delivery

Agentic Delivery Workflow (ADW) is a Hermes-compatible plugin and skill package for moving software changes through a reviewable delivery pipeline:

```text
Plan → Branch → Issue → PR → Review → Preview → Merge → Deploy
```

The PR is the central unit of delivery. ADW keeps planning, implementation, delegation, review, approval, PR/merge policy, and rollback decisions in the agentic workflow layer. It delegates deterministic project operations to a versioned `adw:*` mise task contract.

## Package Source of Truth

- `adw_plugin/` — `/adw` command routing and gateway rewrite hook.
- `skills/adw/` — operational ADW skills.
- `skills/adw/adw-core/` — shared policy, playbooks, templates, ADRs, diagrams, and the mise contract package.
- `scripts/install_adw.sh` — profile-aware install and uninstall entrypoint.
- `tools/` and `tests/` — package, contract, schema, and distribution validation.

Shared artifacts live only under `skills/adw/adw-core/`. Workflow skills reference that package; projects must not depend on obsolete repo-root `playbooks/`, `templates/`, `adr/`, or `docs/` copies.

## ADW and mise Boundary

### Agentic ADW responsibilities

- inspect repository and delivery context;
- create plans, branches, issues, and PRs;
- implement or delegate code changes;
- review diffs and evidence;
- request approval for merge, deployment, rollback, destructive work, or history rewrites;
- preserve traceability and report blockers.

These are not mise tasks.

### Deterministic project operations

Projects expose supported build, test, verification, deployment, status, health, readiness, E2E, context-sync, and temporary-hotfix operations through the canonical `adw:*` ABI. The normative v2 package is:

```text
skills/adw/adw-core/assets/mise/v2/
```

Each project owns its concrete task implementations and `.hermes/adw-task-manifest.json`. Optional context includes provide only proven shared task definitions and non-secret variables. Include precedence is generic ADW → optional context → project-local override.

Missing or invalid manifests fail closed. ADW does not improvise package-manager, deployment-provider, or infrastructure commands.

### Vendored-context freshness

A project may support `adw:context:check` with `context_freshness` in its manifest: the trusted `smarterworkerai/agentic-delivery` `main` branch, a safe release-index path, and either `advisory` or `require-current-compatible` policy. The strict policy is suitable for fast-feedback CI: `mise run adw:context:check` fails when the vendor pin is stale or the trusted upstream lookup is unavailable. Index releases must name exact immutable Git SHAs; a branch or tag is never accepted as the resolved release. `adw:context:sync` explicitly downloads the selected immutable GitHub codeload archive, safely stages only the declared snapshot subtree, verifies its canonical `tasks.toml` checksum, then locally replaces the vendor snapshot and updates the manifest. Neither task commits or opens a PR.

## Install

Requirements:

- Hermes Agent available as `hermes`;
- `curl` and `tar` for remote installation.

Install an explicitly reviewed immutable commit:

```bash
ADW_REF=0123456789abcdef0123456789abcdef01234567
ADW_ARCHIVE_SHA256=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
curl -fsSL "https://raw.githubusercontent.com/smarterworkerai/agentic-delivery/${ADW_REF}/scripts/install_adw.sh" | ADW_REF="${ADW_REF}" ADW_ARCHIVE_SHA256="${ADW_ARCHIVE_SHA256}" bash
```

Replace the example values with the reviewed commit SHA and its published codeload archive SHA-256. Branch names, tags, uppercase SHA text, a missing archive checksum, and an omitted `ADW_REF` are rejected.

The installer downloads and validates the full source before touching active paths, stages on the profile filesystem, installs only the runtime plugin files plus the 14 skill packages, marks owned paths, and restores prior paths if activation or post-install Doctor validation fails. An unmanaged collision is refused unless `ADW_REPLACE_UNMANAGED=yes` is explicitly set after review. Non-interactive automation must set profile and `SOUL.md` choices explicitly. The installer does not request or print secrets.

After installing or updating the plugin, restart the Hermes gateway from a separate shell before using `/adw` through a gateway platform.

## Uninstall

```bash
ADW_REF=0123456789abcdef0123456789abcdef01234567
curl -fsSL "https://raw.githubusercontent.com/smarterworkerai/agentic-delivery/${ADW_REF}/scripts/install_adw.sh" | bash -s -- --uninstall
```

Uninstall removes only marker-owned `adw` plugin and skill paths. It does not delete unproven legacy aliases or unrelated same-named directories. Profile-level `SOUL.md` removal requires an explicit option or prompt and an exact content match with the installed package copy.

## `/adw` Command

The root plugin registers:

```text
/adw <workflow> <payload>
```

Examples:

```text
/adw plan-feature add export support
/adw do-impl issue #42
/adw test-feature PR #42
/adw merge-feature PR #42 to <approved-target>
/adw chain plan impl test merge <scope>
```

An unknown workflow is rejected. `/adw` without arguments lists current workflow tokens.

## Workflow Skills

- `adw-plan-feature`
- `adw-plan-bugfix`
- `adw-do-impl`
- `adw-do-impl-delegate`
- `adw-test-feature`
- `adw-merge-feature`
- `adw-validate-regression`
- `adw-rollback-deployment`
- `adw-create-adr`
- `adw-audit-dependencies`
- `adw-analyze-production`
- `adw-chain`
- `adw-self-improve`
- `adw-core`

Repository metadata, the project adapter, and explicit human input determine branch names, release targets, environment mappings, and deployment strategy. Generic ADW does not hardcode them.

## Validation

The **Required producer quality** check runs `python3 tools/verify_producer.py` on GitHub Actions for branch pushes and PRs. It covers the unit/distribution suite, skill validator, and direct plugin-package tests without a Hermes runtime; this producer-repository check is distinct from the `adw:verify:full` task graph required of consuming projects. It does not claim to run the Hermes Plugin Doctor or live deployments.

Run from the repository root:

```bash
python3 tools/verify_producer.py
/path/to/hermes/venv/bin/python tools/validate_adw_plugin_package.py
```

The plugin validator runs the real `hermes plugins doctor --ci` contract and isolated runtime-only discovery. Run it with a Python interpreter from the Hermes environment so `hermes_cli` is importable; `HERMES_BIN` may select the Doctor executable but does not replace that interpreter requirement.

Generated task evidence belongs under `.hermes/evidence/<run-id>/` and is Git-ignored.
