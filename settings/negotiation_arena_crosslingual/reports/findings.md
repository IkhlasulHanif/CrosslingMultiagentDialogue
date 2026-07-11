One real C0 EN-monolingual buy/sell smoke episode has run through the upstream
NegotiationArena checkout. The smoke used the explicitly allowed OpenAI override
for runner bring-up only, so it is not Qwen3-1.7B research-matrix evidence.

Current Qwen baseline blocker: `bash scripts/run_c0_baseline.sh` is wired but
needs a reachable local Qwen/vLLM endpoint; `modal run scripts/run_c0_baseline_modal.py`
is also wired but Modal app creation is blocked by the workspace billing cycle
spend limit.

Smoke artifact: `artifacts/transcripts/smoke_c0_buy_sell_en_001.json`.
Metrics artifact: `artifacts/results/smoke_c0_buy_sell_en_001.metrics.json`.
The smoke reached a deal in 2 turns with `offer_parse_rate=1.0`; this is only
runner bring-up evidence.

The next Qwen/local C0 baseline command is wired as
`bash scripts/run_c0_baseline.sh`.

Latest baseline attempt: blocked before any baseline episode ran because the
local Qwen/vLLM chat-completions endpoint was unavailable from this sandbox.
Blocker artifact: `artifacts/results/baseline_c0_buy_sell_en_seed001.blocked.json`.
Endpoint probe artifact: `artifacts/results/model_endpoint_probe.json`.
The recorded error is `<urlopen error [Errno 1] Operation not permitted>` for
`http://127.0.0.1:8000/v1/chat/completions`.

A bounded Modal Qwen baseline runner is also wired as
`modal run scripts/run_c0_baseline_modal.py`. The latest Modal attempt was
blocked before app creation because the workspace billing cycle spend limit was
reached. Blocker artifact:
`artifacts/results/baseline_c0_buy_sell_en_seed001.modal_blocked.json`.
Next unblock command after restoring a Qwen path is either
`bash scripts/run_c0_baseline.sh` for local Qwen or
`modal run scripts/run_c0_baseline_modal.py` for Modal Qwen.

Source bring-up remains resolved. `external/NegotiationArena` is a local checkout
of `https://github.com/vinid/NegotiationArena.git` on branch
`paper_experiment_code` at commit
`d35a7a3aa0d94c2d49f1d6ac13c5f931851abf12`. License evidence is recorded in
`licenses.md` and `artifacts/results/bringup_check.json`.

Human bilingual review of the Indonesian translations remains pending. Do not
run or report C1 ID baselines or mixed-language C2/C3 conditions as valid
benchmark evidence until `config/translation_review.json` is completed and
`python3 scripts/validate_translation_review.py` passes.
