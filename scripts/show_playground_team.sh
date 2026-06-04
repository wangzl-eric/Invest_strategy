#!/bin/bash
# Show playground team defaults, overrides, and saved agent-deck commands.

set -euo pipefail

PROJECT_DIR="/Users/zelin/Desktop/PA Investment/Invest_strategy"
AD="$HOME/.local/bin/agent-deck"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib/playground_team.sh"

session_command() {
  local session_name="$1"
  local session_json

  if ! command -v "$AD" >/dev/null 2>&1; then
    printf '(agent-deck unavailable)\n'
    return 0
  fi

  session_json=$("$AD" session show "$session_name" --json 2>/dev/null || true)
  printf '%s' "$session_json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
except Exception:
    print('(not created)')
    raise SystemExit(0)

if data.get('success') is False:
    print('(not created)')
else:
    print(data.get('command', '(unset)') or '(unset)')
" 2>/dev/null || printf '(not created)\n'
}

print_role() {
  local agent="$1"
  local session_name
  local agent_file
  local default_runtime
  local default_model
  local runtime_override_var
  local runtime_override_value
  local override_var
  local override_value
  local effective_command
  local saved_command

  session_name="$(playground_session_name "$agent")"
  agent_file="$(playground_agent_file "$agent")"
  default_runtime="$(default_playground_agent_runtime "$agent")"
  default_model="$(default_playground_agent_model "$agent")"
  runtime_override_var="$(playground_runtime_override_var_name "$agent")"
  runtime_override_value="${!runtime_override_var:-}"
  override_var="$(playground_model_override_var_name "$agent")"
  override_value="${!override_var:-}"
  effective_command="$(playground_command_for_agent "$agent")"
  saved_command="$(session_command "$session_name")"

  printf -- "- %s\n" "$agent"
  printf "  agent file: %s\n" "${agent_file#$PROJECT_DIR/}"
  printf "  default runtime: %s\n" "${default_runtime:-"(unset)"}"
  printf "  env runtime override: %s=%s\n" "$runtime_override_var" "${runtime_override_value:-"(unset)"}"
  printf "  default model: %s\n" "${default_model:-"(unset)"}"
  printf "  env model override: %s=%s\n" "$override_var" "${override_value:-"(unset)"}"
  printf "  effective launch command: %s\n" "$effective_command"
  printf "  saved agent-deck command: %s\n" "$saved_command"
}

echo "Playground Team Model Resolution"
echo ""
print_role "explorer"
print_role "tutor"
print_role "cerebro"
print_role "dev"

echo ""
echo "Override locations"
echo "- Persistent defaults: edit the 'runtime:' and 'model:' frontmatter in book_notes/playground/agents/<agent>.md"
echo "- One-off launch overrides: set PLAYGROUND_<AGENT>_RUNTIME and/or PLAYGROUND_<AGENT>_MODEL before ./scripts/launch_playground_team.sh"
echo "- Existing agent-deck sessions: edit the agent file and let scripts/sync_playground_agents.sh update the saved session command; restart that session when you want the new model to take effect."
