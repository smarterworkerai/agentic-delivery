# ADW Hermes Plugin Spike

This is a project-local spike for routing a single Hermes slash command into the Agentic Delivery Workflow skillset:

```text
/adw <workflow> <payload>
```

## Scope

- Registers `/adw` with `ctx.register_command()` for CLI sessions.
- Registers a `pre_gateway_dispatch` hook for gateway platforms.
- Keeps workflow rules in `skills/adw/*`; the plugin only parses and injects.
- Embeds `adw-core` and the selected operational skill into the generated prompt from this repository.

## Validation

Run from the repository root:

```bash
python3 tools/validate_adw_plugin_spike.py
```

For real Hermes discovery testing with project plugins enabled, the validation script creates a temporary `HERMES_HOME` with `plugins.enabled: [adw]` and calls Hermes' `hermes_cli.plugins` loader directly. This avoids mutating the user's real Hermes config.

To enable manually in an interactive local Hermes session, add `adw` to `plugins.enabled`, start Hermes from this repository with project plugins enabled, then restart the process:

```bash
HERMES_ENABLE_PROJECT_PLUGINS=1 hermes
```
