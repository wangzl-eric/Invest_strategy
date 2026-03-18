# Playground Field Organization

**Purpose:** Organize personal research and exploration by field/topic to maintain clear boundaries and context.

## Field Structure

```
playground/
├── fields/                          # Topic-based research areas
│   ├── volatility/                  # Volatility studies
│   │   ├── README.md               # Field overview
│   │   ├── notebooks/              # Field-specific notebooks
│   │   ├── studies/                # Completed studies
│   │   └── data/                   # Field-specific cached data
│   ├── momentum/                    # Momentum & trend studies
│   ├── carry/                       # Carry & yield studies
│   ├── macro/                       # Macro regime & indicators
│   ├── correlation/                 # Cross-asset relationships
│   ├── options/                     # Options & derivatives
│   ├── fx/                          # Foreign exchange
│   ├── crypto/                      # Cryptocurrency
│   └── portfolio/                   # Portfolio construction
└── shared/                          # Shared resources
    ├── notebooks/                   # General-purpose notebooks
    ├── data_helpers.py             # Data access utilities
    └── viz_helpers.py              # Visualization utilities
```

## Available Fields

### 1. Volatility (`fields/volatility/`)
- VIX analysis and regime detection
- Realized vs implied volatility
- Volatility risk premium studies
- Vol surface analysis
- GARCH modeling

### 2. Momentum (`fields/momentum/`)
- Price momentum signals
- Cross-sectional momentum
- Time-series momentum
- Momentum crashes
- Factor timing

### 3. Carry (`fields/carry/`)
- FX carry strategies
- Commodity carry
- Yield curve positioning
- Roll yield analysis

### 4. Macro (`fields/macro/`)
- Economic regime identification
- Macro indicators (PMI, CPI, etc.)
- Central bank policy analysis
- Business cycle positioning
- Recession indicators

### 5. Correlation (`fields/correlation/`)
- Cross-asset correlation
- Correlation breakdowns
- Diversification analysis
- Regime-dependent correlations

### 6. Options (`fields/options/`)
- Options pricing
- Greeks analysis
- Volatility trading
- Skew and term structure

### 7. FX (`fields/fx/`)
- Currency pairs analysis
- FX carry and momentum
- Central bank divergence
- Real exchange rates

### 8. Crypto (`fields/crypto/`)
- Cryptocurrency analysis
- Crypto-equity correlation
- On-chain metrics
- Crypto momentum

### 9. Portfolio (`fields/portfolio/`)
- Asset allocation
- Risk parity
- Mean-variance optimization
- Rebalancing strategies
- Portfolio construction experiments

## Field Workflow

### Starting a New Study

```bash
# 1. Choose your field
cd playground/fields/volatility

# 2. Create a study folder
mkdir studies/2026-03-18_vix_term_structure

# 3. Copy relevant notebook template
cp notebooks/template.ipynb studies/2026-03-18_vix_term_structure/analysis.ipynb

# 4. Document your hypothesis
cat > studies/2026-03-18_vix_term_structure/README.md << 'EOF'
# VIX Term Structure Study

**Date:** 2026-03-18
**Hypothesis:** VIX term structure slope predicts equity returns
**Data:** VIX, VIX3M, SPY
**Status:** In Progress
EOF
```

### Study Folder Structure

```
studies/2026-03-18_vix_term_structure/
├── README.md                    # Study overview and hypothesis
├── analysis.ipynb              # Main analysis notebook
├── findings.md                 # Key observations
├── data/                       # Study-specific data cache
└── charts/                     # Exported visualizations
```

## Cross-Field Studies

For studies spanning multiple fields, use the primary field and reference others:

```
fields/volatility/studies/2026-03-18_vol_momentum_interaction/
├── README.md                   # Note: "Cross-field: volatility + momentum"
├── analysis.ipynb
└── findings.md
```

## Shared Resources

### Data Helpers (`shared/data_helpers.py`)
Common data access patterns used across all fields.

### Visualization Helpers (`shared/viz_helpers.py`)
Reusable plotting functions and chart templates.

### General Notebooks (`shared/notebooks/`)
- `00_getting_started.ipynb` - Platform introduction
- `data_exploration.ipynb` - General data exploration
- `quick_analysis.ipynb` - Scratch notebook for quick checks

## Field-Specific Agents

Each field can have specialized agent configurations:

```
fields/volatility/agents/
├── vol_tutor.md               # Volatility-focused educational agent
└── vol_explorer.md            # Volatility hypothesis generator
```

## Graduating Studies to Research

When a field study shows promise:

1. **Document in field README** - Add to "Promising Studies" section
2. **Review lessons learned** - Check `memory/LESSONS_LEARNED.md`
3. **Message Cerebro** - Request literature briefing on the topic
4. **Create research strategy folder** - Move to formal `research/strategies/`
5. **Follow v2 workflow** - Multi-round PM review with quantitative gates

## Field Maintenance

### Adding a New Field

```bash
# 1. Create field structure
mkdir -p playground/fields/new_field/{notebooks,studies,data,agents}

# 2. Create field README
cat > playground/fields/new_field/README.md << 'EOF'
# New Field

**Focus:** [Description]
**Key Questions:** [Research questions]
**Data Sources:** [Required data]
EOF

# 3. Create notebook template
cp playground/shared/notebooks/template.ipynb \
   playground/fields/new_field/notebooks/template.ipynb

# 4. Update FIELDS.md
# Add new field to "Available Fields" section
```

### Field Index

Each field maintains an index of studies:

```
fields/volatility/INDEX.md

# Volatility Studies Index

## Active Studies
- 2026-03-18_vix_term_structure - In Progress
- 2026-03-15_vol_risk_premium - Complete

## Promising Studies (Candidates for Research)
- 2026-03-15_vol_risk_premium - Shows predictive power

## Archived Studies
- 2026-03-10_vix_spy_correlation - Inconclusive
```

## Benefits of Field Organization

1. **Context Preservation** - Related studies stay together
2. **Knowledge Building** - Build expertise within a domain
3. **Reduced Clutter** - Clear separation of topics
4. **Easy Navigation** - Find relevant past work quickly
5. **Specialization** - Develop field-specific tools and agents
6. **Cross-Reference** - Identify connections between studies in same field

## Migration from Flat Structure

To migrate existing studies:

```bash
# Move existing studies to appropriate fields
mv playground/studies/2026-03-18_vix_study \
   playground/fields/volatility/studies/

# Update references in notebooks
# Update study README with field context
```
