One real C0 EN-monolingual buy/sell smoke episode has run through the upstream
NegotiationArena checkout using the explicitly allowed OpenAI smoke override.
It reached a deal in 2 turns with `offer_parse_rate=1.0`, but this is only
runner bring-up evidence, not Qwen3-1.7B research-matrix evidence.

Latest real C0 baseline attempt: `bash scripts/run_c0_baseline.sh` passed source
bring-up and parser/process validators, then blocked before any episode ran
because this sandbox cannot reach the local Qwen/vLLM chat-completions endpoint
at `http://127.0.0.1:8000/v1/chat/completions`
(`<urlopen error [Errno 1] Operation not permitted>`). The next Qwen/local C0
baseline command remains `bash scripts/run_c0_baseline.sh`.

Latest baseline attempt (`2026-07-11T12:49:41+00:00`): blocked before any
baseline episode ran because the local Qwen/vLLM chat-completions endpoint was
unavailable from this sandbox.
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
