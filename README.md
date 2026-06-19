# CrosslingMultiagentDialogue

## Automated Codex Loop

Run one non-interactive worker pass, one reviewer pass, then commit and push:

```sh
./scripts/codex_loop.sh
```

Useful environment variables:

- `CODEX_LOOP_MAX_ITERS=1` controls manual loop count. Use `0` to keep running until a Codex/reviewer failure, which is the closest practical "until token limit" mode.
- `CODEX_LOOP_REVIEWER=1` enables the reviewer pass. Set `0` to skip it.
- `CODEX_MODEL=<model>` selects a Codex model.
- `CODEX_LOOP_PROMPT_FILE=<path>` supplies the worker prompt.
- `CODEX_LOOP_REVIEW_PROMPT_FILE=<path>` supplies the reviewer prompt.
- `CODEX_LOOP_SPEC_FILE=docs/harness_design.md` points each worker/reviewer pass at the harness design spec.
- `CODEX_LOOP_RESEARCH_PLAN_FILE=docs/research_plan.md` points each worker/reviewer pass at the research plan.
- `CODEX_LOOP_MAX_DIALOGUES=100` caps trial dialogue runs per pass.
- `CODEX_LOOP_TRIAL_MODEL=gpt-5-mini` is the mini-only default for API-backed trials.
- `CODEX_LOOP_ENV_FILE=<path>` can load local secrets such as `OPENAI_API_KEY`; env files are ignored by Git.
- `CODEX_LOOP_SANDBOX=workspace-write` keeps Codex in the repo sandbox.
- `CODEX_LOOP_APPROVAL=never` runs without approval prompts.

The loop defaults Codex itself to `gpt-5-mini`. It fails before invoking Codex if either the Codex model or trial model is not mini-class, or if `CODEX_LOOP_MAX_DIALOGUES` is above `100`.

The loop writes per-iteration run logs under `runs/codex-loop/`, writes persistent research updates under `research_updates/`, stages all changed files, commits, and pushes to `origin main`.

The default worker prompt treats the loop scripts as part of the project harness. If improving the Codex loop itself is the most useful next step, the worker can edit the loop, cron installer, prompts, logging, or review flow; the reviewer then checks those changes before the outer script commits and pushes.

The runner fails before invoking Codex if `CODEX_LOOP_SPEC_FILE` or `CODEX_LOOP_RESEARCH_PLAN_FILE` is missing, so automated runs do not drift away from the harness design or research plan.

Install a cron job. By default, cron runs every 5 hours and sets `CODEX_LOOP_MAX_ITERS=0`, so each scheduled launch keeps iterating until Codex or the reviewer fails. The lock directory prevents overlapping runs if one launch is still active when the next 5-hour slot arrives.

```sh
./scripts/install_codex_loop_cron.sh
```

Override the schedule or loop count when installing:

```sh
CODEX_LOOP_CRON_SCHEDULE="*/30 * * * *" ./scripts/install_codex_loop_cron.sh
CODEX_LOOP_MAX_ITERS=1 ./scripts/install_codex_loop_cron.sh
```
