# Value Drift Pass 1 - 2026-06-26T15:56:53Z

## What changed

- Updated `scripts/value_drift_autorun.sh` so `VALUE_DRIFT_GIT_PUSH` defaults to `0`, matching the pass contract that workers must not push.
- Added `verify_research_update` to the autorun harness. A Codex pass that exits successfully but does not create a non-empty timestamped research update is now marked `failed:missing-research-update`.
- Updated `docs/value_drift_autorun.md` to document the no-push default and the required research-update check.

## BiVaD protocol mapping

- The draft treats the research update as part of responsible reporting: each pass should preserve settings, failed attempts, and next settings instead of hiding trial-and-error.
- The new post-pass check makes the harness enforce that reporting layer before a pass can be considered successful.
- Disabling push by default keeps small experimental passes local and reviewable, which is consistent with the draft's reproducibility and responsible-reporting constraints.

## Dialogue settings tried

- No model-backed multilingual dialogue was run in this pass.
- Harness dry-run settings:
  - `VALUE_DRIFT_DRY_RUN=1`
  - Draft path: `draft/multilingual_value_drift_neurips.tex`
  - Prompt path: `prompts/value_drift_autorun_prompt.md`
  - Constructed prompt: `runs/value-drift-autorun/20260626T155750Z-dry-run.prompt.txt`
  - Codex model metadata in prompt: `gpt-5.5`
  - Network requested in prompt metadata: `true`

## Checks run

- `bash -n scripts/value_drift_autorun.sh`
  - Outcome: passed.
- `VALUE_DRIFT_DRY_RUN=1 ./scripts/value_drift_autorun.sh`
  - Outcome: passed; wrote `runs/value-drift-autorun/20260626T155750Z-dry-run.prompt.txt`.
- `rg -n "Do not push|Research update path|Draft path|Codex model" runs/value-drift-autorun/20260626T155750Z-dry-run.prompt.txt`
  - Outcome: passed; confirmed the prompt includes `Do not push`, the canonical draft path, an update path, and model metadata.

## Failures or blockers

- No API-backed dialogue trial was attempted. This pass stayed at the harness layer because enforcing no-push behavior and non-empty research updates is a prerequisite for trustworthy repeated BiVaD runs.
- The worktree already contained modified `scripts/value_drift_autorun.sh` and `docs/value_drift_autorun.md` before this pass, including a default model change to `gpt-5.5` and a limit-detection cleanup. Those changes were preserved.
- Existing untracked autorun files under `runs/value-drift-autorun/` were left in place.

## Concrete next pass recommendation

Run a tiny offline or API-backed smoke test of the dialogue loop with one topic, one seed, `T=2`, and one mixed-language pair such as English-Indonesian. The test should verify that the generated transcript keeps debate, private probe, and observer contexts separated, and that any failed language-compliance or missing-update cases are recorded rather than retried blindly.
