# Constraints

- Stay within the task scope and explicitly avoid non-scope work.
- Treat secrets carefully: do not invent credentials, do not print secret values, and do not commit real tokens/keys/passwords.
- Prefer a PR/MR as the primary deliverable for code changes.
- Do not merge or deploy unless the human explicitly requested it for this delegation.
- Record important commands in `11-commands.md`.
- Keep generated artifacts under `result/` or the backend-equivalent artifact location.

- When producing GitHub issue, PR, review, or comment text, use readable Markdown with real newline characters; do not emit visible literal `\n` sequences unless documenting an escape sequence.
