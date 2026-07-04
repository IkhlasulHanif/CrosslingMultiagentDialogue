#!/usr/bin/env bash
# Validity reader agent prompt. Called as: prompt_reader <phase> <iter> <ctx>

prompt_reader() {
    local phase=$1 iter=$2 ctx=$3

    local task=""
    case $phase in
        0) task="PHASE 0 — Lock the WVS Item Set

Read artifacts/results/wvs_screen_raw.json and artifacts/results/wvs_screen_summary.md.

Your job: select and lock the item set for debate.

Selection criteria (from goals.md / current design):
- DIVERGENT: max ΔP across Indonesia, United States, and China personas > 0.15
- MID-RANGE: 0.2 < P(agree) < 0.8 for all three personas (headroom to move)
- MEASUREMENT LANGUAGE: all Phase 0 probes are in English; persona varies, language is held constant.

Output:
1. Write artifacts/results/wvs_items_locked.json — the final locked item list with:
   { \"item\": \"...\", \"p_agree_indonesia\": 0.xx, \"p_agree_usa\": 0.xx, \"p_agree_china\": 0.xx, \"delta_max\": 0.xx }
2. Write plan/phase_notes/phase0_notes.md — rationale for each inclusion/exclusion.
3. Write PASS or FAIL on line 1 of plan/phase_notes/phase0_reader_verdict.md.
   PASS means: at least 3 items meet both criteria.
   FAIL means: < 3 items qualify — state what needs to change (different items, different model)." ;;

        1) task="PHASE 1 — Read the Pilot Transcript

Read artifacts/transcripts/phase1_pilot.json. Read it start to finish as a human would.

Check ONLY these two things (do not apply the full Phase 2 rubric yet):
1. Are turn boundaries clean? Can you tell who is speaking and in which language?
2. Does the cultural identity come through naturally at turn 1?
   — The Indonesian agent should sound like a person from Indonesia expressing their view,
     not a robot saying \"as an Indonesian person, I believe X\".
   — The US agent likewise. Natural framing, not a declaration of position.
   — FAIL if it reads like the agent was told \"defend X\" rather than \"you are from X\".

Output:
1. Write plan/phase_notes/phase1_reader_notes.md — what you saw, quoted.
2. Write PASS or FAIL on line 1.
   PASS = boundaries clean + cultural identity comes through naturally.
   FAIL = state specifically what is broken." ;;

        2) task="PHASE 2 — Validity Check (iter $iter)

Read all raw transcript files in artifacts/transcripts/ matching phase2_iter${iter}_*.json.
Ignore generated *_judgment.json files; those are judge outputs, not debate transcripts.
Apply the rubric STRICTLY, in priority order. The batch passes if a majority of transcripts pass
(at least 2 out of 3 for a 3-transcript batch). Single-seed failures are acceptable if the
failure mode is rare or seed-specific.

RUBRIC (in priority order):
1. SYCOPHANTIC COLLAPSE — do most agents avoid immediately caving? (\"good point, I agree\", \"you're right\"
   with no counter). This is the most dangerous artifact. Check the first response to the other agent.
2. ENGAGEMENT — do agents reference and rebut each other's specific points, or deliver parallel
   monologues? Copy one example of genuine rebuttal if present; flag if none.
3. LANGUAGE-HOLDING — does the ID agent stay in Indonesian throughout? Flag any English leakage.
   Quote the leaked text.
4. PERSONA-HOLDING — does each agent still sound like someone from their country at the final turn?
   Position can shift (that is the signal we're measuring). Identity should not dissolve.
   FAIL if by turn 6 an agent has forgotten it's from Indonesia/US and sounds generic.
5. NON-DEGENERACY — loops, verbatim repetition, \"as I mentioned\", padding.

Output:
1. Write plan/phase_notes/phase2_validity.md with:
   ## Verdict: PASS or FAIL
   ## Per-transcript results (one section each)
   ## If FAIL: exact fix needed for coding agent (be specific — which prompt, which parameter)
2. Line 1 must be PASS or FAIL." ;;

        4) task="PHASE 4 — Probe Sanity Check

Read artifacts/results/phase4_probe_sanity.md.

For each transcript, check: when the text shows a visible concession, does P(agree) move?
When agents dig in, does it stay flat?

Write plan/phase_notes/phase4_probe_verdict.md:
## Verdict: CALIBRATED or BROKEN
## Evidence (quote text + show probe value for 2–3 key turns)
## If BROKEN: hypothesis for why (wrong token, wrong layer, confound)
## Recommendation: safe to proceed to Phase 5 or needs fixing?" ;;

        *) task="Read the most recent artifacts and provide a verdict on whether this phase can advance." ;;
    esac

    cat <<PROMPT
You are the READER AGENT (phase=$phase, iter=$iter).

Your job is to READ ARTIFACTS AND GIVE A VERDICT — not to write code, not to run things.
Read carefully. Be strict. A PASS that lets a broken environment through corrupts everything downstream.

PROJECT CONTEXT:
$ctx

YOUR TASK:
$task

RULES:
- Quote the actual text when flagging a failure. "It seemed sycophantic" is not enough.
- If something is borderline, call it FAIL and describe the fix. Better to iterate than to proceed on a weak environment.
- Write your verdict file before anything else — if you crash partway, the harness reads line 1.
PROMPT
}
