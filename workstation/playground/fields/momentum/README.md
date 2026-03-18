# Momentum Field

**Focus:** Price momentum, trend following, and momentum factor analysis

## Key Questions

- What lookback periods work best for momentum?
- How does momentum interact with volatility?
- When do momentum strategies crash?
- Cross-sectional vs time-series momentum?
- How to combine momentum with other factors?

## Data Sources

### Primary
- **Equity ETFs** - SPY, QQQ, IWM, EFA, EEM
- **Sector ETFs** - XLF, XLE, XLK, XLV, etc.
- **Commodity ETFs** - GLD, USO, DBA, DBC

### Secondary
- **Factor ETFs** - MTUM (momentum factor)
- **Futures data** - For time-series momentum

## Common Analyses

### 1. Price Momentum Signal
```python
# 12-month momentum (skip last month)
momentum = prices.pct_change(252).shift(21)
```

### 2. Cross-Sectional Momentum
```python
# Rank assets by momentum
ranks = momentum.rank(axis=1, pct=True)
```

### 3. Time-Series Momentum
```python
# Sign of past returns
signal = np.sign(prices.pct_change(60))
```

### 4. Momentum Crashes
```python
# Identify momentum drawdowns
momentum_portfolio_returns = ...
drawdowns = (momentum_portfolio_returns.cumsum() - momentum_portfolio_returns.cumsum().cummax())
```

## Study Templates

- `notebooks/momentum_lookback.ipynb` - Optimal lookback period
- `notebooks/cross_sectional_momentum.ipynb` - Ranking-based momentum
- `notebooks/momentum_crashes.ipynb` - Crash analysis
- `notebooks/momentum_vol_interaction.ipynb` - Momentum + volatility

## Completed Studies

See `studies/INDEX.md` for full list.

## Promising Studies (Research Candidates)

None yet - this is a new field.

## Related Fields

- **Volatility** - Vol affects momentum performance
- **Carry** - Momentum + carry combination
- **Macro** - Momentum in different regimes
- **Portfolio** - Momentum in portfolio construction

## References

- "Momentum" by Antonacci
- "Time Series Momentum" (Moskowitz, Ooi, Pedersen)
- "Fact, Fiction, and Momentum Investing" (AQR)

## Notes

- Momentum has strong empirical support
- Works across asset classes
- Prone to crashes during reversals
- Skip recent month to avoid microstructure noise
