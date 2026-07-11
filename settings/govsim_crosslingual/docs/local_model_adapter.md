# Local Model Adapter

This setting uses `code/local_model_adapter.py` as the single chat-completion
boundary for benchmark agents.

## Endpoint Contract

The adapter calls an OpenAI-compatible local endpoint:

```text
POST /v1/chat/completions
```

Default configuration:

| Variable | Default | Purpose |
|---|---|---|
| `GOVSIM_MODEL_BASE_URL` | `http://127.0.0.1:8000/v1` | vLLM or compatible base URL |
| `GOVSIM_MODEL_NAME` | `Qwen3-1.7B` | model string sent in requests |

The adapter does not read `OPENAI_API_KEY` and does not call OpenAI-hosted
models. If later Modal wiring needs authentication, pass an explicit non-OpenAI
token to `VLLMChatAdapter(api_key=...)` from that runner.

## Response Handling

Qwen-style `<think>...</think>` blocks are stripped from `visible_text` and
preserved in `ModelResponse.thinking`. This supports later transcript logging
without exposing hidden reasoning in the visible agent utterance.

## Validation

Run:

```bash
python3 scripts/test_local_model_adapter.py
```

This test is intentionally no-network; it verifies request shape, response
parsing, and `<think>` separation.

## C0 Qwen Baseline

Run one EN C0 baseline episode through the configured local/Modal Qwen endpoint:

```bash
GOVSIM_MODEL_BASE_URL=http://127.0.0.1:8000/v1 GOVSIM_MODEL_NAME=Qwen3-1.7B ./scripts/run_qwen_c0_baseline.sh
```

The command writes either a result/transcript pair or a blocked result artifact.
The first attempt in this sandbox wrote
`artifacts/results/govsim_c0_qwen_baseline_20260711T111220Z.json` and was
blocked before any transcript by `[Errno 1] Operation not permitted` connecting
to `http://127.0.0.1:8000/v1/chat/completions`.
