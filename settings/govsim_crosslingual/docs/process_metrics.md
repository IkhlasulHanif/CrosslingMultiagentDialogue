# GovSim Process Metrics

`code/process_metrics.py` computes setting-local language-process metrics from
transcript JSONL records produced by `code/transcript_logger.py`.

It does not run GovSim and does not infer outcome effects. It only summarizes
visible transcript text so later smoke tests and baseline runs can report the
process layer required by the cross-lingual protocol.

## Metrics

- `language_share`: share of classified EN and ID tokens among classified
  in-pair tokens.
- `code_switch_message_rate`: fraction of visible messages containing at least
  one EN/ID transition.
- `code_switch_points_per_100_pair_tokens`: transition count normalized by
  classified EN/ID token count.
- `off_pair_rate`: share of all tokens classified as off-pair script text.
  Current script flags cover Chinese (`ZH`) and Arabic (`AR`) ranges.
- `convergence_delta`: early mean pairwise agent language-vector distance minus
  late distance. Positive values mean agents became more similar in language
  share over observed rounds.
- `declared_language_mismatch_rate`: fraction of messages where the transcript
  `language` field disagrees with the dominant classified visible language.

## Usage

```bash
python3 code/process_metrics.py artifacts/transcripts/<run>.jsonl \
  --out artifacts/results/<run>_process_metrics.json
```

The classifier is deterministic and dependency-free. It uses small EN and ID
lexicons plus script checks, so it is suitable for smoke gates and audit trails,
not as a replacement for human translation review.
