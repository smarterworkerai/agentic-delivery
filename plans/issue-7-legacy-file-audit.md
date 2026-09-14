# Issue #7 legacy file audit

Source tree: `origin/main` at `8c6e649af2067f80b0fbe2ec12f07c2b3d02e3f0`
Replacement tree: orphan `spike/mise-adw-contract-greenfield`

This audit covers every one of the 58 files in the legacy tree. Decisions were derived from current Hermes discovery, the ADW/mise v1 boundary, explicit PR/merge approval policy, adapter neutrality, runtime reachability, and executed validation.

Summary: 11 retained unchanged, 42 rewritten, 5 removed.

## Root and plugin runtime

- **rewrite** `.gitignore` — keep Python caches and generated `.hermes/evidence/<run-id>/` out of source.
- **retain** `LICENSE` — the MIT license remains current and is referenced by plugin metadata.
- **rewrite** `README.md` — remove historical invoice and fixed branch/environment examples; document the v1 boundary, immutable installer inputs, ownership, and current validation.
- **rewrite** `SOUL.md` — retain ADW identity while adding manifest-first execution and explicit PR-route approval.
- **rewrite** `__init__.py` — use a package-relative router import; remove global `sys.path` mutation.
- **retain** `adw_plugin/__init__.py` — minimal package marker remains valid and has no compatibility behavior.
- **rewrite** `adw_plugin/prompts.py` — load installed skills by name instead of embedding duplicated SKILL bodies.
- **rewrite** `adw_plugin/registry.py` — remove sample-domain wording and automatic deployment/PR implications; keep the 13 operational routes plus help.
- **rewrite** `adw_plugin/router.py` — retain strict routing while replacing historical sample payloads.
- **rewrite** `plugin.yaml` — publish plugin `1.0.0`, license/homepage/tags, and the declared `pre_gateway_dispatch` hook.
- **rewrite** `scripts/install_adw.sh` — require exact commit SHA and archive SHA-256; validate before activation; install runtime-only plugin content; mark ownership; refuse unmanaged collisions; roll back files and enable-state; uninstall marker-owned paths only.

## Removed historical root files

- **remove** `plans/PLAN.md` — completed implementation history, not runtime, contract, or current user documentation.
- **remove** `plans/PLAN_plugin.md` — completed plugin implementation history; current behavior is represented by executable code and validation.

## ADW package index and core

- **rewrite** `skills/adw/README.md` — update workflow descriptions for canonical mise calls, optional deployment, generic rollback, and PR approval.
- **rewrite** `skills/adw/adw-core/SKILL.md` — add the v1 contract package, use the source-only PlantUML diagram, remove embedded example topics, and update shared invariants.
- **rewrite** `skills/adw/adw-core/assets/diagrams/adw-complete-workflow.puml` — replace fixed `main/demo/production`, raw-compose, image-tag, and owning-branch flows with adapter-declared targets and canonical task evidence.
- **remove** `skills/adw/adw-core/assets/diagrams/adw-complete-workflow.svg` — stale rendering contradicted the new source; no local renderer was available, so only the reviewable canonical source remains.

## Architecture and playbooks

- **retain** `skills/adw/adw-core/references/adr/0001-agentic-delivery-workflow.md` — still defines the current skill/playbook/template separation without provider assumptions.
- **retain** `skills/adw/adw-core/references/adr/0002-pr-as-delivery-unit.md` — PR-centric delivery remains a core policy.
- **remove** `skills/adw/adw-core/references/playbooks/branch_environment_releases.md` — mandatory branch-owned environments are not generic; replaced by new `release_targets.md`.
- **rewrite** `skills/adw/adw-core/references/playbooks/deployment_gates.md` — express gates as adapter-declared target resolution plus canonical config/deploy/status/health/readiness/E2E evidence.
- **retain** `skills/adw/adw-core/references/playbooks/github_traceability.md` — still provides current issue/branch/PR linkage rules for this GitHub-oriented plugin.
- **retain** `skills/adw/adw-core/references/playbooks/incident_response.md` — concise evidence-first incident handling remains provider-neutral.
- **retain** `skills/adw/adw-core/references/playbooks/pr_reviewing.md` — current severity and approval/rejection rules remain valid.
- **rewrite** `skills/adw/adw-core/references/playbooks/preview_deployments.md` — remove raw-compose and CI-provider assumptions; require adapter-declared disposable environment and canonical evidence.
- **rewrite** `skills/adw/adw-core/references/project_contexts.md` — make manifest/mise the machine source of truth; remove narrative command expansions and mandatory branch/environment maps.

## Planning and delegation templates

