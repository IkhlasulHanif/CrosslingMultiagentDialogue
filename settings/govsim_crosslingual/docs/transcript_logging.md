# Transcript Logging

`code/transcript_logger.py` defines the setting-local transcript artifact format.
It writes one JSON object per line under `artifacts/transcripts/`.

## Event Shape

Every event includes:

| Field | Meaning |
|---|---|
| `schema_version` | Fixed schema marker, currently `govsim-transcript-v1` |
| `ts` | UTC write time |
| `run_id`, `condition`, `language_pair` | Run context |
| `episode_id`, `seed` | Optional run identifiers |
| `event_type` | Currently `model_message` |
| `round_index`, `phase`, `agent_id`, `role` | GovSim turn coordinates |
| `visible_text` | Model utterance after `<think>...</think>` removal |
| `thinking` | List of stripped hidden thinking blocks |
| `raw_text_sha256` | Hash of the original raw model text |
| `event_hash` | Hash of the emitted event for lightweight integrity checks |

The logger intentionally stores a hash of raw model text instead of duplicating
the raw text in the transcript. This keeps hidden thinking separate from the
visible utterance while still making accidental raw-text changes detectable.

## Usage

```python
from pathlib import Path
from transcript_logger import TranscriptContext, TranscriptWriter

writer = TranscriptWriter.for_run(
    Path("."),
    TranscriptContext(run_id="c0_seed_1", condition="C0", seed=1),
)
writer.log_text(
    round_index=0,
    phase="harvest",
    agent_id="agent_0",
    role="assistant",
    raw_text="<think>private note</think>\nHarvest: 2",
    language="EN",
)
```

Use `log_model_response(...)` when the call already returned a
`local_model_adapter.ModelResponse`.

## Validation

Run:

```bash
python3 scripts/test_transcript_logger.py
```

The test is no-network and writes only to a temporary directory.
