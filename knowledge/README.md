# Market Study Playground

**Purpose:** Interactive learning and exploration environment for studying markets without formal research rigor requirements.

> ## → Start at [`brain/`](brain/README.md)
>
> The **second brain** is where reading is condensed into reusable thought. Everything else in the
> playground produces *source-faithful* notes (L1); the brain holds the *transferable* atoms (L2) those
> notes collapse into, and links back to them:
>
> | | | |
> |---|---|---|
> | **Mechanisms** — what to trade, who pays | 46 atoms | [`reports/IDEAS.md`](reports/IDEAS.md) |
> | **Concepts** — the machinery beneath them | 10 atoms | [`brain/concepts/`](brain/concepts/) |
> | **Verdicts** — what we tried and what happened | 13 records | [`brain/VERDICTS.md`](brain/VERDICTS.md) |
> | **Inbox** — your own raw thoughts, unpolished | live | [`brain/INBOX.md`](brain/INBOX.md) |
>
> Nothing in the brain replaces its source. Run `python3 scripts/check_brain_integrity.py` after edits.

## What is the Playground?

The playground is a **separate space** from the formal research workflow (`research/`) where you can:
- Explore market data interactively
- Test ideas quickly without statistical gates
- Learn quantitative techniques through tutorials
- Generate hypotheses for future research
- Study market relationships and regimes

## Key Differences from Research Workflow

| Aspect | Formal research (`alpha_research/`) | Knowledge tree (`knowledge/`) |
|--------|----------------------|---------------------------|
| **Purpose** | Production strategies | Learning & exploration |
| **Rigor** | 11 quantitative gates, PM review | No gates, no formal review |
| **Agents** | PM (gatekeeper), Cerebro (challenge) | Tutor (guide), Explorer (suggest) |
| **Output** | Strategy folders, verdicts | Study folders, observations |
| **Backtest** | Mandatory (walk-forward, costs) | Optional (visualization focus) |
| **Timeline** | Multi-round review (days/weeks) | Single session (hours) |
| **Documentation** | STRATEGY_TRACKER.md | Lightweight `studies/<topic>/README.md` |

## Quick Start

```bash
# Activate environment
conda activate ibkr-analytics
export PYTHONPATH=.

# Launch Jupyter
jupyter lab

# Open a tutorial notebook
knowledge/tutorials/00_getting_started.ipynb
```

## Directory Structure

```
knowledge/
├── README.md                    # This file
├── QUICK_REFERENCE.md          # Cheat sheet for common tasks
├── GET_STARTED_QUICK.md        # Quick start workflow
├── FIELDS.md                   # RETIRED taxonomy — kept for reference
├── brain/                      # Concept/verdict KB (indexed, pre-commit guarded)
├── domains/                    # KNOWLEDGE_{FX,EQUITY,MACRO,VOL}.md
├── papers/                     # Paper notes + INDEX.md
├── reports/                    # Report library + IDEAS.md (the idea pool)
├── books/                      # Book chapter notes, one folder per book
├── studies/                    # ← your own investigations live here
│   ├── TEMPLATE.md            # the single study template
│   └── <YYYY-MM-DD>_<topic>/
├── fields/                     # Field primers only (README.md per field)
├── sources/                    # Source PDFs
├── shared/                     # viz_helpers.py + notebook templates
├── tutorials/                  # Numbered platform tutorials (00-08)
├── agents/                     # Study-team agent definitions
└── skills/                     # market-study (not harness-loaded)
```

## Where work goes

| What you are doing | Where it goes |
|---|---|
| Reading a paper / report / book | `papers/`, `reports/`, `books/` |
| **Your own investigation** | **`studies/<YYYY-MM-DD>_<topic>/`** |
| A claim that survived the work | `brain/` (concepts, verdicts) or `domains/` |
| An idea queued for formal rigor | `reports/IDEAS.md` |
| Rigor-gated, promotable strategy | `alpha_research/` (leaves this tree) |

**`fields/` is retired** (2026-08-18) — see [FIELDS.md](FIELDS.md). The nine field
`README.md` files remain as useful primers (key questions, data sources per field),
but do not file new work there. Topic organisation now derives from content:
`domain:` frontmatter in `brain/concepts/` and the mechanism families in
`reports/IDEAS.md`.

The nine field primers under `fields/` list key questions and data sources per field
(volatility, momentum, carry, macro, correlation, options, fx, crypto, portfolio).
Read them for orientation; file the work itself in `studies/`.

