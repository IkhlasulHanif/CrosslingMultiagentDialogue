One real C0 EN-monolingual buy/sell smoke episode has run through the upstream
NegotiationArena checkout using the explicitly allowed OpenAI smoke override.
It reached a deal in 2 turns with `offer_parse_rate=1.0`, but this is only
runner bring-up evidence, not Qwen3-1.7B research-matrix evidence.

One real Qwen3-1.7B C0 EN-monolingual buy/sell baseline has now run through the
same upstream checkout using the cached local Transformers provider
`hf-cache://Qwen/Qwen3-1.7B`. Artifact paths:
`artifacts/transcripts/baseline_c0_buy_sell_en_seed001.json` and
`artifacts/results/baseline_c0_buy_sell_en_seed001.metrics.json`.

Baseline result: deal reached in 2 turns at price 40. Metrics:
`deal_rate=1.0`, `offer_parse_rate=1.0`, first-offer price 40, final price 40,
anchoring signed delta 0, seller payoff 0, buyer payoff 60. Payoff asymmetry is
not defined for C0 because both roles are EN.

The first direct-Qwen baseline attempt failed before transcript writing because
Qwen expressed acceptance in prose while leaving malformed XML for the upstream
NegotiationArena parser. The runner now canonicalizes common casing/tag errors
and copies an already visible prior offer into `<newly proposed trade>` when the
model explicitly accepts that trade. The successful baseline above is the rerun
with that normalization.

Source bring-up remains resolved. `external/NegotiationArena` is a local checkout
of `https://github.com/vinid/NegotiationArena.git` on branch
`paper_experiment_code` at commit
`d35a7a3aa0d94c2d49f1d6ac13c5f931851abf12`. License evidence is recorded in
`licenses.md` and `artifacts/results/bringup_check.json`.

Human bilingual review of the Indonesian translations remains pending. Do not
run or report C1 ID baselines or mixed-language C2/C3 conditions as valid
benchmark evidence until `config/translation_review.json` is completed and
`python3 scripts/validate_translation_review.py` passes.
