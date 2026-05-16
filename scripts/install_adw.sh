#!/usr/bin/env bash
set -euo pipefail

REPO="smarterworkerai/agentic-delivery"
PLUGIN_NAME="adw"
ADW_SKILLS=(
  "adw-core"
  "plan-feature"
  "plan-bugfix"
  "do-impl"
  "do-impl-delegate"
  "test-feature"
  "merge-feature"
  "promote-release"
  "rollback-deployment"
  "validate-regression"
  "create-adr"
  "audit-dependencies"
  "analyze-production"
)
ADW_INSTALLED_SKILL_NAMES=(
  "adw-core"
  "adw-plan-feature"
  "adw-plan-bugfix"
  "adw-do-impl"
  "adw-do-impl-delegate"
  "adw-test-feature"
  "adw-merge-feature"
  "adw-promote-release"
  "adw-rollback-deployment"
  "adw-validate-regression"
  "adw-create-adr"
  "adw-audit-dependencies"
  "adw-analyze-production"
)

log() { printf '\n==> %s\n' "$*"; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

command -v hermes >/dev/null 2>&1 || fail "hermes is not on PATH. Install Hermes Agent first."

log "Hermes version"
hermes --version || warn "Could not read Hermes version; continuing."

if hermes profile list >/dev/null 2>&1; then
  log "Available Hermes profiles"
  hermes profile list || true
fi

printf '\nTarget Hermes profile (leave empty for default): '
read -r PROFILE_NAME || PROFILE_NAME=""

HERMES_CMD=(hermes)
if [[ -n "${PROFILE_NAME}" ]]; then
  HERMES_CMD+=(--profile "${PROFILE_NAME}")
  log "Target profile: ${PROFILE_NAME}"
else
  log "Target profile: default"
fi

run_required() {
  printf '+ '
  printf '%q ' "$@"
  printf '\n'
  "$@"
}

run_optional() {
  printf '+ '
  printf '%q ' "$@"
  printf '\n'
  if ! "$@"; then
    warn "Command failed but is optional/idempotent: $*"
  fi
}

log "Removing previous ADW-owned skills (safe if not installed)"
for skill in "${ADW_INSTALLED_SKILL_NAMES[@]}"; do
  run_optional "${HERMES_CMD[@]}" skills uninstall "${skill}"
done

log "Removing previous ADW plugin installs (safe if not installed)"
run_optional "${HERMES_CMD[@]}" plugins remove "${PLUGIN_NAME}"
run_optional "${HERMES_CMD[@]}" plugins remove "agentic-delivery"

log "Adding/updating ADW skill tap"
run_optional "${HERMES_CMD[@]}" skills tap add "${REPO}"

log "Installing ADW skills"
for skill_dir in "${ADW_SKILLS[@]}"; do
  run_required "${HERMES_CMD[@]}" skills install "${REPO}/skills/adw/${skill_dir}"
done

log "Installing and enabling ADW plugin"
run_required "${HERMES_CMD[@]}" plugins install "${REPO}" --enable

log "Post-install verification"
SKILLS_OUTPUT=$("${HERMES_CMD[@]}" skills list || true)
PLUGINS_OUTPUT=$("${HERMES_CMD[@]}" plugins list || true)

printf '%s\n' "${SKILLS_OUTPUT}" | grep -q "adw-core" || fail "adw-core was not found in hermes skills list output."
printf '%s\n' "${SKILLS_OUTPUT}" | grep -q "adw-plan-feature" || fail "adw-plan-feature was not found in hermes skills list output."
printf '%s\n' "${PLUGINS_OUTPUT}" | grep -Eq "adw|agentic-delivery" || fail "ADW plugin was not found in hermes plugins list output."

log "ADW installation complete"
printf '%s\n' "Next steps:"
printf '%s\n' "- If you use Telegram/Discord/another gateway, restart it:"
if [[ -n "${PROFILE_NAME}" ]]; then
  printf '  hermes --profile %q gateway restart\n' "${PROFILE_NAME}"
else
  printf '%s\n' "  hermes gateway restart"
fi
printf '%s\n' "- Try: /adw"
printf '%s\n' "- Then try: /adw plan-feature invoice CSV export"
