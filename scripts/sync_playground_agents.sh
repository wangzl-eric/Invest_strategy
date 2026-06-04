#!/bin/bash
# sync_playground_agents.sh — Auto-sync playground agent definitions to live agent-deck sessions

set -euo pipefail

PROJECT_DIR="/Users/zelin/Desktop/PA Investment/Invest_strategy"
AGENTS_DIR="$PROJECT_DIR/book_notes/playground/agents"
LAUNCH_SCRIPT="$PROJECT_DIR/scripts/launch_playground_team.sh"
LOG_FILE="$PROJECT_DIR/.claude/sync_agents.log"
AD="$HOME/.local/bin/agent-deck"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib/playground_team.sh"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

CHANGED_FILE=""
if [ -n "${CLAUDE_TOOL_INPUT:-}" ]; then
  CHANGED_FILE=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('file_path', ''))
except Exception:
    print('')
" 2>/dev/null || true)
fi

if [[ "$CHANGED_FILE" != "$AGENTS_DIR"/* ]]; then
  exit 0
fi

log "Playground agent file changed: $CHANGED_FILE"

AGENT_NAME=$(basename "$CHANGED_FILE" .md)
if [ "$AGENT_NAME" = "conductor" ]; then
  SESSION_NAME="conductor-playground"
  TARGET_COMMAND=""
  TARGET_TOOL=""
  TARGET_WRAPPER=""
else
  SESSION_NAME="$(playground_session_name "$AGENT_NAME")"
  TARGET_TOOL="$(playground_tool_for_agent "$AGENT_NAME")"
  TARGET_WRAPPER="$(playground_wrapper_for_agent "$AGENT_NAME")"
  TARGET_COMMAND="$(playground_command_for_agent "$AGENT_NAME")"
fi

if command -v "$AD" &>/dev/null; then
  SESSION_JSON=$("$AD" session show "$SESSION_NAME" --json 2>/dev/null || true)
  SESSION_STATUS=$(printf '%s' "$SESSION_JSON" \
    | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('status', 'not_found'))
except Exception:
    print('not_found')
" 2>/dev/null || true)
  SESSION_STATUS="${SESSION_STATUS:-not_found}"
  CURRENT_COMMAND=$(printf '%s' "$SESSION_JSON" \
    | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('command', ''))
except Exception:
    print('')
" 2>/dev/null || true)

  if [[ "$SESSION_STATUS" != "not_found" && -n "$TARGET_COMMAND" ]]; then
    if SET_OUTPUT=$("$AD" session set "$SESSION_NAME" tool "$TARGET_TOOL" -q 2>&1 \
      && "$AD" session set "$SESSION_NAME" command "$TARGET_TOOL" -q 2>&1 \
      && "$AD" session set "$SESSION_NAME" wrapper "$TARGET_WRAPPER" -q 2>&1); then
      if [[ "$CURRENT_COMMAND" != "$TARGET_COMMAND" ]]; then
        log "Updated '$SESSION_NAME' command: '$CURRENT_COMMAND' -> '$TARGET_COMMAND'"
      fi
    elif printf '%s' "$SET_OUTPUT" | grep -qi "readonly database"; then
      log "WARNING: Could not persist command for '$SESSION_NAME' because the agent-deck database is read-only in this environment. Desired command remains '$TARGET_COMMAND'."
    else
      log "WARNING: Failed to update command for '$SESSION_NAME' to '$TARGET_COMMAND' ($SET_OUTPUT)"
    fi
  elif [[ "$SESSION_STATUS" = "not_found" ]]; then
    log "Session '$SESSION_NAME' not found. Stored command sync skipped."
  fi

  if [[ "$SESSION_STATUS" == "idle" || "$SESSION_STATUS" == "waiting" || "$SESSION_STATUS" == "running" ]]; then
    log "Session '$SESSION_NAME' is live (status: $SESSION_STATUS). Sending reload message."
    "$AD" session send "$SESSION_NAME" \
      "[SYSTEM] Your playground agent definition file (${CHANGED_FILE#$PROJECT_DIR/}) has been updated. Please re-read it now, acknowledge the changes, and continue your current task. ${TARGET_COMMAND:+Default launch command is now: $TARGET_COMMAND. Restart the session later if you need the model change to take effect.}" \
      --no-wait -q 2>/dev/null && log "Reload message sent to $SESSION_NAME." \
      || log "WARNING: Failed to send reload message to $SESSION_NAME."
  else
    log "Session '$SESSION_NAME' not running (status: $SESSION_STATUS). No message sent."
  fi
else
  log "agent-deck not found at $AD. Skipping live session notification."
fi

UTILITY_AGENTS=("conductor")
MISSING=()
for agent_file in "$AGENTS_DIR"/*.md; do
  agent=$(basename "$agent_file" .md)
  is_utility=false
  for u in "${UTILITY_AGENTS[@]}"; do
    [[ "$agent" == "$u" ]] && is_utility=true && break
  done
  $is_utility && continue
  if ! grep -q "$agent" "$LAUNCH_SCRIPT" 2>/dev/null; then
    MISSING+=("$agent")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  log "WARNING: The following playground agents have .md files but are NOT referenced in launch_playground_team.sh:"
  for m in "${MISSING[@]}"; do
    log "  - $m  (book_notes/playground/agents/$m.md)"
  done
else
  log "Playground launch script coverage OK — all playground agents are referenced."
fi

log "sync_playground_agents.sh complete."
