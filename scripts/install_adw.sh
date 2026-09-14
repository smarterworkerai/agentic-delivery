#!/usr/bin/env bash
set -euo pipefail

REPO="smarterworkerai/agentic-delivery"
PLUGIN_NAME="adw"
OWNER_MARKER=".agentic-delivery-owner"
OWNER_VALUE="agentic-delivery/v1"
ADW_SKILLS=(
  "adw-core"
  "plan-feature"
  "plan-bugfix"
  "do-impl"
  "do-impl-delegate"
  "test-feature"
  "merge-feature"
  "rollback-deployment"
  "validate-regression"
  "create-adr"
  "audit-dependencies"
  "analyze-production"
  "chain"
  "self-improve"
)
ADW_INSTALLED_SKILL_NAMES=(
  "adw-core"
  "adw-plan-feature"
  "adw-plan-bugfix"
  "adw-do-impl"
  "adw-do-impl-delegate"
  "adw-test-feature"
  "adw-merge-feature"
  "adw-rollback-deployment"
  "adw-validate-regression"
  "adw-create-adr"
  "adw-audit-dependencies"
  "adw-analyze-production"
  "adw-chain"
  "adw-self-improve"
)

log() { printf '\n==> %s\n' "$*"; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'USAGE'
Usage: install_adw.sh [--uninstall] [--help]

Install variables:
  ADW_REF=<40-char-lowercase-commit-sha>  Required immutable source revision.
  ADW_ARCHIVE_SHA256=<64-char-sha256>     Required source archive checksum.
  ADW_PROFILE=<profile>                   Target profile; empty means default.
  ADW_INSTALL_SOUL=yes|no                 Install the package SOUL.md.
  ADW_REPLACE_UNMANAGED=yes|no            Explicitly replace colliding paths not
                                          marked as agentic-delivery-owned.

Uninstall variables:
  ADW_PROFILE=<profile>                   Target profile; empty means default.
  ADW_UNINSTALL_SOUL=yes|no               Remove profile SOUL.md only when it
                                          matches the installed package copy.

The installer validates the fetched source and stages the complete payload before
replacing any active path. Uninstall removes marker-owned paths only.
USAGE
}

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
  local answer=""
  answer=$(prompt_from_tty "$1" "")
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

UNINSTALL="${ADW_UNINSTALL:-no}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --uninstall) UNINSTALL="yes"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) fail "Unknown argument: $1" ;;
  esac
done

command -v hermes >/dev/null 2>&1 || fail "hermes is not on PATH. Install Hermes Agent first."

PROFILE_NAME="${ADW_PROFILE:-}"
if [[ -z "${PROFILE_NAME}" ]]; then
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

CONFIG_PATH=$("${HERMES_CMD[@]}" config path)
[[ -n "${CONFIG_PATH}" ]] || fail "Could not resolve Hermes profile config path."
HERMES_HOME_DIR=$(cd "$(dirname "${CONFIG_PATH}")" && pwd)
[[ "${HERMES_HOME_DIR}" != "/" ]] || fail "Refusing to use filesystem root as Hermes home."
log "Target Hermes home: ${HERMES_HOME_DIR}"

LOCK_DIR="${HERMES_HOME_DIR}/.adw-install.lock"
if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
  fail "Another ADW install or uninstall is active for this profile: ${LOCK_DIR}"
fi
TMP_DIR=""
cleanup() {
  if [[ -n "${TMP_DIR}" && -d "${TMP_DIR}" ]]; then
    rm -rf "${TMP_DIR}"
  fi
  rmdir "${LOCK_DIR}" 2>/dev/null || warn "Could not remove installer lock ${LOCK_DIR}."
}
trap cleanup EXIT

path_exists() {
  [[ -e "$1" || -L "$1" ]]
}

is_owned_path() {
  local target="$1"
  local marker="${target}/${OWNER_MARKER}"
  [[ -d "${target}" && ! -L "${target}" && -f "${marker}" && ! -L "${marker}" ]] &&
    [[ "$(<"${marker}")" == "${OWNER_VALUE}" ]]
}

device_id() {
  if stat -c '%d' "$1" >/dev/null 2>&1; then
    stat -c '%d' "$1"
  else
    stat -f '%d' "$1"
  fi
}

archive_sha256() {
  local archive="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "${archive}" | python3 -c 'import sys; print(sys.stdin.read().split()[0])'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "${archive}" | python3 -c 'import sys; print(sys.stdin.read().split()[0])'
  else
    fail "sha256sum or shasum is required."
  fi
}

remove_owned_path() {
  local target="$1"
  if ! path_exists "${target}"; then
    return 0
  fi
  if ! is_owned_path "${target}"; then
    warn "Leaving unmanaged path unchanged: ${target}"
    return 0
  fi
  printf '+ remove marker-owned path %s\n' "${target}"
  rm -rf "${target}"
}