## Leveraging Existing Infrastructure

The knowledge tree reuses your existing components:

### Data Access
- **alpha_research/quant_data/** - `api.get_data()`, DuckDB store, connectors (Binance, Stooq, Polygon, ECB FX)
- **backend/market_data_store.py** - Parquet data lake
- **backend/market_data_service.py** - FRED macro data
- **shared/viz_helpers.py** - Reusable plotting functions

### Skills
- **data-pulling** - Pull market data (relaxed validation for playground)
- **market-intelligence-synthesizer** - Read research reports and articles

### Agents (Advisory Mode)
- **Cerebro** - Literature search and research discovery
- **Data** - Data coverage and source selection
- **Marco/Elena** - Domain expertise (no gatekeeper role)

### Existing Notebooks
The playground complements (not replaces) existing tutorials:
- `tutorials/01_beginner_research.ipynb` - Backtrader basics
- `tutorials/06_portfolio_builder.ipynb` - Portfolio optimization
- `tutorials/04_signal_research.ipynb` - Signal development

## Agents

### Tutor Agent
Educational guide that explains concepts and suggests next steps WITHOUT enforcing rigor gates.

**Note:** `tutor` is an agent-deck / codex session, launched by
`./scripts/launch_playground_team.sh` — it is *not* a slash command and is not
reachable from an ordinary Claude Code session. For market-mechanism Q&A from a
Claude Code session, use the skill instead:

```bash
# Explain a market instrument, spread, or convention (desk register)
/explain-mechanism "how does the cross-currency basis actually work?"
```

### Explorer Agent
Hypothesis generation agent that suggests interesting market relationships and study ideas.

```bash
# Invoke explorer for ideas
/explorer "What's interesting in the market right now?"
```

## Playground Agent-Deck Team

For paper reading and knowledge-scope expansion, you can launch a dedicated `agent-deck` team:

```bash
# Show defaults and override points
./scripts/show_playground_team.sh

# Launch playground team
./scripts/launch_playground_team.sh "volatility regime papers"

# Stop sessions
./scripts/cleanup_playground_team.sh
```

Team roles:
- **Explorer** — turns readings into study ideas and open hypotheses
- **Tutor** — explains concepts, methods, and reading paths
- **Cerebro** — builds reading queues and expands adjacent literature scope
- **Dev** — helps reproduce ideas in notebooks, helpers, and lightweight tooling

Model defaults are summarized in `PLAYGROUND_TEAM_MODELS.md`. Persistent defaults live in `knowledge/agents/*.md` frontmatter (`runtime:` and `model:`). One-off launch overrides use env vars like `PLAYGROUND_CEREBRO_MODEL=sonnet` or `PLAYGROUND_EXPLORER_RUNTIME=claude`.

## Starting a New Study

```bash
# 1. Create the study folder (date-prefixed, topic-named)
mkdir -p knowledge/studies/2026-09-04_my_study/{notebooks,data}

# 2. Copy the single template
cp knowledge/studies/TEMPLATE.md knowledge/studies/2026-09-04_my_study/README.md

# 3. Skim the relevant field primer for key questions and data sources
cat knowledge/fields/volatility/README.md

# 4. Start analyzing
jupyter lab
```

See [GET_STARTED_QUICK.md](GET_STARTED_QUICK.md) for detailed workflow.

## Graduating to Research

When a playground study shows promise:

1. **Review prior verdicts** - Check `brain/VERDICTS.md` and the relevant `domains/KNOWLEDGE_*.md`
2. **Check data requirements** - Verify data quality meets research standards
3. **Message Cerebro** - Request literature briefing
4. **Create strategy folder** - Use `research/strategies/{name}_{date}_in_review/`
5. **Use research template** - Switch to formal notebook template
6. **Follow v2 workflow** - Multi-round PM review with quantitative gates

## Common Tasks

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for detailed reference on:
- Loading market data
- Creating visualizations
- Computing correlations
- Identifying regimes
- Using agents

See [GET_STARTED_QUICK.md](GET_STARTED_QUICK.md) for quick start workflow and common analysis patterns.

## Getting Help

- **Mechanism Q&A**: `/explain-mechanism "your question"` (the `tutor` agent is an agent-deck/codex session, launched by `./scripts/launch_playground_team.sh`, not a slash command)
- **Documentation**: See QUICK_REFERENCE.md
- **Existing tutorials**: Check `notebooks/` directory
- **Research workflow**: See `research/README.md`
