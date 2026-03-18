# PM Framework Advisory — Portfolio Manager's Assessment

> **Author:** PM (Portfolio Manager) | **Date:** 2026-03-15
> **Classification:** Internal — Zelin Investment Research
> **Status:** FINAL

---

## Executive Summary

After a thorough line-by-line review of the backtesting codebase (`backtests/`, `portfolio/`, `execution/`), strategy proposals, and the framework audit, I am issuing this advisory on **framework fitness for purpose** relative to our strategy pipeline.

**Bottom line:** The framework is sound enough to produce *directionally useful* research results for our CONDITIONAL strategies, but it is NOT yet trustworthy enough for capital allocation decisions. Several structural gaps must be closed before any strategy can receive APPROVED status with confidence.

The 9 critical/high bugs fixed on 2026-03-13 resolved the most dangerous issues (PortfolioBuilder ignoring weights, walk-forward metric mapping, GridSearch overfitting, SignalBlender look-ahead). However, the framework still lacks key capabilities that institutional-grade backtesting requires, and certain residual issues could introduce systematic bias into results.

---

## 1. Strategic Prioritization — What Matters for Our Pipeline

### Current Strategy Pipeline State

| Strategy | Verdict | Primary Framework Dependencies | Blocking Gaps |
|----------|---------|-------------------------------|---------------|
| Vol-Scaled Momentum (P1) | CONDITIONAL | SignalBlender, PortfolioBuilder, WalkForward, CostSensitivity | Moderate — all core bugs fixed, needs validation |
| FX Carry + Momentum (P2) | CONDITIONAL | FXCarrySignal (new), rate data pipeline, SignalBlender | Severe — missing data connectors, no FX cost model |
| Cross-Sectional Momentum (P3) | CONDITIONAL | CrossSectionalRankSignal (new), 100+ stock universe, event-driven engine | Severe — universe scaling, no corporate action handling |
| Sector Rotation (P4) | CONDITIONAL | Macro overlay, regime detection, sector ETF data | Moderate — RegimeAnalyzer adequate but untested at scale |

### What Each Strategy Needs from the Framework

**Vol-Scaled Momentum (shortest path to approval):**
- The vectorized backtest path through `PortfolioBuilder.backtest()` is now functional (bug fixed)
- `SignalBlender` now uses expanding-window normalization (bug fixed)
- Walk-forward has proper train/test split (bug fixed)
- **Remaining needs:** Cost sensitivity validation at 2x realistic costs, parameter stability tests, decay analysis via `strategy_half_life()`
- **Framework risk:** LOW — this strategy can be researched with current infrastructure

**FX Carry + Momentum (significant data gaps):**
- Missing non-USD short-rate data (EURIBOR3MD, SONIA, TONAR, BBSW3M)
- No `FXCarrySignal` class exists — needs implementation
- FX-specific cost model needed (wider spreads for EM, rollover costs)
- Current cost models in `backtests/costs/` are equity-centric
- **Framework risk:** HIGH — data pipeline gaps are the binding constraint, not the backtesting engine

**Cross-Sectional Momentum (scaling challenge):**
- No `CrossSectionalRankSignal` class exists
- Current data pipeline untested with 100+ instruments simultaneously
- No corporate action handling (splits, dividends) — biases survivorship
- Event-driven engine (`EventDrivenBacktester`) is minimal: no multi-asset support, no portfolio-level risk management
- **Framework risk:** HIGH — needs infrastructure investment before valid research

---

## 2. Risk Assessment — Framework Gaps vs. Strategy Validity

### BLOCKERS (Must Fix Before APPROVED Verdict)

| # | Gap | Affected Strategies | Risk if Ignored | Effort |
|---|-----|-------------------|-----------------|--------|
| B1 | No multi-asset event-driven backtesting | P3, P4 | Cannot validate realistic execution for portfolios | HIGH |
| B2 | No corporate action handling | P3 | Survivorship bias corrupts 100+ stock universe results | MEDIUM |
| B3 | Vectorized backtest uses static weights | P1, P2 | Weights computed once, not re-optimized at each rebalance | LOW |
| B4 | Cost models not integrated with vectorized path | P1 | `PortfolioBuilder.backtest()` uses simple `commission` rate, not `CostModel` hierarchy | LOW |