remove_adw_soul_if_safe() {
  local soul_target="${HERMES_HOME_DIR}/SOUL.md"
  local soul_reference="${HERMES_HOME_DIR}/plugins/${PLUGIN_NAME}/SOUL.md"
  if ! path_exists "${soul_target}"; then
    return 0
  fi
  if [[ -L "${soul_target}" ]] || ! is_owned_path "${HERMES_HOME_DIR}/plugins/${PLUGIN_NAME}" || [[ ! -f "${soul_reference}" || -L "${soul_reference}" ]]; then
    warn "Cannot prove ADW ownership of profile SOUL.md; leaving it unchanged."
    return 0
  fi
  if cmp -s "${soul_reference}" "${soul_target}"; then
    local backup="${soul_target}.bak.$(date +%Y%m%d%H%M%S)"
    cp "${soul_target}" "${backup}"
    rm -f "${soul_target}"
    printf '+ removed matching ADW SOUL.md; backup: %s\n' "${backup}"
  else
    warn "Profile SOUL.md differs from the installed ADW copy; leaving it unchanged."
  fi
}

if is_truthy "${UNINSTALL}"; then
  UNINSTALL_SOUL="${ADW_UNINSTALL_SOUL:-}"
  if [[ -z "${UNINSTALL_SOUL}" ]]; then
    if confirm_from_tty "Remove profile SOUL.md when ownership and content match? [y/N]: "; then
      UNINSTALL_SOUL="yes"
    else
      UNINSTALL_SOUL="no"
    fi
  fi
  if is_owned_path "${HERMES_HOME_DIR}/plugins/${PLUGIN_NAME}"; then
    "${HERMES_CMD[@]}" plugins disable "${PLUGIN_NAME}" || fail "Could not disable plugin; no installed paths were removed."
  fi
  if is_truthy "${UNINSTALL_SOUL}"; then
    remove_adw_soul_if_safe
  fi
  for skill_name in "${ADW_INSTALLED_SKILL_NAMES[@]}"; do
    remove_owned_path "${HERMES_HOME_DIR}/skills/adw/${skill_name}"
  done
  remove_owned_path "${HERMES_HOME_DIR}/plugins/${PLUGIN_NAME}"
  rmdir "${HERMES_HOME_DIR}/skills/adw" 2>/dev/null || true
  log "ADW uninstall complete"
  exit 0
fi

command -v curl >/dev/null 2>&1 || fail "curl is not on PATH."
command -v tar >/dev/null 2>&1 || fail "tar is not on PATH."
command -v python3 >/dev/null 2>&1 || fail "python3 is not on PATH."

ADW_REF="${ADW_REF:-}"
if [[ -z "${ADW_REF}" ]]; then
  ADW_REF=$(prompt_from_tty "Exact lowercase 40-character ADW commit SHA: " "")
fi
[[ "${ADW_REF}" =~ ^[0-9a-f]{40}$ ]] || fail "ADW_REF must be an immutable lowercase 40-character Git commit SHA."
ADW_ARCHIVE_SHA256="${ADW_ARCHIVE_SHA256:-}"
[[ "${ADW_ARCHIVE_SHA256}" =~ ^[0-9a-f]{64}$ ]] || fail "ADW_ARCHIVE_SHA256 must be the expected lowercase SHA-256 of the source archive."
ADW_ARCHIVE_URL="https://codeload.github.com/${REPO}/tar.gz/${ADW_REF}"

TMP_DIR=$(mktemp -d "${HERMES_HOME_DIR}/.adw-install.XXXXXX")
SOURCE_DIR="${TMP_DIR}/source"
mkdir -p "${SOURCE_DIR}"

log "Fetching immutable ADW source ${REPO}@${ADW_REF}"
curl -fsSL "${ADW_ARCHIVE_URL}" -o "${TMP_DIR}/adw.tar.gz"
ACTUAL_ARCHIVE_SHA256=$(archive_sha256 "${TMP_DIR}/adw.tar.gz")
[[ "${ACTUAL_ARCHIVE_SHA256}" == "${ADW_ARCHIVE_SHA256}" ]] || fail "Source archive checksum mismatch."
tar -xzf "${TMP_DIR}/adw.tar.gz" -C "${SOURCE_DIR}" --strip-components=1

log "Preflight validation"
for required in plugin.yaml __init__.py SOUL.md adw_plugin/router.py adw_plugin/registry.py adw_plugin/prompts.py tools/validate_adw_skills.py; do
  [[ -f "${SOURCE_DIR}/${required}" ]] || fail "Fetched source is missing ${required}."
done
for skill_dir in "${ADW_SKILLS[@]}"; do
  [[ -f "${SOURCE_DIR}/skills/adw/${skill_dir}/SKILL.md" ]] || fail "Fetched source is missing skill ${skill_dir}."
