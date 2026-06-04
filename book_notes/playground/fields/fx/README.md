# FX Field

**Focus:** Foreign exchange analysis, currency strategies, and FX market dynamics

## Key Questions

- What drives currency movements?
- How to trade FX carry strategies?
- What's the role of central bank policy?
- How do real exchange rates mean-revert?
- How does FX correlate with other assets?

## Data Sources

### Primary (ECB)
- **Major Pairs** - EUR/USD, GBP/USD, USD/JPY, USD/CHF
- **EM Currencies** - USD/BRL, USD/MXN, USD/ZAR
- **Interest Rates** - Central bank policy rates (FRED)

### Secondary
- **PPP Data** - Purchasing power parity (OECD)
- **Trade Balances** - Current account data
- **FX Volatility** - Implied volatility indices

## Common Analyses

### 1. FX Carry Strategy
```python
# Interest rate differential
carry = domestic_rate - foreign_rate
# Long high-yielding currencies
```

### 2. Real Exchange Rates
```python
# PPP-adjusted exchange rates
real_fx = nominal_fx * (foreign_cpi / domestic_cpi)
# Mean reversion analysis
```

### 3. FX Momentum
```python
# 12-month momentum
fx_momentum = fx_rate.pct_change(252)
```

### 4. Central Bank Divergence
```python
# Policy rate differentials
rate_diff = fed_funds - ecb_rate
# Predict FX moves
```

## Study Templates

- `notebooks/fx_carry_strategy.ipynb` - Carry trade analysis
- `notebooks/real_exchange_rates.ipynb` - PPP and mean reversion
- `notebooks/fx_momentum.ipynb` - Currency momentum
- `notebooks/central_bank_divergence.ipynb` - Policy impact on FX

## Completed Studies

See `studies/INDEX.md` for full list.

## Promising Studies (Research Candidates)

None yet - this is a new field.

## Related Fields

- **Carry** - FX carry is primary carry strategy
- **Momentum** - FX momentum strategies
- **Macro** - Central bank policy drives FX
- **Portfolio** - FX in multi-asset portfolios

## References

- "Currency Carry Trade" (Burnside et al.)
- "Exchange Rate Disconnect" (Meese & Rogoff)
- "Carry Trade and Global FX Volatility" (Menkhoff et al.)

## Notes

- FX is zero-sum (excluding carry)
- Carry strategies crash during risk-off
- Real exchange rates mean-revert slowly
- Central bank policy is key driver
- FX provides diversification to equity portfolios