**B3 is particularly insidious.** Looking at `builder.py:321-327`, the `backtest()` method has a comment saying "re-optimization is optional" and uses pre-computed static weights throughout. For a monthly-rebalanced strategy over multiple years, this means the backtest assumes perfect foresight about optimal weights for the entire period. This is NOT the same as look-ahead bias (the signals use past data), but it dramatically overstates the stability of a real implementation where weights would be re-optimized monthly with only information available at each rebalance.

### ACCEPTABLE RISKS (Can Proceed with Caveats)

| # | Gap | Mitigation | PM Assessment |
|---|-----|-----------|---------------|
| A1 | Sharpe ratio still not risk-free adjusted in some paths | `decay_analysis.py:rolling_sharpe()` IS adjusted; `builder.py:347-350` is NOT. Delta is ~0.2-0.3 at current rates | Accept — document the difference, use `rolling_sharpe()` for official numbers |
| A2 | CarrySignal is mislabeled (actually short-term momentum) | Not used by any active strategy | Accept — rename when convenient |
| A3 | VolumeSignal always returns zero | Not used by any active strategy | Accept — remove or implement when needed |
| A4 | ATR double-normalization | Minor impact on blended signals | Accept — fix as part of next signal review |
| A5 | Event-driven engine fills at market price from previous bar | EOD convention documented in CLAUDE.md | Accept — reasonable for daily strategies |

### UNKNOWN RISKS (Need Investigation)

| # | Gap | Concern |
|---|-----|---------|
| U1 | Walk-forward combined_equity includes train + test curves | May inflate visual appearance of equity; metrics are computed on test-only (confirmed in code). Visual artifact only. |
| U2 | `_risk_parity_weights()` uses sample covariance without shrinkage | `builder.py:263` uses `returns.cov()` directly, while `optimize_weights()` at line 245 correctly uses `ledoit_wolf_cov()`. Inconsistency — risk parity path could be unstable with small sample sizes. |
| U3 | `parallel.py` serializes data to Parquet for IPC | Safe, but introduces PyArrow dependency for parallel runs. Need to verify this doesn't silently drop timezone info or truncate datetime precision. |

---

## 3. Build vs. Adopt — PM Risk/Reward Assessment

### Option Analysis

#### A. Data Pipeline (qlib-style)

**Our current state:** `quant_data/` has connectors for Binance, Stooq, Polygon, ECB FX. DuckDB-backed Parquet store. Functional but limited metadata, no corporate action handling, no calendar alignment.

**Adopt qlib data pipeline?**
- **Pro:** Sophisticated instrument management, calendar handling, corporate action adjustment, built-in caching
- **Con:** Heavy dependency (Microsoft, ~10K star project), requires adapting to qlib's data format, learning curve
- **PM verdict:** **DO NOT adopt wholesale.** The investment to integrate qlib's data layer is disproportionate to the benefit for our 4-strategy pipeline. Instead, **cherry-pick** the corporate action handling pattern and implement a thin adapter. Our Parquet store is fine for the current scale.
- **Risk/Reward:** Low reward at current scale, high integration risk.

#### B. Event-Driven Backtesting (backtrader wrapper)

**Our current state:** `EventDrivenBacktester` in `backtests/event_driven/engine.py` is minimal — 118 lines, single-asset, no portfolio-level logic, no multi-asset support. We also have Backtrader integration in `backtrader_compat.py` but it's largely a shim.

**Wrap backtrader for event-driven backtesting?**
- **Pro:** Mature execution model, multi-asset, realistic fills, large community
- **Con:** Backtrader is unmaintained (last commit 2020), Python 3.10+ compatibility issues, API is baroque, poor documentation
- **PM verdict:** **USE BACKTRADER ONLY FOR VALIDATION.** Do not build production strategies on it. Our vectorized path is sufficient for P1 and P2. For P3/P4 (multi-asset portfolios), invest in extending our own `EventDrivenBacktester` with portfolio-level logic. The technical debt of wrapping backtrader would exceed the cost of building what we actually need.
- **Risk/Reward:** Medium reward (saves development time), high maintenance risk (unmaintained dependency).

#### C. Trading Calendar (zipline-style)

