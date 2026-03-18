# Macro Field

**Focus:** Macroeconomic indicators, business cycle analysis, and regime-based investing

## Key Questions

- How do macro regimes affect asset returns?
- Which indicators predict recessions?
- How to position portfolios across business cycles?
- What drives central bank policy changes?
- How do macro factors correlate with equity factors?

## Data Sources

### Primary (FRED)
- **GDP** - Real GDP growth (GDPC1)
- **Inflation** - CPI, PCE (CPIAUCSL, PCEPI)
- **Unemployment** - Unemployment rate (UNRATE)
- **Interest Rates** - Fed Funds, 10Y Treasury (DFF, DGS10)
- **Yield Curve** - 10Y-2Y spread (T10Y2Y)

### Secondary
- **PMI** - Manufacturing PMI (ISM)
- **Consumer Sentiment** - University of Michigan (UMCSENT)
- **Leading Indicators** - Conference Board LEI
- **Credit Spreads** - High yield spreads

## Common Analyses

### 1. Recession Indicators
```python
# Yield curve inversion
yield_curve = fred['DGS10'] - fred['DGS2']
recession_signal = yield_curve < 0
```

### 2. Business Cycle Phases
```python
# Growth + inflation matrix
growth = gdp.pct_change(4)  # YoY
inflation = cpi.pct_change(12)  # YoY
# Classify: Expansion, Stagflation, Recession, Recovery
```

### 3. Central Bank Policy
```python
# Fed tightening/easing cycles
fed_funds_change = fed_funds.diff(12)  # 12-month change
```

### 4. Macro Regime Detection
```python
# Combine multiple indicators
from sklearn.cluster import KMeans
features = pd.DataFrame({
    'growth': gdp_growth,
    'inflation': cpi_yoy,
    'yield_curve': yield_curve,
    'unemployment': unemployment
})
regimes = KMeans(n_clusters=4).fit_predict(features)
```

## Study Templates

- `notebooks/recession_indicators.ipynb` - Recession prediction
- `notebooks/business_cycle.ipynb` - Cycle phase identification
- `notebooks/macro_regime_returns.ipynb` - Asset returns by regime
- `notebooks/central_bank_policy.ipynb` - Policy cycle analysis

## Completed Studies

See `studies/INDEX.md` for full list.

## Promising Studies (Research Candidates)

None yet - this is a new field.

## Related Fields

- **Volatility** - Volatility spikes during recessions
- **Carry** - Carry strategies affected by rate cycles
- **Portfolio** - Macro-based asset allocation
- **Correlation** - Correlations change across regimes

## References

- "Business Cycles and Asset Allocation" (Fidelity)
- "A Practitioner's Guide to Asset Allocation" (Ang)
- FRED Economic Data documentation

## Notes

- Macro data is low-frequency (monthly/quarterly)
- Long lags in data releases
- Regime changes are rare but impactful
- Combine multiple indicators for robustness
