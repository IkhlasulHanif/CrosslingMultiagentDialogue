# CrosslingMultiagentDialogue

## Automated Codex Loop

Run one non-interactive worker pass, one reviewer pass, then commit and push:

```sh
./scripts/codex_loop.sh
```

Useful environment variables:

- `CODEX_LOOP_MAX_ITERS=1` controls loop count. Use `0` to keep running until a Codex/reviewer failure, which is the closest practical "until token limit" mode.
- `CODEX_LOOP_REVIEWER=1` enables the reviewer pass. Set `0` to skip it.
- `CODEX_MODEL=<model>` selects a Codex model.
- `CODEX_LOOP_PROMPT_FILE=<path>` supplies the worker prompt.
- `CODEX_LOOP_REVIEW_PROMPT_FILE=<path>` supplies the reviewer prompt.
- `CODEX_LOOP_SPEC_FILE=docs/harness_design.md` points each worker/reviewer pass at the harness design spec.
- `CODEX_LOOP_SANDBOX=workspace-write` keeps Codex in the repo sandbox.
- `CODEX_LOOP_APPROVAL=never` runs without approval prompts.

The loop writes per-iteration run logs under `runs/codex-loop/`, stages all changed files, commits, and pushes to `origin main`.

The default worker prompt treats the loop scripts as part of the project harness. If improving the Codex loop itself is the most useful next step, the worker can edit the loop, cron installer, prompts, logging, or review flow; the reviewer then checks those changes before the outer script commits and pushes.

Install a cron job that runs one cycle hourly:

```sh
./scripts/install_codex_loop_cron.sh
```

Override the schedule when installing:

```sh
CODEX_LOOP_CRON_SCHEDULE="*/30 * * * *" ./scripts/install_codex_loop_cron.sh
```
