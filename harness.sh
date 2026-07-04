#!/usr/bin/env bash
# Cross-lingual value drift — experiment harness
# Phases: 0(screen) → 1(pilot) → 2(validity loop) → 3(discovery loop) → 4(probe) → 5(factorial)
# Loops forever. Ctrl+C to stop. Sleeps 900s on any failure (token limit / API error).

set -uo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
STATE="${STATE:-$ROOT/.harness_state}"
SLEEP_ON_FAIL=900   # 15 min — only hit on token limit / API error
VALIDITY_PASSES_NEEDED=2   # Phase 2: advance after this many consecutive majority-pass batches

# ── backend config (override before sourcing, or via env) ────────────────────
# BACKEND: "claude" (default) or "codex"
BACKEND="${BACKEND:-claude}"
# Claude-specific
CLAUDE_ALLOWED_TOOLS="${CLAUDE_ALLOWED_TOOLS:-Bash,Read,Write,Edit,WebSearch,WebFetch}"
# Codex-specific
CODEX_BYPASS_APPROVALS_AND_SANDBOX="${CODEX_BYPASS_APPROVALS_AND_SANDBOX:-0}"
# Phase 3 defaults to one checker agent over the whole matched block. Set this
# to 1 only when you explicitly want one judge agent per transcript.
PHASE3_PER_TRANSCRIPT_JUDGES="${PHASE3_PER_TRANSCRIPT_JUDGES:-0}"
# Set to a positive integer to run an extra Phase 3 supervisor every N iters.
PHASE3_SUPERVISOR_EVERY="${PHASE3_SUPERVISOR_EVERY:-0}"
# Set to 0 to disable the one-agent human-readable Phase 3 report.
PHASE3_REPORT_EVERY="${PHASE3_REPORT_EVERY:-1}"

# Source secrets
if [[ -f "$ROOT/secrets/modal.env" ]]; then
    set -a; source "$ROOT/secrets/modal.env"; set +a
fi

# Source agent prompts
source "$ROOT/agents/coding.sh"
source "$ROOT/agents/reader.sh"
source "$ROOT/agents/discovery.sh"
source "$ROOT/agents/report.sh"
source "$ROOT/agents/paper.sh"
source "$ROOT/agents/judge.sh"
source "$ROOT/agents/supervisor.sh"

mkdir -p "$ROOT/artifacts/transcripts" \
         "$ROOT/artifacts/results" \
         "$ROOT/artifacts/golden" \
         "$ROOT/artifacts/logs" \
         "$ROOT/plan/phase_notes" \
         "$ROOT/paper"

# ─── state helpers ────────────────────────────────────────────────────────────
# State file: one key=value per line
state_get() { [[ -f "$STATE" ]] && grep "^$1=" "$STATE" | cut -d= -f2 || echo "${2:-}"; }
state_set() {
    local key=$1 val=$2
    if [[ -f "$STATE" ]] && grep -q "^$key=" "$STATE"; then
        sed -i.bak "s/^$key=.*/$key=$val/" "$STATE" && rm -f "$STATE.bak"
    else
        echo "$key=$val" >> "$STATE"
    fi
}
state_init() {
    [[ -f "$STATE" ]] && return
    printf 'phase=0\niter=0\npass_count=0\n' > "$STATE"
}

# ─── context builder ──────────────────────────────────────────────────────────
build_context() {
    local ctx=""
    for f in "$ROOT/goals.md" \
              "$ROOT/plan/plan.md" \
              "$ROOT/plan/loop_notes.md" \
              "$ROOT/plan/phase_notes/phase0_notes.md" \
              "$ROOT/plan/phase_notes/phase0_reader_verdict.md" \
              "$ROOT/plan/phase_notes/phase1_reader_notes.md" \
              "$ROOT/plan/phase_notes/phase2_validity.md" \
              "$ROOT/plan/phase_notes/phase3_discovery.md" \
              "$ROOT/plan/phase_notes/phase4_probe_notes.md" \
              "$ROOT/paper/phase3_story_report.md" \
              "$ROOT/artifacts/results/wvs_items_locked.json"; do
        if [[ -f "$f" && -s "$f" ]]; then
            local name content
            name=$(basename "$f")
            case "$name" in
                phase3_discovery.md)
                    content="$(tail -n 260 "$f")"
                    ;;
                loop_notes.md|supervisor_notes.md)
                    content="$(tail -n 180 "$f")"
                    ;;
                phase3_story_report.md)
                    content="$(tail -n 220 "$f")"
                    ;;
                *)
                    content="$(cat "$f")"
                    ;;
            esac
            ctx+=$'\n\n'"=== $name ==="$'\n'"$content"
        fi
    done
    echo "$ctx"
}

