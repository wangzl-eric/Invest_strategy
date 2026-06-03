# Strategy: Global Yield Curve Steepener/Flattener

> **Researcher:** Marco | **Asset Class:** Rates | **Verdict:** REJECTED

## Economic Rationale

The yield curve is the most empirically robust macro predictor:
- Campbell & Shiller (1988) — yield spread predicts bond excess returns
- Estrella & Hardouvelis (1991) — inverted curve predicts recessions 12-18 months ahead
- Fed liquidity regime (WALCL, RRP) modulates duration premium

## Signal Construction

1. **Primary:** z-score of T10Y2Y (rolling 252-day)
2. **Liquidity filter:** WALCL 13-week momentum (expanding = long duration, shrinking = reduce)
3. **Trade vehicle:** Long TLT / short SHY when curve inverted & flattening; reverse when steepening
4. **Position sizing:** Inverse-vol on TLT/SHY 20-day realized vol

## Data Availability

- FRED: T10Y2Y, DGS2, DGS10, full curve (daily, 2024-2026) — AVAILABLE
- Price data: TLT, IEF, SHY in catalog — AVAILABLE
- FRED: WALCL, RRPONTSYD — AVAILABLE

## Expected Risk/Return (Marco's Estimate)

- Sharpe: 0.8-1.4
- Max drawdown: 8-15%
- Correlation to equity: -0.3 to 0

## Rejection Rationale (PM)

1. **No futures infrastructure.** `ticker_universe.py` shows US futures are "NOT ACTIVATED (requires CME subscription)." Cannot implement proper carry/roll-down with ETFs alone.
2. **ETF-based approximations lose term structure information.** TLT/SHY spread is a crude proxy for 2s10s curve trading. The duration mismatch (TLT ~17yr, SHY ~2yr) doesn't map cleanly to 2s10s.
3. **Short data window.** Only 2024-2026 in catalog. Yield curve strategies need 20+ years for regime coverage.

## Path to Reconsideration

- Activate CME futures data subscription and infrastructure
- Extend FRED history to 2000+ for proper regime backtesting
- Implement proper futures roll and carry calculations
- Re-propose with futures-based implementation

---
*Last updated: 2026-03-13*
