# Knowledge Quick Reference

Quick reference for common tasks in the Market Study Playground.

## Data Access

### Load Price Data

```python
from alpha_research.quant_data.api import get_prices

# Returns LONG format: (date, ticker, open, high, low, close, volume)
spy = get_prices('SPY', start='2020-01-01', end='2024-12-31')

tickers = ['SPY', 'TLT', 'GLD']
raw = get_prices(tickers, start='2020-01-01', end='2024-12-31')

# Pivot to wide for anything cross-sectional
prices = raw.pivot(index='date', columns='ticker', values='close')
```

### Load Macro Data (FRED)

```python
from alpha_research.quant_data.api import get_fred

# Returns LONG format: (date, series_id, value, reference_date)
vix = get_fred('VIXCLS', start='2020-01-01')
vix_s = vix.set_index('date')['value']          # as a Series

series_ids = ['DGS10', 'DGS2', 'VIXCLS']
macro = (get_fred(series_ids, start='2020-01-01')
         .pivot(index='date', columns='series_id', values='value'))
```

Macro series are PIT-shifted to their publication date by default. Never pass
`pit=False` in anything that resembles a backtest.

### Get a Cross-Asset Snapshot

```python
from alpha_research.quant_data.api import get_data

basket = ['SPY', 'TLT', 'GLD', 'UUP']
snapshot = (get_data(basket, start='2024-01-01')
            .pivot(index='date', columns='ticker', values='close')
            .tail(1))
print(snapshot)
```

## Visualization

### Price Chart

```python
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=spy.index, y=spy['close'], name='SPY'))
fig.update_layout(title='SPY Price', xaxis_title='Date', yaxis_title='Price')
fig.show()
```

### Correlation Heatmap

```python
from alpha_research.quant_data.analytics import compute_correlation_matrix
import plotly.express as px

# compute_correlation_matrix takes a RETURNS DataFrame, not tickers
from alpha_research.quant_data.api import get_data
wide = (get_data(['SPY', 'TLT', 'GLD'], start='2020-01-01')
        .pivot(index='date', columns='ticker', values='close'))
corr = compute_correlation_matrix(wide.pct_change().dropna())

# Plot heatmap
fig = px.imshow(corr, text_auto=True, aspect='auto',
                title='Asset Correlation (60-day)')
fig.show()
```

### Rolling Correlation

```python
import pandas as pd

# Use the wide frame from Data Access above
rolling_corr = prices['SPY'].pct_change().rolling(60).corr(prices['TLT'].pct_change())

# Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=rolling_corr.index, y=rolling_corr,
                         name='SPY-TLT Correlation'))
fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.update_layout(title='SPY-TLT Rolling Correlation (60-day)')
fig.show()
```

## Analysis

### Returns Calculation

```python
# Simple returns
returns = spy['close'].pct_change()

# Log returns
log_returns = np.log(spy['close'] / spy['close'].shift(1))

# Cumulative returns
cum_returns = (1 + returns).cumprod() - 1
```

### Volatility

```python
# Rolling volatility (annualized)
vol = returns.rolling(20).std() * np.sqrt(252)

# Exponentially weighted volatility
ewm_vol = returns.ewm(span=20).std() * np.sqrt(252)
```

### Drawdown

```python
# Calculate drawdown
cum_returns = (1 + returns).cumprod()
running_max = cum_returns.expanding().max()
drawdown = (cum_returns - running_max) / running_max

# Max drawdown
max_dd = drawdown.min()
print(f"Max Drawdown: {max_dd:.2%}")
```

## Regime Detection

### Simple VIX Regime

```python
from alpha_research.quant_data.api import get_fred

vix = get_fred('VIXCLS', start='2020-01-01')

# Define regimes
vix['regime'] = pd.cut(vix['value'],
                       bins=[0, 15, 25, 100],
                       labels=['Low Vol', 'Medium Vol', 'High Vol'])

# Count regime days
print(vix['regime'].value_counts())
```

### Yield Curve Regime

```python
# Get 10Y and 2Y yields
yields = get_fred(['DGS10', 'DGS2'], start='2020-01-01')

# Calculate spread
spread = yields['DGS10'] - yields['DGS2']

# Define regimes
regime = pd.cut(spread, bins=[-10, 0, 0.5, 10],
                labels=['Inverted', 'Flat', 'Steep'])
```

## Saving Studies

### Create Study Folder

```python
from pathlib import Path
from datetime import datetime

# Create timestamped folder
date = datetime.now().strftime('%Y-%m-%d')
topic = 'vix_spy_correlation'
study_dir = Path(f'knowledge/studies/{date}_{topic}')
study_dir.mkdir(parents=True, exist_ok=True)

print(f"Study folder created: {study_dir}")
```

### Save Findings

