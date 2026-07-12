Active plan update: benchmark execution is now OpenAI `gpt-5.4-mini-2026-03-17` per user
request on 2026-07-12, and the active language pairs are EN-ID, EN-ZH, and
ZH-ID. The old Qwen C0 runs remain useful historical capability evidence, but
new benchmark runs should be labeled as OpenAI `gpt-5.4-mini-2026-03-17` evidence.

Control definition: language means required interaction-output channel, not
translated benchmark rules. For this setting, benchmark rules/private state may
remain in English; C0/C1/C2/C3 should constrain only the agents' visible
negotiation messages and validate channel compliance from transcripts. The next
implementation work is output-channel instruction templates for EN/ID/ZH plus
channel-compliance metrics for EN share, ID share, ZH share, code switching,
and off-pair language.

Historical Qwen3-1.7B C0 EN baselines for buy/sell and resource_exchange pass
the floor (deal_rate=1.0, offer_parse_rate=1.0). Those runs are not the active
OpenAI evidence. The old EN-ID prompt translation review artifacts are
historical and are not the active gate for channel-only experiments.

A fresh real C0 OpenAI buy/sell attempt at 2026-07-12T00:14:31 UTC produced no
transcript because `api.openai.com` could not be resolved by urllib or curl.
Blocker artifact: `artifacts/results/benchmark_model_probe.json`. DNS now
resolves from the parent shell, so retry with `bash scripts/run_c0_openai_baseline.sh`
using the setting-local key file path. If it fails, write an artifact that
distinguishes DNS, certificate, auth, quota, and model-not-found.

No channel-controlled C1/C2/C3 empirical evidence has been produced yet.

The C1/C2/C3 runners should select the explicit OpenAI benchmark provider
(`openai_benchmark` / `gpt-5.4-mini-2026-03-17`) and label resulting artifacts
as OpenAI `gpt-5.4-mini-2026-03-17` evidence, not Qwen evidence.

One real C0 EN-monolingual buy/sell smoke episode previously ran through
upstream NegotiationArena using the explicitly allowed OpenAI smoke override;
it remains runner bring-up evidence only, not Qwen3-1.7B research-matrix
evidence. The latest smoke probe artifact is
`artifacts/results/smoke_model_probe.json` and records an OK probe from
2026-07-11T23:22:16 UTC.

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

The C1 ID baseline command exists as `bash scripts/run_c1_baseline.sh`, but it
currently still follows the old translated-rule gate. Update it so C1 means
both agents must output only ID during negotiation messages while rules/private
state can remain English. Then rerun `bash scripts/run_c1_baseline.sh` and
`python3 scripts/check_g2_capability_floor.py`.

The C0 resource-exchange baseline command is
`bash scripts/run_c0_resource_exchange_baseline.sh`.
The capability-floor gate summary command is
`python3 scripts/check_g2_capability_floor.py`.
