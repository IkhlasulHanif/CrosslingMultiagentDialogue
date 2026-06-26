#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCHEDULE="${VALUE_DRIFT_CRON_SCHEDULE:-*/30 * * * *}"
LOG_FILE="${ROOT_DIR}/runs/value-drift-autorun/cron.log"
MARKER="# multilingual value drift autorun"

mkdir -p "$(dirname "${LOG_FILE}")"

ENV_PREFIX="VALUE_DRIFT_MAX_PASSES=${VALUE_DRIFT_MAX_PASSES:-0}"

append_env_if_set() {
  local name="$1"
  local value="${!name:-}"
  if [[ -n "${value}" ]]; then
    ENV_PREFIX="${ENV_PREFIX} ${name}=$(printf '%q' "${value}")"
  fi
}

append_env_if_set VALUE_DRIFT_CODEX_MODEL
append_env_if_set VALUE_DRIFT_DRAFT_FILE
append_env_if_set VALUE_DRIFT_PROMPT_FILE
append_env_if_set VALUE_DRIFT_SLEEP_ON_LIMIT_SECONDS
append_env_if_set VALUE_DRIFT_SLEEP_BETWEEN_PASSES_SECONDS
append_env_if_set VALUE_DRIFT_CONTINUE_ON_ERROR
append_env_if_set VALUE_DRIFT_SANDBOX
append_env_if_set VALUE_DRIFT_APPROVAL
append_env_if_set VALUE_DRIFT_NETWORK_ACCESS
append_env_if_set VALUE_DRIFT_EXTRA_CODEX_ARGS
append_env_if_set VALUE_DRIFT_GIT_PUSH
append_env_if_set VALUE_DRIFT_GIT_REMOTE
append_env_if_set VALUE_DRIFT_GIT_BRANCH

CRON_LINE="${SCHEDULE} cd ${ROOT_DIR} && ${ENV_PREFIX} /bin/bash ${ROOT_DIR}/scripts/value_drift_autorun.sh >> ${LOG_FILE} 2>&1 ${MARKER}"

tmp_file="$(mktemp)"
trap 'rm -f "${tmp_file}"' EXIT

crontab -l 2>/dev/null | grep -v "${MARKER}" > "${tmp_file}" || true
echo "${CRON_LINE}" >> "${tmp_file}"
crontab "${tmp_file}"

echo "Installed cron job:"
echo "${CRON_LINE}"
