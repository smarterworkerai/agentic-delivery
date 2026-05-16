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

prompt_from_tty() {
  local prompt="$1"
  local default_value="${2:-}"
  local answer=""

  if [[ -e /dev/tty ]]; then
    { printf '%s' "${prompt}" > /dev/tty; } 2>/dev/null || true
    if { IFS= read -r answer < /dev/tty; } 2>/dev/null; then
      printf '%s' "${answer}"
      return 0
    fi
  fi

  printf '%s' "${default_value}"
}

confirm_from_tty() {
  local prompt="$1"
  local answer=""

  answer=$(prompt_from_tty "${prompt}" "")
  case "${answer}" in
    y|Y|yes|YES|Yes) return 0 ;;
    *) return 1 ;;
  esac
}

command -v hermes >/dev/null 2>&1 || fail "hermes is not on PATH. Install Hermes Agent first."

log "Hermes version"
hermes --version || warn "Could not read Hermes version; continuing."

if hermes profile list >/dev/null 2>&1; then
  log "Available Hermes profiles"
  hermes profile list || true
fi

PROFILE_NAME="${ADW_PROFILE:-}"
if [[ -z "${PROFILE_NAME}" ]]; then
  printf '\n'
  PROFILE_NAME=$(prompt_from_tty "Target Hermes profile (leave empty for default): " "")
elif [[ "${PROFILE_NAME}" == "default" ]]; then
  PROFILE_NAME=""
fi

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
REMOVE_EXISTING="${ADW_REMOVE_EXISTING:-}"
if [[ -z "${REMOVE_EXISTING}" ]]; then
  if confirm_from_tty "Remove previous ADW-owned skills and plugin installs? [y/N]: "; then
    REMOVE_EXISTING="yes"
  else
    REMOVE_EXISTING="no"
  fi
fi

case "${REMOVE_EXISTING}" in
  y|Y|yes|YES|Yes|true|TRUE|1)
    for skill in "${ADW_INSTALLED_SKILL_NAMES[@]}"; do
      printf '+ '
      printf '%q ' "${HERMES_CMD[@]}" skills uninstall "${skill}"
      printf '\n'
      if ! printf 'y\n' | "${HERMES_CMD[@]}" skills uninstall "${skill}"; then
        warn "Command failed but is optional/idempotent: ${HERMES_CMD[*]} skills uninstall ${skill}"
      fi
    done

    log "Removing previous ADW plugin installs (safe if not installed)"
    for plugin in "${PLUGIN_NAME}" "agentic-delivery"; do
      printf '+ '
      printf '%q ' "${HERMES_CMD[@]}" plugins remove "${plugin}"
      printf '\n'
      if ! printf 'y\n' | "${HERMES_CMD[@]}" plugins remove "${plugin}"; then
        warn "Command failed but is optional/idempotent: ${HERMES_CMD[*]} plugins remove ${plugin}"
      fi
    done
    ;;
  *)
    warn "Skipping removal of previous ADW installs. Set ADW_REMOVE_EXISTING=yes to force cleanup."
    ;;
esac

log "Adding/updating ADW skill tap"
run_optional "${HERMES_CMD[@]}" skills tap add "${REPO}"

log "Installing ADW skills"
for skill_dir in "${ADW_SKILLS[@]}"; do
  run_required "${HERMES_CMD[@]}" skills install --yes "${REPO}/skills/adw/${skill_dir}"
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
