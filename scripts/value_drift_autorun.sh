#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/runs/value-drift-autorun"
UPDATE_DIR="${ROOT_DIR}/research_updates"
LOCK_DIR="${ROOT_DIR}/.value-drift-autorun.lock"

MODEL="${VALUE_DRIFT_CODEX_MODEL:-gpt-5-mini}"
DRAFT_FILE="${VALUE_DRIFT_DRAFT_FILE:-draft/multilingual_value_drift_neurips.tex}"
PROMPT_FILE="${VALUE_DRIFT_PROMPT_FILE:-prompts/value_drift_autorun_prompt.md}"
MAX_PASSES="${VALUE_DRIFT_MAX_PASSES:-0}"
SLEEP_ON_LIMIT_SECONDS="${VALUE_DRIFT_SLEEP_ON_LIMIT_SECONDS:-18000}"
SLEEP_BETWEEN_PASSES_SECONDS="${VALUE_DRIFT_SLEEP_BETWEEN_PASSES_SECONDS:-0}"
CONTINUE_ON_ERROR="${VALUE_DRIFT_CONTINUE_ON_ERROR:-0}"
SANDBOX_MODE="${VALUE_DRIFT_SANDBOX:-workspace-write}"
APPROVAL_MODE="${VALUE_DRIFT_APPROVAL:-never}"
NETWORK_ACCESS="${VALUE_DRIFT_NETWORK_ACCESS:-true}"
EXTRA_CODEX_ARGS="${VALUE_DRIFT_EXTRA_CODEX_ARGS:-}"
DRY_RUN="${VALUE_DRIFT_DRY_RUN:-0}"
GIT_PUSH="${VALUE_DRIFT_GIT_PUSH:-1}"
GIT_REMOTE="${VALUE_DRIFT_GIT_REMOTE:-origin}"
GIT_BRANCH="${VALUE_DRIFT_GIT_BRANCH:-}"

