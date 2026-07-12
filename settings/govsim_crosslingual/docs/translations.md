# EN-ID Translation Pack

This setting has a draft translation pack at
`config/translations/en_id_fishery_draft.json`.

Current status: source-covered draft, pending human review.

The pack covers the upstream fishery prompt primitives used by the current
smoke runner: system rules, dynamic resource text, memory text, harvest tasks,
conversation instructions, summaries, and numeric limit extraction. The source
files are `vendor/govsim/subskills/fishing/utils.py`,
`vendor/govsim/subskills/fishing/reasoning_free_format.py`, and the current
setting smoke runner.

Run:

```bash
python3 code/translation_pack.py --root . --out artifacts/logs/translation_status.json
```

To regenerate the human-review packet and the machine-readable review manifest:

```bash
python3 code/translation_pack.py --root . \
  --out artifacts/logs/translation_status.json \
  --review-out artifacts/logs/translation_human_review_packet.md \
  --review-manifest-out artifacts/logs/translation_human_review_manifest.json
```

Use `--strict` only after each entry has `human_checked: true`; strict mode
returns nonzero while the pack is still awaiting human review.
