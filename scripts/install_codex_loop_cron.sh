#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCHEDULE="${CODEX_LOOP_CRON_SCHEDULE:-17 */5 * * *}"
MAX_ITERS="${CODEX_LOOP_MAX_ITERS:-0}"
REVIEWER="${CODEX_LOOP_REVIEWER:-1}"
LOG_FILE="${ROOT_DIR}/runs/codex-loop/cron.log"
MARKER="# CrosslingMultiagentDialogue codex loop"

mkdir -p "$(dirname "${LOG_FILE}")"

CRON_LINE="${SCHEDULE} cd ${ROOT_DIR} && CODEX_LOOP_MAX_ITERS=${MAX_ITERS} CODEX_LOOP_REVIEWER=${REVIEWER} /bin/bash ${ROOT_DIR}/scripts/codex_loop.sh >> ${LOG_FILE} 2>&1 ${MARKER}"

tmp_file="$(mktemp)"
trap 'rm -f "${tmp_file}"' EXIT

crontab -l 2>/dev/null | grep -v "${MARKER}" > "${tmp_file}" || true
echo "${CRON_LINE}" >> "${tmp_file}"
crontab "${tmp_file}"

echo "Installed cron job:"
echo "${CRON_LINE}"
