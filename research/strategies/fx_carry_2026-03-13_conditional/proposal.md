# Strategy: FX Carry + Momentum Composite

> **Researcher:** Marco | **Asset Class:** FX | **Verdict:** CONDITIONAL | **Priority:** 2

## Economic Rationale

- Brunnermeier et al. (2008) — FX carry premium compensates for crash risk
- Lustig & Verdelhan (2007) — high-yield currencies earn persistent excess returns
- Menkhoff et al. (2012) — combining carry with 12-1 momentum increases Sharpe by ~30%

## Signal Construction

1. **Carry signal:** SOFR/FRED short-rate differentials as proxy interest rate differential
   - USD: DGS3MO (3M T-Bill) available
   - Non-USD: EURIBOR3MD, SONIA, etc. — GAP, needs to be added to FRED catalog
2. **Momentum overlay:** 12-1 momentum on 8 major FX pairs using `MomentumSignal(lookback=252, skip=21)`
3. **Composite:** Blend carry (60%) + momentum (40%) via `SignalBlender`
4. **Volatility filter:** Cut gross exposure 50% when 20-day realized vol > 2 std above 252-day avg
5. **Dollar hedging:** Net USD exposure limited to +/-20% of NAV

## Universe

- G10 pairs: EURUSD, GBPUSD, USDJPY, USDCAD, USDCHF, AUDUSD, NZDUSD + DXY
- Available via: yfinance (catalog `fx` dataset, 2024-2026) + IBKR IDEALPRO (real-time)

## Data Gaps

| Data | Source | Status |
|------|--------|--------|
| FX spot prices (G10) | yfinance/IBKR | AVAILABLE |
| USD short rate (DGS3MO) | FRED | AVAILABLE |
| EUR short rate (EURIBOR3MD) | FRED | MISSING — needs adding |
| GBP short rate (SONIA) | FRED | MISSING — needs adding |
| JPY short rate (TONAR) | FRED | MISSING — needs adding |
| AUD short rate (BBSW3M) | FRED | MISSING — needs adding |

## Expected Risk/Return

| Metric | Marco's Estimate | PM Notes |
|--------|-----------------|----------|
| Sharpe | 0.7-1.2 | Carry returns compressed post-GFC |
| Max Drawdown | 12-20% | Fat left tails in carry (2008, 2015, 2020) |
| Annual Vol Target | 8-10% | Reasonable with vol-scaling |

## PM Challenges

1. **Carry returns compressed post-GFC.** Interest rate differentials in G10 have narrowed.
2. **Crash risk in carry.** Funding currency squeeze during crises produces extreme drawdowns.
3. **EM pairs have wider bid-ask spreads** (5-20 bps) that eat into carry.
4. **Non-USD short-rate data gap** must be addressed before production.

## Requirements for Approval

- [ ] Implement FXCarrySignal using actual interest rate differentials (not just momentum proxy)
- [ ] Add EURIBOR3MD, SONIA, TONAR, BBSW3M to FRED catalog
- [ ] Add proper risk-off overlay (VIX threshold or credit spread widening trigger)
- [ ] Account for EM pair bid-ask spreads in cost model
- [ ] Fix walk-forward (CRITICAL-3) before parameter optimization
- [ ] Paper trade 6 months minimum

## New Signal Class Needed

```python
class FXCarrySignal(BaseSignal):
    """Cross-sectional FX carry using interest rate differentials."""
    def compute(self, fx_prices: pd.DataFrame, rate_diffs: pd.DataFrame) -> pd.Series:
        # rate_diffs: columns = currency pairs, values = yield spread vs USD
        # Rank pairs by carry (highest yield diff = long)
        carry_rank = rate_diffs.rank(axis=1, pct=True)
        return carry_rank
```

---
*Last updated: 2026-03-13*
