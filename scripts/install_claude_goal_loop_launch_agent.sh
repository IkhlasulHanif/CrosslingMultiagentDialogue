#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.multiagent.claude-goal-loop"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$ROOT_DIR/logs/claude_loop"

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

# ── Resolve Modal credentials ──────────────────────────────────────────────────
# Priority: environment vars → ~/.modal.toml → secrets/modal.env → abort with hint
resolve_modal_token_id() {
  [[ -n "${MODAL_TOKEN_ID:-}" ]] && { echo "$MODAL_TOKEN_ID"; return; }
  local toml="$HOME/.modal.toml"
  [[ -f "$toml" ]] && awk -F'"' '/^token_id/{print $2}' "$toml" | grep -q . && {
    awk -F'"' '/^token_id/{print $2}' "$toml"; return
  }
  for f in "$ROOT_DIR/secrets/modal.env" "$ROOT_DIR/.env"; do
    [[ -f "$f" ]] && grep -E '^MODAL_TOKEN_ID=' "$f" | cut -d= -f2- | tr -d '"' | grep -q . && {
      grep -E '^MODAL_TOKEN_ID=' "$f" | cut -d= -f2- | tr -d '"'; return
    }
  done
  echo ""
}

resolve_modal_token_secret() {
  [[ -n "${MODAL_TOKEN_SECRET:-}" ]] && { echo "$MODAL_TOKEN_SECRET"; return; }
  local toml="$HOME/.modal.toml"
  [[ -f "$toml" ]] && awk -F'"' '/^token_secret/{print $2}' "$toml" | grep -q . && {
    awk -F'"' '/^token_secret/{print $2}' "$toml"; return
  }
  for f in "$ROOT_DIR/secrets/modal.env" "$ROOT_DIR/.env"; do
    [[ -f "$f" ]] && grep -E '^MODAL_TOKEN_SECRET=' "$f" | cut -d= -f2- | tr -d '"' | grep -q . && {
      grep -E '^MODAL_TOKEN_SECRET=' "$f" | cut -d= -f2- | tr -d '"'; return
    }
  done
  echo ""
}

MODAL_TOKEN_ID_VAL="$(resolve_modal_token_id)"
MODAL_TOKEN_SECRET_VAL="$(resolve_modal_token_secret)"

if [[ -z "$MODAL_TOKEN_ID_VAL" || -z "$MODAL_TOKEN_SECRET_VAL" ]]; then
  echo "WARNING: Modal credentials not found."
  echo "  Run one of:"
  echo "    modal setup                          # interactive — writes ~/.modal.toml"
  echo "    export MODAL_TOKEN_ID=ak-xxx MODAL_TOKEN_SECRET=as-xxx  # then re-run this script"
  echo "    echo 'MODAL_TOKEN_ID=ak-xxx' > $ROOT_DIR/secrets/modal.env"
  echo ""
  echo "The LaunchAgent will be installed without Modal credentials."
  echo "The loop script will also attempt to load them at runtime from the same sources."
fi

MODEL="${MODEL:-claude-sonnet-4-6}"
RUN_SLEEP_SECONDS="${RUN_SLEEP_SECONDS:-60}"
LIMIT_SLEEP_SECONDS="${LIMIT_SLEEP_SECONDS:-900}"
PROBE_SLEEP_SECONDS="${PROBE_SLEEP_SECONDS:-300}"

# ── Write plist ────────────────────────────────────────────────────────────────
cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>

  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$ROOT_DIR/scripts/claude_goal_loop.sh</string>
  </array>

  <key>WorkingDirectory</key>
  <string>$ROOT_DIR</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>MODEL</key>
    <string>$MODEL</string>
    <key>RUN_SLEEP_SECONDS</key>
    <string>$RUN_SLEEP_SECONDS</string>
    <key>LIMIT_SLEEP_SECONDS</key>
    <string>$LIMIT_SLEEP_SECONDS</string>
    <key>PROBE_SLEEP_SECONDS</key>
    <string>$PROBE_SLEEP_SECONDS</string>
    <key>MODAL_TOKEN_ID</key>
    <string>$MODAL_TOKEN_ID_VAL</string>
    <key>MODAL_TOKEN_SECRET</key>
    <string>$MODAL_TOKEN_SECRET_VAL</string>
    <key>HOME</key>
    <string>$HOME</string>
    <key>PATH</key>
    <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:$HOME/.local/bin</string>
  </dict>

  <key>RunAtLoad</key>
  <true/>

  <key>StandardOutPath</key>
  <string>$LOG_DIR/launchd.out</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/launchd.err</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl kickstart -k "gui/$(id -u)/$LABEL"

echo "Installed and started $LABEL"
echo "Plist:          $PLIST"
echo "Loop log:       $LOG_DIR/loop.log"
echo "Stop loop:      touch $ROOT_DIR/.claude-loop-stop"
echo "Unload agent:   launchctl bootout gui/$(id -u) $PLIST"
if [[ -n "$MODAL_TOKEN_ID_VAL" ]]; then
  echo "Modal token:    ${MODAL_TOKEN_ID_VAL:0:8}… (baked into plist)"
else
  echo "Modal token:    NOT SET — run modal setup and reinstall"
fi
