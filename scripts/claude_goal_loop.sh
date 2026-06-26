#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GOALS_FILE="${GOALS_FILE:-$ROOT_DIR/GOALS.md}"
LOG_DIR="${LOG_DIR:-$ROOT_DIR/logs/claude_loop}"
STOP_FILE="${STOP_FILE:-$ROOT_DIR/.claude-loop-stop}"
SKILLS_DIR="${SKILLS_DIR:-$HOME/.claude/skills}"

MODEL="${MODEL:-claude-sonnet-4-6}"

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

load_modal_secrets() {
  # 1. Already in environment — nothing to do.
  if [[ -n "${MODAL_TOKEN_ID:-}" && -n "${MODAL_TOKEN_SECRET:-}" ]]; then
    log "modal credentials: loaded from environment"
    return 0
  fi

  # 2. ~/.modal.toml (written by `modal token set` / `modal setup`)
  local toml="$HOME/.modal.toml"
  if [[ -f "$toml" ]]; then
    MODAL_TOKEN_ID="$(awk -F'"' '/^token_id/{print $2}' "$toml")"
    MODAL_TOKEN_SECRET="$(awk -F'"' '/^token_secret/{print $2}' "$toml")"
    if [[ -n "$MODAL_TOKEN_ID" && -n "$MODAL_TOKEN_SECRET" ]]; then
      export MODAL_TOKEN_ID MODAL_TOKEN_SECRET
      log "modal credentials: loaded from $toml"
      return 0
    fi
  fi

  # 3. Secrets file in repo root (.env or secrets/modal.env)
  for env_file in "$ROOT_DIR/secrets/modal.env" "$ROOT_DIR/.env"; do
    if [[ -f "$env_file" ]]; then
      # shellcheck disable=SC1090
      set -a; source "$env_file"; set +a
      if [[ -n "${MODAL_TOKEN_ID:-}" && -n "${MODAL_TOKEN_SECRET:-}" ]]; then
        export MODAL_TOKEN_ID MODAL_TOKEN_SECRET
        log "modal credentials: loaded from $env_file"
        return 0
      fi
    fi
  done

  log "WARNING: MODAL_TOKEN_ID / MODAL_TOKEN_SECRET not found — Modal GPU calls will fail"
  log "         Set them via: modal setup  OR  export in environment  OR  secrets/modal.env"
}

# Concatenate SKILL.md + all reference docs for the four Modal skills into a single block
# that gets injected into every prompt, so Claude has the full skill context even in -p mode.
build_skill_context() {
  local modal_skills=(modal-basic-skills modal-gpu-dev modal-gpu-experiment sub-agents)
  for skill in "${modal_skills[@]}"; do
    local skill_dir="$SKILLS_DIR/$skill"
    [[ -d "$skill_dir" ]] || continue

    printf "\n\n---\n## Loaded Skill: %s\n\n" "$skill"

    [[ -f "$skill_dir/SKILL.md" ]] && cat "$skill_dir/SKILL.md"

    if [[ -d "$skill_dir/references" ]]; then
      for ref in "$skill_dir"/references/*.md; do
        [[ -f "$ref" ]] || continue
        printf "\n### %s/%s\n\n" "references" "$(basename "$ref")"
        cat "$ref"
      done
    fi
  done
}

is_usage_limit_output() {
  local file="$1"
  grep -Eiq \
    "usage limit|rate limit|quota|capacity|too many requests|try again|reset|5[ -]?hour|hours?|429|overloaded" \
    "$file"
}

build_goal_prompt() {
  cat <<PROMPT
You are running as an autonomous follow-up Claude goal loop for this repository.

Read GOALS.md and work through the checklist pragmatically. Prioritize empirical checks,
scripts, artifacts, and concrete edits over prose polish. If a checklist item is already
handled, mark it in GOALS.md with a short note. If you cannot complete an item, write the
blocker and the smallest next action.

Important:
- Do not fabricate experiment results.
- Keep changes focused on this repository.
- Use model $MODEL for loop work unless the user changes the environment.
- For any GPU compute, use Modal serverless. Your MODAL_TOKEN_ID and MODAL_TOKEN_SECRET are
  already exported in the environment — use them directly. Do NOT assume local CUDA/MPS for
  GPU workloads; offload to Modal instead.
- To authenticate within a Modal app use: modal.Secret.from_dict({"MODAL_TOKEN_ID": os.environ["MODAL_TOKEN_ID"], "MODAL_TOKEN_SECRET": os.environ["MODAL_TOKEN_SECRET"]})
  Or, if the secret is already stored as a Modal named secret, prefer modal.Secret.from_name().
- Put experiment implementation and harness code under code/. Keep scripts/ for repo/agent
  operations only (like this loop launcher).
- The user has instructed this loop to push. If you make meaningful source/doc changes,
  inspect git status, stage only the files relevant to your work, commit with a concise
  message, and push the current branch. Do not stage unrelated pre-existing deletions or
  logs unless they are directly part of your change.
- Leave enough state in tracked files that the next loop iteration can continue.

$(build_skill_context)

---
Current GOALS.md:

$(cat "$GOALS_FILE")
PROMPT
}

run_claude_once() {
  local iter="$1"
  local stamp="$2"
  local out="$LOG_DIR/run_${iter}_${stamp}.log"
  local prompt_file="$LOG_DIR/prompt_${iter}_${stamp}.md"

  build_goal_prompt > "$prompt_file"
  log "starting claude iteration $iter (model=$MODEL)"

  claude \
    --dangerously-skip-permissions \
    --model "$MODEL" \
    -p "$(cat "$prompt_file")" \
    > "$out" 2>&1

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

    log "probing whether Claude usage window reset"
    claude \
      --dangerously-skip-permissions \
      --model "$MODEL" \
      -p "Reply with exactly: READY" \
      > "$out" 2>&1

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

  load_modal_secrets

  log "claude goal loop started"
  log "root=$ROOT_DIR model=$MODEL"
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

    run_claude_once "$iter" "$stamp"
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

  log "claude goal loop stopped"
}

main "$@"
