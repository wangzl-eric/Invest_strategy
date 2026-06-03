# Playground Quick Start Guide

## Getting Started

### 1. Choose Your Field

Browse available fields in `playground/fields/`:
- **volatility** - VIX, vol regimes, volatility risk premium
- **momentum** - Price momentum, trend following
- **carry** - FX carry, commodity carry
- **macro** - Economic indicators, business cycles
- **correlation** - Cross-asset correlations
- **options** - Options pricing, Greeks
- **fx** - Currency analysis
- **crypto** - Cryptocurrency analysis
- **portfolio** - Portfolio construction

### 2. Start a New Study

```bash
# Navigate to your field
cd playground/fields/volatility

# Create study folder
mkdir studies/2026-03-18_my_study

# Copy template
cp ../STUDY_TEMPLATE.md studies/2026-03-18_my_study/README.md

# Create notebook
jupyter lab
# Open: studies/2026-03-18_my_study/analysis.ipynb
```

### 3. Load Data

```python
# In your notebook
import sys
sys.path.append('/Users/zelin/Desktop/PA Investment/Invest_strategy')

from playground.shared.data_helpers import load_market_data, load_fred_data

# Load equity data
spy = load_market_data('SPY')

# Load macro data
vix = load_fred_data('VIXCLS')
```

### 4. Analyze & Visualize

```python
from playground.shared.viz_helpers import plot_time_series, plot_correlation_matrix

# Plot time series
fig = plot_time_series(
    data=pd.DataFrame({'SPY': spy, 'VIX': vix}),
    columns=['SPY', 'VIX'],
    title='SPY vs VIX'
)

# Save chart
fig.savefig('studies/2026-03-18_my_study/charts/spy_vix.png', dpi=300)
```

### 5. Document Findings

Edit `studies/2026-03-18_my_study/README.md`:
- Update hypothesis
- Document methodology
- List key findings
- Add next steps

### 6. Update Field Index

```bash
# Add to field's INDEX.md
echo "- 2026-03-18_my_study - In Progress" >> studies/INDEX.md
```

## Common Workflows

### Correlation Analysis

```python
from playground.shared.viz_helpers import plot_correlation_matrix, plot_rolling_correlation

# Load multiple assets
assets = load_market_data(['SPY', 'TLT', 'GLD', 'VIX'])

# Correlation matrix
fig = plot_correlation_matrix(assets, title='Asset Correlations')

# Rolling correlation
fig = plot_rolling_correlation(
    assets['SPY'],
    assets['TLT'],
    window=60,
    title='SPY-TLT 60-Day Rolling Correlation'
)
```

### Regime Detection

```python
# Define regimes based on VIX
import pandas as pd

vix = load_fred_data('VIXCLS')
regimes = pd.cut(vix, bins=[0, 15, 25, 100], labels=['Low', 'Medium', 'High'])

# Plot with regime overlay
from playground.shared.viz_helpers import plot_regime_overlay
spy = load_market_data('SPY')
fig = plot_regime_overlay(spy, regimes, regime_labels={0: 'Low Vol', 1: 'Medium Vol', 2: 'High Vol'})
```

### Momentum Analysis

```python
# Calculate momentum
prices = load_market_data(['SPY', 'QQQ', 'IWM'])
momentum = prices.pct_change(252)  # 12-month

# Rank assets
ranks = momentum.rank(axis=1, pct=True)
```

## Tips

1. **Start Simple** - Begin with basic analysis, add complexity later
2. **Document as You Go** - Update README.md throughout the study
3. **Save Charts** - Export visualizations to `charts/` folder
4. **Cache Data** - Save processed data to `data/` folder to avoid reloading
5. **Cross-Reference** - Link to related studies in other fields
6. **Graduate Promising Ideas** - Move strong findings to formal research

## Getting Help

- **Field README** - Each field has overview and common analyses
- **Tutor Agent** - Ask questions: `/tutor "How do I..."`
- **Explorer Agent** - Get ideas: `/explorer "What's interesting in..."`
- **QUICK_REFERENCE.md** - Detailed reference guide

## Next Steps

After completing a study:
1. Mark status as "Complete" in README.md
2. Update field INDEX.md
3. If promising, add to "Research Candidates" section
4. Consider graduating to formal research workflow
