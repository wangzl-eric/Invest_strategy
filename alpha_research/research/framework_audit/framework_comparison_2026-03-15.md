# Backtesting Framework Comparison Report — 2026-03-15

> **Author:** Dev (Quantitative Developer) | **Date:** 2026-03-15
> **Context:** Evaluation for Vol-Scaled Momentum, FX Carry+Momentum, and Cross-Sectional Momentum strategies (all CONDITIONAL)

---

## Executive Summary

Our local framework has strong statistical rigor infrastructure (PSR, Deflated Sharpe, CPCV, MinBTL, proper walk-forward) and a clean signal architecture (`BaseSignal`). The 9 critical/high bugs identified in March 2026 are all fixed. However, compared to production-grade external frameworks, we have notable gaps in: ML/AI signal generation, realistic multi-asset execution simulation, live-trading integration, a point-in-time data system, and portfolio-level performance attribution.

**Recommendation**: Do not replace the local framework. Selectively integrate two components — qlib's formulaic alpha expression engine for factor research, and NautilusTrader's execution/live-trading layer for paper-to-live graduation. All four currently-evaluated strategies (Zipline/backtrader/vnpy/qlib) have partial overlaps with our needs, but none fully matches our statistical rigor pipeline.

**Key Findings by Framework:**
- **qlib**: Most relevant. Superior data layer, ML model zoo, formulaic alpha engine. High integration complexity. Actively maintained by Microsoft.
- **backtrader**: Well-matched event-driven API but effectively unmaintained. We already built a compatible layer (`backtrader_compat.py`). No value in adopting.
- **vnpy**: Production-grade live trading, Chinese-market focus, difficult English integration. No backtesting statistical rigor.
- **zipline (reloaded)**: Best Pipeline API for cross-sectional equity factor research; maintained community fork. Strong fit for Cross-Sectional Momentum strategy universe selection.

---

## 1. External Framework Analysis

### 1.1 qlib (Microsoft)

**Repository:** `microsoft/qlib` | **Stars:** ~31,100 | **Forks:** ~4,800 | **Status:** Actively maintained (2025 paper published; 6,000+ new stars in 2025 alone)

**Design Philosophy:**
AI-oriented quant investment platform. Every component is a loose-coupled module that can be used standalone. The central abstraction is the `Dataset` class connecting data processing to model training. Research-to-production with minimal config changes via YAML workflow files (`qrun`).

**Architecture:**
```
Data Layer (PIT DB + binary format + 3-tier cache)
    ↓
Feature Engineering (formulaic alpha expressions)
    ↓
ML Model Training (40+ models: LSTM, Transformer, TCN, HIST)
    ↓
Portfolio Optimization
    ↓
Execution (Nested Decision Framework: daily outer + intraday inner)
    ↓
Online Deployment (OnlineManager + RD-Agent automation)
```

**Key Features:**

| Component | Details |
|-----------|---------|
| **Point-in-Time DB** | Eliminates look-ahead in financial statement data; binary format 20-50x faster than CSV |
| **3-Tier Cache** | MemCache (hot) + ExpressionCache (computed) + DatasetCache (complete) |
| **Formulaic Alphas** | Expression strings: `EMA($close,12) - EMA($close,26)`, Alpha158, Alpha101 built-in |
| **ML Model Zoo** | 40+ models including Transformer, TCN, HIST; supervised + RL paradigms |
| **Walk-Forward** | Built-in rolling train/val/test splits; annual recalibration |
| **Nested Execution** | Daily strategy nesting intraday executor; realistic slippage + partial fills |
| **RD-Agent (2025)** | LLM-driven automated factor discovery and model optimization |

**Pros:**
- Best-in-class data layer with PIT guarantees and caching
- Formulaic alpha engine eliminates boilerplate signal code
- 40+ pre-built ML models with standardized interfaces
- Active Microsoft Research Asia team; growing community
- Research-to-production with same codebase

**Cons:**
- Heavy dependency footprint (PyTorch, etc.); setup complexity is HIGH
- Opinionated YAML config system requires significant learning
- Alpha 158 / Alpha 101 oriented toward Chinese equity markets
- No built-in PSR / Deflated Sharpe / MinBTL statistical tests
- Integration into existing Python infrastructure requires adapter layer
- Documentation assumes ML workflow; pure signal research is secondary