done
python3 "${SOURCE_DIR}/tools/validate_adw_skills.py"
"${HERMES_CMD[@]}" plugins doctor "${SOURCE_DIR}" --ci

PLUGIN_WAS_ENABLED=$(
  "${HERMES_CMD[@]}" plugins list --enabled --json |
    python3 -c 'import json,sys; print("yes" if any(item.get("name") == "adw" for item in json.load(sys.stdin)) else "no")'
) || fail "Could not inspect the current plugin enable state."

STAGE_ROOT="${TMP_DIR}/stage"
STAGED_SKILLS="${STAGE_ROOT}/skills"
STAGED_PLUGIN="${STAGE_ROOT}/plugin"
BACKUP_ROOT="${TMP_DIR}/backup"
mkdir -p "${STAGED_SKILLS}" "${STAGED_PLUGIN}" "${BACKUP_ROOT}"

for skill_dir in "${ADW_SKILLS[@]}"; do
  src="${SOURCE_DIR}/skills/adw/${skill_dir}"
  skill_name=$(python3 -c 'import sys; from pathlib import Path; print(next(line.split(":",1)[1].strip() for line in Path(sys.argv[1]).read_text().splitlines() if line.startswith("name:")))' "${src}/SKILL.md")
  [[ -n "${skill_name}" ]] || fail "Could not resolve skill name from ${src}/SKILL.md."
  target="${STAGED_SKILLS}/${skill_name}"
  mkdir -p "${target}"
  tar -C "${src}" --exclude='__pycache__' --exclude='*.pyc' -cf - . | tar -C "${target}" -xf -
  printf '%s\n' "${OWNER_VALUE}" > "${target}/${OWNER_MARKER}"
done

cp "${SOURCE_DIR}/plugin.yaml" "${SOURCE_DIR}/__init__.py" "${SOURCE_DIR}/SOUL.md" "${STAGED_PLUGIN}/"
mkdir -p "${STAGED_PLUGIN}/adw_plugin"
tar -C "${SOURCE_DIR}/adw_plugin" --exclude='__pycache__' --exclude='*.pyc' -cf - . | tar -C "${STAGED_PLUGIN}/adw_plugin" -xf -
printf '%s\n' "${OWNER_VALUE}" > "${STAGED_PLUGIN}/${OWNER_MARKER}"
"${HERMES_CMD[@]}" plugins doctor "${STAGED_PLUGIN}" --ci

REPLACE_UNMANAGED="${ADW_REPLACE_UNMANAGED:-no}"
for skill_name in "${ADW_INSTALLED_SKILL_NAMES[@]}"; do
  target="${HERMES_HOME_DIR}/skills/adw/${skill_name}"
  if path_exists "${target}" && ! is_owned_path "${target}" && ! is_truthy "${REPLACE_UNMANAGED}"; then
    fail "Refusing unmanaged collision at ${target}; set ADW_REPLACE_UNMANAGED=yes only after review."
  fi
done
PLUGIN_TARGET="${HERMES_HOME_DIR}/plugins/${PLUGIN_NAME}"
if path_exists "${PLUGIN_TARGET}" && ! is_owned_path "${PLUGIN_TARGET}" && ! is_truthy "${REPLACE_UNMANAGED}"; then
  fail "Refusing unmanaged collision at ${PLUGIN_TARGET}; set ADW_REPLACE_UNMANAGED=yes only after review."
fi

INSTALL_SOUL="${ADW_INSTALL_SOUL:-}"
if [[ -z "${INSTALL_SOUL}" ]]; then
  if confirm_from_tty "Install ADW SOUL.md into this Hermes profile? [y/N]: "; then
    INSTALL_SOUL="yes"
  else
    INSTALL_SOUL="no"
  fi
fi

SOUL_TARGET="${HERMES_HOME_DIR}/SOUL.md"
if is_truthy "${INSTALL_SOUL}" && path_exists "${SOUL_TARGET}" && ! is_truthy "${REPLACE_UNMANAGED}"; then
  if [[ -L "${SOUL_TARGET}" || ! -f "${SOUL_TARGET}" ]] || ! cmp -s "${SOURCE_DIR}/SOUL.md" "${SOUL_TARGET}"; then
    fail "Refusing to replace existing profile SOUL.md; set ADW_REPLACE_UNMANAGED=yes only after review."
  fi
fi

TARGETS=()
STAGED=()
POLICIES=()
for skill_name in "${ADW_INSTALLED_SKILL_NAMES[@]}"; do
  TARGETS+=("${HERMES_HOME_DIR}/skills/adw/${skill_name}")
  STAGED+=("${STAGED_SKILLS}/${skill_name}")
  POLICIES+=("owned")
