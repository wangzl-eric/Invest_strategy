# Carry Field

**Focus:** Carry strategies across asset classes (FX, commodities, fixed income)

## Key Questions

- What drives carry returns?
- How does carry interact with momentum?
- When do carry strategies crash?
- How to measure carry across different assets?
- What's the optimal carry portfolio construction?

## Data Sources

### Primary
- **FX Rates** - Major currency pairs (ECB data)
- **Interest Rates** - Short-term rates by country (FRED)
- **Commodity Futures** - Contango/backwardation (if available)
- **Bond Yields** - Government bond yields

### Secondary
- **Inflation Rates** - Real vs nominal carry
- **Credit Spreads** - Corporate bond carry

## Common Analyses

### 1. FX Carry
```python
# Interest rate differential
carry = domestic_rate - foreign_rate
# Expected return = carry - expected depreciation
```

### 2. Commodity Carry
```python
# Roll yield from futures curve
carry = (front_month - next_month) / front_month
```

### 3. Carry Portfolio
```python
# Rank assets by carry, go long high carry
ranks = carry.rank(axis=1, pct=True)
weights = (ranks > 0.7).astype(float)  # Top 30%
```

### 4. Carry Crashes
```python
# Identify drawdowns during risk-off events
carry_returns = ...
crashes = carry_returns < carry_returns.quantile(0.05)
```

## Study Templates

- `notebooks/fx_carry.ipynb` - FX carry strategy
- `notebooks/carry_momentum.ipynb` - Carry + momentum combination
- `notebooks/carry_crashes.ipynb` - Crash analysis
- `notebooks/real_carry.ipynb` - Inflation-adjusted carry

## Completed Studies

See `studies/INDEX.md` for full list.

## Promising Studies (Research Candidates)

None yet - this is a new field.

## Related Fields

- **FX** - FX carry is primary application
- **Momentum** - Carry + momentum combination
- **Macro** - Carry affected by rate cycles
- **Portfolio** - Carry in multi-asset portfolios

## References

- "Currency Carry Trade" (Burnside et al.)
- "Carry" (Koijen et al.)
- "Value and Momentum Everywhere" (Asness et al.)

## Notes

- Carry is compensation for risk
- Crashes during risk-off events
- Works across asset classes
- Combine with momentum for better risk-adjusted returns
- Real carry (inflation-adjusted) matters