- **retain** `skills/adw/adw-core/templates/bugfix_plan.md` — minimal symptom/root-cause/regression plan remains current and neutral.
- **rewrite** `skills/adw/adw-core/templates/delegation/acceptance_criteria.md` — make PR/MR delivery conditional on exact approved route.
- **rewrite** `skills/adw/adw-core/templates/delegation/constraints.md` — prohibit worker-selected PR route and preserve approval boundaries.
- **retain** `skills/adw/adw-core/templates/delegation/environment.md` — backend details remain isolated from portable ADW documents.
- **retain** `skills/adw/adw-core/templates/delegation/input_artifacts.md` — explicit, redacted, minimal input handoff remains current.
- **rewrite** `skills/adw/adw-core/templates/delegation/output_summary.md` — allow validated commit/patch output when PR creation is not approved.
- **rewrite** `skills/adw/adw-core/templates/delegation/status.schema.json` — correct `$id`, close top-level properties, constrain run IDs, and validate timestamps.
- **rewrite** `skills/adw/adw-core/templates/delegation/task_brief.md` — require an explicit deliverable type and exact PR route before worker-created PR/MR.
- **retain** `skills/adw/adw-core/templates/implementation_plan.md` — scoped steps, test strategy, risks, rollback, and acceptance criteria remain current.

## Delivery and report templates

- **rewrite** `skills/adw/adw-core/templates/deployment_report.md` — use opaque environment, adapter release target, immutable source/artifact identity, and canonical task evidence instead of mandatory image/tag fields.
- **rewrite** `skills/adw/adw-core/templates/github_issue_bugfix.md` — replace fixed `bugfix/` branch naming with adapter-compatible branch identity.
- **rewrite** `skills/adw/adw-core/templates/github_issue_feature.md` — replace fixed `feature/` branch naming with adapter-compatible branch identity.
- **rewrite** `skills/adw/adw-core/templates/project_adw_adapter.md` — make `.hermes/adw-task-manifest.json` and mise authoritative; retain `.hermes/ADW.md` as narrative policy only.
- **rewrite** `skills/adw/adw-core/templates/pull_request.md` — do not auto-close issues unless repository completion policy permits it; use generic deployment impact.
- **remove** `skills/adw/adw-core/templates/review_report.md` — no operational consumer remained; review findings are owned by the review playbook/platform.
- **rewrite** `skills/adw/adw-core/templates/rollback_report.md` — replace owning branch/image assumptions with adapter-selected restore strategy and immutable identities.
- **rewrite** `skills/adw/adw-core/templates/validation_report.md` — record canonical task/evidence identity and honest skipped/unsupported/blocked states.

## Operational workflow skills

- **rewrite** `skills/adw/analyze-production/SKILL.md` — normalize trigger metadata, bind incident playbook, and use generic source/deployment/artifact identity plus canonical read-only evidence.
- **rewrite** `skills/adw/audit-dependencies/SKILL.md` — normalize trigger metadata and preserve dependency/build/tooling audit as an agentic review workflow.
- **rewrite** `skills/adw/chain/SKILL.md` — remove hardcoded release-branch promotion and require exact route approval before any PR/merge/deploy stage.
- **rewrite** `skills/adw/create-adr/SKILL.md` — normalize trigger metadata while retaining ADR creation as an agentic, non-mise workflow.
- **rewrite** `skills/adw/do-impl-delegate/SKILL.md` — allow commit/patch handoff without PR; worker PR/MR requires exact approved source/target route; verify returned work independently with canonical tasks.
- **rewrite** `skills/adw/do-impl/SKILL.md` — implement and locally commit validated work, then stop before push/PR until exact route approval.
- **rewrite** `skills/adw/merge-feature/SKILL.md` — resolve target through adapter policy, merge only after explicit approval, deploy only when requested, and close issues according to repository completion policy.
- **rewrite** `skills/adw/plan-bugfix/SKILL.md` — remove mandatory `bugfix/` naming; keep root-cause and regression planning agentic.
- **rewrite** `skills/adw/plan-feature/SKILL.md` — remove implicit `main` and mandatory `feature/` defaults; use repository/adapter metadata.
- **rewrite** `skills/adw/rollback-deployment/SKILL.md` — remove mandatory branch restore and image-tag procedure; choose an approved adapter strategy and verify through canonical tasks.
- **rewrite** `skills/adw/self-improve/SKILL.md` — retain confirm-first workflow improvement, but require exact route approval before push/PR.
- **rewrite** `skills/adw/test-feature/SKILL.md` — bind preview/deployment playbooks, remove CI-default-branch historical caveat, and require canonical preview validation evidence.
- **rewrite** `skills/adw/validate-regression/SKILL.md` — normalize trigger metadata and keep targeted/full regression mapped to canonical verification tasks.

## Repository validators

- **rewrite** `tools/validate_adw_plugin_package.py` — validate package-relative imports, non-embedded prompts, runtime-only copying, declared hook, real Plugin Doctor, and isolated discovery without machine-local source paths.
- **rewrite** `tools/validate_adw_skills.py` — validate the canonical v1 shared package, renamed/removed artifacts, current README, and safe installer invariants instead of legacy example sections.

## New greenfield artifacts

The 19 new-only files are the issue necessity log, this per-file legacy audit, the canonical 13-file ADW/mise v1 package, the replacement `release_targets.md`, and three test modules. They are not inherited from legacy `main`; their necessity is documented in `plans/issue-7-greenfield-necessity.md` and enforced by distribution tests.
