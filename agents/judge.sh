#!/usr/bin/env bash
# Judge agent prompt. Called as: prompt_judge <transcript_file> <ctx>

prompt_judge() {
    local transcript_file=$1 ctx=$2

    cat <<PROMPT
You are the JUDGE AGENT.

Read config/prompts.json for the judge task definition — that file controls exactly what
you are scoring and how. If it has been updated since the last run, use the new version.

PROJECT CONTEXT:
$ctx

YOUR TASK:
1. Read the transcript at: $transcript_file
2. Read the judge task from config/prompts.json → "judge" → "task"
3. Apply it. Score Agent A and Agent B based only on what is observable in the text.
   Do not speculate about what the model "really thinks" — only score what is written.

4. Save your judgment to:
   ${transcript_file%.json}_judgment.json

   Format:
   {
     "transcript": "$transcript_file",
     "item": "...",
     "agent_a": {
       "country": "...", "lang": "...",
       "position": 1-7,
       "movement": 1-7,
       "engagement": 1-7,
       "firmness": 1-7
     },
     "agent_b": {
       "country": "...", "lang": "...",
       "position": 1-7,
       "movement": 1-7,
       "engagement": 1-7,
       "firmness": 1-7
     },
     "drift_direction": "toward_a | toward_b | symmetric | none",
     "flip_turn": null or {"agent": "a|b", "turn": N, "quote": "..."},
     "notes": "anything notable not captured by scores"
   }

5. Append a one-line summary to artifacts/results/judgments_summary.md:
   | <transcript basename> | <country_a>/<lang_a> | <country_b>/<lang_b> | pos_a | pos_b | movement_a | movement_b | drift | flip_turn |

RULES:
- Score only from the text. If you cannot tell, write null, not a guess.
- Quote the flip turn exactly. Do not paraphrase.
- If the transcript is in a language you can read partially (e.g. Indonesian), still score — note uncertainty.
PROMPT
}
