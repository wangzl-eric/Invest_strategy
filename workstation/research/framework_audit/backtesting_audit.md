# Backtesting Framework Audit Report

> **Auditor:** Dev (Quantitative Developer) | **Date:** 2026-03-12
> **Verified by:** PM (Portfolio Manager) | **Date:** 2026-03-13

## Executive Summary

24 issues identified across 4 severity levels. 3 confirmed CRITICAL bugs make all backtest results currently unreliable. The `PortfolioBuilder` pipeline is fundamentally broken — it computes signals and optimizes weights, then ignores them entirely.

**Solid foundations:** `portfolio/optimizer.py` (clean CVXPY), `execution/risk.py` (conservative, kill-switch enabled), `backtests/metrics.py` (numerically defensive).

---

## CRITICAL Issues (Must Fix Before Any Strategy Is Trusted)

### CRITICAL-1: Walk-Forward `annualized_return` Mapped to `sharpe_ratio`
- **File:** `backtests/walkforward.py:322`
- **Bug:** `"annualized_return": result.get("sharpe_ratio", 0) or 0`
- **Impact:** Corrupts ALL walk-forward aggregate statistics (avg_test_return, return_consistency, Calmar)
- **PM Verification:** CONFIRMED
- **Fix:** `result.get("annualized_return", 0)`
- **Status:** NOT FIXED

### CRITICAL-2: GridSearch Has No Train/Test Split
- **File:** `backtests/walkforward.py:370-440`
- **Bug:** `GridSearch._run_backtest(params)` evaluates on `self.data` (entire dataset). `cv_folds` parameter accepted but never implemented.
- **Impact:** All "best params" are in-sample optimized. Guarantees overfitting.
- **PM Verification:** CONFIRMED
- **Fix:** Implement proper train/validate split, or implement cv_folds logic
- **Status:** NOT FIXED

### CRITICAL-3: PortfolioBuilder.backtest() Ignores Computed Weights
- **File:** `backtests/builder.py:260-334`
- **Bug:** The method spends 240 lines computing signals and optimizing weights, then uses a hardcoded `SimpleMomentum` strategy (SMA period=50) for every asset.
- **Impact:** The entire PortfolioBuilder pipeline from signals through optimization is theater. Backtest results have NO relationship to configured signals/weights.
- **PM Verification:** CONFIRMED — "This is the most damaging bug."
- **Fix:** Pass computed weights/signals into the strategy, or use `run_portfolio_backtest()` which correctly implements signal→weight→return pipeline
- **Status:** NOT FIXED

---

## HIGH Issues (Should Fix Before Publishing Results)

### HIGH-1: Look-Ahead Bias in BacktraderSignalIndicator
- **File:** `backtests/strategies/backtrader_compat.py:44-68`
- **Original severity:** CRITICAL (Dev) → Downgraded to HIGH (PM)
- **Details:** Signal uses data up to `close[-1]`, trades at `close[0]`. Acceptable for EOD models but undocumented.
- **Fix:** Document the EOD convention; add shift(1) option for intraday

### HIGH-2: Sharpe Ratio Not Risk-Free Adjusted (Vectorized Path)
- **File:** `backtests/metrics.py:9`
- **Bug:** `mean / std * sqrt(252)` without subtracting risk-free rate. Overstates Sharpe by ~0.2-0.5.
- **Fix:** Accept `risk_free_rate` parameter

### HIGH-3: No Warmup Period Enforcement
- **File:** `backtests/strategies/signals.py:446`
- **Bug:** `min_periods=lookback//2` allows signals to fire with half the required data.
- **Fix:** Enforce `min_periods = lookback`

### HIGH-4: PortfolioBuilder Uses Full History for Covariance
- **File:** `backtests/builder.py:207`
- **Bug:** Covariance estimated on all data including future. Look-ahead bias in optimization.
- **Fix:** Pass covariance estimation cutoff date

### HIGH-5: SignalBlender Normalizes with Full-Sample Stats
- **File:** `backtests/strategies/signals.py:329`
- **Bug:** `sig.mean()` and `sig.std()` over entire history (includes future data). Look-ahead bias.
- **Fix:** Use rolling or expanding window statistics

### HIGH-6: No Transaction Costs in `run_signal_research()`
- **File:** `backtests/strategies/signals.py:604`
- **Bug:** `signal_returns = positions.shift(1) * returns` — no costs. Optimistic results.
- **Fix:** Accept `cost_bps` parameter

### HIGH-7: Event-Driven Engine Fills at Stale Price
- **File:** `backtests/event_driven/engine.py:91-96`
- **Bug:** Orders filled at `last_prices` from previous MarketEvent. No slippage, no commission.
- **Fix:** Add commission/slippage parameters to `__init__()`

### HIGH-8: EventDrivenSignalComputer.get_position() Reads Price Not Signal
- **File:** `backtests/strategies/backtrader_compat.py:302-303`
- **Bug:** `sig = self._prices[-1]` reads raw price, not signal value. Completely broken method.
- **Original severity:** LOW (Dev) → Upgraded to HIGH (PM)
- **Fix:** Read from signal values, not price array

### HIGH-9: RegimeAnalyzer Mutates Equity DataFrame
- **File:** `backtests/walkforward.py:538`
- **Bug:** `equity["returns"] = ...` mutates passed DataFrame in place.
- **Fix:** Operate on `equity.copy()`

---

## MEDIUM Issues

| # | Issue | File | Details |
|---|-------|------|---------|
| 1 | CarrySignal is not carry (mislabeled) | signals.py:79 | Actually a short-term momentum signal |
| 2 | ATR double-normalization | signals.py:154 | Divides by price twice |
| 3 | Walk-forward includes training windows | walkforward.py:101 | combined_equity has train+test data |
| 4 | Unused cv_folds parameter | walkforward.py:374 | Accepted but never implemented |
| 5 | Duplicate inconsistent Sharpe calculation | backtest_engine | Backtrader vs custom calc may diverge |
| 6 | Risk parity uses sample cov (no shrinkage) | builder.py:251 | Should use ledoit_wolf_cov() |
| 7 | Mutable TradeRecord fields | trade_tracker.py:254 | Mutation after appending to list |

## LOW Issues

| # | Issue | File | Details |
|---|-------|------|---------|
| 1 | ensure_datetime_index() forces UTC | core.py:55 | Can misalign with tz-naive data |
| 2 | VolumeSignal always returns zero | signals.py:301 | No-op stub dilutes blended signals |
| 3 | No statistical significance testing | — | No p-values or bootstrap CIs on Sharpe |
| 4 | No corporate action handling | — | No adjusted vs unadjusted price tracking |

---

## Recommended Fix Priority

| Priority | Issue | Effort | Impact |
|----------|-------|--------|--------|
| 1 | CRITICAL-3: Builder ignores weights | Medium | Makes entire pipeline work |
| 2 | CRITICAL-1: Walk-forward wrong metric | Trivial (1 line) | Fixes all WF analysis |
| 3 | CRITICAL-2: GridSearch no CV | Medium | Enables valid param optimization |
| 4 | HIGH-5: SignalBlender look-ahead | Low | Fixes all blended signals |
| 5 | HIGH-6: No costs in signal research | Low | Realistic research metrics |
| 6 | HIGH-8: get_position reads price | Low | Fixes event-driven signals |
| 7 | Everything else | Varies | Quality improvements |

---
*Last updated: 2026-03-13*
