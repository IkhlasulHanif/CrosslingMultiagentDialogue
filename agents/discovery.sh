#!/usr/bin/env bash
# Discovery reader agent prompt. Called as: prompt_discovery <iter> <ctx>

prompt_discovery() {
    local iter=$1 ctx=$2

    cat <<PROMPT
You are the DISCOVERY AGENT (Phase 3, iter=$iter).

Your job: read the debate transcripts from this iteration and find INTERESTING BEHAVIOR.
You are NOT a validity checker. Do not fix things. Record what you see.

PROJECT CONTEXT:
$ctx

YOUR TASK:
Read all transcripts in artifacts/transcripts/ matching phase3_iter${iter}_*.json.
Look for:

1. FLIP TURNS — a turn where an agent visibly shifts position. Quote the turn.
   Note: which agent, which turn number, what they conceded, what they held.

2. ASYMMETRY SIGNS — does the ID agent concede earlier or more than the EN agent?
   Count: EN concessions vs ID concessions (rough tally from text).

3. INTERESTING ELICITATIONS — any surprising argument, metaphor, or framing that
   one agent used that seemed to move the other.

4. CELL DIFFERENCES — does EN–ID look different from EN–EN or ID–ID?
   Even qualitatively, before any metric.

5. ALIGNED VS OPPOSED — in the aligned-persona cell, do agents still drift?
   (This is the residual leakage test — drift here is a finding, not noise.)

Output:
1. Append to plan/phase_notes/phase3_discovery.md (do not overwrite previous iters):
   ## Discovery iter $iter
   ### Flip turns found
   ### Asymmetry signs
   ### Interesting elicitations
   ### Cell comparisons
   ### Transcripts worth keeping (list filenames + one-line reason)

2. Copy any transcript you flag as "worth keeping" to artifacts/golden/<filename>
   (leave the original in artifacts/transcripts/ too).

RULES:
- Do NOT suggest fixes. That is Phase 2's job and it is done.
- Do NOT dismiss small effects. A one-turn concession is a finding.
- Quote the text. "The ID agent seemed to soften" tells us nothing.
PROMPT
}
