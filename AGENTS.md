# Instructions for agents working on this repository

Validate changes with:

```bash
python3 tools/build_skills.py --check
python3 tools/verify_producer.py
python3 tools/validate_adw_plugin_package.py  # when Hermes is installed
```

Never hand-edit generated blocks. Edit `skills/_shared/guardrails.md`, skill frontmatter, or `VERSION`, then run `python3 tools/build_skills.py`.

Hard constraints:

- Keep the contract snapshot at `skills/adw/adw-core/assets/mise/v2`.
- Keep all 26 canonical tasks, manifest/evidence schemas, statuses, exit classes, and contract major v2.
- Keep skill names used by `pzagent-adw-context`: `adw-core`, `adw-chain`, `adw-self-improve`, `adw-merge-feature`, and `adw-do-impl-delegate`.
- Keep legacy `/adw` router tokens working when skills consolidate.
- Preserve the installer model: immutable SHA, archive checksum, marker-owned paths, and restore after a failed Doctor check.
- Release-index refs must name a commit containing the exact indexed snapshot. No later release commit may alter that snapshot.
- Merge release work without squash because the release index may reference an implementation commit inside the pull request.

Use `.adw/` for new generic project adapters. Retain `.hermes/` when an existing project or selected context requires it. Treat both present as `contract-error`.
