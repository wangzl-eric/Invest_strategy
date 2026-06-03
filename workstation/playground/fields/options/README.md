# Options Field

**Focus:** Options pricing, volatility trading, and derivatives strategies

## Key Questions

- How to price options accurately?
- What drives option implied volatility?
- How to trade volatility skew?
- What's the optimal options strategy for different views?
- How do Greeks behave in practice?

## Data Sources

### Primary
- **VIX** - S&P 500 implied volatility
- **Options Data** - If available from IBKR
- **Underlying Prices** - SPY, QQQ, etc.

### Secondary
- **SKEW Index** - Tail risk measure
- **Put/Call Ratios** - Sentiment indicators

## Common Analyses

### 1. Implied vs Realized Volatility
```python
# Compare IV to RV
implied_vol = vix
realized_vol = spy_returns.rolling(20).std() * np.sqrt(252) * 100
vol_premium = implied_vol - realized_vol
```

### 2. Volatility Skew
```python
# OTM put IV vs ATM IV
skew = otm_put_iv - atm_iv
```

### 3. Greeks Analysis
```python
# Delta, gamma, theta, vega
from scipy.stats import norm
# Black-Scholes Greeks
```

### 4. Options Strategies
```python
# Covered calls, protective puts, spreads
# Payoff diagrams and P&L analysis
```

## Study Templates

- `notebooks/options_pricing.ipynb` - Black-Scholes and Greeks
- `notebooks/volatility_skew.ipynb` - Skew analysis
- `notebooks/options_strategies.ipynb` - Strategy comparison
- `notebooks/vol_trading.ipynb` - Volatility trading

## Completed Studies

See `studies/INDEX.md` for full list.

## Promising Studies (Research Candidates)

None yet - this is a new field.

## Related Fields

- **Volatility** - Core input for options pricing
- **Portfolio** - Options for hedging and income
- **Macro** - Options reflect macro uncertainty

## References

- "Options, Futures, and Other Derivatives" (Hull)
- "Volatility Trading" (Sinclair)
- "Option Volatility and Pricing" (Natenberg)

## Notes

- Options are non-linear instruments
- Implied volatility often overstates realized
- Skew reflects tail risk concerns
- Greeks change with market conditions
- Options provide asymmetric payoffs
