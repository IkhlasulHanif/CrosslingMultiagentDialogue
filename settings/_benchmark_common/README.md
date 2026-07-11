# Benchmark Setting Harness

Shared helper used by each cross-lingual benchmark setting. Each benchmark is a
separate setting folder under `settings/`, but they share this small harness
utility so implementation looping, status reporting, and blocker logging stay
consistent.

Each benchmark setting should expose:

- `goals.md` - benchmark-specific checklist and gates.
- `harness.sh` - local entry point.
- `config/benchmark.json` - machine-readable benchmark metadata.
- `reports/status.md` - the one concise human-readable file to read first.
- `reports/findings.md` - optional human-written current story, included in the
  generated status report when present.
- `plan/events.jsonl` - append-only run, error, quota, and decision notes.

Commands:

```bash
./harness.sh status
./harness.sh check
./harness.sh once
./harness.sh loop --sleep 900
./harness.sh error "token quota exhausted"
./harness.sh note "human decision"
```

`once` spawns one Codex implementation-and-execution pass inside the benchmark
setting. The pass is expected to resolve canonical source/data/install blockers,
implement the minimum next runner, and run the next allowed smoke or baseline
command. After Codex exits successfully, the parent harness also invokes
`scripts/run_smoke.sh` when present.

`loop` repeats that pass until stopped. Codex is invoked through the local CLI;
OpenAI API key environment variables are removed from the child process so the
implementation agent does not consume the debate/model API key.

The prompt also tells Codex agents to commit and push periodically after
meaningful validated milestones, while avoiding unrelated user changes. When a
post-Codex smoke succeeds, the parent harness also attempts a scoped
commit/push for the active setting and shared harness files.