# ─── run one agent (blocking) — backend-aware ────────────────────────────────
run_agent() {
    local name="$1" prompt="$2"
    local ts; ts=$(date +%Y%m%d_%H%M%S)
    local log="$ROOT/artifacts/logs/${name}_${ts}.txt"

    echo "  [$name] starting... (backend=$BACKEND)"
    local ok=0
    case "$BACKEND" in
        claude)
            claude -p "$prompt" \
                --allowedTools "$CLAUDE_ALLOWED_TOOLS" \
                --output-format text \
                > "$log" 2>&1 && ok=1
            ;;
        codex)
            local codex_args=()
            if [[ "$CODEX_BYPASS_APPROVALS_AND_SANDBOX" == "1" ]]; then
                codex_args+=(--dangerously-bypass-approvals-and-sandbox)
            fi
            if [[ ${#codex_args[@]} -gt 0 ]]; then
                codex "${codex_args[@]}" \
                    --cd "$ROOT" \
                    exec \
                    --color never \
                    "$prompt" \
                    > "$log" 2>&1 && ok=1
            else
                codex \
                    --cd "$ROOT" \
                    exec \
                    --color never \
                    "$prompt" \
                    > "$log" 2>&1 && ok=1
            fi
            ;;
        *)
            echo "  [$name] ERROR — unknown BACKEND='$BACKEND'" | tee -a "$log"
            ;;
    esac

    if [[ $ok -eq 1 ]]; then
        echo "  [$name] done → artifacts/logs/$(basename "$log")"
        return 0
    else
        echo "  [$name] FAILED — see artifacts/logs/$(basename "$log")"
        return 1
    fi
}

# ─── push any new commits to remote ──────────────────────────────────────────
git_push() {
    local ahead
    ahead=$(git -C "$ROOT" rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
    if [[ "$ahead" -gt 0 ]]; then
        echo "  [harness] Pushing $ahead commit(s) to remote..."
        git -C "$ROOT" push origin main 2>&1 | sed 's/^/  [git] /' || echo "  [harness] Push failed — will retry next iter"
    fi
}

# ─── read line 1 of a verdict file ────────────────────────────────────────────
verdict() {
    local file="$1"
    [[ -f "$file" ]] && head -1 "$file" | tr '[:lower:]' '[:upper:]' | tr -d '[:space:]' || echo "MISSING"
}

# ─── phase banner ─────────────────────────────────────────────────────────────
banner() {
    local phase=$1 iter=$2 label=$3
    echo ""
    echo "══════════════════════════════════════════════════"
    echo "  PHASE $phase  |  iter=$iter  |  $label"
    echo "  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "══════════════════════════════════════════════════"
}

# ─── clean exit on Ctrl+C only ───────────────────────────────────────────────
trap 'echo "[harness] Stopped."; exit 0' INT TERM

# ─── sleep that survives pkill (only Ctrl+C exits) ───────────────────────────
safe_sleep() {
    echo "[harness] Sleeping ${SLEEP_ON_FAIL}s (Ctrl+C to quit)..."
    sleep "$SLEEP_ON_FAIL" || true   # pkill/kill won't exit the harness
}

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
state_init
echo "[harness] Cross-lingual value drift loop. Ctrl+C to stop."
echo "[harness] Phase: $(state_get phase) | Iter: $(state_get iter) | Pass count: $(state_get pass_count)"

while true; do
    phase=$(state_get phase)
    iter=$(state_get iter)
    pass_count=$(state_get pass_count)
    ctx=$(build_context)

    # ── Phase 0: WVS screening ──────────────────────────────────────────────
    if [[ $phase -eq 0 ]]; then
        banner 0 "$iter" "WVS Item Screening"

        if [[ ! -f "$ROOT/artifacts/results/wvs_screen_raw.json" ]]; then
            prompt=$(prompt_coding 0 "$iter" "$ctx")
            run_agent "phase0_coding" "$prompt" || { safe_sleep; continue; }
        fi

        prompt=$(prompt_reader 0 "$iter" "$ctx")
        run_agent "phase0_reader" "$prompt" || { safe_sleep; continue; }

        v=$(verdict "$ROOT/plan/phase_notes/phase0_reader_verdict.md")
        if [[ $v == PASS* ]]; then
            echo "[harness] Phase 0 PASSED — item set locked."
            prompt=$(prompt_supervisor 0 "$iter" "$ctx")
            run_agent "supervisor_phase0" "$prompt" || true
            git_push
            state_set phase 1; state_set iter 0
        else
            echo "[harness] Phase 0 FAILED — retrying immediately."
            rm -f "$ROOT/artifacts/results/wvs_screen_raw.json" \
                  "$ROOT/artifacts/results/wvs_screen_summary.md" \
                  "$ROOT/artifacts/results/wvs_items_locked.json"
            git_push
        fi
        continue
    fi

    # ── Phase 1: Pilot debate ────────────────────────────────────────────────
    if [[ $phase -eq 1 ]]; then
        banner 1 "$iter" "Pilot Debate (EN–ID, Opposed)"

        if [[ ! -f "$ROOT/artifacts/transcripts/phase1_pilot.json" ]]; then
            prompt=$(prompt_coding 1 "$iter" "$ctx")
            run_agent "phase1_coding" "$prompt" || { safe_sleep; continue; }
        fi

        # Judge the pilot transcript
        if [[ -f "$ROOT/artifacts/transcripts/phase1_pilot.json" ]]; then
            prompt=$(prompt_judge "$ROOT/artifacts/transcripts/phase1_pilot.json" "$ctx")
            run_agent "phase1_judge" "$prompt" || true   # judge failure doesn't block
        fi

        prompt=$(prompt_reader 1 "$iter" "$ctx")
        run_agent "phase1_reader" "$prompt" || { safe_sleep; continue; }

        v=$(verdict "$ROOT/plan/phase_notes/phase1_reader_notes.md")
        if [[ $v == PASS* ]]; then
            echo "[harness] Phase 1 PASSED — pilot transcript approved."
            prompt=$(prompt_supervisor 1 "$iter" "$ctx")
            run_agent "supervisor_phase1" "$prompt" || true
            git_push
            state_set phase 2; state_set iter 0; state_set pass_count 0
        else
            echo "[harness] Phase 1 FAILED — retrying immediately."
            rm -f "$ROOT/artifacts/transcripts/phase1_pilot.json"
            git_push
        fi
        continue
    fi

    # ── Phase 2: Validity loop ───────────────────────────────────────────────
    if [[ $phase -eq 2 ]]; then
        banner 2 "$iter" "Validity Loop"

        # Coding agent generates transcripts (and applies fix if iter > 0)
        prompt=$(prompt_coding 2 "$iter" "$ctx")
        run_agent "phase2_coding_iter${iter}" "$prompt" || { safe_sleep; continue; }

        # Judge all new transcripts from this iter
        for t in "$ROOT/artifacts/transcripts/phase2_iter${iter}"_*.json; do
            [[ -f "$t" ]] || continue
            [[ "$t" == *_judgment*.json ]] && continue
            prompt=$(prompt_judge "$t" "$ctx")
            run_agent "phase2_judge_$(basename "$t" .json)" "$prompt" || true
        done

        # Reader checks against rubric
        prompt=$(prompt_reader 2 "$iter" "$ctx")
        run_agent "phase2_reader_iter${iter}" "$prompt" || { safe_sleep; continue; }

        v=$(verdict "$ROOT/plan/phase_notes/phase2_validity.md")
        if [[ $v == PASS* ]]; then
            pass_count=$(( pass_count + 1 ))
            state_set pass_count "$pass_count"
            echo "[harness] Phase 2 iter $iter PASSED ($pass_count/$VALIDITY_PASSES_NEEDED)"
            if [[ $pass_count -ge $VALIDITY_PASSES_NEEDED ]]; then
                echo "[harness] Phase 2 complete — environment is valid."
                prompt=$(prompt_supervisor 2 "$iter" "$ctx")
                run_agent "supervisor_phase2" "$prompt" || true
                git_push
                state_set phase 3; state_set iter 0; state_set pass_count 0
            else
                git_push
                state_set iter $(( iter + 1 ))
            fi
        else
            echo "[harness] Phase 2 iter $iter FAILED — will fix and re-run."
            state_set pass_count 0
            git_push
            state_set iter $(( iter + 1 ))
        fi
        continue
    fi

    # ── Phase 3: Discovery loop ──────────────────────────────────────────────
    if [[ $phase -eq 3 ]]; then
        banner 3 "$iter" "Discovery Loop"

        # Generate batch unless this iter already has a completed manifest.
        if [[ -f "$ROOT/artifacts/transcripts/phase3_iter${iter}_manifest.txt" ]]; then
            echo "  [phase3_coding_iter${iter}] skipped — manifest already exists"
        else
            prompt=$(prompt_coding 3 "$iter" "$ctx")
            run_agent "phase3_coding_iter${iter}" "$prompt" || { safe_sleep; continue; }
        fi

        # Optional expensive path: one judge agent per transcript. The default
        # checker is the single discovery reader below.
        if [[ "$PHASE3_PER_TRANSCRIPT_JUDGES" == "1" ]]; then
            for t in "$ROOT/artifacts/transcripts/phase3_iter${iter}"_*.json; do
                [[ -f "$t" ]] || continue
                [[ "$t" == *_judgment*.json ]] && continue
                prompt=$(prompt_judge "$t" "$ctx")
                run_agent "phase3_judge_$(basename "$t" .json)" "$prompt" || true
            done
        fi

        # Single discovery reader checks the whole matched block and records
        # phenomena. It does NOT fix.
        prompt=$(prompt_discovery "$iter" "$ctx")
        run_agent "phase3_discovery_iter${iter}" "$prompt" || { safe_sleep; continue; }

        # Single report writer updates the human-readable Phase 3 story.
        if [[ "$PHASE3_REPORT_EVERY" -gt 0 ]]; then
            if (( (iter + 1) % PHASE3_REPORT_EVERY == 0 )); then
                prompt=$(prompt_report 3 "$iter" "$ctx")
                run_agent "phase3_report_iter${iter}" "$prompt" || true
            fi
        fi

        # Optional supervisor checks.
        if [[ "$PHASE3_SUPERVISOR_EVERY" -gt 0 ]]; then
            if (( (iter + 1) % PHASE3_SUPERVISOR_EVERY == 0 )); then
                prompt=$(prompt_supervisor 3 "$iter" "$ctx")
                run_agent "supervisor_phase3_iter${iter}" "$prompt" || true
            fi
        fi
        git_push
        state_set iter $(( iter + 1 ))
        echo "[harness] Phase 3 iter $iter done. Continuing discovery..."
        # Discovery runs until user stops it (or we manually advance to phase 4)
        # To advance: edit .harness_state: phase=4
        continue
    fi

    # ── Phase 4: Probe sanity ────────────────────────────────────────────────
    if [[ $phase -eq 4 ]]; then
        banner 4 "$iter" "Probe Sanity"

        prompt=$(prompt_coding 4 "$iter" "$ctx")
        run_agent "phase4_coding" "$prompt" || { safe_sleep; continue; }

        prompt=$(prompt_reader 4 "$iter" "$ctx")
        run_agent "phase4_reader" "$prompt" || { safe_sleep; continue; }

        v=$(verdict "$ROOT/plan/phase_notes/phase4_probe_verdict.md")
        if [[ $v == CALIBRATED* ]]; then
            echo "[harness] Phase 4 PASSED — probe is calibrated."
            state_set phase 5; state_set iter 0
        else
            echo "[harness] Phase 4 FAILED — retrying immediately."
        fi
        continue
    fi

    # ── Phase 5: Factorial + metrics + paper ────────────────────────────────
    if [[ $phase -eq 5 ]]; then
        banner 5 "$iter" "Factorial + Metrics + Paper"

        prompt=$(prompt_coding 5 "$iter" "$ctx")
        run_agent "phase5_coding_iter${iter}" "$prompt" || { safe_sleep; continue; }

        prompt=$(prompt_paper 5 "$iter" "$ctx")
        run_agent "phase5_paper_iter${iter}" "$prompt" || { safe_sleep; continue; }

        git_push
        state_set iter $(( iter + 1 ))
        echo "[harness] Phase 5 iter $iter done. Looping to refine..."
        # Loops until user stops. To restart from an earlier phase: edit .harness_state
        continue
    fi

    echo "[harness] Unknown phase $phase — check .harness_state"
    safe_sleep
done
