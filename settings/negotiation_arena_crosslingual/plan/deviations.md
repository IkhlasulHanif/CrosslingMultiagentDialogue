# Deviations

## 2026-07-12 - OpenAI Benchmark Execution Override

The user explicitly allowed OpenAI for benchmark loop execution. Setting-local
benchmark scripts may use the configured OpenAI key for agent/judge calls.

Constraints:

- Codex auth must not use the OpenAI key.
- Artifacts from this path must be labeled as OpenAI benchmark evidence.
- Do not report these runs as Qwen3-1.7B or Qwen3-8B evidence.
- Original Qwen/Modal target remains recorded for comparison or later reruns.
