#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GOALS_FILE="${GOALS_FILE:-$ROOT_DIR/GOALS.md}"
LOG_DIR="${LOG_DIR:-$ROOT_DIR/logs/codex_loop}"
STOP_FILE="${STOP_FILE:-$ROOT_DIR/.codex-loop-stop}"

MODEL="${MODEL:-gpt-5.5}"
SANDBOX="${SANDBOX:-danger-full-access}"
APPROVAL="${APPROVAL:-never}"
REASONING_EFFORT="${REASONING_EFFORT:-medium}"

RUN_SLEEP_SECONDS="${RUN_SLEEP_SECONDS:-60}"
LIMIT_SLEEP_SECONDS="${LIMIT_SLEEP_SECONDS:-900}"
PROBE_SLEEP_SECONDS="${PROBE_SLEEP_SECONDS:-300}"
MAX_ITERATIONS="${MAX_ITERATIONS:-0}"
MAX_CONSECUTIVE_FAILURES="${MAX_CONSECUTIVE_FAILURES:-3}"

mkdir -p "$LOG_DIR"

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

log() {
  local line
  line="[$(timestamp)] $*"
  printf "%s\n" "$line" >> "$LOG_DIR/loop.log"
  if [[ -t 1 ]]; then
    printf "%s\n" "$line"
  fi
}

is_usage_limit_output() {
  local file="$1"
  grep -Eiq \
    "usage limit|rate limit|quota|capacity|too many requests|try again|reset|5[ -]?hour|hours?|429" \
    "$file"
}

build_goal_prompt() {
  cat <<PROMPT
You are running as an autonomous follow-up Codex loop for this repository.

Read GOALS.md and work through the checklist pragmatically. Prioritize empirical checks,
scripts, artifacts, and concrete edits over prose polish. If a checklist item is already
handled, mark it in GOALS.md with a short note. If you cannot complete an item, write the
blocker and the smallest next action.

Important:
- Do not fabricate experiment results.
- Keep changes focused on this repository.
- Use model gpt-5.5 with medium reasoning for Codex loop work unless the user changes
  the loop environment.
- GPU experiment runs must use Modal serverless only. Do not use Apple MPS or local
  CUDA for empirical runs, and do not rely on remote model APIs or OPENAI_API_KEY for
  current experiment implementation. CPU-only local code is acceptable for API-free
  audits, validation, synthetic fixtures, and non-empirical schema checks.
- Put experiment implementation and experiment harness code under code/. Keep scripts/
  for repo/agent operations only, such as this Codex loop launcher.
- The user has instructed this loop to push. If you make meaningful source/doc changes,
  inspect git status, stage only the files relevant to your work, commit them with a
  concise message, and push the current branch. Do not stage unrelated pre-existing
  deletions or logs unless they are directly part of your change.
- Leave enough state in tracked files that the next loop can continue.

Current GOALS.md:

$(cat "$GOALS_FILE")
PROMPT
}

run_codex_once() {
  local iter="$1"
  local stamp="$2"
  local out="$LOG_DIR/run_${iter}_${stamp}.log"
  local prompt="$LOG_DIR/prompt_${iter}_${stamp}.md"
  local model_args=()
  if [[ -n "$MODEL" ]]; then
    model_args=(--model "$MODEL")
  fi

  build_goal_prompt > "$prompt"
  log "starting codex iteration $iter"

  codex --ask-for-approval "$APPROVAL" -c model_reasoning_effort="$REASONING_EFFORT" exec \
    --cd "$ROOT_DIR" \
    "${model_args[@]}" \
    --sandbox "$SANDBOX" \
    -o "$LOG_DIR/last_message_${iter}_${stamp}.txt" \
    - < "$prompt" > "$out" 2>&1

  local status=$?
  log "iteration $iter exited with status $status; log=$out"

  if is_usage_limit_output "$out"; then
    log "usage/rate limit detected from iteration $iter"
    return 75
  fi

  return "$status"
}

probe_until_reset() {
  while [[ ! -f "$STOP_FILE" ]]; do
    log "sleeping before reset probe for ${PROBE_SLEEP_SECONDS}s"
    sleep "$PROBE_SLEEP_SECONDS"

    local stamp
    stamp="$(date "+%Y%m%d_%H%M%S")"
    local out="$LOG_DIR/reset_probe_${stamp}.log"
    local model_args=()
    if [[ -n "$MODEL" ]]; then
      model_args=(--model "$MODEL")
    fi

    log "probing whether Codex usage window reset"
    codex --ask-for-approval never -c model_reasoning_effort="$REASONING_EFFORT" exec \
      --cd "$ROOT_DIR" \
      "${model_args[@]}" \
      --sandbox read-only \
      "Reply with exactly: READY" > "$out" 2>&1

    local status=$?
    if [[ "$status" -eq 0 ]] && ! is_usage_limit_output "$out"; then
      log "reset probe succeeded; resuming loop"
      return 0
    fi

    log "reset probe still blocked; log=$out"
  done
}

main() {
  if [[ ! -f "$GOALS_FILE" ]]; then
    log "missing goals file: $GOALS_FILE"
    exit 1
  fi

  log "codex goal loop started"
  if [[ -n "$MODEL" ]]; then
    log "root=$ROOT_DIR model=$MODEL sandbox=$SANDBOX approval=$APPROVAL reasoning=$REASONING_EFFORT"
  else
    log "root=$ROOT_DIR model=<codex default> sandbox=$SANDBOX approval=$APPROVAL reasoning=$REASONING_EFFORT"
  fi
  log "stop by creating $STOP_FILE"

  local iter=1
  local consecutive_failures=0
  while [[ ! -f "$STOP_FILE" ]]; do
    if [[ "$MAX_ITERATIONS" -gt 0 ]] && [[ "$iter" -gt "$MAX_ITERATIONS" ]]; then
      log "max iterations reached: $MAX_ITERATIONS"
      break
    fi

    local stamp
    stamp="$(date "+%Y%m%d_%H%M%S")"

    run_codex_once "$iter" "$stamp"
    local status=$?

    if [[ "$status" -eq 75 ]]; then
      consecutive_failures=0
      log "sleeping for limit window: ${LIMIT_SLEEP_SECONDS}s"
      sleep "$LIMIT_SLEEP_SECONDS"
      probe_until_reset
    elif [[ "$status" -ne 0 ]]; then
      consecutive_failures=$((consecutive_failures + 1))
      if [[ "$consecutive_failures" -ge "$MAX_CONSECUTIVE_FAILURES" ]]; then
        log "stopping after $consecutive_failures consecutive non-limit failures"
        break
      fi
      log "non-limit failure; sleeping ${RUN_SLEEP_SECONDS}s before retry"
      sleep "$RUN_SLEEP_SECONDS"
    else
      consecutive_failures=0
      log "iteration $iter complete; sleeping ${RUN_SLEEP_SECONDS}s"
      sleep "$RUN_SLEEP_SECONDS"
      iter=$((iter + 1))
    fi
  done

  log "codex goal loop stopped"
}

main "$@"
