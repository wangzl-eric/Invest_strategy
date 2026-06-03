# Strategy: Cross-Sectional Equity Momentum

> **Researcher:** Elena | **Asset Class:** Equity | **Verdict:** CONDITIONAL

## Economic Rationale

Cross-sectional momentum is one of the most documented anomalies in finance:
- Jegadeesh & Titman (1993) — "Returns to Buying Winners and Selling Losers": 12-1 month momentum earns ~1%/month
- Fama & French (1996) — momentum is the premier anomaly surviving 3-factor model
- Asness, Moskowitz & Pedersen (2013) — momentum works across asset classes and geographies

## Signal Construction

1. 12-1 month momentum: `(P_{t-21} / P_{t-252}) - 1`
2. 6-1 month momentum: `(P_{t-21} / P_{t-126}) - 1`
3. Blend: `alpha = 0.6 * mom_12_1 + 0.4 * mom_6_1` (z-scored cross-sectionally)
4. Rank stocks by alpha score
5. Long top quintile, short bottom quintile
6. Weight within quintile by inverse volatility (60-day realized vol)

## Specification

- **Universe:** US Large Cap (originally 30 stocks — PM requires 100+)
- **Rebalancing:** Monthly (end of month)
- **Position sizing:** Inverse-vol weighted within quintiles
- **Existing signals used:** `MomentumSignal(lookback=252, skip=21)`, `MomentumSignal(lookback=126, skip=21)`
- **New signal needed:** `CrossSectionalMomentumSignal` — cross-sectional z-scoring + ranking

## Expected Risk/Return

| Metric | Elena's Estimate | PM's Realistic Estimate |
|--------|-----------------|------------------------|
| Annual Alpha | 8-10% gross | 2-4% (post-publication decay) |
| Sharpe Ratio | 0.7-0.9 | 0.3-0.5 |
| Max Drawdown | 25-35% | 50%+ (momentum crashes) |
| Turnover | ~150-200% annual | Same |

## PM Challenges

1. **Alpha decay is real.** Post-2000 US large-cap long/short momentum: ~2-4% annually, not 8-10%.
2. **Crash risk unaddressed.** 2009 momentum crash: -73% in one quarter. Need crash hedge.
3. **30-stock universe too narrow.** 6 stocks per leg = massive idiosyncratic risk. Need 100+.
4. **Short leg problematic.** Shorting mega-caps is expensive (borrow costs, crowding, squeezes).
5. **No CrossSectionalRankSignal exists** in the codebase yet.

## Requirements for Approval

- [ ] Expand universe to 100+ US equities (Russell 1000 or S&P 500)
- [ ] Implement CrossSectionalRankSignal class
- [ ] Add momentum crash hedge (vol-scaling, reversal filter)
- [ ] Reduce expected alpha to 2-4%, Sharpe to 0.3-0.5
- [ ] Fix CRITICAL-5 in builder before any backtest
- [ ] Run cost sensitivity with realistic transaction costs + short borrow costs
- [ ] Paper trade minimum 6 months before capital allocation

## Implementation Notes

```python
# Pseudocode for CrossSectionalMomentumSignal
class CrossSectionalMomentumSignal(BaseSignal):
    def compute(self, prices_df: pd.DataFrame) -> pd.Series:
        # prices_df has columns = tickers
        mom_12_1 = prices_df.shift(21) / prices_df.shift(252) - 1
        mom_6_1 = prices_df.shift(21) / prices_df.shift(126) - 1
        alpha = 0.6 * mom_12_1 + 0.4 * mom_6_1
        # Cross-sectional z-score at each date
        alpha_z = alpha.sub(alpha.mean(axis=1), axis=0).div(alpha.std(axis=1), axis=0)
        return alpha_z
```

---
*Last updated: 2026-03-13*