**Maintenance Status:** Very active. 2025 research paper published. Surge of community engagement. Microsoft backing ensures continuity. Python 3.10+ supported.

---

### 1.2 backtrader

**Repository:** `mementum/backtrader` | **Stars:** ~15,000 | **Status:** EFFECTIVELY UNMAINTAINED (no significant commits for 2+ years)

**Design Philosophy:**
Object-oriented, event-driven framework designed so traders can focus on strategy logic rather than infrastructure. The `Cerebro` engine orchestrates data feeds, strategy execution, and reporting. Heavily Pythonic with per-bar `next()` loop.

**Architecture:**
```
Cerebro Engine
    ├── Data Feeds (CSV, Pandas, broker real-time)
    ├── Indicators (built-in library + custom)
    ├── Strategy (next() method, order management)
    ├── Analyzer (Sharpe, DrawDown, TradeAnalyzer)
    └── Sizer + Broker (slippage, commission, order types)
```

**Key Features:**

| Component | Details |
|-----------|---------|
| **Order Types** | Market, Limit, Stop, StopLimit, StopTrail, OCO, Bracket |
| **Slippage** | Volume-based and fixed slippage models |
| **Analyzers** | Sharpe, Calmar, SQN, DrawDown, TimeReturn, TradeAnalyzer |
| **Optimization** | Built-in `optstrategy()` for parameter sweeps (single-process) |
| **Plotting** | One-line `cerebro.plot()` via Matplotlib |
| **Live Trading** | IBKR, OANDA integrations |

**Pros:**
- Most complete event-driven API for retail quant strategies
- Extensive documentation and community examples
- IBKR broker integration already works
- Rich order-type simulation (closest to realistic execution)

**Cons:**
- Effectively unmaintained — Python 3.10+ has compatibility issues
- Single-threaded, slow for large parameter sweeps
- No statistical significance testing (PSR, MinBTL)
- No walk-forward with proper train/test split
- No ML/AI integration
- We already built `backtests/strategies/backtrader_compat.py` to wrap it

**Maintenance Status:** DEAD for practical purposes. Last significant release: 2019. Community fork `backtrader_next` exists but is minimal. Do not adopt.

**Note:** We already have a compatibility layer. The remaining HIGH-1 issue (undocumented EOD convention in `backtrader_compat.py:44-68`) should be documented, not extended.

---

### 1.3 vnpy (VeighNa)

**Repository:** `vnpy/vnpy` | **Stars:** ~32,900 | **Status:** Actively maintained; v4.0 released 2025

**Design Philosophy:**
Production-grade event-driven platform for professional and institutional traders. Emphasis on live trading across global markets (Chinese equities, futures, crypto, FX). Architecture built for distributed deployment and low-latency execution. Version 4.0 adds `vnpy.alpha` ML module with Alpha 158 factor library (from qlib).

**Architecture:**
```
Event Engine (vnpy.event)
    ├── Trading Gateways (30+ market connections)
    ├── RPC Framework (inter-process / distributed)
    ├── Strategy Modules (CTA, Spread, Options, HFT)
    ├── Data Services (XtQuant, RQData, TuShare)
    ├── Multi-DB Support (TDengine, TimescaleDB, MongoDB, InfluxDB)
    └── Web Trader (REST + WebSocket server)
```

**Key Features:**

| Component | Details |
|-----------|---------|
| **Trading Gateways** | 30+ connections: Chinese equities/futures/options, crypto, FX, global |
| **Strategy Modules** | CTA (trend-following), Spread, Options, Algorithm, HFT |
| **Database Layer** | TDengine (primary), MongoDB, InfluxDB, TimescaleDB, LevelDB |
| **vnpy.alpha (v4.0)** | ML factor engineering; Alpha 158 (from qlib); batch feature calc |
| **Async I/O** | REST + WebSocket clients built on async; high-concurrency |
| **Web Trader** | Full B-S architecture with push/pull API |

**Pros:**
- Most production-complete for live trading and order routing
- Largest community (33k stars) + most active for live strategies
- v4.0 Alpha 158 ML features align with our ML roadmap
- Distributed architecture ready for institutional scale
- Python 3.13 supported; actively maintained

