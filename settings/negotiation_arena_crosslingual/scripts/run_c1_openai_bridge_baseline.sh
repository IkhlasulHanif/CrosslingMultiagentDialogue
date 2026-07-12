#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE="$ROOT/artifacts/tmp/c1_openai_bridge_state.json"
REQUEST="$ROOT/artifacts/tmp/c1_openai_bridge_request.json"
PAYLOAD="$ROOT/artifacts/tmp/c1_openai_bridge_payload.json"
RESPONSE="$ROOT/artifacts/tmp/c1_openai_bridge_response.json"
CURL_STDERR="$ROOT/artifacts/tmp/c1_openai_bridge_curl.stderr"
FAILED_COMMAND="bash scripts/run_c1_openai_bridge_baseline.sh"

mkdir -p "$ROOT/artifacts/tmp"
printf '{"responses":[]}\n' > "$STATE"
rm -f "$REQUEST" "$PAYLOAD" "$RESPONSE" "$CURL_STDERR"

python3 "$ROOT/scripts/bringup_check.py" --write-event
python3 "$ROOT/scripts/validate_offer_parser.py"
python3 "$ROOT/scripts/validate_process_metrics.py"
python3 "$ROOT/scripts/validate_language_channels.py"

read_openai_key() {
  if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    printf '%s' "$OPENAI_API_KEY"
    return 0
  fi
  if [[ -s "$ROOT/../../secrets/open_ai.txt" ]]; then
    tr -d '\r\n' < "$ROOT/../../secrets/open_ai.txt"
    return 0
  fi
  if [[ -s "$ROOT/secrets/open_ai.txt" ]]; then
    tr -d '\r\n' < "$ROOT/secrets/open_ai.txt"
    return 0
  fi
  return 1
}

write_blocker() {
  local message="$1"
  local artifact="$ROOT/artifacts/results/baseline_c1_buy_sell_id_seed001.bridge_blocked.json"
  python3 - "$artifact" "$FAILED_COMMAND" "$message" "$CURL_STDERR" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

artifact = Path(sys.argv[1])
failed_command = sys.argv[2]
message = sys.argv[3]
stderr_path = Path(sys.argv[4])
stderr = stderr_path.read_text(encoding="utf-8", errors="replace")[:1000] if stderr_path.exists() else ""
payload = {
    "checked_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "status": "BLOCKED",
    "blocker": "openai_shell_bridge_unavailable",
    "failed_command": failed_command,
    "condition": "C1",
    "game_id": "buy_sell",
    "language_pair": "EN-ID",
    "active_benchmark_provider": "openai_benchmark_shell_bridge",
    "message": message,
    "curl_stderr_preview": stderr,
    "next_action": "Fix shell curl/API access, then rerun bash scripts/run_c1_openai_bridge_baseline.sh.",
    "evidence_scope": "No C1 empirical evidence produced by this bridge attempt.",
}
artifact.parent.mkdir(parents=True, exist_ok=True)
artifact.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
event = {
    "ts": payload["checked_at"],
    "kind": "baseline",
    "status": "BLOCKED",
    "message": f"C1 ID OpenAI shell bridge blocked; artifact={artifact.relative_to(Path.cwd())}; failed_command={failed_command}",
}
events = Path("plan/events.jsonl")
with events.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(event, ensure_ascii=False) + "\n")
PY
}

for _attempt in $(seq 1 24); do
  set +e
  NEGOTIATION_BENCHMARK_PROVIDER=openai_benchmark_shell_bridge \
  NEGOTIATION_OPENAI_BRIDGE_STATE="$STATE" \
  NEGOTIATION_OPENAI_BRIDGE_REQUEST="$REQUEST" \
  NEGOTIATION_OPENAI_BRIDGE_PAYLOAD="$PAYLOAD" \
    python3 "$ROOT/scripts/run_c1_baseline.py"
  status=$?
  set -e

  if [[ "$status" -eq 0 ]]; then
    exit 0
  fi
  if [[ "$status" -ne 75 ]]; then
    exit "$status"
  fi
  if [[ ! -s "$REQUEST" || ! -s "$PAYLOAD" ]]; then
    write_blocker "Python bridge requested an OpenAI response but did not write the expected request/payload files."
    exit 2
  fi

  endpoint="$(python3 - "$REQUEST" <<'PY'
import json
import sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["endpoint"])
PY
)"
  key="$(read_openai_key || true)"
  if [[ -z "$key" ]]; then
    write_blocker "No OpenAI API key found in OPENAI_API_KEY or configured setting-local key file candidates."
    exit 2
  fi

  curl_status=6
  for curl_attempt in 1 2 3 4 5; do
    set +e
    curl --config - > "$RESPONSE" 2> "$CURL_STDERR" <<CURL
url = "$endpoint"
request = "POST"
header = "Content-Type: application/json"
header = "Authorization: Bearer $key"
data-binary = "@$PAYLOAD"
max-time = 120
silent
show-error
location
fail-with-body
CURL
    curl_status=$?
    set -e
    if [[ "$curl_status" -eq 0 ]]; then
      break
    fi
    sleep "$curl_attempt"
  done
  unset key

  if [[ "$curl_status" -ne 0 ]]; then
    write_blocker "Top-level shell curl failed while sending an OpenAI benchmark request."
    exit 2
  fi

  python3 - "$STATE" "$RESPONSE" "$REQUEST" <<'PY'
import json
import sys
from pathlib import Path

state_path = Path(sys.argv[1])
response_path = Path(sys.argv[2])
request_path = Path(sys.argv[3])
state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"responses": []}
raw = json.loads(response_path.read_text(encoding="utf-8"))
choices = raw.get("choices")
if not isinstance(choices, list) or not choices:
    raise SystemExit("OpenAI response has no choices")
message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
content = message.get("content")
if not isinstance(content, str) or not content.strip():
    raise SystemExit("OpenAI response content is empty")
request = json.loads(request_path.read_text(encoding="utf-8"))
state.setdefault("responses", []).append(
    {
        "request_index": request.get("request_index"),
        "text": content,
        "raw_response_path": str(response_path),
    }
)
state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
  rm -f "$REQUEST" "$PAYLOAD"
done

write_blocker "OpenAI shell bridge exceeded 24 request/replay iterations before the C1 episode completed."
exit 2