**Our current state:** No trading calendar — `backtests/` assumes continuous daily data, `walkforward.py` uses integer index offsets. No holiday handling, no half-day sessions.

**Adopt zipline's calendar?**
- **Pro:** Correct handling of holidays, early closes, market sessions
- **Con:** zipline is effectively abandoned, the calendar module (`exchange_calendars`) is maintained separately
- **PM verdict:** **ADOPT `exchange_calendars` (not full zipline).** This is a lightweight, maintained package that provides exactly what we need. Low integration effort, high correctness benefit. Missing holidays can introduce 1-3 day look-ahead artifacts in daily strategies.
- **Risk/Reward:** High reward, low risk.

#### D. Invest in Our Own Infrastructure

**PM verdict:** **YES, selectively.** Our framework has good bones:
- `backtests/stats/` is excellent — PSR, Deflated Sharpe, CPCV, bootstrap, MinBTL, decay analysis
- `backtests/costs/` cost models are well-designed (immutable, composable)
- `backtests/parallel.py` provides scalable parameter sweeps
- `portfolio/optimizer.py` uses CVXPY properly
- Signal framework (`signals.py`) is extensible and clean after bug fixes

The right strategy is to **invest incrementally** in the gaps that block specific strategies, not undertake a wholesale framework rewrite.

---

## 4. Recommended Roadmap

### Phase 1: Immediate (Pre-Strategy-Approval, 1-2 weeks)

These must be complete before Vol-Scaled Momentum can receive APPROVED:

| # | Action | Effort | Owner | Rationale |
|---|--------|--------|-------|-----------|
| 1.1 | Implement dynamic weight re-optimization in `PortfolioBuilder.backtest()` | 2-3 days | Dev | B3 — static weights overstate stability |
| 1.2 | Integrate `CostModel` hierarchy into vectorized backtest path | 1 day | Dev | B4 — current `commission` param is too simplistic |
| 1.3 | Fix risk parity path to use `ledoit_wolf_cov()` | 1 hour | Dev | U2 — inconsistency between optimization paths |
| 1.4 | Validate all 11 quantitative gates can be computed end-to-end | 1-2 days | Dev | Must confirm PSR, Deflated Sharpe, MinBTL, half-life all run against Vol-Scaled Momentum output |
| 1.5 | Install `exchange_calendars` and add trading-day alignment to data loading | 1 day | Dev | C — correct holiday handling |

**Phase 1 exit criterion:** Vol-Scaled Momentum research notebook executes with dynamic rebalancing, realistic costs via `CompositeCostModel`, and all 11 gates computed. PM re-reviews.

### Phase 2: Important Improvements (1-3 months)

| # | Action | Effort | Owner | Rationale |
|---|--------|--------|-------|-----------|
| 2.1 | Add FRED series for non-USD rates (EURIBOR, SONIA, TONAR, BBSW) | 2-3 days | Dev/Marco | Unblocks FX Carry strategy |
| 2.2 | Implement `FXCarrySignal` with proper interest rate differentials | 3-5 days | Marco + Dev | Required for P2 |
| 2.3 | Add FX-specific cost model (wider spreads, rollover) to `backtests/costs/` | 2 days | Dev | P2 needs realistic FX costs |
| 2.4 | Extend `EventDrivenBacktester` for multi-asset portfolio execution | 1-2 weeks | Dev | Required for P3, P4 |
| 2.5 | Add basic corporate action handling (splits, dividends) to data pipeline | 1 week | Dev | Required for P3 (100+ stock universe) |
| 2.6 | Implement `CrossSectionalRankSignal` class | 2-3 days | Elena + Dev | Required for P3 |
| 2.7 | Set up paper trading infrastructure (execution runner + sim broker) | 1-2 weeks | Dev | Required for capital policy gate |

**Phase 2 exit criterion:** FX Carry and Cross-Sectional Momentum can produce valid research notebooks.

### Phase 3: Nice-to-Have Enhancements (3-6 months)

