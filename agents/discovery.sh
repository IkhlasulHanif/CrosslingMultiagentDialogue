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
Treat this iteration as one controlled matched block. The first job is not to
find the most vivid transcript; it is to compare matched seeds across baseline
and exploratory cells.

Look for:

1. FLIP TURNS — a turn where an agent visibly shifts position. Quote the turn.
   Note: which agent, which turn number, what they conceded, what they held.

2. ASYMMETRY SIGNS — does the lower-resource-language side concede earlier or more than
   the English-language side? Track ID/ZH vs EN concessions separately from persona:
   count concessions by persona (ID/US/CN) and by generation language (ID/EN/ZH).

3. INTERESTING ELICITATIONS — any surprising argument, metaphor, or framing that
   one agent used that seemed to move the other.

4. CELL DIFFERENCES — compare normal same-language or native-language baselines
   against exploratory cells. For P3-R1 ID/US, compare natural, inverted, mono-EN,
   and mono-ID cells. For active P3-R2 ID/China, compare English baseline and
   native-language cell against the two one-side-native cross cells. For 3-4
   agent blocks, compare all-shared-language baselines against natural-language
   and rotated-language cells.

5. MATCHED BASELINE COMPARISON — before calling any behavior cross-lingual interaction
   drift, read matched monolingual baselines side by side for the same seed/item/personas.
   Identify the baseline and exploratory cells from transcript configs first.
   For P3-R1, compare \`idus_idid\`, \`idus_enen\`, \`idus_nat\`, and \`idus_inv\`.
   For active P3-R2, compare \`idcn_enen\`, \`idcn_idzh\`, \`idcn_iden\`, and
   \`idcn_enzh\` for each seed. Read baselines first, then cross cells. Write
   what happens in the first three turns of each dialogue and say whether the
   cross-lingual behavior is new or just repeats baseline movement.
   For 3-4 agent debates, identify the matched baseline cells from the transcript
   configs and compare each exploratory cell to its closest baseline. If this
   iteration is missing a required baseline, still write the section and
   explicitly say which comparison is unavailable.

6. OPENING PRIOR VS INTERACTION DRIFT — explicitly label turn-1 stance differences as
   generation-language priors. Only call a case interaction drift if the focal agent
   changes after receiving an other-language turn and that movement is not already
   present in both matched monolingual baselines.

7. EMERGENT MULTI-AGENT BEHAVIOR — for 3-4 agent blocks, look for behavior that
   cannot be seen in a dyad: coalition formation, mediator roles, pile-ons,
   translation-bridge behavior, one agent becoming a norm-setter, polarization,
   consensus collapse, or late minority influence.

Output:
1. Append to plan/phase_notes/phase3_discovery.md (do not overwrite previous iters):
   ## Discovery iter $iter
   ### Matched block summary
   State the agent set, item, cells, seeds found, baseline cells, exploratory cells,
   provider/model if visible in config, and missing files.
   ### Flip turns found
   ### Asymmetry signs
   ### Interesting elicitations
   ### Cell comparisons
   ### Seed-level baseline matrix
   For each matched seed, write one compact row or bullet with:
   \`seed\`, \`baseline change\`, \`exploratory change\`, and
   \`candidate excess movement\`. Use the actual cells present. For P3-R1 include
   \`mono-ID change\`, \`mono-EN change\`, \`natural cross change\`, and
   \`inverted cross change\`. For active P3-R2 include \`English baseline change\`,
   \`native-language change\`, \`ID-native/CN-English cross change\`, and
   \`ID-English/CN-native cross change\`.
   ### Matched baseline comparisons
   For each seed present, include bullets named \`seed <S> baseline read\` that summarize
   turns 1-3 in all cells present for that seed side by side. For active P3-R2,
   this means \`idcn_enen\`, \`idcn_idzh\`, \`idcn_iden\`, and \`idcn_enzh\`.
   For 3-4 agent blocks, summarize the first cycle of turns in each baseline and
   exploratory cell. If one is missing, write \`missing: <cell>\`.
   ### Opening-prior vs interaction-drift split
   For each seed present, label at least one observation as \`opening language prior\`,
   \`monolingual movement\`, or \`candidate cross-lingual excess movement\`.
   ### Emergent behavior notes
   Required for 3-agent or 4-agent blocks; write \`not applicable: 2-agent block\`
   otherwise.
   ### Transcripts worth keeping (list filenames + one-line reason)

   These section headings are mandatory. Do not fold seed-level or matched-baseline
   comparisons into general prose; the supervisor checklist stays incomplete unless
   the explicit \`### Matched block summary\`, \`### Seed-level baseline matrix\`,
   \`### Matched baseline comparisons\`, and
   \`### Opening-prior vs interaction-drift split\` sections appear for the iteration.

2. Copy any transcript you flag as "worth keeping" to artifacts/golden/<filename>
   (leave the original in artifacts/transcripts/ too).

RULES:
- Do NOT suggest fixes. That is Phase 2's job and it is done.
- Do NOT dismiss small effects. A one-turn concession is a finding.
- Quote the text. "The ID agent seemed to soften" tells us nothing.
PROMPT
}
