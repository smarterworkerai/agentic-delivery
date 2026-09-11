# Issue #7 greenfield necessity log

Branch: `spike/mise-adw-contract-greenfield`
Base: orphan/empty tree
Parent: smarterworkerai/mwcal2#37
Issue: smarterworkerai/agentic-delivery#7

## Included top-level artifacts

### `contracts/mise/v1/`

Necessary because issue #7 requires a versioned, standalone contract distribution that projects can vendor without carrying the ADW plugin/skill repository. It contains only the normative specification, standard-library validator, canonical task snapshot, machine schemas, generation guide, and two conformance fixtures.

### `tests/`

Necessary to prove validator behavior and distribution completeness before any existing ADW implementation is copied. Tests cover blocked/unsupported semantics, canonical capability completeness, environment validation, secret-field rejection, evidence writing, task catalog shape, schemas, fixtures, and required documentation boundaries.

### `README.md`

Necessary to explain why this unrelated-history branch is intentionally minimal and provide exact validation commands. The full existing repository README is not copied because plugin installation and workflow examples are not needed to prove the contract package.

### `.gitignore`

Necessary to exclude Python cache files and generated `.hermes/evidence/` artifacts from the spike.

### `plans/issue-7-greenfield-necessity.md`

Necessary because the approved greenfield strategy requires every introduced/copied artifact to be justified and the later port decision to be auditable.

## Explicitly not copied from current `main`

- Existing operational skills: required only during the subsequent integration port, not to derive the contract.
- Plugin/router: workflow routing is unchanged by the standalone contract proof.
- Installer: packaging changes are evaluated only after the minimal contract artifact is proven.
- Existing playbooks/templates/diagrams: not needed to prove task ABI, schemas, validator, or fixtures.
- Existing plans and generated caches: unrelated historical material.

## Port decision gate

After all greenfield tests pass:

1. review every spike file for generic/provider-neutral behavior;
2. create a normal feature branch from current `origin/main` unless direct orphan delivery is separately approved;
3. port the complete minimal contract package;
4. modify only the existing ADW skills, package validator, installer, and README sections proven necessary to consume/package the contract;
5. run existing repository validators plus the new contract tests;
6. open the issue-linked PR from the normal branch.

## Normal-branch delivery port

The reviewed greenfield package is ported without duplication to `skills/adw/adw-core/assets/mise/v1/` on the normal `main`-based delivery branch. This path is required because the existing installer copies the whole `adw-core` skill, making the contract, schemas, validator, fixtures, guide, and templates available to the installed runtime. The greenfield branch retains the standalone `contracts/mise/v1/` layout as the empty-tree proof.
