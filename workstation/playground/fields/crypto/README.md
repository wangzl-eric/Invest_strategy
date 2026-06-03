# Crypto Field

**Focus:** Cryptocurrency analysis, crypto-equity relationships, and digital asset strategies

## Key Questions

- How does crypto correlate with traditional assets?
- What drives crypto volatility?
- Is crypto a diversifier or risk-on asset?
- How to analyze crypto momentum?
- What's the role of on-chain metrics?

## Data Sources

### Primary (Binance)
- **BTC/USDT** - Bitcoin price
- **ETH/USDT** - Ethereum price
- **Major Altcoins** - If available

### Secondary
- **On-chain Data** - If available (Glassnode, etc.)
- **Crypto Volatility** - Realized and implied
- **Funding Rates** - Perpetual futures funding

## Common Analyses

### 1. Crypto-Equity Correlation
```python
# Rolling correlation with SPY
btc_spy_corr = btc_returns.rolling(60).corr(spy_returns)
```

### 2. Crypto Momentum
```python
# 12-month momentum
crypto_momentum = btc_price.pct_change(252)
```

### 3. Volatility Analysis
```python
# Realized volatility
btc_vol = btc_returns.rolling(20).std() * np.sqrt(252) * 100
```

### 4. Risk-On/Risk-Off
```python
# Crypto as risk-on indicator
risk_on = (btc_returns > 0) & (spy_returns > 0)
```

## Study Templates

- `notebooks/crypto_equity_correlation.ipynb` - Correlation analysis
- `notebooks/crypto_momentum.ipynb` - Momentum strategies
- `notebooks/crypto_volatility.ipynb` - Volatility dynamics
- `notebooks/crypto_diversification.ipynb` - Portfolio diversification

## Completed Studies

See `studies/INDEX.md` for full list.

## Promising Studies (Research Candidates)

None yet - this is a new field.

## Related Fields

- **Correlation** - Crypto-equity correlation
- **Volatility** - Crypto is highly volatile
- **Momentum** - Crypto momentum strategies
- **Portfolio** - Crypto in multi-asset portfolios

## References

- "Cryptoassets" (Burniske & Tatar)
- "Bitcoin and Cryptocurrency Technologies" (Narayanan et al.)
- Academic papers on crypto-equity correlation

## Notes

- Crypto is highly volatile
- Correlation with equities has increased
- Behaves like risk-on asset in recent years
- Limited history for statistical analysis
- Regulatory uncertainty affects prices