```python
findings = """
# VIX-SPY Correlation Study

## Question
How does VIX-SPY correlation change during market stress?

## Data
- SPY: 2020-01-01 to 2024-12-31
- VIX: FRED series VIXCLS

## Observations
1. Correlation becomes more negative during high VIX periods
2. Rolling 60-day correlation ranges from -0.8 to -0.2
3. Correlation breakdown during March 2020 COVID crash

## Next Steps
- Investigate correlation stability across different vol regimes
- Compare to other equity indices
- Consider for risk overlay strategy
"""

with open(study_dir / 'findings.md', 'w') as f:
    f.write(findings)
```

### Export Chart

```python
# Save plotly figure
fig.write_html(study_dir / 'correlation_chart.html')

# Save as static image (requires kaleido)
fig.write_image(study_dir / 'correlation_chart.png')
```

## Using Agents

### Mechanism Q&A (`/explain-mechanism`)

Desk-register explanation of a market instrument, spread, or convention — identity
first, numbers always, sign traps and hidden exposures named. Writes no file.

```bash
/explain-mechanism "what is an asset swap spread?"
/explain-mechanism "describe the cash flows for a variance swap"
/explain-mechanism "what exposure is an invoice spread payer taking?"
```

### Tutor Agent (Educational Guidance)

`tutor` is an agent-deck / codex session launched by
`./scripts/launch_playground_team.sh` — **not** a slash command, and not reachable
from an ordinary Claude Code session. Its register is intuition-before-formulas for
a beginner; use `/explain-mechanism` above for the desk register.

### Explorer Agent (Hypothesis Generation)

```bash
# Get study ideas
/explorer "What's interesting in the market right now?"

# Suggest relationships
/explorer "What assets should I analyze together?"

# Identify anomalies
/explorer "Are there any unusual patterns in recent data?"
```

## Data Sources

### Available via alpha_research.quant_data

- **Equities**: SPY, QQQ, IWM, VTI, etc. (via yfinance or Parquet lake)
- **Bonds**: TLT, IEF, SHY, AGG, LQD, HYG
- **Commodities**: GLD, SLV, USO, DBC
- **FX**: UUP, FXE, FXY (ETF proxies)
- **Volatility**: VIX, VVIX (via FRED)
- **Macro**: FRED series (rates, spreads, economic indicators)

### FRED Series IDs (Common)

```python
fred_series = {
    'rates': ['DGS10', 'DGS2', 'DFF', 'T10Y2Y'],
    'volatility': ['VIXCLS', 'VVIX'],
    'credit': ['BAMLH0A0HYM2', 'BAMLC0A0CM'],
    'economic': ['UNRATE', 'CPIAUCSL', 'GDP'],
    'liquidity': ['WALCL', 'WRESBAL']
}
```

## Common Patterns

### Compare Asset Performance

```python
# Normalize to 100
assets = ['SPY', 'TLT', 'GLD']
prices = (get_prices(assets, start='2020-01-01')
          .pivot(index='date', columns='ticker', values='close'))

normalized = {a: prices[a] / prices[a].iloc[0] * 100 for a in assets}

# Plot
fig = go.Figure()
for asset, values in normalized.items():
    fig.add_trace(go.Scatter(x=values.index, y=values, name=asset))
fig.update_layout(title='Normalized Performance', yaxis_title='Index (100 = start)')
fig.show()
```

### Correlation Matrix Over Time

```python
# Calculate rolling correlation matrix
window = 60
tickers = ['SPY', 'TLT', 'GLD']
close_prices = (get_prices(tickers, start='2020-01-01')
                .pivot(index='date', columns='ticker', values='close'))

# Rolling correlation of RETURNS (correlating price levels is spurious)
rolling_corr = close_prices.pct_change().rolling(window).corr()

# Extract specific pair
spy_tlt_corr = rolling_corr.loc[(slice(None), 'SPY'), 'TLT']
```

### Regime-Conditional Statistics

```python
# Calculate returns by regime
vix = get_fred('VIXCLS', start='2020-01-01').set_index('date')['value']
spy = get_prices('SPY', start='2020-01-01').set_index('date')['close']

regime = pd.cut(vix, bins=[0, 20, 100], labels=['Low Vol', 'High Vol'])

merged = pd.DataFrame({
    'returns': spy.pct_change(),
    'regime': regime.reindex(spy.index).ffill(),
}).dropna()

# Stats by regime
print(merged.groupby('regime')['returns'].agg(['mean', 'std', 'count']))
```

## Tips

- **Start simple**: Use existing notebooks as templates
- **Iterate fast**: No need for statistical rigor in playground
- **Document findings**: Save interesting observations to findings.md
- **Graduate to research**: When ready, follow migration path in README.md
- **Leverage skills**: Use `/data-pulling` for data, `/market-intelligence-synthesizer` for articles
- **Ask agents**: Tutor for learning, Explorer for ideas

## Next Steps

1. Open `knowledge/tutorials/00_getting_started.ipynb`
2. Try loading data with `alpha_research.quant_data.api`
3. Create your first visualization
4. Save your first study
5. Ask Tutor agent for guidance
