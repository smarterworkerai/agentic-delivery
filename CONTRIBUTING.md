# Contributing

Run the portable producer gate before opening a pull request:

```bash
python3 tools/build_skills.py
python3 tools/verify_producer.py
```

When Hermes is installed, also run its runtime integration check:

```bash
python3 tools/validate_adw_plugin_package.py
```

For Claude Code changes, run `claude plugin validate --strict .` with a current Claude Code installation.

## Generated content

Do not hand-edit generated guardrail blocks, the README skill table, the Hermes workflow registry, or copied version fields. Edit `skills/_shared/guardrails.md`, a skill's frontmatter, or `VERSION`, then run `python3 tools/build_skills.py`. CI runs the same command with `--check`.

## Adding a skill

1. Create `skills/adw/<name>/SKILL.md`; the directory and frontmatter `name` must match the Agent Skills specification.
2. Keep metadata a flat string map and describe both what the skill does and when it should load.
3. Put single-owner templates under that skill's `assets/`. Put shared operational playbooks under `adw-core/references/` and refer to them by skill name, not an escaping relative path.
4. Add `router-tokens`, `human-gate`, and any alias presets as flat metadata strings when the skill is routable.
5. Add the generated guardrail markers, rebuild, and add focused tests.

Keep task names, schemas, statuses, exit classes, the installer security model, and `skills/adw/adw-core/assets/mise/v2` stable within contract major v2.
