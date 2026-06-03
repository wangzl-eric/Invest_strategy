# Strategy: Commodity Momentum + Inflation Regime

> **Researcher:** Marco | **Asset Class:** Commodities | **Verdict:** REJECTED

## Economic Rationale

- Erb & Harvey (2006) — commodity momentum SR ~0.4-0.7
- Gorton & Rouwenhorst (2006) — commodities trend over medium horizons
- Inflation regime matters: rising breakeven inflation amplifies commodity momentum ~2x

## Signal Construction

1. **Commodity momentum:** 12-1 momentum across WTI (CL=F), Brent (BZ=F), Gold (GC=F), Silver (SI=F), Copper (HG=F), Natural Gas (NG=F)
2. **Inflation regime filter:** 3-month momentum on T10YIE. Positive → full position; negative → 50% or flat
3. **Cross-sectional ranking:** Long top 2, short bottom 2 (dollar-neutral), inverse-vol sized
4. **Fed liquidity cross-check:** WALCL shrinking AND T10YIE falling → cut to flat

## Data Availability

- Commodities: CL=F, BZ=F, GC=F, HG=F, NG=F, SI=F — AVAILABLE (yfinance continuous contracts)
- FRED: T10YIE, T5YIE, T5YIFR, WALCL — AVAILABLE

## Expected Risk/Return (Marco's Estimate)

- Sharpe: 0.6-1.0
- Max drawdown: 15-25%
- Inflation hedge: +0.3-0.5 correlation to CPI surprises

## Rejection Rationale (PM)

1. **No futures infrastructure.** USO, UNG are terrible proxies for commodity futures (contango drag, roll costs). Without direct futures access, implementation slippage is massive.
2. **Roll costs not explicitly modeled.** yfinance continuous contracts embed roll costs but don't expose them. Backtest P&L will not match live trading.
3. **Short data window.** 2024-2026 only. Commodity momentum needs 10+ years for robust estimation.
4. **NG=F is highly seasonal.** Seasonality adjustment or exclusion needed.

## Path to Reconsideration

- Use commodity ETFs (GLD, USO, COPX, DBA) as proxies with explicit cost adjustments
- OR activate CME futures data
- Extend price history to 10+ years
- Add seasonality adjustment for natural gas
- Re-propose with realistic implementation vehicle

---
*Last updated: 2026-03-13*