**Cons:**
- Primary documentation and community are in Mandarin Chinese; English docs are thin
- Backtesting module is secondary; no walk-forward, PSR, MinBTL, or CPCV
- Designed for Chinese domestic markets first; global asset coverage is secondary
- Heavy for our current scale (no need for distributed RPC)
- Integration into our Parquet/DuckDB data lake would require adapters
- Not aligned with our research workflow (notebook → signal → backtest pipeline)

**Maintenance Status:** Very active. v4.0 shipped on 10th anniversary (2025). Python 3.13 recommended. Large paid community (QQ group). English adoption growing via forks.

---

### 1.4 zipline (Quantopian / zipline-reloaded)

**Repository:** `stefan-jansen/zipline-reloaded` | **Stars:** ~1,700 | **Original:** `quantopian/zipline` (Quantopian closed 2020)

**Design Philosophy:**
Event-driven equity backtesting library designed for cross-sectional factor research. The Pipeline API is the standout feature: enables complex universe selection and ranking across thousands of securities. Batteries included with PyData integration (Pandas DataFrames in/out). Structurally enforces data quality to minimize look-ahead bias.

**Architecture:**
```
TradingAlgorithm (initialize + handle_data)
    ├── Pipeline API (universe selection, factor ranking, cross-sectional)
    ├── Data Bundle (price/fundamental data with corporate actions)
    ├── BarData (real-time access within handle_data; enforces PIT)
    ├── Portfolio (position tracking, P&L)
    └── Blotter (order management, fills, commissions)
```

**Key Features:**

| Component | Details |
|-----------|---------|
| **Pipeline API** | Factor definitions + universe filters; cross-sectional ranking; vectorized |
| **Data Bundles** | Corporate-action-adjusted prices; fundamental data integration |
| **PIT Enforcement** | Structural prevention of look-ahead in data access |
| **PyData Integration** | Returns pd.DataFrames; integrates with Alphalens, Pyfolio |
| **Scale** | Designed for thousands of securities at once |
| **Alphalens** | Built-in factor analysis: IC, factor quantile returns, turnover |

**Pros:**
- Pipeline API is best-in-class for cross-sectional equity factor research
- Structural look-ahead bias prevention (not just a convention)
- Alphalens factor analysis integration (IC, decay, quantile returns)
- Corporate action handling built in
- Maintained by Stefan Jansen (ML for Algorithmic Trading author)
- Python 3.9+, pandas 2.2+, NumPy 2.0 compatible (as of v3.05)

**Cons:**
- No ML model integration (unlike qlib); pure signal/factor framework
- Slow per-bar Python execution; not suitable for large minute-level backtests
- No live trading (Quantopian infrastructure is gone)
- No walk-forward, PSR, MinBTL, or CPCV (statistical rigor gap)
- Limited to equity-like instruments; no FX carry, futures curve, commodity signals
- Data bundle setup is non-trivial; requires Ingestion pipeline configuration
- No real transaction cost modeling beyond fixed commission

**Maintenance Status:** Community maintained (Stefan Jansen). Active in 2025 — NumPy 2.0 and pandas 2.2 compatibility added. ~1,700 stars (smaller community than others). Ecosystem of forks (zipline-polygon-bundle, RustyBT) is growing.

---

## 2. Our Local Framework Assessment

### 2.1 Strengths

1. **Statistical rigor is best-in-class.** PSR, Deflated Sharpe, MinBTL, CPCV, purged K-fold with embargo, block bootstrap, White's Reality Check, Bonferroni/BH-FDR multiple testing correction — none of the four external frameworks have this built in. This is a genuine differentiator.

2. **Clean signal architecture.** `BaseSignal` subclass pattern is simple, testable, and extensible. `SignalBlender` with expanding-window normalization (after the HIGH-5 fix) is correct. Signal caching via `SignalCache` (Parquet-backed, mtime invalidation, thread-safe) avoids recomputation.

3. **Walk-forward with correct train/test split.** After CRITICAL-1 and CRITICAL-2 fixes: `WalkForwardAnalyzer` properly separates train/test windows and correctly maps `annualized_return`. This was absent from all external frameworks reviewed (except qlib which has it via YAML config).

4. **Transaction cost infrastructure.** `FixedCostModel`, `ProportionalCostModel`, `MarketImpactModel` (Almgren-Chriss square-root), `CompositeCostModel`, `SlippageModel` — cost modeling is comprehensive. The event-driven engine (`EventDrivenBacktester`) applies slippage + commission on fills.

