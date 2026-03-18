# Market Study Playground

**Purpose:** Interactive learning and exploration environment for studying markets without formal research rigor requirements.

## What is the Playground?

The playground is a **separate space** from the formal research workflow (`research/`) where you can:
- Explore market data interactively
- Test ideas quickly without statistical gates
- Learn quantitative techniques through tutorials
- Generate hypotheses for future research
- Study market relationships and regimes

## Key Differences from Research Workflow

| Aspect | Research (`research/`) | Playground (`playground/`) |
|--------|----------------------|---------------------------|
| **Purpose** | Production strategies | Learning & exploration |
| **Rigor** | 11 quantitative gates, PM review | No gates, no formal review |
| **Agents** | PM (gatekeeper), Cerebro (challenge) | Tutor (guide), Explorer (suggest) |
| **Output** | Strategy folders, verdicts | Study folders, observations |
| **Backtest** | Mandatory (walk-forward, costs) | Optional (visualization focus) |
| **Timeline** | Multi-round review (days/weeks) | Single session (hours) |
| **Documentation** | STRATEGY_TRACKER.md | Lightweight findings.md |

## Quick Start

```bash
# Activate environment
conda activate ibkr-analytics
export PYTHONPATH=.

# Launch Jupyter
jupyter lab

# Open a tutorial notebook
playground/notebooks/00_getting_started.ipynb
```

## Directory Structure

```
playground/
├── README.md                    # This file
├── FIELDS.md                   # Field organization guide
├── QUICK_REFERENCE.md          # Cheat sheet for common tasks
├── fields/                     # Topic-based research areas
│   ├── volatility/            # Volatility studies
│   ├── momentum/              # Momentum & trend studies
│   ├── carry/                 # Carry & yield studies
│   ├── macro/                 # Macro regime & indicators
│   ├── correlation/           # Cross-asset relationships
│   ├── options/               # Options & derivatives
│   ├── fx/                    # Foreign exchange
│   ├── crypto/                # Cryptocurrency
│   └── portfolio/             # Portfolio construction
├── shared/                     # Shared resources
│   ├── notebooks/             # General-purpose notebooks
│   ├── data_helpers.py        # Data access utilities
│   └── viz_helpers.py         # Visualization utilities
├── agents/                     # Playground-specific agents
│   ├── tutor.md               # Educational guide
│   └── explorer.md            # Hypothesis generator
└── skills/                     # Playground-specific skills
    └── market-study/          # Exploratory workflow
```

**Note:** See [FIELDS.md](FIELDS.md) for detailed field organization and workflow.

## Field-Based Organization

Studies are organized by research field/topic in `fields/`:

- **volatility/** - VIX analysis, vol regimes, volatility risk premium
- **momentum/** - Price momentum, trend following, momentum crashes
- **carry/** - FX carry, commodity carry, yield strategies
- **macro/** - Economic indicators, business cycles, recession signals
- **correlation/** - Cross-asset correlations, diversification analysis
- **options/** - Options pricing, Greeks, volatility trading
- **fx/** - Currency analysis, FX carry and momentum
- **crypto/** - Cryptocurrency analysis, crypto-equity correlation
- **portfolio/** - Portfolio construction, optimization, rebalancing

Each field contains:
- `README.md` - Field overview, key questions, common analyses
- `notebooks/` - Field-specific analysis notebooks
- `studies/` - Completed studies with findings
- `INDEX.md` - Study tracker for the field

See [FIELDS.md](FIELDS.md) for detailed organization guide and [GET_STARTED_QUICK.md](GET_STARTED_QUICK.md) for quick start workflow.

## Leveraging Existing Infrastructure

The playground reuses your existing components:

### Data Access
- **quant_data/** - DuckDB store, connectors (Binance, Stooq, Polygon, ECB FX)
- **backend/market_data_store.py** - Parquet data lake
- **backend/market_data_service.py** - FRED macro data
- **shared/data_helpers.py** - Simplified wrappers for playground use
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
- `notebooks/beginner_research_tutorial.ipynb` - Backtrader basics
- `notebooks/portfolio_builder_tutorial.ipynb` - Portfolio optimization
- `notebooks/signal_research_tutorial.ipynb` - Signal development

## Agents

### Tutor Agent
Educational guide that explains concepts and suggests next steps WITHOUT enforcing rigor gates.

```bash
# Invoke tutor for guidance
/tutor "How do I analyze correlation between assets?"
```

### Explorer Agent
Hypothesis generation agent that suggests interesting market relationships and study ideas.

```bash
# Invoke explorer for ideas
/explorer "What's interesting in the market right now?"
```

## Starting a New Study

```bash
# 1. Choose your field
cd playground/fields/volatility

# 2. Create study folder
mkdir studies/2026-03-18_my_study

# 3. Copy template
cp ../STUDY_TEMPLATE.md studies/2026-03-18_my_study/README.md

# 4. Create notebook and start analyzing
jupyter lab
```

See [GET_STARTED_QUICK.md](GET_STARTED_QUICK.md) for detailed workflow.

## Graduating to Research

When a playground study shows promise:

1. **Review lessons learned** - Check `memory/LESSONS_LEARNED.md`
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

- **Tutor agent**: `/tutor "your question"`
- **Documentation**: See QUICK_REFERENCE.md
- **Existing tutorials**: Check `notebooks/` directory
- **Research workflow**: See `research/README.md`
