#!/bin/bash
# Show Claude/agent-deck research team defaults, overrides, and effective commands.

set -euo pipefail

PROJECT_DIR="/Users/zelin/Desktop/PA Investment/Invest_strategy"
AD="$HOME/.local/bin/agent-deck"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib/research_team.sh"

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

print_claude_role() {
  local agent="$1"
  local session_name
  local agent_file
  local default_model
  local override_var
  local override_value
  local effective_model
  local effective_command
  local saved_command

  session_name="$(research_session_name "$agent")"
  agent_file="$(research_agent_file "$agent")"
  default_model="$(default_claude_agent_model "$agent")"
  override_var="$(agent_model_override_var_name "$agent")"
  override_value="${!override_var:-}"
  effective_model="$(effective_claude_agent_model "$agent")"
  effective_command="$(claude_command_for_agent "$agent")"
  saved_command="$(session_command "$session_name")"

  printf -- "- %s\n" "$agent"
  printf "  agent file: %s\n" "${agent_file#$PROJECT_DIR/}"
  printf "  default model: %s\n" "${default_model:-"(unset)"}"
  printf "  env override: %s=%s\n" "$override_var" "${override_value:-"(unset)"}"
  printf "  effective launch command: %s\n" "$effective_command"
  printf "  saved agent-deck command: %s\n" "$saved_command"
}

echo "Research Team Model Resolution"
echo ""
echo "Claude roles"
print_claude_role "marco"
print_claude_role "elena"
print_claude_role "pm"
print_claude_role "cerebro"
print_claude_role "dev"
print_claude_role "data"

echo ""
echo "Codex runner"
printf -- "- codex-runner\n"
printf "  default model: %s\n" "$(default_codex_model)"
printf "  env override: RESEARCH_CODEX_MODEL=%s\n" "${RESEARCH_CODEX_MODEL:-${CODEX_RUNNER_MODEL:-"(unset)"}}"
printf "  effective launch command: %s\n" "$(codex_command)"
printf "  saved agent-deck command: %s\n" "$(session_command "codex-runner")"

echo ""
echo "Override locations"
echo "- Persistent Claude-role default: edit the 'model:' frontmatter in .claude/agents/<agent>.md"
echo "- One-off agent-deck launch: set RESEARCH_<AGENT>_MODEL before ./scripts/launch_research_team.sh"
echo "- Codex runner launch: set RESEARCH_CODEX_MODEL before ./scripts/launch_research_team.sh"
echo "- Existing agent-deck sessions: edit the agent file and let scripts/sync_agents.sh update the saved session command; restart that session when you want the new model to take effect."