5. **Parallel backtesting.** `ParallelBacktester` (ProcessPoolExecutor, Parquet serialization to avoid pickle overhead) enables parameter sweeps without shared state. No external framework reviewed has this cleanly implemented for our use case.

6. **Reproducibility.** `RunManager` tracks UUID runs with git commit hash, YAML config, and metrics comparison. This is comparable to qlib's `qrun` workflow.

7. **Integrated with our data lake.** DuckDB/Parquet pipeline, catalog.json, multi-source connectors (Binance, Stooq, Polygon, ECB FX) — tightly integrated with our `quant_data/` module. External frameworks would require adapters.

8. **Strategy half-life and decay analysis.** `backtests/stats/decay_analysis.py` — rolling Sharpe decay, strategy half-life, correlation matrix, capacity estimate. This is unique to our framework.

### 2.2 Weaknesses

1. **No point-in-time financial data system.** Fundamental data (P/E, EPS, book value) used at the wrong timestamp would introduce look-ahead. We currently have no PIT DB. Critical if we add fundamental factors.

2. **Event-driven engine is minimal.** `EventDrivenBacktester` has ~120 lines. Missing: partial fills, order book simulation, volume constraints, multiple order types (only market orders implied), realistic bid-ask spreads.

3. **No corporate action handling.** No adjusted vs. unadjusted price tracking. Splits and dividends can silently corrupt signals (identified as LOW-4 in audit). For equity momentum strategies, this matters.

4. **No cross-sectional factor analysis tooling.** No IC (Information Coefficient), factor quantile returns, or factor turnover analysis — the features Alphalens (zipline ecosystem) provides. Our signal research is return-based only.

5. **No ML signal integration.** No pipeline for training ML models on signals, cross-validating, and deploying. qlib's model zoo (40+ models) would require full reimplementation.

6. **CarrySignal is mislabeled (MEDIUM-1).** `CarrySignal` is actually a short-term momentum signal. This corrupts the FX Carry strategy's core signal.

7. **ATR double-normalization (MEDIUM-2).** `ATRSignal` divides by price twice, producing incorrect volatility-normalized returns.

8. **No live trading integration.** `execution/runner.py` handles paper trading via `SimBroker` but has no path to live execution. Our IBKR integration (`backend/ibkr_client.py`) exists but is not wired to the backtesting execution framework.

9. **Single data source per backtest.** Cannot easily run multi-frequency backtests (e.g., daily signal generation + weekly rebalancing with intraday execution). qlib's nested execution framework handles this natively.

10. **VolumeSignal is a no-op stub (LOW-2).** Returns zero always — silently dilutes any blended signal that includes it.

### 2.3 Feature Gap Analysis

| Feature Area | Our Framework | Gap Level |
|---|---|---|
| Statistical significance testing (PSR, DSR, MinBTL) | COMPLETE | None |
| Walk-forward with proper train/test | COMPLETE (post-fix) | None |
| Transaction cost models | COMPLETE | None |
| Signal caching | COMPLETE | None |
| Parallel parameter sweeps | COMPLETE | None |
| Run reproducibility / tracking | COMPLETE | None |
| Purged K-fold / CPCV | COMPLETE | None |
| Strategy decay / half-life | COMPLETE | None |
| Point-in-time fundamental data | ABSENT | CRITICAL for fundamental factors |
| Cross-sectional factor analysis (IC, quantile) | ABSENT | HIGH for equity cross-sectional strategies |
| ML signal pipeline | ABSENT | HIGH for future enhancement |
| Corporate action handling | ABSENT | HIGH for equity strategies |
| Event-driven: partial fills, order book | MINIMAL | MEDIUM |
| Multi-frequency nested execution | ABSENT | MEDIUM |
| Live trading integration | ABSENT | LOW (paper trading only now) |
| Carry signal accuracy | BROKEN (mislabeled) | HIGH — fix before FX Carry strategy |
| ATR signal accuracy | BROKEN (double-norm) | MEDIUM — fix before vol-scaling |

---

## 3. Detailed Comparison Matrix