resolve_path() {
  local path="$1"
  if [[ "${path}" = /* ]]; then
    echo "${path}"
  else
    echo "${ROOT_DIR}/${path}"
  fi
}

timestamp() {
  date -u +"%Y%m%dT%H%M%SZ"
}

usage() {
  cat <<USAGE
Usage: VALUE_DRIFT_MAX_PASSES=1 ./scripts/value_drift_autorun.sh

Runs Codex passes that use ${DRAFT_FILE} as context and keep iterating until a configured
pass limit, a non-limit failure, or manual interruption. If Codex stops because logs look
like a quota/rate/token limit, the harness sleeps for ${SLEEP_ON_LIMIT_SECONDS} seconds
before retrying.

Key environment variables:
  VALUE_DRIFT_CODEX_MODEL              default: ${MODEL}
  VALUE_DRIFT_MAX_PASSES               default: ${MAX_PASSES} (0 means unlimited)
  VALUE_DRIFT_SLEEP_ON_LIMIT_SECONDS   default: ${SLEEP_ON_LIMIT_SECONDS}
  VALUE_DRIFT_SLEEP_BETWEEN_PASSES_SECONDS default: ${SLEEP_BETWEEN_PASSES_SECONDS}
  VALUE_DRIFT_CONTINUE_ON_ERROR        default: ${CONTINUE_ON_ERROR}
  VALUE_DRIFT_NETWORK_ACCESS           default: ${NETWORK_ACCESS}
  VALUE_DRIFT_EXTRA_CODEX_ARGS         appended to codex exec
  VALUE_DRIFT_DRY_RUN                  build the first prompt and exit without running Codex
  VALUE_DRIFT_GIT_PUSH                 default: ${GIT_PUSH} (1 commits and pushes after each pass)
  VALUE_DRIFT_GIT_REMOTE               default: ${GIT_REMOTE}
  VALUE_DRIFT_GIT_BRANCH               default: current branch
USAGE
}

looks_like_limit_stop() {
  local log_file="$1"
  local last_file="$2"
  local combined="${RUN_DIR}/.last-combined-error.txt"
  : > "${combined}"
  [[ -f "${log_file}" ]] && cat "${log_file}" >> "${combined}"
  [[ -f "${last_file}" ]] && cat "${last_file}" >> "${combined}"

  grep -Eiq \
    'rate.?limit|usage.?limit|quota|429|too many requests|token.?limit|context.?length|context_length_exceeded|exceeded.*tokens|limit.*refresh|try again later' \
    "${combined}"
}

build_prompt() {
  local update_file="$1"
  local prompt_path="$2"
  local draft_path="$3"
  local draft_rel="$4"
  local prompt_rel="$5"

  cat "${prompt_path}"
  cat <<PROMPT

Harness metadata:
- Repository root: ${ROOT_DIR}
- Draft path: ${draft_rel}
- Draft absolute path: ${draft_path}
- Base prompt path: ${prompt_rel}
- Research update path for this pass: ${update_file}
- Codex model: ${MODEL}
- Network access requested: ${NETWORK_ACCESS}

The paper draft is embedded below as context. Still read the on-disk draft before changing files.

<draft path="${draft_rel}">
PROMPT
  cat "${draft_path}"
  cat <<'PROMPT'
</draft>
PROMPT
}

push_repo_state() {
  local pass="$1"
  local stamp="$2"
  local outcome="$3"

  if [[ "${GIT_PUSH}" != "1" ]]; then
    return 0
  fi
  if ! git -C "${ROOT_DIR}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "git push skipped: ${ROOT_DIR} is not a git worktree" >&2
    return 1
  fi
  if ! git -C "${ROOT_DIR}" remote get-url "${GIT_REMOTE}" >/dev/null 2>&1; then
    echo "git push skipped: remote not found: ${GIT_REMOTE}" >&2
    return 1
  fi

  local branch="${GIT_BRANCH}"
  if [[ -z "${branch}" ]]; then
    branch="$(git -C "${ROOT_DIR}" branch --show-current)"
  fi
  if [[ -z "${branch}" ]]; then
    echo "git push skipped: cannot determine current branch; set VALUE_DRIFT_GIT_BRANCH" >&2
    return 1
  fi

  git -C "${ROOT_DIR}" add -A
  if ! git -C "${ROOT_DIR}" diff --cached --quiet; then
    git -C "${ROOT_DIR}" commit -m "value drift autorun: pass ${pass} ${outcome} ${stamp}"
  else
    echo "no worktree changes to commit before push"
  fi

  git -C "${ROOT_DIR}" push "${GIT_REMOTE}" "HEAD:${branch}"
}

run_one_pass() {
  local pass="$1"
  local stamp="$2"
  local draft_path="$3"
  local prompt_path="$4"
  local draft_rel="$5"
  local prompt_rel="$6"

  local update_file="${UPDATE_DIR}/${stamp}-value-drift-pass-${pass}.md"
  local prompt_out="${RUN_DIR}/${stamp}-pass-${pass}.prompt.txt"
  local log_file="${RUN_DIR}/${stamp}-pass-${pass}.log"
  local last_file="${RUN_DIR}/${stamp}-pass-${pass}.last.md"
  local status_file="${RUN_DIR}/${stamp}-pass-${pass}.status"

  build_prompt "${update_file}" "${prompt_path}" "${draft_path}" "${draft_rel}" "${prompt_rel}" > "${prompt_out}"

  local cmd=(codex exec --cd "${ROOT_DIR}" --ask-for-approval "${APPROVAL_MODE}" --sandbox "${SANDBOX_MODE}" --model "${MODEL}" --output-last-message "${last_file}")
  if [[ "${SANDBOX_MODE}" == "workspace-write" && "${NETWORK_ACCESS}" == "true" ]]; then
    cmd+=(-c sandbox_workspace_write.network_access=true)
  fi
  if [[ -n "${EXTRA_CODEX_ARGS}" ]]; then
    # shellcheck disable=SC2206
    local extra_args=( ${EXTRA_CODEX_ARGS} )
    cmd+=("${extra_args[@]}")
  fi

  echo "starting value-drift Codex pass ${pass} at ${stamp}"
  if "${cmd[@]}" - < "${prompt_out}" > "${log_file}" 2>&1; then
    echo "success" > "${status_file}"
    echo "pass ${pass} completed"
    push_repo_state "${pass}" "${stamp}" "success"
    return 0
  fi

  local rc=$?
  echo "failed:${rc}" > "${status_file}"
  echo "pass ${pass} failed with status ${rc}; log: ${log_file}" >&2
  push_repo_state "${pass}" "${stamp}" "failed-${rc}" || true
  return "${rc}"
}

main() {
  if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
  fi

  local draft_path
  local prompt_path
  draft_path="$(resolve_path "${DRAFT_FILE}")"
  prompt_path="$(resolve_path "${PROMPT_FILE}")"

  if [[ ! -f "${draft_path}" ]]; then
    echo "missing draft file: ${draft_path}" >&2
    exit 2
  fi
  if [[ ! -f "${prompt_path}" ]]; then
    echo "missing prompt file: ${prompt_path}" >&2
    exit 2
  fi
  if ! [[ "${MAX_PASSES}" =~ ^[0-9]+$ ]]; then
    echo "VALUE_DRIFT_MAX_PASSES must be a non-negative integer; got ${MAX_PASSES}" >&2
    exit 2
  fi
  if ! [[ "${SLEEP_ON_LIMIT_SECONDS}" =~ ^[0-9]+$ ]]; then
    echo "VALUE_DRIFT_SLEEP_ON_LIMIT_SECONDS must be a non-negative integer; got ${SLEEP_ON_LIMIT_SECONDS}" >&2
    exit 2
  fi

  mkdir -p "${RUN_DIR}" "${UPDATE_DIR}"

  if [[ "${DRY_RUN}" == "1" ]]; then
    local stamp
    stamp="$(timestamp)"
    local prompt_out="${RUN_DIR}/${stamp}-dry-run.prompt.txt"
    local update_file="${UPDATE_DIR}/${stamp}-value-drift-dry-run.md"
    build_prompt "${update_file}" "${prompt_path}" "${draft_path}" "${DRAFT_FILE}" "${PROMPT_FILE}" > "${prompt_out}"
    echo "wrote dry-run prompt: ${prompt_out}"
    exit 0
  fi

  if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
    echo "value-drift autorun already active: ${LOCK_DIR}" >&2
    exit 0
  fi
  trap 'rm -rf "${LOCK_DIR}"' EXIT

  local pass=1
  while true; do
    local stamp
    stamp="$(timestamp)"
    local log_file="${RUN_DIR}/${stamp}-pass-${pass}.log"
    local last_file="${RUN_DIR}/${stamp}-pass-${pass}.last.md"

    if run_one_pass "${pass}" "${stamp}" "${draft_path}" "${prompt_path}" "${DRAFT_FILE}" "${PROMPT_FILE}"; then
      if [[ "${MAX_PASSES}" != "0" && "${pass}" -ge "${MAX_PASSES}" ]]; then
        echo "reached VALUE_DRIFT_MAX_PASSES=${MAX_PASSES}"
        break
      fi
      pass=$((pass + 1))
      if [[ "${SLEEP_BETWEEN_PASSES_SECONDS}" -gt 0 ]]; then
        echo "sleeping ${SLEEP_BETWEEN_PASSES_SECONDS}s before next pass"
        sleep "${SLEEP_BETWEEN_PASSES_SECONDS}"
      fi
      continue
    fi

    if looks_like_limit_stop "${log_file}" "${last_file}"; then
      echo "detected likely quota/rate/token limit; sleeping ${SLEEP_ON_LIMIT_SECONDS}s before retry"
      sleep "${SLEEP_ON_LIMIT_SECONDS}"
      continue
    fi

    if [[ "${CONTINUE_ON_ERROR}" == "1" ]]; then
      echo "non-limit failure; continuing because VALUE_DRIFT_CONTINUE_ON_ERROR=1"
      pass=$((pass + 1))
      continue
    fi

    echo "stopping after non-limit failure"
    exit 1
  done
}

main "$@"
