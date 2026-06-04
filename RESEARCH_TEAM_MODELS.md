# Research Team Models

Quick reference for the Claude research team and the `agent-deck` launch defaults.

## Current Defaults

| Role | Session | Default model | Source of truth | One-off override |
|------|---------|---------------|-----------------|------------------|
| Marco | `research-marco` | `opus` | `.claude/agents/marco.md` `model:` | `RESEARCH_MARCO_MODEL=...` |
| Elena | `research-elena` | `opus` | `.claude/agents/elena.md` `model:` | `RESEARCH_ELENA_MODEL=...` |
| PM | `research-pm` | `opus` | `.claude/agents/pm.md` `model:` | `RESEARCH_PM_MODEL=...` |
| Cerebro | `research-cerebro` | `opus` | `.claude/agents/cerebro.md` `model:` | `RESEARCH_CEREBRO_MODEL=...` |
| Dev | `research-dev` | `opus` | `.claude/agents/dev.md` `model:` | `RESEARCH_DEV_MODEL=...` |
| Data | `research-data` | `sonnet` | `.claude/agents/data.md` `model:` | `RESEARCH_DATA_MODEL=...` |
| Codex runner | `codex-runner` | `gpt-5.4` | `scripts/lib/research_team.sh` | `RESEARCH_CODEX_MODEL=...` |

## Fast Checks

```bash
# Show effective defaults, env overrides, and saved agent-deck commands
./scripts/show_agent_team.sh

# Launch the team with defaults
./scripts/launch_research_team.sh <strategy_name> <elena|marco>
```

## Override Rules

- Persistent Claude-role defaults: edit the `model:` frontmatter in `.claude/agents/*.md`
- One-off `agent-deck` launch overrides: export `RESEARCH_<AGENT>_MODEL=...` before launch
- Codex runner one-off override: export `RESEARCH_CODEX_MODEL=...` before launch
- After changing an agent file, `scripts/sync_agents.sh` notifies the matching live session to re-read its identity file
- Restart a session when you want a model change to take effect in that running session

## Examples

```bash
# Temporarily run PM on sonnet for one launch
RESEARCH_PM_MODEL=sonnet ./scripts/launch_research_team.sh fx_carry marco

# Temporarily run Codex on a different model
RESEARCH_CODEX_MODEL=gpt-5.2 ./scripts/launch_research_team.sh fx_carry marco
```