| Feature | Our Framework | qlib | backtrader | vnpy | zipline-reloaded |
|---|---|---|---|---|---|
| **Backtesting type** | Vectorized + Event-driven | Vectorized + Nested exec | Event-driven | Event-driven | Event-driven |
| **PSR / Deflated Sharpe** | YES | No | No | No | No |
| **MinBTL** | YES | No | No | No | No |
| **CPCV / Purged K-fold** | YES | No | No | No | No |
| **Walk-forward (proper)** | YES | YES (YAML) | No | No | No |
| **Multiple testing correction** | YES | No | No | No | No |
| **Transaction cost models** | YES (4 models) | YES | YES (basic) | YES (basic) | YES (basic) |
| **Signal caching** | YES (Parquet) | YES (3-tier) | No | No | No |
| **Parallel sweeps** | YES (ProcessPool) | YES (Cython) | No (single-threaded) | Partial | No |
| **Cross-sectional factor analysis (IC)** | No | Partial (Alpha 158) | No | No | YES (Alphalens) |
| **Point-in-time data** | No | YES (PIT DB) | No | No | Partial (bundles) |
| **Corporate actions** | No | YES | No | No | YES |
| **ML model zoo** | No | YES (40+ models) | No | YES (v4.0 alpha) | No |
| **LLM / AI automation** | Cerebro (partial) | YES (RD-Agent) | No | No | No |
| **Live trading** | SimBroker only | No | YES (IBKR, OANDA) | YES (30+ gateways) | No |
| **Multi-frequency execution** | No | YES (nested) | Partial | YES | No |
| **RunManager / reproducibility** | YES (UUID+git) | YES (qrun) | No | No | No |
| **Strategy decay analysis** | YES | No | No | No | No |
| **Active maintenance** | YES | YES (Microsoft) | NO | YES | YES (Jansen) |
| **Python 3.10+ support** | YES | YES | Partial (issues) | YES (3.13) | YES (3.9+) |
| **English documentation** | Internal only | YES | YES | Partial | YES |
| **Integration complexity** | N/A (we own it) | HIGH | MEDIUM | HIGH | MEDIUM |
| **GitHub Stars** | N/A | ~31,100 | ~15,000 | ~32,900 | ~1,700 |

---

## 4. Specific Gaps and Recommendations

### 4.1 Critical Gaps

**GAP-1: CarrySignal is not carry** (HIGH — blocks FX Carry strategy)
- File: `backtests/strategies/signals.py:71-96`
- `CarrySignal` computes rolling mean of past returns — this is momentum, not carry.
- Carry requires: (forward yield / spot yield) - 1, or for FX: interest rate differential
- Impact: FX Carry + Momentum strategy (Priority 2) uses an incorrect signal at its core
- Fix: Implement true FX carry signal using ECB rate data already in `quant_data/connectors/ecb_fx.py`

**GAP-2: ATR double-normalization** (MEDIUM — affects vol-scaled strategies)
- File: `backtests/strategies/signals.py:154` (ATRSignal area)
- Divides by price twice, producing wrong volatility-normalized returns
- Impact: Vol-Scaled Momentum (Priority 1) uses ATR for scaling — result is overstated
- Fix: Single normalization; verify against reference implementation

**GAP-3: Cross-sectional factor analysis tooling** (HIGH — affects Cross-Sectional Momentum)
- No IC calculation, no factor quantile returns, no factor decay plot
- These are essential for validating signal alpha in cross-sectional strategies
- Fix: Build a lightweight `backtests/factor_analysis.py` module (IC, ICIR, quantile returns)
- Alternative: Integrate `alphalens-reloaded` (maintained fork of Quantopian Alphalens)

**GAP-4: VolumeSignal is a no-op** (LOW — affects blended signals)
- File: `backtests/strategies/signals.py:301`
- Returns zero always; silently dilutes `SignalBlender` weights
- Fix: Implement or remove; do not keep a broken stub in the registry

### 4.2 Nice-to-Have Improvements

