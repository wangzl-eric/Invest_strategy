# Playground Team Models

Quick reference for the `agent-deck` playground paper-reading and knowledge-expansion team.

## Current Defaults

| Role | Session | Default runtime | Default model | Source of truth | One-off override |
|------|---------|-----------------|---------------|-----------------|------------------|
| Explorer | `playground-explorer` | `codex` | `gpt-5.4` | `workstation/playground/agents/explorer.md` `runtime:` + `model:` | `PLAYGROUND_EXPLORER_RUNTIME=...` / `PLAYGROUND_EXPLORER_MODEL=...` |
| Tutor | `playground-tutor` | `codex` | `gpt-5.4` | `workstation/playground/agents/tutor.md` `runtime:` + `model:` | `PLAYGROUND_TUTOR_RUNTIME=...` / `PLAYGROUND_TUTOR_MODEL=...` |
| Cerebro | `playground-cerebro` | `claude` | `opus` | `workstation/playground/agents/cerebro.md` `runtime:` + `model:` | `PLAYGROUND_CEREBRO_RUNTIME=...` / `PLAYGROUND_CEREBRO_MODEL=...` |
| Dev | `playground-dev` | `codex` | `gpt-5.4` | `workstation/playground/agents/dev.md` `runtime:` + `model:` | `PLAYGROUND_DEV_RUNTIME=...` / `PLAYGROUND_DEV_MODEL=...` |

## Fast Checks

```bash
# Show effective defaults, env overrides, and saved agent-deck commands
./scripts/show_playground_team.sh

# Launch the team with defaults
./scripts/launch_playground_team.sh "volatility regime papers"
```

## Override Rules

- Persistent defaults: edit the `runtime:` and `model:` frontmatter in `workstation/playground/agents/*.md`
- One-off launch overrides: export `PLAYGROUND_<AGENT>_RUNTIME=...` and/or `PLAYGROUND_<AGENT>_MODEL=...` before launch
- After changing a playground agent file, `scripts/sync_playground_agents.sh` notifies the matching live session to re-read its identity file
- Restart a session when you want a model change to take effect in that running session

## Examples

```bash
# Temporarily run Cerebro on sonnet for one launch
PLAYGROUND_CEREBRO_MODEL=sonnet ./scripts/launch_playground_team.sh "macro regime papers"

# Temporarily run Explorer on Claude Opus for a deeper ideation pass
PLAYGROUND_EXPLORER_RUNTIME=claude PLAYGROUND_EXPLORER_MODEL=opus \
  ./scripts/launch_playground_team.sh "market microstructure papers"
```
