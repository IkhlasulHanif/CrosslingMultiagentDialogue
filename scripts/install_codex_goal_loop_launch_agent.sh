#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="com.multiagent.codex-goal-loop"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$ROOT_DIR/logs/codex_loop"

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR"

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
    <string>$ROOT_DIR/scripts/codex_goal_loop.sh</string>
  </array>

  <key>WorkingDirectory</key>
  <string>$ROOT_DIR</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>MODEL</key>
    <string>gpt-5.5</string>
    <key>REASONING_EFFORT</key>
    <string>medium</string>
    <key>SANDBOX</key>
    <string>danger-full-access</string>
    <key>APPROVAL</key>
    <string>never</string>
    <key>RUN_SLEEP_SECONDS</key>
    <string>60</string>
    <key>LIMIT_SLEEP_SECONDS</key>
    <string>900</string>
    <key>PROBE_SLEEP_SECONDS</key>
    <string>300</string>
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
echo "Plist: $PLIST"
echo "Loop log: $LOG_DIR/loop.log"
echo "Stop loop: touch $ROOT_DIR/.codex-loop-stop"
echo "Unload agent: launchctl bootout gui/$(id -u) $PLIST"