**NTH-1: Alphalens integration for factor analysis**
- `pip install alphalens-reloaded` (maintained fork, pandas 2.x compatible)
- Provides IC, factor quantile returns, turnover, factor decay without full zipline adoption
- Directly useful for Cross-Sectional Momentum (Elena's Priority 3 strategy)
- Effort: LOW (1-2 days to wrap in research notebook template)

**NTH-2: Formulaic alpha expression engine (from qlib)**
- qlib's `QlibDataLoader` allows signal definition as expression strings
- Enables rapid factor prototyping without writing Python classes
- Could be adopted as an optional research accelerator without full qlib integration
- Effort: MEDIUM (adapter layer needed)

**NTH-3: Corporate action adjustment flag**
- Add `adjusted: bool` field to `BaseSignal` / data loading layer
- Track adjusted vs. unadjusted price source in `catalog.json`
- Effort: LOW-MEDIUM

**NTH-4: Multi-frequency execution support**
- Allow daily signal generation + weekly rebalancing in a single backtest
- Currently requires two separate runs manually stitched
- Effort: MEDIUM-HIGH (requires event engine extension)

**NTH-5: Position-sizing module**
- Currently signal-to-position conversion is in `BaseSignal.to_positions()` (simple sign clip)
- A dedicated `PositionSizer` class (Kelly, target-volatility, equal-risk) would be cleaner
- Effort: LOW

### 4.3 Integration Options: Adopt vs. Build

| Component | Recommended Action | Framework Source | Effort |
|---|---|---|---|
| Cross-sectional factor analysis (IC, quantile) | ADOPT | alphalens-reloaded (zipline ecosystem) | LOW |
| Carry signal (true FX carry) | BUILD | — (use ECB FX connector) | LOW |
| Volume signal | BUILD or REMOVE | — | TRIVIAL |
| Corporate action handling | BUILD (flag + source tracking) | — | LOW-MEDIUM |
| ML signal pipeline | DEFER (not in current strategy set) | qlib (future) | HIGH |
| Live trading integration | DEFER (paper trading phase) | backtrader IBKR or vnpy | HIGH |
| Formulaic alpha engine | ADOPT (optional research tool) | qlib subset | MEDIUM |

**Do NOT adopt full qlib, backtrader, vnpy, or zipline as replacements.** Our statistical rigor layer (PSR, Deflated Sharpe, MinBTL, CPCV) is not available in any of them. Replacing the local framework would mean losing these guarantees. The right strategy is targeted borrowing.

---

## 5. Priority Recommendations

### For the Active Strategy Pipeline (CONDITIONAL strategies awaiting approval)

**Priority 1 — Vol-Scaled Momentum (Elena, Priority 1)**
- Fix ATR double-normalization before any new backtest results are trusted
- `backtests/strategies/signals.py` (MEDIUM-2 from audit)
- Action: Dev to fix in `signals.py` before Elena's next research round

**Priority 2 — FX Carry + Momentum (Marco, Priority 2)**
- CarrySignal is fundamentally wrong. This is a BLOCKING issue for this strategy.
- Implement true FX carry using ECB rate differentials (`quant_data/connectors/ecb_fx.py`)
- Action: Dev to implement `FXCarrySignal` class in `signals.py` (new `BaseSignal` subclass)

**Priority 3 — Cross-Sectional Momentum (Elena, Priority 3)**
- Add alphalens-reloaded for IC analysis to validate signal alpha across 100+ stocks
- Add `factor_analysis.py` helper module or research notebook template section
- Action: Dev to integrate alphalens in notebook template (NTH-1)

**Priority 4 — Sector Rotation (Elena, Priority 4)**
- No new framework gaps block this strategy specifically
- Ensure macro overlay rules use only lagged macro data (no look-ahead)

### For Framework Longevity

| Horizon | Action |
|---|---|
| Immediate (before next research round) | Fix ATR double-normalization, fix CarrySignal, remove VolumeSignal stub |
| Short-term (1-2 months) | Add alphalens integration, add corporate action tracking flag |
| Medium-term (3-6 months) | Evaluate qlib formulaic alpha engine as optional research tool |
| Long-term (live trading phase) | Evaluate backtrader IBKR connector or vnpy gateway for paper-to-live |

### On Replacing the Local Framework

**The local framework should NOT be replaced.** The statistical rigor infrastructure (PSR, Deflated Sharpe, MinBTL, CPCV, purged K-fold, multiple testing correction) represents months of careful implementation and is absent from every major open-source framework reviewed. This is our moat. The correct posture is: own the research and validation pipeline; borrow focused components where they provide clear value without compromising rigor.

---

*Report complete. Next actions in `research/STRATEGY_TRACKER.md`.*
*Last updated: 2026-03-15*