| # | Action | Effort | Rationale |
|---|--------|--------|-----------|
| 3.1 | Monte Carlo simulation for tail risk / VaR | 1 week | Portfolio-level risk assessment |
| 3.2 | Real-time signal monitoring dashboard | 2 weeks | Paper trading observability |
| 3.3 | Automatic strategy capacity estimation with live volume data | 1 week | Scale planning |
| 3.4 | Regime-aware dynamic allocation across strategies | 2-3 weeks | Portfolio construction |
| 3.5 | Integration with Cerebro for automated signal discovery feedback loop | 2-3 weeks | Research velocity |
| 3.6 | Full event replay / audit trail for backtest reproducibility | 1 week | Regulatory / audit readiness |

---

## 5. Framework Integrity Assessment

### Can We Trust Current CONDITIONAL Strategy Results?

**Short answer: Partially, with significant caveats.**

#### What IS Trustworthy

1. **Signal computation** — `MomentumSignal`, `VolatilitySignal`, `MeanReversionSignal` are mathematically correct and use `min_periods=lookback` (fixed from `lookback//2`).
2. **SignalBlender normalization** — now uses expanding-window statistics (no look-ahead after fix).
3. **Walk-forward train/test split** — properly separates in-sample from out-of-sample after GridSearch fix.
4. **Statistical testing suite** — `backtests/stats/` provides legitimate PSR, Deflated Sharpe, CPCV, bootstrap CI, MinBTL. These are correctly implemented and tested (26 unit tests pass).
5. **Cost model architecture** — `CostModel` hierarchy is clean, immutable (`@dataclass(frozen=True)`), composable. The models themselves are reasonable.
6. **Triple-barrier labeling** — correct implementation with proper forward-scan and vol-adaptive barriers.
7. **Portfolio optimizer** — CVXPY-based mean-variance with Ledoit-Wolf shrinkage is sound.

#### What Is NOT Trustworthy

1. **Backtest equity curves from `PortfolioBuilder.backtest()`** — static weight assumption (B3) means the equity curve does NOT represent what a live strategy would produce. Weights would drift and be re-optimized periodically in reality.
2. **Any Sharpe ratio from `PortfolioBuilder`** — `builder.py:347-350` does not subtract the risk-free rate. All Sharpe numbers from this path are overstated by ~0.2-0.3.
3. **Cost sensitivity numbers** — `CostSensitivityAnalyzer` in `walkforward.py:719-789` uses the Backtrader engine path, which has its own cost model separate from `backtests/costs/`. Results may not be consistent between vectorized and event-driven paths.
4. **Multi-asset event-driven results** — the `EventDrivenBacktester` cannot run multi-asset strategies. Any multi-asset results came from the vectorized path only.

#### Validation Needed Before Any APPROVED Verdict

1. **Run Vol-Scaled Momentum through both paths** (vectorized and event-driven where applicable) and compare results. Discrepancies > 10% in Sharpe indicate a framework bug.
2. **Compute all 11 gates from the STRATEGY_TRACKER table** in a single end-to-end run. Currently there is no evidence this has been done for any strategy.
3. **Verify walk-forward with dynamic re-optimization** — the current walk-forward runs backtests on each test fold, but it is unclear whether the weights are re-optimized per fold or kept static.
4. **Paper trade for 3+ months** (capital policy requirement). No framework shortcut for this.

---

## 6. PM Directives

### Standing Orders

1. **ZERO capital deployment** remains in effect until Phase 1 is complete AND one strategy completes 3 months paper trading with positive OOS Sharpe.
2. **No strategy receives APPROVED** until all 11 quantitative gates are computed from a single end-to-end notebook run using the corrected framework (post-Phase 1).
3. **Vol-Scaled Momentum is the critical path.** All Phase 1 work should prioritize unblocking this strategy's approval process.
4. **FX Carry is gated by data, not framework.** Do not invest in framework improvements for FX until rate data is available.
5. **Cross-Sectional Momentum requires the most infrastructure.** This is Phase 2 work. Do not attempt the 100+ stock universe on current infrastructure.

### Risk Limits (Unchanged)

- Max allocation per strategy: 20% of portfolio
- Aggregate gross leverage: 2.0x
- Per-strategy drawdown stop: -15%
- Portfolio drawdown stop: -10%

### Escalation Triggers

Report immediately to PM if:
- Any backtest produces Sharpe > 2.0 for monthly equity (almost certainly a bug)
- Walk-forward OOS Sharpe exceeds IS Sharpe (suspicious)
- Deflated Sharpe is negative for any CONDITIONAL strategy (suggests data mining)
- Paper trading results diverge > 30% from backtest expectations

