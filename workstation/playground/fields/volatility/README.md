# Volatility Field

**Focus:** Volatility dynamics, regime detection, and volatility-based trading strategies

## Key Questions

- How does implied volatility predict realized volatility?
- What drives volatility risk premium (VRP)?
- How do volatility regimes affect asset returns?
- Can volatility term structure predict market moves?
- How does volatility clustering impact portfolio risk?

## Data Sources

### Primary
- **VIX** - CBOE Volatility Index (S&P 500 implied vol)
- **VIX3M** - CBOE 3-Month Volatility Index
- **SPY** - S&P 500 ETF (for realized vol calculation)
- **VVIX** - Volatility of VIX

### Secondary
- **VXN** - NASDAQ-100 Volatility Index
- **RVX** - Russell 2000 Volatility Index
- **OVX** - Oil Volatility Index
- **GVZ** - Gold Volatility Index

## Common Analyses

### 1. Volatility Risk Premium
```python
# VRP = Implied Vol - Realized Vol
vrp = vix - realized_vol_20d
```

### 2. Term Structure
```python
# Contango/backwardation
term_structure = vix3m / vix - 1
```

### 3. Volatility Regimes
```python
# Low/Medium/High vol regimes
regimes = pd.cut(vix, bins=[0, 15, 25, 100], labels=['Low', 'Medium', 'High'])
```

### 4. Realized Volatility
```python
# 20-day realized vol (annualized)
returns = np.log(spy / spy.shift(1))
realized_vol = returns.rolling(20).std() * np.sqrt(252) * 100
```

## Study Templates

- `notebooks/vix_term_structure.ipynb` - Term structure analysis
- `notebooks/vrp_analysis.ipynb` - Volatility risk premium
- `notebooks/vol_regime_detection.ipynb` - Regime identification
- `notebooks/realized_vs_implied.ipynb` - Forecast accuracy

## Completed Studies

See `studies/INDEX.md` for full list.

## Promising Studies (Research Candidates)

None yet - this is a new field.

## Related Fields

- **Momentum** - Volatility affects momentum strategies
- **Portfolio** - Volatility targeting and risk parity
- **Options** - Volatility is key input for options pricing
- **Macro** - Volatility spikes during recessions

## References

- CBOE VIX White Paper
- "Volatility Trading" by Euan Sinclair
- "The VIX Index and Volatility-Based Global Indexes and Trading Instruments" (CBOE)

## Notes

- VIX is forward-looking (30-day implied vol)
- VRP tends to be positive (insurance premium)
- Volatility clustering: high vol follows high vol
- Volatility mean-reverts over time
