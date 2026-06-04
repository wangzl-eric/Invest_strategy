# Portfolio Manager Review — Full Verdicts

> **Reviewer:** PM | **Date:** 2026-03-13

## Overall Assessment

The team produced solid work. The strategy ideas have genuine economic merit, and the framework audit was excellent. However, the platform has structural integrity issues that must be resolved before ANY capital decision.

**Capital allocation: ZERO** until framework bugs are fixed and paper trading validates results.

---

## Strategy Verdicts

### Elena's Strategies

| Strategy | Verdict | Key Issue | Path Forward |
|----------|---------|-----------|--------------|
| Cross-Sectional Momentum | CONDITIONAL | Universe too narrow (30 stocks), alpha overstated, crash risk unaddressed | Expand to 100+ stocks, add crash hedge, realistic 2-4% alpha |
| Sector Rotation | CONDITIONAL | Macro overlay underspecified, FRED publication lag risk, alpha overstated | Pre-commit rules, handle data lag, realistic 1-2% alpha |
| Vol-Scaled Momentum | CONDITIONAL (closest) | Signal weights ad hoc, "quality" misnomer, SignalBlender look-ahead | Fix blender, pre-commit weights, rename, realistic 2-4% alpha |

### Marco's Strategies

| Strategy | Verdict | Key Issue | Path Forward |
|----------|---------|-----------|--------------|
| Yield Curve | REJECTED | No futures infrastructure, ETFs lose term structure info | Need CME subscription |
| Commodity Momentum | REJECTED | No futures infrastructure, ETF proxies unreliable | Need CME subscription or ETF-based redesign |
| FX Carry + Momentum | CONDITIONAL | Non-USD rate data missing, crash risk | Add FRED rate series, implement risk-off overlay |

### Dev's Framework Audit

| Assessment | Details |
|-----------|---------|
| Overall quality | Excellent — thorough, accurate, well-prioritized |
| Severity corrections | CRITICAL-1 → HIGH (EOD convention acceptable), LOW-3 → HIGH (completely broken method) |
| Unverified claim | CRITICAL-4 (equity curve fabrication) — needs investigation |
| Missing issues | None significant |

---

## Key Principle

> "Any strategy claiming Sharpe > 1.0 in US large-cap equities at monthly frequency should be treated with extreme skepticism."

## Risk Budget Framework (For Future Use)

When strategies are approved for paper trading:
- Maximum 20% of portfolio to any single strategy
- Aggregate gross leverage cap: 2.0x
- Per-strategy drawdown stop: -15%
- Portfolio-level drawdown stop: -10%
- Monthly review of all strategy performance vs expectations

---
*Last updated: 2026-03-13*
