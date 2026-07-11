# Cross-Lingual Benchmark Protocol

Shared protocol for the benchmark settings.

## Headline Question

When LLM agents that could interact in either of two languages are placed in
dynamic contact, does the language of interaction change task outcomes or
asymmetrically steer whose framing dominates?

## Core Design

- Core language pair: EN-ID.
- Ladder pairs for cheap benchmarks: EN-ZH, EN-AR, ZH-ID, AR-ID, optional ID-AR
  and gated EN-JV.
- Conditions:
  - C0: Lx monolingual baseline.
  - C1: Ly monolingual baseline and capability floor.
  - C2: forced mixed-language contact with counterbalancing.
  - C3: free-choice bilingual contact when the benchmark supports it.
- Default model: Qwen3-1.7B.
- Escalation model: Qwen3-8B, only for a whole benchmark after gate G2.
- Optional benchmark execution override: if a setting has
  `config/benchmark_model.json` with provider `openai`, the user has explicitly
  allowed setting-local benchmark scripts to call OpenAI for agents/judges.
  These runs must be labeled as OpenAI evidence and must not be reported as
  Qwen evidence.
- Report both outcome metrics and process metrics.

## Harness Meaning

The per-benchmark harness is an implementation-and-execution loop. A useful
Codex pass should not stop at writing scaffolding. It should:

1. resolve canonical source, data, license, branch, package, or endpoint
   blockers from the paper/GitHub when possible;
2. implement the minimum code needed for the next smoke or baseline run;
3. run that smoke or baseline command; and
4. write a concise human-readable report of what ran, what failed, and what the
   next exact unblock command is.

If the benchmark cannot run, the blocker must be concrete and evidenced by an
artifact, for example a failed fetch report, package import probe, license
report, or model-endpoint probe. Do not keep adding validators around a blocker
that can be solved by inspecting the paper or canonical repository.

## Source Resolution

- Use canonical sources: paper links, GitHub repos, README, LICENSE, pyproject,
  requirements, package metadata, branches, and source tree search.
- Use setting-local source/data locations only: `vendor/`, `external/`,
  `code/vendor/`, `data/source/`, or equivalent benchmark-local folders.
- Record URL, branch/commit, license evidence, and local path.
- If the paper/repo says experiments live on a non-default branch, use that
  branch.
- If Python download code fails because of DNS or local certificate problems,
  try `curl -L` before declaring the source unavailable.
- Never install dependencies globally; create/use a setting-local `.venv` or
  document an offline wheel/source-archive path.
- If a missing local/Modal Qwen endpoint is the only blocker and
  `config/benchmark_model.json` allows OpenAI, implement/run the OpenAI-backed
  benchmark command instead of stopping at the endpoint blocker.

## Periodic Pushes

Benchmark Codex agents should periodically commit and push meaningful validated
increments to `origin`. Push boundaries should be real milestones, such as a
resolved source/data blocker, a runnable smoke command, a produced smoke or
baseline artifact, or a coherent implementation batch.

If a Codex pass finishes with a successful smoke/baseline or an executable
runner that unblocks the benchmark, it should make one final scoped commit/push
attempt before exiting. The parent harness also makes a best-effort scoped
commit/push after successful post-Codex smoke, limited to the active benchmark
setting and the shared harness files.

Before committing, inspect `git status --short`, stage only relevant benchmark
files plus intentionally changed shared harness/protocol files, and avoid
capturing unrelated user work. If auth/network blocks push, log it in the
benchmark-local `plan/events.jsonl` and continue the research loop.

## Evidence Rule

Do not report a cross-lingual effect from C2/C3 alone. Compare against both
monolingual baselines. The effect of interest is mixed-language behavior that
deviates from the C0/C1 interpolation, after role-language counterbalancing.

## Readable Reporting

Each benchmark has one human-readable status file:

`settings/<benchmark_setting>/reports/status.md`

That file should state what ran, what failed, what is blocked, what question
needs a human decision, and the current empirical story.
