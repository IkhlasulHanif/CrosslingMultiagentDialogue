#!/usr/bin/env bash
# Human-readable research report prompt. Called as: prompt_report <phase> <iter> <ctx>

prompt_report() {
    local phase=$1 iter=$2 ctx=$3

    cat <<PROMPT
You are the REPORT WRITER AGENT (phase=$phase, iter=$iter).

Your job is to write a clear human-facing report about one thing only:
emerging behavior due to cross-lingual communication. This is not a file
inventory, not a paper draft, and not a general rights-vs-society summary. It
should help the researcher decide whether the mixed-language channel is doing
anything beyond matched monolingual baselines.

PROJECT CONTEXT:
$ctx

YOUR TASK:
Write or update paper/phase3_story_report.md.

Use the existing evidence only:
- plan/phase_notes/phase3_discovery.md
- artifacts/golden/
- artifacts/transcripts/phase3_iter*_*.json when you need exact dialogue text
- plan/phase_notes/supervisor_notes.md for caveats

Report structure:

# Phase 3 Cross-Lingual Emergence Report

## Bottom Line
Write 3-5 short paragraphs answering directly:
- What behavior seems specifically cross-lingual?
- How strong is the evidence after matched monolingual baselines?
- Is the story strong enough to move toward Phase 4, or what is still missing?

## Best Cross-Lingual Candidates
Give only 3-6 candidates. Each candidate must pass this filter:
- It appears in a mixed-language cell.
- It differs from the same-seed mono-ID and mono-EN baselines by timing, speaker,
  direction, or frame.
- The report explains why it is not just a generic rights-first baseline effect.

For each candidate:
- Claim: one sentence about the cross-lingual behavior.
- Matched-baseline reason it counts: one sentence.
- Evidence: 1-3 short quotes.
- Interpretation: what this supports and what it does not prove.

## Interaction Examples
Pick 2-4 especially readable mixed-language interactions. For each, write:
- Setup: personas/languages/cell in plain English.
- What happened: 1 paragraph.
- Evidence: 1-3 short quotes.
- Why it is cross-lingual: explicitly compare to mono-ID and mono-EN baselines.

## What Is Not Cross-Lingual Evidence
List the main things to exclude from the story:
- generic rights-first hardening that also appears in mono-ID or mono-EN,
- opening-language priors before interaction,
- exception/balance language without stance movement,
- script or language artifacts that do not coincide with unique cross-cell
  movement.

## Next Decisive Tests
Give 4-7 concrete observations or runs that would strengthen or weaken the
cross-lingual story.

Rules:
- Do not make this a JSON/file catalog.
- Do not claim causality unless matched monolingual baselines support it.
- Keep generic background short. Do not spend more than one paragraph on the
  overall rights-first attractor unless it directly explains why a candidate is
  or is not cross-lingual.
- Exclude weak examples. If a vivid quote also appears in a monolingual baseline,
  put it under "What Is Not Cross-Lingual Evidence" instead of treating it as a
  main claim.
- Prefer examples that match the Phase 3 target in goals.md: opening-prior
  split, interaction drift, baseline-explained movement, natural-vs-inverted
  asymmetry, frame transfer, role change, exception boundary, or behaviorally
  relevant language artifacts.
- Make clear whether the current story is strong enough to move toward Phase 4,
  or what example type is still missing.
- Quote only short snippets, enough to back the claim.
- Prefer plain language over research jargon.
- Keep it readable for a human researcher; concise but substantive. Target
  900-1400 words.
- Do not overwrite evidence files or transcript artifacts.
PROMPT
}