done
TARGETS+=("${PLUGIN_TARGET}")
STAGED+=("${STAGED_PLUGIN}")
POLICIES+=("owned")
if is_truthy "${INSTALL_SOUL}"; then
  TARGETS+=("${SOUL_TARGET}")
  STAGED+=("${SOURCE_DIR}/SOUL.md")
  POLICIES+=("identical")
fi

mkdir -p "${HERMES_HOME_DIR}/skills/adw" "${HERMES_HOME_DIR}/plugins"
for index in "${!TARGETS[@]}"; do
  target_parent=$(dirname "${TARGETS[$index]}")
  if [[ "$(device_id "${STAGED[$index]}")" != "$(device_id "${target_parent}")" ]]; then
    fail "Staged payload and target parent are on different filesystems: ${TARGETS[$index]}"
  fi
done
BACKUPS=()
ACTIVATED=0
activation_failed="no"
set +e
for index in "${!TARGETS[@]}"; do
  target="${TARGETS[$index]}"
  staged="${STAGED[$index]}"
  policy="${POLICIES[$index]}"
  backup="${BACKUP_ROOT}/${index}"
  BACKUPS+=("")
  if path_exists "${target}"; then
    if ! mv "${target}" "${backup}"; then activation_failed="yes"; break; fi
    BACKUPS[$index]="${backup}"
  fi
  ACTIVATED=$((index + 1))
  if [[ -n "${BACKUPS[$index]}" ]] && ! is_truthy "${REPLACE_UNMANAGED}"; then
    if [[ "${policy}" == "owned" ]] && ! is_owned_path "${backup}"; then
      activation_failed="yes"
      break
    fi
    if [[ "${policy}" == "identical" ]] && { [[ -L "${backup}" || ! -f "${backup}" ]] || ! cmp -s "${staged}" "${backup}"; }; then
      activation_failed="yes"
      break
    fi
  fi
  if [[ -d "${staged}" ]]; then
    mv "${staged}" "${target}"
  else
    cp "${staged}" "${target}"
  fi
  if [[ $? -ne 0 ]]; then activation_failed="yes"; break; fi
done
set -e

rollback_activation() {
  local index
  local rollback_failed="no"
  set +e
  for ((index=ACTIVATED-1; index>=0; index--)); do
    rm -rf "${TARGETS[$index]}" || rollback_failed="yes"
    if [[ -n "${BACKUPS[$index]:-}" ]] && path_exists "${BACKUPS[$index]}"; then
      mv "${BACKUPS[$index]}" "${TARGETS[$index]}" || rollback_failed="yes"
    fi
  done
  set -e
  [[ "${rollback_failed}" == "no" ]]
}

rollback_and_fail() {
  local message="$1"
  local rollback_failed="no"
  if ! rollback_activation; then
    warn "One or more filesystem rollback operations failed."
    rollback_failed="yes"
  fi
  if [[ "${PLUGIN_WAS_ENABLED}" == "yes" ]]; then
    if ! "${HERMES_CMD[@]}" plugins enable "${PLUGIN_NAME}" >/dev/null 2>&1; then
      warn "Could not restore the prior enabled plugin state."
      rollback_failed="yes"
    fi
  else
    if ! "${HERMES_CMD[@]}" plugins disable "${PLUGIN_NAME}" >/dev/null 2>&1; then
      warn "Could not restore the prior disabled plugin state."
      rollback_failed="yes"
    fi
  fi
  if [[ "${rollback_failed}" == "yes" ]]; then
    fail "${message}; rollback is incomplete and requires inspection."
  fi
  fail "${message}; prior paths and plugin state were restored."
}

if is_truthy "${activation_failed}"; then
  rollback_and_fail "Activation failed"
fi

if ! "${HERMES_CMD[@]}" plugins enable "${PLUGIN_NAME}"; then
  rollback_and_fail "Plugin enable failed"
fi

log "Post-install verification"
if ! "${HERMES_CMD[@]}" plugins doctor "${PLUGIN_TARGET}" --ci; then
  rollback_and_fail "Installed plugin validation failed"
fi
for skill_name in "${ADW_INSTALLED_SKILL_NAMES[@]}"; do
  skill_file="${HERMES_HOME_DIR}/skills/adw/${skill_name}/SKILL.md"
  [[ -f "${skill_file}" ]] || rollback_and_fail "Missing installed skill ${skill_name}."
  grep -Eq "^name:[[:space:]]*${skill_name}[[:space:]]*$" "${skill_file}" || rollback_and_fail "Unexpected skill name in ${skill_file}."
  is_owned_path "${HERMES_HOME_DIR}/skills/adw/${skill_name}" || rollback_and_fail "Missing ownership marker for ${skill_name}."
done

log "ADW installation complete at ${ADW_REF}"
printf '%s\n' "Restart the gateway from a separate shell, then try /adw."
