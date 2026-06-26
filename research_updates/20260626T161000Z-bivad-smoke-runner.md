# BiVaD Smoke Runner Implementation - 2026-06-26T16:10:00Z

## What changed

- Added `scripts/run_bivad_smoke.py`, an offline deterministic BiVaD smoke runner.
- Added `docs/bivad_smoke_runner.md` with usage notes.
- Ran one mixed-language English-Indonesian smoke trial and one no-dialogue control.

## BiVaD protocol mapping

- Implements value-disagreement screening with a retained candidate threshold.
- Generates a public dialogue transcript with required-language tracking.
- Keeps private probes and observer readouts as separate artifact layers.
- Computes private drift, final private distance, convergence ratio, and private-public gap.
- Writes JSON and Markdown artifacts under `runs/bivad-smoke/`.

## Dialogue settings tried

- Mixed-language:
  - Topic: whether platforms should remove harmful misinformation
  - Languages: Agent A English, Agent B Indonesian
  - Turn budget: 2
  - Artifact: `runs/bivad-smoke/20260626T161000Z-smoke.json`
- No-dialogue control:
  - Same priors and topic
  - Turn budget: 0
  - Artifact: `runs/bivad-smoke/20260626T161001Z-no-dialogue.json`

## Checks run

- `python3 -m py_compile scripts/run_bivad_smoke.py`
  - Outcome: passed.
- `python3 scripts/run_bivad_smoke.py --run-id 20260626T161000Z-smoke`
  - Outcome: passed.
- `python3 scripts/run_bivad_smoke.py --condition no-dialogue --turns 0 --run-id 20260626T161001Z-no-dialogue`
  - Outcome: passed.
- JSON inspection confirmed the mixed-language run retained the screened candidate and produced nonzero private drift; the no-dialogue control produced zero drift.

## Failures or blockers

- This is not model-backed evidence. It is a protocol smoke test for artifact shape, metric plumbing, and context-layer separation.
- Language compliance is deterministic metadata in this runner, not automatic language identification.

## Concrete next pass recommendation

Replace the deterministic speaker, probe, and observer functions with API-backed calls behind the same JSON schema. Start with one topic, one seed, `T=2`, and the English-Indonesian mixed-language condition plus no-dialogue control.
