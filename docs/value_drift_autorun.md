# Value Drift Autorun Harness

This harness repeatedly launches non-interactive Codex passes for the multilingual value drift project. Each pass embeds and points to `draft/multilingual_value_drift_neurips.tex`, then asks the agent to improve the BiVaD experiment loop, run or prepare small dialogue trials, and write a timestamped research update.

Run one pass:

```sh
VALUE_DRIFT_MAX_PASSES=1 ./scripts/value_drift_autorun.sh
```

Run continuously until a non-limit failure or manual interruption:

```sh
./scripts/value_drift_autorun.sh
```

If a pass fails with logs that look like quota, rate, context, or token-limit exhaustion, the harness sleeps for five hours by default (`18000` seconds) and retries. Override this with:

```sh
VALUE_DRIFT_SLEEP_ON_LIMIT_SECONDS=900 ./scripts/value_drift_autorun.sh
```

Install a cron retry. The default schedule starts the harness every 30 minutes, while the lock directory prevents overlapping runs:

```sh
./scripts/install_value_drift_autorun_cron.sh
```

Useful environment variables:

- `VALUE_DRIFT_CODEX_MODEL`, default `gpt-5.5`.
- `VALUE_DRIFT_MAX_PASSES`, default `0`, meaning unlimited.
- `VALUE_DRIFT_DRAFT_FILE`, default `draft/multilingual_value_drift_neurips.tex`.
- `VALUE_DRIFT_PROMPT_FILE`, default `prompts/value_drift_autorun_prompt.md`.
- `VALUE_DRIFT_SLEEP_ON_LIMIT_SECONDS`, default `18000`.
- `VALUE_DRIFT_SLEEP_BETWEEN_PASSES_SECONDS`, default `0`.
- `VALUE_DRIFT_CONTINUE_ON_ERROR`, default `0`.
- `VALUE_DRIFT_NETWORK_ACCESS`, default `true`.
- `VALUE_DRIFT_EXTRA_CODEX_ARGS`, appended to `codex exec`.
- `VALUE_DRIFT_GIT_PUSH`, default `1`, commits and pushes after each pass attempt.
- `VALUE_DRIFT_GIT_REMOTE`, default `origin`.
- `VALUE_DRIFT_GIT_BRANCH`, default current branch.

Outputs:

- `runs/value-drift-autorun/*.prompt.txt` contains the exact prompt sent to Codex.
- `runs/value-drift-autorun/*.log` contains the Codex CLI log.
- `runs/value-drift-autorun/*.last.md` contains the final agent message.
- `research_updates/*-value-drift-pass-*.md` should contain the worker's experiment note for that pass.

Successful passes are required to create a non-empty research update. If Codex exits
successfully but the update is missing, the harness marks that pass as failed so the
missing BiVaD trial note is visible in review.

Verify prompt construction without launching Codex:

```sh
VALUE_DRIFT_DRY_RUN=1 ./scripts/value_drift_autorun.sh
```
