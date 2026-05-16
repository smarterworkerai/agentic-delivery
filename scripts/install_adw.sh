#!/usr/bin/env bash
set -euo pipefail

REPO="smarterworkerai/agentic-delivery"
PLUGIN_NAME="adw"
ADW_REF="${ADW_REF:-feature/initial-skills}"
ADW_ARCHIVE_URL="https://github.com/${REPO}/archive/refs/heads/${ADW_REF}.tar.gz"
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

usage() {
  cat <<'USAGE'
Usage: install_adw.sh [--uninstall] [--help]

Install options are controlled with environment variables:
  ADW_PROFILE=<profile>              Target Hermes profile; default profile when empty.
  ADW_INSTALL_SOUL=yes|no            Install ADW SOUL.md into the profile root.
  ADW_REMOVE_EXISTING=yes|no         Remove existing ADW-owned files before install.
  ADW_REF=<branch-or-tag>            Git ref to fetch; defaults to feature/initial-skills.

Uninstall options:
  --uninstall                        Remove ADW-owned skills and plugin files.
  ADW_UNINSTALL_SOUL=yes|no          Also remove profile SOUL.md, but only when it
                                     matches the installed ADW plugin copy.

Pipe usage:
  curl -fsSL <install_adw.sh URL> | bash
  curl -fsSL <install_adw.sh URL> | bash -s -- --uninstall
USAGE
}

UNINSTALL="${ADW_UNINSTALL:-no}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --uninstall)
      UNINSTALL="yes"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown argument: $1"
      ;;
  esac
done

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

is_truthy() {
  case "${1:-}" in
    y|Y|yes|YES|Yes|true|TRUE|1) return 0 ;;
    *) return 1 ;;
  esac
}

command -v hermes >/dev/null 2>&1 || fail "hermes is not on PATH. Install Hermes Agent first."
if ! is_truthy "${UNINSTALL}"; then
  command -v curl >/dev/null 2>&1 || fail "curl is not on PATH."
  command -v tar >/dev/null 2>&1 || fail "tar is not on PATH."
fi

TMP_DIR=""
cleanup_tmp() {
  if [[ -n "${TMP_DIR}" && -d "${TMP_DIR}" ]]; then
    rm -rf "${TMP_DIR}"
  fi
}
trap cleanup_tmp EXIT

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

CONFIG_PATH=$("${HERMES_CMD[@]}" config path 2>/dev/null || true)
if [[ -z "${CONFIG_PATH}" ]]; then
  fail "Could not resolve Hermes profile config path."
fi
HERMES_HOME_DIR=$(cd "$(dirname "${CONFIG_PATH}")" && pwd)
log "Target Hermes home: ${HERMES_HOME_DIR}"

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

remove_adw_owned_files() {
  log "Removing ADW-owned skills (safe if not installed)"
  for skill in "${ADW_INSTALLED_SKILL_NAMES[@]}"; do
    target="${HERMES_HOME_DIR}/skills/adw/${skill}"
    printf '+ remove local skill %s\n' "${target}"
    rm -rf "${target}"
  done
  rmdir "${HERMES_HOME_DIR}/skills/adw" 2>/dev/null || true

  log "Disabling ADW plugin if Hermes supports it"
  run_optional "${HERMES_CMD[@]}" plugins disable "${PLUGIN_NAME}"
  run_optional "${HERMES_CMD[@]}" plugins disable "agentic-delivery"

  log "Removing ADW plugin files (safe if not installed)"
  for plugin in "${PLUGIN_NAME}" "agentic-delivery"; do
    printf '+ remove local plugin %s\n' "${HERMES_HOME_DIR}/plugins/${plugin}"
    rm -rf "${HERMES_HOME_DIR}/plugins/${plugin}"
  done
}

remove_adw_soul_if_safe() {
  local soul_target="${HERMES_HOME_DIR}/SOUL.md"
  local soul_reference="${HERMES_HOME_DIR}/plugins/${PLUGIN_NAME}/SOUL.md"

  if [[ ! -f "${soul_target}" ]]; then
    warn "No profile SOUL.md found; nothing to remove."
    return 0
  fi

  if [[ ! -f "${soul_reference}" ]]; then
    warn "Cannot verify SOUL.md ownership because ${soul_reference} is missing; leaving SOUL.md unchanged."
    return 0
  fi

  if cmp -s "${soul_reference}" "${soul_target}"; then
    SOUL_BACKUP="${soul_target}.bak.$(date +%Y%m%d%H%M%S)"
    printf '+ backup ADW SOUL.md -> %s\n' "${SOUL_BACKUP}"
    cp "${soul_target}" "${SOUL_BACKUP}"
    printf '+ remove ADW SOUL.md %s\n' "${soul_target}"
    rm -f "${soul_target}"
  else
    warn "Profile SOUL.md differs from the installed ADW copy; leaving it unchanged."
  fi
}

