# Strategy: Volatility-Scaled Momentum (Low-Turnover Core)

> **Researcher:** Elena | **Asset Class:** Equity | **Verdict:** CONDITIONAL (Closest to Approval) | **Priority:** 1

## Economic Rationale

- Frazzini & Pedersen (2014) — "Betting Against Beta": low-vol stocks outperform risk-adjusted
- Novy-Marx (2013) — "The Other Side of Value": gross profitability predicts cross-sectional returns
- Asness, Frazzini & Pedersen (2019) — combining quality and momentum produces strongest results
- Blitz & van Vliet (2007) — low-volatility anomaly in global equities

## Signal Construction

1. **Inverse Volatility** (weight 0.40): Rank by lowest 60-day realized vol
   - Uses: `VolatilitySignal(lookback=60)`
2. **Risk-Adjusted Momentum** (weight 0.40): 12-1 momentum / trailing 12-month vol (Sharpe-like)
   - Uses: `compute_sharpe_ratio()` from `features.py`
3. **Mean Reversion Dampener** (weight -0.20): Penalize stocks with 20-day z-score > 2.0
   - Uses: `MeanReversionSignal(lookback=20)`

**Alpha formula:**
```python
alpha = 0.4 * zscore(-vol_60d) + 0.4 * zscore(sharpe_252d) + (-0.2) * zscore(zscore_20d)
```

## Specification

- **Universe:** US Large Cap (30 stocks initially)
- **Rebalancing:** Bi-monthly (every 2 months)
- **Position count:** 10-15 long-only
- **Optimization:** Mean-variance, `risk_aversion=3.0`, `max_weight=0.12`
- **Covariance:** Ledoit-Wolf shrinkage (available in `portfolio/risk.py`)
- **Turnover control:** `turnover_aversion=0.5` in `OptimizationConfig`
- **All signals exist** in the codebase — no new signal classes needed

## Expected Risk/Return

| Metric | Elena's Estimate | PM's Realistic Estimate |
|--------|-----------------|------------------------|
| Annual Alpha | 4-6% | 2-4% |
| Strategy Vol | 10-14% | Same |
| Sharpe Ratio | 0.8-1.0 | 0.5-0.7 |
| Max Drawdown | 15-22% | Same |
| Annual Turnover | 50-70% | Same |

## PM Challenges

1. **Alpha/Sharpe still optimistic.** Realistic: 2-4% alpha, Sharpe 0.5-0.7.
2. **Mean reversion dampener weight (-0.20) is ad hoc.** Will be overfit if optimized in-sample.
3. **Bi-monthly rebalance is unusual.** Cost savings vs monthly are minimal for 30-stock long-only.
4. **"Quality" is not in the signal.** No ROE, earnings stability, or leverage factor. Name is misleading.
5. **SignalBlender look-ahead bias** must be fixed before any backtest.

## Requirements for Approval

- [ ] Fix SignalBlender look-ahead (use expanding-window normalization)
- [ ] Rename strategy (remove "quality" or add actual quality signals)
- [ ] Reduce expected alpha to 2-4%, Sharpe to 0.5-0.7
- [ ] Fix CRITICAL-5 in builder so backtest uses these signals
- [ ] Pre-commit signal weights before backtesting (avoid data-mining blend ratios)
- [ ] Run cost sensitivity analysis
- [ ] Paper trade 3 months minimum

## Why This Is Priority 1

- All component signals already exist in the codebase
- Lowest implementation effort of any proposed strategy
- Most conservative risk profile (lower vol, lower drawdown)
- Designed as core/satellite complement to higher-alpha strategies
- Shortest paper trading requirement (3 months)

---
*Last updated: 2026-03-13*