---

## Addendum: Incorporating Dev's Framework Comparison Report (2026-03-15)

After reviewing the full comparison report (`research/framework_audit/framework_comparison_2026-03-15.md`), I am upgrading several items and adding new directives.

### Points of Agreement

1. **Do NOT replace the local framework.** Dev correctly identifies that our statistical rigor pipeline (PSR, Deflated Sharpe, MinBTL, CPCV, purged K-fold, multiple testing correction) is absent from ALL four external frameworks reviewed. This is our moat. I concur completely.

2. **Adopt `alphalens-reloaded` for cross-sectional factor analysis.** This is a lightweight, maintained package that provides IC, ICIR, factor quantile returns, and factor turnover. Critical for validating Cross-Sectional Momentum (P3). **I am adding this to Phase 1 work** as item 1.6, since Elena's P3 strategy cannot produce valid evidence without it.

3. **backtrader is dead.** Dev confirms last significant release was 2019. Our existing `backtrader_compat.py` shim is sufficient. No further adoption. Aligns with my original recommendation.

### PM-Level Corrections to Dev's Findings

**ATR double-normalization — CONFIRMED but NOT a P1 blocker.**
I verified the code at `signals.py:149-156`. Line 151 uses `pct_change().abs()` (already price-normalized), then line 154 divides by price again. This produces `|delta_P| / P^2` instead of `|delta_P| / P`. **However**, ATR is NOT one of the three signals in the Vol-Scaled Momentum strategy (which uses VolatilitySignal, Sharpe ratio, and MeanReversionSignal). Dev's claim that it "affects Vol-Scaled Momentum" is overstated. ATR should be fixed, but it is not blocking P1.

**Reclassification:** Moved from Phase 1 to Phase 1.5 (fix before any strategy uses ATR in production, but not blocking Vol-Scaled Momentum approval).

**CarrySignal mislabeling — CONFIRMED, already in my advisory as A2.**
I classified this as an "acceptable risk" since no active strategy uses `CarrySignal`. The FX Carry strategy explicitly calls for a NEW `FXCarrySignal` class (see proposal.md). The mislabeled `CarrySignal` will not be used. Dev is correct that it should be renamed or removed to prevent confusion, but this is not a blocker.

**VolumeSignal no-op — CONFIRMED, already in my advisory as A3.**
Dev correctly notes this dilutes blended signals. However, `VolumeSignal` is only invoked if explicitly included in a blend. None of our CONDITIONAL strategies include it. **Directive:** Remove from default registry (`_init_defaults()`) to prevent accidental inclusion. Do NOT delete the class — fix it when volume data is available.

### Updated Phase 1 (Revised)

Adding two items from Dev's report:

| # | Action | Effort | Owner | Rationale |
|---|--------|--------|-------|-----------|
| 1.6 | Install `alphalens-reloaded` and add IC/quantile analysis to notebook template | 1-2 days | Dev | Unblocks P3 Cross-Sectional Momentum validation |
| 1.7 | Remove `VolumeSignal` from default signal registry (keep class, remove from `_init_defaults()`) | 15 min | Dev | Prevents accidental signal dilution |

### New Standing Directive

**Signal Registry Hygiene:** No signal class that returns a constant, is mislabeled, or is numerically incorrect shall remain in the default signal registry (`_init_defaults()` in `signals.py`). Broken signals must be either fixed or deregistered. Keeping them registered creates a latent risk that a researcher unknowingly includes them via `list_signals()` or `run_signal_research()`.

### qlib — PM Assessment

Dev recommends evaluating qlib's formulaic alpha engine for research acceleration. I agree this is interesting but want to be clear about timing:
- **NOT NOW.** Our priority is getting Vol-Scaled Momentum through the approval gate.
- **Phase 3 at earliest.** Only after at least one strategy is paper trading successfully.
- **Risk:** qlib's Alpha 158/Alpha 101 factors are calibrated to Chinese equity markets. Blindly applying them to US equities would be a form of data mining without economic rationale. Any qlib factor adoption must pass the "who loses money?" test.

---

*This advisory, including this addendum, supersedes all previous PM framework assessments. Next review scheduled after Phase 1 completion.*

*PM — Zelin Investment Research*
