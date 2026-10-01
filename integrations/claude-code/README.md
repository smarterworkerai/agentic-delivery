# Claude Code integration

This repository is both a Claude Code plugin and its marketplace. It declares `skills/adw/` as the custom skill path.

```text
claude plugin marketplace add smarterworkerai/agentic-delivery
claude plugin install agentic-delivery@agentic-delivery
```

Inside an interactive session, the equivalent commands begin with `/plugin`. Installed skills are namespaced by the plugin. Validate a checkout with `claude plugin validate --strict .`.