if is_truthy "${UNINSTALL}"; then
  log "Uninstalling ADW from target Hermes profile"

  UNINSTALL_SOUL="${ADW_UNINSTALL_SOUL:-}"
  if [[ -z "${UNINSTALL_SOUL}" ]]; then
    if confirm_from_tty "Also remove profile SOUL.md if it matches the installed ADW copy? [y/N]: "; then
      UNINSTALL_SOUL="yes"
    else
      UNINSTALL_SOUL="no"
    fi
  fi

  if is_truthy "${UNINSTALL_SOUL}"; then
    remove_adw_soul_if_safe
  else
    warn "Leaving profile SOUL.md unchanged. Set ADW_UNINSTALL_SOUL=yes to remove it when safely identifiable."
  fi

  remove_adw_owned_files

  log "ADW uninstall complete"
  printf '%s\n' "Next steps:"
  if [[ -n "${PROFILE_NAME}" ]]; then
    printf '  hermes --profile %q gateway restart\n' "${PROFILE_NAME}"
  else
    printf '%s\n' "  hermes gateway restart"
  fi
  exit 0
fi

INSTALL_SOUL="${ADW_INSTALL_SOUL:-}"
if [[ -z "${INSTALL_SOUL}" ]]; then
  if confirm_from_tty "Install ADW SOUL.md into this Hermes profile? [y/N]: "; then
    INSTALL_SOUL="yes"
  else
    INSTALL_SOUL="no"
  fi
fi

log "Removing previous ADW-owned skills (safe if not installed)"
REMOVE_EXISTING="${ADW_REMOVE_EXISTING:-}"
if [[ -z "${REMOVE_EXISTING}" ]]; then
  if confirm_from_tty "Remove previous ADW-owned skills and plugin installs? [y/N]: "; then
    REMOVE_EXISTING="yes"
  else
    REMOVE_EXISTING="no"
  fi
fi

if is_truthy "${REMOVE_EXISTING}"; then
  remove_adw_owned_files
else
  warn "Skipping removal of previous ADW installs. Set ADW_REMOVE_EXISTING=yes to force cleanup."
fi

log "Fetching ADW source (${REPO}@${ADW_REF})"
TMP_DIR=$(mktemp -d)
ADW_SOURCE_DIR="${TMP_DIR}/source"
mkdir -p "${ADW_SOURCE_DIR}"
run_required curl -fsSL "${ADW_ARCHIVE_URL}" -o "${TMP_DIR}/adw.tar.gz"
run_required tar -xzf "${TMP_DIR}/adw.tar.gz" -C "${ADW_SOURCE_DIR}" --strip-components=1

if is_truthy "${INSTALL_SOUL}"; then
  [[ -f "${ADW_SOURCE_DIR}/SOUL.md" ]] || fail "Missing SOUL.md in fetched source."
  log "Installing ADW SOUL.md into target profile"
  SOUL_TARGET="${HERMES_HOME_DIR}/SOUL.md"
  if [[ -f "${SOUL_TARGET}" ]] && ! cmp -s "${ADW_SOURCE_DIR}/SOUL.md" "${SOUL_TARGET}"; then
    SOUL_BACKUP="${SOUL_TARGET}.bak.$(date +%Y%m%d%H%M%S)"
    printf '+ backup existing SOUL.md -> %s\n' "${SOUL_BACKUP}"
    cp "${SOUL_TARGET}" "${SOUL_BACKUP}"
  fi
  printf '+ install SOUL.md -> %s\n' "${SOUL_TARGET}"
  cp "${ADW_SOURCE_DIR}/SOUL.md" "${SOUL_TARGET}"
else
  warn "Skipping ADW SOUL.md install. Set ADW_INSTALL_SOUL=yes to force installation."
fi

log "Installing ADW skills from fetched source"
mkdir -p "${HERMES_HOME_DIR}/skills/adw"
for skill_dir in "${ADW_SKILLS[@]}"; do
  src="${ADW_SOURCE_DIR}/skills/adw/${skill_dir}"
  [[ -f "${src}/SKILL.md" ]] || fail "Missing skill package: ${src}/SKILL.md"

  skill_name=$(grep -m1 '^name:' "${src}/SKILL.md" | cut -d: -f2- | xargs)
  [[ -n "${skill_name}" ]] || fail "Could not resolve skill name from ${src}/SKILL.md"

  target="${HERMES_HOME_DIR}/skills/adw/${skill_name}"
  printf '+ install skill %s -> %s\n' "${skill_name}" "${target}"
  rm -rf "${target}"
  mkdir -p "${target}"
  tar -C "${src}" -cf - . | tar -C "${target}" -xf -
done

log "Installing and enabling ADW plugin from fetched source"
mkdir -p "${HERMES_HOME_DIR}/plugins"
PLUGIN_TARGET="${HERMES_HOME_DIR}/plugins/${PLUGIN_NAME}"
printf '+ install plugin %s -> %s\n' "${PLUGIN_NAME}" "${PLUGIN_TARGET}"
rm -rf "${PLUGIN_TARGET}"
mkdir -p "${PLUGIN_TARGET}"
tar -C "${ADW_SOURCE_DIR}" --exclude='.git' -cf - . | tar -C "${PLUGIN_TARGET}" -xf -
run_required "${HERMES_CMD[@]}" plugins enable "${PLUGIN_NAME}"

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
