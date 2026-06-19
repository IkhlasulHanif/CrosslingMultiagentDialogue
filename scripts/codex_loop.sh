#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${ROOT_DIR}/runs/codex-loop"
RESEARCH_UPDATE_DIR="${ROOT_DIR}/research_updates"
LOCK_DIR="${ROOT_DIR}/.codex-loop.lock"

MODEL="${CODEX_MODEL:-gpt-5-mini}"
MAX_ITERS="${CODEX_LOOP_MAX_ITERS:-1}"
RUN_REVIEWER="${CODEX_LOOP_REVIEWER:-1}"
PUSH_REMOTE="${CODEX_LOOP_REMOTE:-origin}"
PUSH_BRANCH="${CODEX_LOOP_BRANCH:-main}"
SANDBOX_MODE="${CODEX_LOOP_SANDBOX:-workspace-write}"
APPROVAL_MODE="${CODEX_LOOP_APPROVAL:-never}"
NETWORK_ACCESS="${CODEX_LOOP_NETWORK_ACCESS:-true}"
WORK_PROMPT_FILE="${CODEX_LOOP_PROMPT_FILE:-}"
REVIEW_PROMPT_FILE="${CODEX_LOOP_REVIEW_PROMPT_FILE:-}"
SPEC_FILE="${CODEX_LOOP_SPEC_FILE:-docs/harness_design.md}"
RESEARCH_PLAN_FILE="${CODEX_LOOP_RESEARCH_PLAN_FILE:-docs/research_plan.md}"
MAX_DIALOGUES="${CODEX_LOOP_MAX_DIALOGUES:-100}"
TRIAL_MODEL="${CODEX_LOOP_TRIAL_MODEL:-gpt-5-mini}"
ENV_FILE="${CODEX_LOOP_ENV_FILE:-}"

