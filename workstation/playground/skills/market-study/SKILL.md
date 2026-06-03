---
name: market-study
description: Exploratory market study workflow for the Playground. Guides users through data exploration, visualization, and observation WITHOUT enforcing research rigor or statistical gates.
---

# Market Study Skill

Conduct exploratory market studies in the Playground environment. This skill guides you through a lightweight workflow for investigating market patterns, relationships, and anomalies without formal research requirements.

## When to Use

Use this skill when:
- Exploring market data interactively
- Testing ideas quickly without formal backtest
- Learning quantitative techniques
- Generating hypotheses for future research
- Studying market relationships and regimes

Do NOT use for:
- Formal strategy research (use rigorous-backtest skill instead)
- Production-ready backtesting
- PM review or verdict process

## Workflow

### 1. Define Question

Start with a clear, specific question:
- "How does SPY-TLT correlation change during high VIX periods?"
- "What happens to momentum strategies in low volatility regimes?"
- "Is the gold-real rates relationship stable over time?"

### 2. Load Data

Use `playground/data_helpers.py` for simplified access:

```python
from playground.data_helpers import get_prices, get_macro_series

# Load price data
spy = get_prices('SPY', start='2020-01-01')
tlt = get_prices('TLT', start='2020-01-01')

# Load macro data
vix = get_macro_series('VIXCLS', start='2020-01-01')
```

### 3. Explore & Visualize

Create visualizations to understand the data:

```python
import plotly.graph_objects as go

# Price chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=spy.index, y=spy['close'], name='SPY'))
fig.show()

# Correlation heatmap
from playground.data_helpers import get_correlation_matrix
corr = get_correlation_matrix(['SPY', 'TLT', 'GLD'], window=60)
```

### 4. Analyze

Compute relevant metrics:

```python
from playground.data_helpers import calculate_returns, calculate_volatility

# Returns
returns = calculate_returns(spy['close'])

# Volatility
vol = calculate_volatility(returns, window=20)

# Regime-conditional stats
high_vol = returns[vix['value'] > 25]
low_vol = returns[vix['value'] < 15]
```

### 5. Document Observations

Save findings in a lightweight format:

```markdown
# Study: SPY-TLT Correlation in High Vol

## Question
How does SPY-TLT correlation change during high VIX periods?

## Data
- SPY, TLT: 2020-01-01 to 2024-12-31
- VIX: FRED series VIXCLS

## Observations
1. Correlation more negative during VIX > 25 (-0.6 vs -0.3)
2. Relationship stable across multiple high vol episodes
3. Breakdown during March 2020 (both fell together)

## Next Steps
- Compare to other equity indices
- Test stability across longer history
- Consider for risk overlay strategy
```

### 6. Save Study (Optional)

If findings are interesting, save for future reference:

```bash
# Create study folder
mkdir -p playground/studies/2026-03-18_spy_tlt_correlation

# Copy notebook
cp playground/notebooks/02_correlation_explorer.ipynb \
   playground/studies/2026-03-18_spy_tlt_correlation/study.ipynb

# Save findings
# (write findings.md as shown above)
```

## Key Principles

### DO
✅ Start with a specific question
✅ Use existing notebooks as templates
✅ Create visualizations to build intuition
✅ Document interesting observations
✅ Iterate quickly without rigor requirements
✅ Ask Tutor agent for guidance
✅ Ask Explorer agent for study ideas

### DON'T
❌ Enforce statistical significance tests
❌ Require formal backtesting
❌ Demand walk-forward validation
❌ Compare to research standards
❌ Create formal strategy proposals
❌ Seek PM approval or verdict

## Available Notebooks

Use these as starting points:

- `00_getting_started.ipynb` - Platform tour, data access
- `01_market_overview.ipynb` - Cross-asset snapshot
- `02_correlation_explorer.ipynb` - Correlation analysis
- `03_regime_detector.ipynb` - Regime identification
- `04_signal_sandbox.ipynb` - Signal prototyping

## Common Study Types

### Correlation Study
1. Load 2+ assets
2. Calculate rolling correlation
3. Visualize over time
4. Split by regime (optional)
5. Document stability/changes

### Regime Analysis
1. Define regime indicator (VIX, yield curve, etc.)
2. Split data into regimes
3. Calculate regime-conditional statistics
4. Compare distributions
5. Document regime differences

### Event Study
1. Identify event dates
2. Load relevant assets
3. Calculate returns around events
4. Aggregate across events
5. Document patterns

### Factor Analysis
1. Define factor (momentum, value, etc.)
2. Rank assets by factor
3. Compare top vs bottom quintile
4. Analyze over time
5. Document factor behavior

## Graduating to Research

When a playground study shows promise:

1. **Check lessons learned** - Review `memory/LESSONS_LEARNED.md`
2. **Verify data quality** - Ensure data meets research standards
3. **Message Cerebro** - Request literature briefing
4. **Create strategy folder** - Use `research/strategies/{name}_{date}_in_review/`
5. **Use research template** - Switch to formal notebook
6. **Follow v2 workflow** - Multi-round PM review with gates

See `playground/README.md` for full migration path.

## Example: Quick Correlation Study

```python
# 1. Question: How stable is SPY-TLT correlation?

# 2. Load data
from playground.data_helpers import get_prices
spy = get_prices('SPY', start='2020-01-01')
tlt = get_prices('TLT', start='2020-01-01')

# 3. Calculate rolling correlation
import pandas as pd
spy_returns = spy['close'].pct_change()
tlt_returns = tlt['close'].pct_change()
rolling_corr = spy_returns.rolling(60).corr(tlt_returns)

# 4. Visualize
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Scatter(x=rolling_corr.index, y=rolling_corr, name='SPY-TLT Corr'))
fig.add_hline(y=0, line_dash="dash")
fig.update_layout(title='SPY-TLT Rolling Correlation (60-day)')
fig.show()

# 5. Observations
print(f"Mean correlation: {rolling_corr.mean():.2f}")
print(f"Std correlation: {rolling_corr.std():.2f}")
print(f"Min correlation: {rolling_corr.min():.2f}")
print(f"Max correlation: {rolling_corr.max():.2f}")

# 6. Document in findings.md (see template above)
```

## Tips

- **Start simple** - Don't overcomplicate initial analysis
- **Visualize first** - Charts build intuition faster than numbers
- **Iterate quickly** - No need for perfection in playground
- **Document findings** - Future you will thank you
- **Ask for help** - Use Tutor agent for guidance, Explorer for ideas
- **Have fun** - Playground is for learning and exploration!

## References

- `playground/README.md` - Playground overview
- `playground/QUICK_REFERENCE.md` - Common tasks cheat sheet
- `playground/data_helpers.py` - Data access functions
- `playground/agents/tutor.md` - Educational guidance
- `playground/agents/explorer.md` - Hypothesis generation
