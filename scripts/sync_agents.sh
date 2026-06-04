#!/bin/bash
# sync_agents.sh — Auto-sync Claude team agent definitions to live agent-deck sessions
#
# Triggered by PostToolUse hook when Write/Edit touches .claude/agents/*.md
# Environment variables provided by Claude Code PostToolUse hook:
#   CLAUDE_TOOL_NAME        — "Write" or "Edit"
#   CLAUDE_TOOL_INPUT       — JSON of the tool call input
#
# Behaviour:
#   1. Detect which agent file changed from tool input
#   2. If a matching agent-deck session is running, send it a reload message
#   3. Validate that all .md files under .claude/agents/ are referenced in launch_research_team.sh
#      and warn if any are missing

set -euo pipefail

PROJECT_DIR="/Users/zelin/Desktop/PA Investment/Invest_strategy"
AGENTS_DIR="$PROJECT_DIR/.claude/agents"
LAUNCH_SCRIPT="$PROJECT_DIR/scripts/launch_research_team.sh"
LOG_FILE="$PROJECT_DIR/.claude/sync_agents.log"
AD="$HOME/.local/bin/agent-deck"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib/research_team.sh"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ── 1. Extract changed file path from tool input ──────────────────────────────
# CLAUDE_TOOL_INPUT is JSON. Extract file_path (Write) or file_path (Edit).
CHANGED_FILE=""
if [ -n "${CLAUDE_TOOL_INPUT:-}" ]; then
  # Both Write and Edit have a file_path key
  CHANGED_FILE=$(echo "$CLAUDE_TOOL_INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('file_path', ''))
except Exception:
    print('')
" 2>/dev/null || true)
fi

# Only proceed if the changed file is under .claude/agents/
if [[ "$CHANGED_FILE" != "$AGENTS_DIR"/* ]]; then
  exit 0
fi

log "Agent file changed: $CHANGED_FILE"

# ── 2. Derive agent name from filename ────────────────────────────────────────
# e.g. .claude/agents/marco.md  →  marco
AGENT_NAME=$(basename "$CHANGED_FILE" .md)

# Map agent name to the session name used in launch_research_team.sh
# Convention: sessions are named  research-<agent>  (e.g. research-marco)
SESSION_NAME="$(research_session_name "$AGENT_NAME")"
TARGET_MODEL="$(effective_claude_agent_model "$AGENT_NAME")"
TARGET_TOOL="claude"
TARGET_WRAPPER="$(claude_wrapper_for_agent "$AGENT_NAME")"
TARGET_COMMAND="$(claude_command_for_model "$TARGET_MODEL")"

# ── 3. Check if that session is live and send reload message ──────────────────
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

  if [[ "$SESSION_STATUS" != "not_found" ]]; then
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
  else
    log "Session '$SESSION_NAME' not found. Stored command sync skipped."
  fi

  if [[ "$SESSION_STATUS" == "idle" || "$SESSION_STATUS" == "waiting" || "$SESSION_STATUS" == "running" ]]; then
    log "Session '$SESSION_NAME' is live (status: $SESSION_STATUS). Sending reload message."
    "$AD" session send "$SESSION_NAME" \
      "[SYSTEM] Your agent definition file (.claude/agents/$AGENT_NAME.md) has been updated. Please re-read it now with: Read .claude/agents/$AGENT_NAME.md — then acknowledge the changes and continue your current task. Default launch command is now: $TARGET_COMMAND. Restart the session later if you need the model change to take effect." \
      --no-wait -q 2>/dev/null && log "Reload message sent to $SESSION_NAME." \
      || log "WARNING: Failed to send reload message to $SESSION_NAME."
  else
    log "Session '$SESSION_NAME' not running (status: $SESSION_STATUS). No message sent."
  fi
else
  log "agent-deck not found at $AD. Skipping live session notification."
fi

# ── 4. Validate launch script coverage ───────────────────────────────────────
# Agents that are intentionally NOT launched as standing sessions (utility/slash-command agents)
UTILITY_AGENTS=("kb-curator")

# Find all agent .md files and check each is referenced in launch_research_team.sh
MISSING=()
for agent_file in "$AGENTS_DIR"/*.md; do
  agent=$(basename "$agent_file" .md)
  # Skip known utility agents
  is_utility=false
  for u in "${UTILITY_AGENTS[@]}"; do
    [[ "$agent" == "$u" ]] && is_utility=true && break
  done
  $is_utility && continue
  # launch script references agents via:  .claude/agents/<agent>.md  or  -t "research-<agent>"
  if ! grep -q "$agent" "$LAUNCH_SCRIPT" 2>/dev/null; then
    MISSING+=("$agent")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  log "WARNING: The following agents have .md files but are NOT referenced in launch_research_team.sh:"
  for m in "${MISSING[@]}"; do
    log "  - $m  (.claude/agents/$m.md)"
  done
  log "  Consider adding them to scripts/launch_research_team.sh"
else
  log "Launch script coverage OK — all agents are referenced."
fi

log "sync_agents.sh complete."
