Active plan update: benchmark execution is OpenAI `gpt-5.4-mini-2026-03-17`
per user request on 2026-07-12, and active language pairs are EN-ID, EN-ZH,
and ZH-ID. New benchmark artifacts must be labeled as OpenAI evidence, not
Qwen evidence.

Control definition: language means required interaction-output channel, not
translated benchmark rules. Rules/private state may remain in English; C0/C1/C2/C3
constrain visible negotiation messages and validate channel compliance from
transcripts.

Current executable blocker: `bash scripts/run_c1_baseline.sh` uses the active
OpenAI benchmark provider by default, but Python cannot resolve
`api.openai.com` in this Codex sandbox. A fallback bridge command exists:
`bash scripts/run_c1_openai_bridge_baseline.sh`. It lets Python generate/replay
the upstream NegotiationArena prompts while the surrounding shell performs the
OpenAI `curl` calls.

Fresh pass result: the standard C1 ID baseline command was rerun at
2026-07-12T04:27:51 UTC and blocked during the OpenAI benchmark probe with
`nodename nor servname provided, or not known`; curl fallback also failed with
exit 6. The shell bridge was then rerun at 2026-07-12T04:28:18 UTC. It reached
the first real C1 model request after bring-up, offer parser validation,
process-metric validation, and EN/ID/ZH channel validation all passed, but
top-level shell `curl` failed with `Could not resolve host: api.openai.com`.
No C1 transcript or metrics were created.

Fresh blocker artifacts:

- `artifacts/results/benchmark_model_probe.json`
- `artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json`
- `artifacts/results/baseline_c1_buy_sell_id_seed001.bridge_blocked.json`

No channel-controlled C1/C2/C3 empirical evidence has been produced yet.

Pairwise channel-run planning is in place for EN-ID, EN-ZH, and ZH-ID at
`config/pairwise_channel_plan.json`. It covers C0, C1, both C2 role-language
counterbalances, and C3 free-choice rows for each active pair. Validator
artifact: `artifacts/results/pairwise_channel_plan_validation.json`.

Historical Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass
the floor (deal_rate=1.0, offer_parse_rate=1.0). Those runs are historical
capability evidence, not the active OpenAI benchmark evidence.

Source bring-up remains resolved. `external/NegotiationArena` is a local
checkout of `https://github.com/vinid/NegotiationArena.git` on branch
`paper_experiment_code` at commit
`d35a7a3aa0d94c2d49f1d6ac13c5f931851abf12`. License evidence is recorded in
`licenses.md` and `artifacts/results/bringup_check.json`.

Next exact command after network/DNS is restored:
`bash scripts/run_c1_openai_bridge_baseline.sh`, then
`python3 scripts/check_g2_capability_floor.py`.