resolve_path() {
  local path="$1"
  if [[ "${path}" = /* ]]; then
    echo "${path}"
  else
    echo "${ROOT_DIR}/${path}"
  fi
}

SPEC_PATH="$(resolve_path "${SPEC_FILE}")"
RESEARCH_PLAN_PATH="$(resolve_path "${RESEARCH_PLAN_FILE}")"
BASE_CODEX=(codex --cd "${ROOT_DIR}" --ask-for-approval "${APPROVAL_MODE}" --sandbox "${SANDBOX_MODE}")
BASE_CODEX+=(--model "${MODEL}")
if [[ "${SANDBOX_MODE}" == "workspace-write" && "${NETWORK_ACCESS}" == "true" ]]; then
  BASE_CODEX+=(-c sandbox_workspace_write.network_access=true)
fi

export CODEX_LOOP_MAX_DIALOGUES="${MAX_DIALOGUES}"
export CODEX_LOOP_TRIAL_MODEL="${TRIAL_MODEL}"

if [[ -n "${ENV_FILE}" ]]; then
  ENV_PATH="$(resolve_path "${ENV_FILE}")"
  if [[ ! -f "${ENV_PATH}" ]]; then
    echo "missing Codex loop env file: ${ENV_FILE}" >&2
    exit 2
  fi
  set -a
  # shellcheck source=/dev/null
  source "${ENV_PATH}"
  set +a
fi

mkdir -p "${RUN_DIR}" "${RESEARCH_UPDATE_DIR}"

if [[ ! -f "${SPEC_PATH}" ]]; then
  echo "missing harness specification: ${SPEC_PATH}" >&2
  echo "Set CODEX_LOOP_SPEC_FILE to the intended spec path, or restore docs/harness_design.md." >&2
  exit 2
fi

if [[ ! -f "${RESEARCH_PLAN_PATH}" ]]; then
  echo "missing research plan: ${RESEARCH_PLAN_PATH}" >&2
  echo "Set CODEX_LOOP_RESEARCH_PLAN_FILE to the intended plan path, or restore docs/research_plan.md." >&2
  exit 2
fi

if [[ "${MODEL}" != *mini* || "${TRIAL_MODEL}" != *mini* ]]; then
  echo "mini-only policy violation: CODEX_MODEL=${MODEL}, CODEX_LOOP_TRIAL_MODEL=${TRIAL_MODEL}" >&2
  exit 2
fi

if ! [[ "${MAX_DIALOGUES}" =~ ^[0-9]+$ ]] || [[ "${MAX_DIALOGUES}" -gt 100 ]]; then
  echo "CODEX_LOOP_MAX_DIALOGUES must be an integer from 0 to 100; got ${MAX_DIALOGUES}" >&2
  exit 2
fi

if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
  echo "codex loop already running: ${LOCK_DIR}" >&2
  exit 0
fi

cleanup() {
  rm -rf "${LOCK_DIR}"
}
trap cleanup EXIT

timestamp() {
  date -u +"%Y%m%dT%H%M%SZ"
}

default_work_prompt() {
  cat <<'PROMPT'
You are running inside an automated harness for the CrosslingMultiagentDialogue repository.

Operate non-interactively. Do not ask the user questions. Treat the harness specification path below as the product specification and make the most useful small, shippable improvement toward that design.

Before changing files, always read both the harness specification and the research plan. Prefer work that advances the documented experimental harness:
- config- and prompt-driven operation rather than hard-coded experiment knobs
- decoupled generation, judge, metrics, and viewer stages
- content-addressed/replayable logs with exact rendered prompts and raw responses
- small dev-mode runs that produce inspectable artifacts
- schemas and CLIs that make later batch runs reproducible
- improvements to this Codex harness loop itself when that makes future automated passes safer, more useful, or easier to inspect

Every pass must persist a research update at the research update path below. Include: what changed, how it maps to the research plan, evidence/checks run, dialogue-trial results if any, and concrete next steps.

If you run or implement API-backed agent/judge trials, use only mini-class models. If OpenAI credentials are already available through the environment, CODEX_LOOP_ENV_FILE, or configured OpenAI/openai-docs secrets, you may use them, but never print, create, or commit secrets. Keep trial runs at or below the maximum dialogue count below.

Keep each pass scoped. Do not rewrite the whole project at once. Add or update tests/checks when feasible. Leave a clear final summary naming what was advanced in the harness design and what remains.

Do not push. The outer harness will review, commit, and push all results.
PROMPT
}

default_review_prompt() {
  cat <<'PROMPT'
Review the uncommitted changes from the automated worker pass against the harness specification path and research plan path below. Confirm the worker read both docs, respected the mini-only policy, kept dialogue trials at or below the maximum dialogue count, and persisted the required research update. Prioritize correctness bugs, broken scripts, unsafe automation behavior, missing checks, repository hygiene, deviations from the documented harness architecture, and flaws in this Codex harness loop itself. If you can safely fix issues directly, do so. Keep the review/fix pass non-interactive and concise.

Do not push. The outer harness will commit and push all results.
PROMPT
}

read_prompt() {
  local path="$1"
  local fallback="$2"
  if [[ -n "${path}" && -f "${path}" ]]; then
    cat "${path}"
  else
    "${fallback}"
  fi
}

build_prompt() {
  local body="$1"
  local research_update_file="$2"
  cat <<PROMPT
${body}

Harness specification path: ${SPEC_FILE}
Harness specification absolute path: ${SPEC_PATH}
Research plan path: ${RESEARCH_PLAN_FILE}
Research plan absolute path: ${RESEARCH_PLAN_PATH}
Research update path: ${research_update_file}
Codex model: ${MODEL}
Mini-only trial model: ${TRIAL_MODEL}
Maximum dialogue trials this pass: ${MAX_DIALOGUES}
Workspace network access enabled: ${NETWORK_ACCESS}

This loop must follow those documents. If a requested change conflicts with the specification or research plan, prefer the documents unless the change is explicitly about improving the loop's ability to execute them.
PROMPT
}

run_codex_worker() {
  local iter="$1"
  local stamp="$2"
  local out_file="${RUN_DIR}/${stamp}-iter-${iter}-worker.md"
  local log_file="${RUN_DIR}/${stamp}-iter-${iter}-worker.log"
  local research_update_file="${RESEARCH_UPDATE_DIR}/${stamp}-iter-${iter}.md"
  local prompt
  prompt="$(build_prompt "$(read_prompt "${WORK_PROMPT_FILE}" default_work_prompt)" "${research_update_file}")"

  {
    echo "# Worker ${stamp} Iteration ${iter}"
    echo
    echo "Harness specification: ${SPEC_FILE}"
    echo "Research plan: ${RESEARCH_PLAN_FILE}"
    echo "Research update: ${research_update_file}"
    echo "Codex model: ${MODEL}"
    echo "Mini-only trial model: ${TRIAL_MODEL}"
    echo "Maximum dialogue trials: ${MAX_DIALOGUES}"
    echo
    echo "Prompt:"
    echo '```text'
    echo "${prompt}"
    echo '```'
    echo
    echo "Output:"
  } > "${out_file}"

  if ! "${BASE_CODEX[@]}" exec --output-last-message "${out_file}.last" "${prompt}" > "${log_file}" 2>&1; then
    {
      echo
      echo "Worker failed. See ${log_file}."
      echo
      cat "${log_file}"
    } >> "${out_file}"
    return 1
  fi

  {
    echo
    echo '```text'
    cat "${out_file}.last"
    echo '```'
  } >> "${out_file}"
  rm -f "${out_file}.last"
  return 0
}

run_codex_reviewer() {
  local iter="$1"
  local stamp="$2"
  local out_file="${RUN_DIR}/${stamp}-iter-${iter}-reviewer.md"
  local log_file="${RUN_DIR}/${stamp}-iter-${iter}-reviewer.log"
  local research_update_file="${RESEARCH_UPDATE_DIR}/${stamp}-iter-${iter}.md"
  local prompt
  prompt="$(build_prompt "$(read_prompt "${REVIEW_PROMPT_FILE}" default_review_prompt)" "${research_update_file}")"

  if git -C "${ROOT_DIR}" diff --quiet && git -C "${ROOT_DIR}" diff --cached --quiet && [[ -z "$(git -C "${ROOT_DIR}" ls-files --others --exclude-standard)" ]]; then
    echo "# Reviewer ${stamp} Iteration ${iter}" > "${out_file}"
    echo >> "${out_file}"
    echo "No uncommitted changes to review." >> "${out_file}"
    return 0
  fi

  {
    echo "# Reviewer ${stamp} Iteration ${iter}"
    echo
    echo "Harness specification: ${SPEC_FILE}"
    echo "Research plan: ${RESEARCH_PLAN_FILE}"
    echo "Research update: ${research_update_file}"
    echo "Codex model: ${MODEL}"
    echo "Mini-only trial model: ${TRIAL_MODEL}"
    echo "Maximum dialogue trials: ${MAX_DIALOGUES}"
    echo
    echo "Prompt:"
    echo '```text'
    echo "${prompt}"
    echo '```'
    echo
    echo "Output:"
  } > "${out_file}"

  if ! "${BASE_CODEX[@]}" exec review --uncommitted --output-last-message "${out_file}.last" "${prompt}" > "${log_file}" 2>&1; then
    {
      echo
      echo "Reviewer failed. See ${log_file}."
      echo
      cat "${log_file}"
    } >> "${out_file}"
    return 1
  fi

  {
    echo
    echo '```text'
    cat "${out_file}.last"
    echo '```'
  } >> "${out_file}"
  rm -f "${out_file}.last"
  return 0
}

commit_and_push() {
  local iter="$1"
  local stamp="$2"

  git -C "${ROOT_DIR}" add -A

  if git -C "${ROOT_DIR}" diff --cached --quiet; then
    echo "No changes to commit for iteration ${iter}."
    return 0
  fi

  git -C "${ROOT_DIR}" commit -m "automated codex loop ${stamp} iter ${iter}"
  git -C "${ROOT_DIR}" push "${PUSH_REMOTE}" "${PUSH_BRANCH}"
}

iter=1
while true; do
  stamp="$(timestamp)"
  echo "Starting Codex loop iteration ${iter} at ${stamp}"

  worker_status=0
  run_codex_worker "${iter}" "${stamp}" || worker_status=$?

  reviewer_status=0
  if [[ "${RUN_REVIEWER}" == "1" ]]; then
    run_codex_reviewer "${iter}" "${stamp}" || reviewer_status=$?
  fi

  commit_and_push "${iter}" "${stamp}"

  if [[ "${worker_status}" -ne 0 || "${reviewer_status}" -ne 0 ]]; then
    echo "Stopping after failure in iteration ${iter}."
    exit 1
  fi

  if [[ "${MAX_ITERS}" != "0" && "${iter}" -ge "${MAX_ITERS}" ]]; then
    break
  fi

  iter=$((iter + 1))
done
