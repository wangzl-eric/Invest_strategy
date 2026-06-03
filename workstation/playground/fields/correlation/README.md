# Correlation Field

**Focus:** Cross-asset correlations, diversification, and correlation regime analysis

## Key Questions

- How do correlations change over time?
- What drives correlation breakdowns?
- How stable are diversification benefits?
- Do correlations spike during crises?
- How to build truly diversified portfolios?

## Data Sources

### Primary
- **Equity Indices** - SPY, QQQ, IWM, EFA, EEM
- **Fixed Income** - TLT, IEF, SHY, LQD, HYG
- **Commodities** - GLD, USO, DBA
- **Alternatives** - VIX, USD index

### Secondary
- **Sector ETFs** - For intra-equity correlations
- **Factor ETFs** - For factor correlations

## Common Analyses

### 1. Rolling Correlation
```python
# 60-day rolling correlation
rolling_corr = returns1.rolling(60).corr(returns2)
```

### 2. Correlation Matrix
```python
# Full correlation matrix
corr_matrix = returns.corr()
```

### 3. Correlation Regimes
```python
# High/low correlation periods
avg_corr = returns.corr().mean().mean()
high_corr_regime = rolling_avg_corr > threshold
```

### 4. Crisis Correlation
```python
# Correlation during market stress
crisis_periods = (spy_returns < spy_returns.quantile(0.05))
crisis_corr = returns[crisis_periods].corr()
normal_corr = returns[~crisis_periods].corr()
```

## Study Templates

- `notebooks/correlation_stability.ipynb` - Time-varying correlations
- `notebooks/crisis_correlation.ipynb` - Correlation during stress
- `notebooks/diversification_analysis.ipynb` - Portfolio diversification
- `notebooks/correlation_clustering.ipynb` - Asset clustering by correlation

## Completed Studies

See `studies/INDEX.md` for full list.

## Promising Studies (Research Candidates)

None yet - this is a new field.

## Related Fields

- **Portfolio** - Correlations drive portfolio optimization
- **Volatility** - Correlations spike with volatility
- **Macro** - Correlations change across regimes
- **All fields** - Correlations relevant everywhere

## References

- "Correlation Risk" (Driessen et al.)
- "Diversification Return" (Booth & Fama)
- "When Diversification Fails" (Ang & Chen)

## Notes

- Correlations are not stable
- Tend to increase during crises ("correlation goes to 1")
- Sample correlation is noisy with short histories
- Use shrinkage estimators for robustness
- Focus on tail correlations for risk management
