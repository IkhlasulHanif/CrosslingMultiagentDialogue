Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass the floor:
deal_rate=1.0 and offer_parse_rate=1.0. In this pass, buy/sell was rerun after
the runtime prompt was wired to `config/prompt_translations.json`; it again
reached a deal in 2 turns. C1 ID and G2 remain blocked only on pending human
review of 16 EN-ID translation units.

One real C0 EN-monolingual buy/sell smoke episode previously ran through
upstream NegotiationArena using the explicitly allowed OpenAI smoke override;
it remains runner bring-up evidence only, not Qwen3-1.7B research-matrix
evidence. In this pass, `bash scripts/run_smoke.sh` was blocked by DNS for
`api.openai.com`; the blocker is recorded in
`artifacts/results/smoke_model_probe.json`.

Buy/sell result: deal reached at price 40. First-offer price and final price
were both 40, anchoring signed delta was 0, seller payoff was 0, and buyer
payoff was 60. Payoff asymmetry is not defined for C0 because both roles are EN.

Resource-exchange result: upstream accepted a deal in 2 turns. The accepted
trade was effectively a zero-progress allocation, so final resources matched
the initial allocation and both upstream ResourceGoal outcomes were false. The
runner records those boolean outcomes as numeric 1/0 goal-satisfaction payoffs
for now; inspect trade-legality and payoff semantics before treating
resource_exchange as full matrix-ready.

Source bring-up remains resolved. `external/NegotiationArena` is a local checkout
of `https://github.com/vinid/NegotiationArena.git` on branch
`paper_experiment_code` at commit
`d35a7a3aa0d94c2d49f1d6ac13c5f931851abf12`. License evidence is recorded in
`licenses.md` and `artifacts/results/bringup_check.json`.

Human bilingual review of the Indonesian translations remains pending. The
review queue now includes the upstream buy/sell XML response-format instruction
that the runner actually appends, so there are 16 pending review units. The
queue validates as aligned with `config/prompt_translations.json`, but this is
not human approval. Do not run or report C1 ID baselines or mixed-language C2/C3
conditions as valid benchmark evidence until `config/translation_review.json` is
completed and `python3 scripts/validate_translation_review.py` passes.

The C1 ID baseline command exists as `bash scripts/run_c1_baseline.sh`. Current
run result is a gate artifact, not empirical evidence:
`artifacts/results/baseline_c1_buy_sell_id_seed001.blocked.json`, refreshed at
2026-07-11T15:50:27+00:00 by the real C1 command. It blocks on 16 pending
translation-review units and points reviewers to `docs/id_translation_review.md`
for side-by-side EN/ID text. `artifacts/results/g2_capability_floor.json` was
refreshed at 2026-07-11T15:52:16+00:00 and confirms C0 passes while G2 remains
blocked on missing C1 ID metrics. Once the human review file is approved, rerun
`python3 scripts/validate_translation_review.py`,
`bash scripts/run_c1_baseline.sh`, and
`python3 scripts/check_g2_capability_floor.py`.

The C0 resource-exchange baseline command is
`bash scripts/run_c0_resource_exchange_baseline.sh`.
The capability-floor gate summary command is
`python3 scripts/check_g2_capability_floor.py`.
