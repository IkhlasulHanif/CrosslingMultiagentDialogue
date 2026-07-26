# X-DuET-PD

Cross-lingual multi-turn persuasion harness for measuring language-channel,
persona, and comprehension effects in LLM persuadability.

The contract is `goals.md`. Operational work must enter through `make`.

```bash
make bootstrap
make run CELL=m0_smoke
make check-m0.1
```

Real experiment cells require:

```bash
export OPENAI_API_KEY=...
export XDUETPD_PROVIDER=openai
```

The default smoke cell uses a deterministic mock model so schema, logging, and
report mechanics can be tested offline. Mock output is never treated as
experiment evidence.

`results/manifest.json` is append-only JSONL by design: one JSON object per
completed or skipped cell. The filename follows the contract; the storage
format preserves the append-only requirement.
