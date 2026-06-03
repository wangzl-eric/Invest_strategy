# Strategy Tracker
# 2026-03-15: Fix rebalance_frequency passthrough bug in builder.py (Dev)

> Master tracker for all strategy proposals. Updated after each review cycle.

## Status Legend

- **APPROVED** — Added to strategy pool for paper trading
- **CONDITIONAL** — Needs specific improvements before approval
- **IN REVIEW** — Active multi-round challenge loop with PM
- **REJECTED** — Fundamental flaws identified
- **IN DEVELOPMENT** — Being implemented by Dev
- **PAPER TRADING** — Live paper trading in progress

## Strategy Pipeline

| # | Strategy | Researcher | Asset Class | Verdict | Priority | Round | Lessons Applied | Folder |
|---|----------|-----------|-------------|---------|----------|-------|-----------------|--------|
| 1 | Cross-Sectional Equity Momentum | Elena | Equity | CONDITIONAL | 3 | — | — | `equity_momentum_2026-03-13_conditional/` |
| 2 | Sector Rotation (Macro-Linked) | Elena | Equity/Macro | CONDITIONAL | 4 | — | — | `sector_rotation_2026-03-13_conditional/` |
| 3 | Vol-Scaled Momentum | Elena | Equity | REJECTED | — | 3 | [L1, L2, L3](#lessons-from-rejections) | `vol_scaled_momentum_2026-03-13_rejected/` |
| 4 | Yield Curve Steepener/Flattener | Marco | Rates | REJECTED | — | — | — | `yield_curve_2026-03-13_rejected/` |
| 5 | Commodity Momentum + Inflation | Marco | Commodities | REJECTED | — | — | — | `commodity_momentum_2026-03-13_rejected/` |
| 6 | FX Carry + Momentum | Marco | FX | CONDITIONAL | 1 | — | — | `fx_carry_2026-03-13_conditional/` |
| 7 | VIX Regime (VRP + Term Structure) | Elena + Marco | Equity/Vol | REJECTED | — | 2 | [L4, L5, L6, L7](#lessons-from-rejections) | `vix_regime_2026-03-15_rejected/` |
| 8 | Quality + Safe-Haven Overlay | Elena | Equity/Multi-Asset | IN REVIEW | 2 | — | — | `quality_safe_haven_2026-03-17_in_review/` |

All folders under `research/strategies/`.

### Lessons from Rejections

**L1:** Always benchmark vs equal-weight from Round 1 (Vol-Scaled Momentum: -3.32% alpha vs EW)
**L2:** MVO with tight constraints adds noise not alpha (prefer ranking-based allocation)
**L3:** Vol targeting doesn't fix crash risk for equity long-only (backward-looking can't react to shocks)
**L4:** VRP is crisis signal not alpha signal (spanning alpha t=-0.18 after controlling for market/momentum)
**L5:** Position-sizing overlays have structural headwind (must add alpha, not just reduce risk)
**L6:** Always compare vs simplest alternative (VRP lost to trailing vol on all metrics)
**L7:** Daily rebalancing of regime signals generates catastrophic turnover (2430%/yr → 916% weekly)

See `~/.claude/projects/-Users-zelin-Desktop-PA-Investment-Invest-strategy/memory/LESSONS_LEARNED.md` for full details.

## Quantitative Verdict Gates

A strategy CANNOT receive APPROVED unless ALL gates pass:

| Gate | Threshold |
|------|-----------|
| Deflated Sharpe Ratio | > 0 |
| Walk-forward hit rate | > 55% |
| Survives 2x realistic costs | Sharpe > 0 |
| PSR | > 0.80 |
| Worst regime annual loss | > -15% |
| LLM verdict | != ABANDON |
| Strategy half-life | > 2 years |
| MinBTL | < available data length |

## Multi-Round Challenge Loop

Each strategy goes through a mandatory review process:

1. **Researcher** messages Cerebro for literature briefing
2. **Researcher** creates strategy folder, writes proposal.md, executes research_r1.ipynb
3. **PM** reads notebook + Cerebro contradiction search -> Round 1 challenges
4. **Researcher** addresses challenges in research_r2.ipynb
5. **PM** verifies fixes -> Round 2 (optional Round 3 if unresolved CRITICAL)
6. **PM** issues verdict: APPROVED / CONDITIONAL / REJECT

## Blocking Requirements (Before ANY Strategy Can Be Trusted)

These framework bugs must be fixed first. See `framework_audit/backtesting_audit.md` for details.

| # | Issue | Severity | File | Status |
|---|-------|----------|------|--------|
| 1 | PortfolioBuilder.backtest() ignores computed weights | CRITICAL | backtests/builder.py:260-334 | **FIXED** |
| 2 | Walk-forward annualized_return mapped to sharpe_ratio | CRITICAL | backtests/walkforward.py:322 | **FIXED** |
| 3 | GridSearch has no train/test split | CRITICAL | backtests/walkforward.py:370-440 | **FIXED** |
| 4 | SignalBlender normalizes with full-sample stats | HIGH | backtests/strategies/signals.py:329 | **FIXED** |

All critical/high bugs fixed as of 2026-03-13. Tests: `tests/unit/test_bugfixes.py` (13 tests pass).

## Capital Allocation Policy

**ZERO capital** until:
1. ~~All 4 blocking framework bugs are fixed~~ **DONE**
2. At least one strategy completes 3+ months of paper trading
3. Walk-forward analysis (with proper train/test split) shows positive OOS Sharpe

## Next Steps

### Phase 2 (Strategy Research — v2 Workflow)
- [ ] Vol-Scaled Momentum (Priority 1) — Elena to run full notebook with 16-cell template
- [ ] FX Carry + Momentum (Priority 2) — Marco to run full notebook
- [ ] Cross-Sectional Momentum (Priority 3) — Elena to expand universe to 100+ stocks
- [ ] Sector Rotation (Priority 4) — Elena to specify macro overlay rules

### Phase 3 (Validation)
- [ ] Run walk-forward on first APPROVED strategy
- [ ] Set up paper trading infrastructure
- [ ] Define risk budgets per strategy

---

### 2026-03-14 — Migrated to folder structure and v2 workflow
- Strategy files moved from flat .md to `{main_idea}_{date}_{verdict}/proposal.md`
- Agent prompts updated: multi-round challenge loop, notebook-based evidence
- Notebook template created: `notebooks/templates/strategy_research_template.ipynb` (16 cells)
- Bug status updated: all 4 blocking bugs marked FIXED
- Files modified: all agent .md files, STRATEGY_TRACKER.md, notebook template
- Status: COMPLETE

### 2026-03-15 — PM Framework Advisory issued
- PM completed line-by-line review of backtests/builder.py, backtests/walkforward.py, backtests/strategies/signals.py, backtests/event_driven/engine.py, backtests/stats/, backtests/costs/, backtests/parallel.py
- Identified 4 blockers (B1-B4), 5 acceptable risks (A1-A5), 3 unknowns (U1-U3)
- Key finding: PortfolioBuilder.backtest() uses static weights (not re-optimized per rebalance) — overstates stability
- Issued 3-phase roadmap: Phase 1 (1-2 weeks) for Vol-Scaled Momentum approval, Phase 2 (1-3 months) for FX/CS Momentum, Phase 3 (3-6 months) enhancements
- Recommended adopting exchange_calendars (lightweight), NOT qlib or backtrader wholesale
- Framework assessment: partially trustworthy — signals and stats are sound, but backtest equity curves from vectorized path need dynamic rebalancing
- Files created: research/framework_audit/pm_framework_advisory_2026-03-15.md
- Status: COMPLETE

### 2026-03-15 — Framework comparison report (Dev)
- Researched qlib, backtrader, vnpy, zipline-reloaded vs. local framework
- Identified 4 gaps blocking current strategies: CarrySignal wrong (FX Carry), ATR double-norm (Vol-Scaled Momentum), no cross-sectional factor analysis (CS Momentum), VolumeSignal no-op stub
- Recommendation: do NOT replace local framework; selectively adopt alphalens-reloaded for IC analysis; fix CarrySignal and ATR bugs first
- Files modified: research/framework_audit/framework_comparison_2026-03-15.md (created)
- Status: COMPLETE

### 2026-03-15 — PM addendum implemented (Dev)
- Fixed ATR double-normalization: removed second /prices division in ATRSignal.compute() — signal values now ~0.01 (correct) not ~0.0001 (wrong). File: backtests/strategies/signals.py:149-156
- Removed VolumeSignal from _init_defaults(): class retained but not auto-registered; list_signals() and run_signal_research() no longer silently include a zero signal
- Updated CarrySignal docstring: clearly documents it is a short-term momentum proxy, NOT true carry; instructs use of FXCarrySignal (not yet implemented)
- Installed alphalens-reloaded==0.4.6; added to requirements.txt — ready for Elena's CS Momentum research round
- All 23 existing unit tests pass (test_blend.py, test_bugfixes.py)
- Status: COMPLETE

### 2026-03-15 — Phase 1 structural items completed (items 1.1–1.5)

**Item 1.1 — Dynamic weight re-optimization in PortfolioBuilder.backtest():**
- Added `dynamic_reoptimize: bool = True` parameter to `PortfolioBuilder.backtest()`
- At each rebalance date, `_optimize_weights_as_of(as_of_date, common_assets)` is called
  using only data available up to that date — no static-weight look-ahead (blocker B3)
- New helper `_alpha_as_of()` extracts per-asset signal values as-of each rebalance date
- Fallback to equal-weight when optimization fails or signals are unavailable
- Files modified: backtests/builder.py

**Item 1.2 — CostModel hierarchy wired into vectorized backtest path:**
- `PortfolioBuilder.backtest()` now accepts `cost_model: Optional[CostModel]` parameter
- When a `CostModel` instance is provided, costs are applied via `cost_model.calculate_cost()`
  at each rebalance turnover event, replacing the flat `config.commission` rate
- Compatible with `CompositeCostModel`, `ProportionalCostModel`, `MarketImpactModel`
- Files modified: backtests/builder.py

**Item 1.3 — Risk parity Ledoit-Wolf covariance fix:**
- `_risk_parity_weights()` now uses `ledoit_wolf_cov()` instead of `returns.cov()`
- Consistent with the mean-variance path (which already used Ledoit-Wolf)
- Prevents instability when sample size is small relative to asset count
- Files modified: backtests/builder.py

**Item 1.4 — End-to-end validation of all 11 quantitative gates:**
- New test file: tests/unit/test_phase1_gates.py (15 tests, all pass)
- Gates validated: DSR, CPCV splits, 2x cost survival, PSR, regime loss,
  LLM verdict stub, strategy half-life, MinBTL, dynamic rebalancing equity
  curve, CompositeCostModel integration, exchange_calendars alignment
- All 15 gate tests pass with synthetic data
- Files created: tests/unit/test_phase1_gates.py

**Item 1.5 — exchange_calendars install + trading-day alignment:**
- Installed exchange-calendars==4.13.2 (via pip); added to requirements.txt
- New module: backtests/calendar.py — thin wrapper providing:
  - `get_trading_days(start, end, exchange)` — returns NYSE/NASDAQ/LSE sessions
  - `align_to_trading_days(df, exchange)` — drops holiday/weekend rows
  - `is_trading_day(date, exchange)` — single-date check
- `PortfolioBuilder.load_data()` now accepts `align_calendar=True` (default) and
  `exchange="XNYS"` — automatically strips non-trading rows after loading
- Files created: backtests/calendar.py
- Files modified: backtests/builder.py, requirements.txt

**Test summary after Phase 1:**
- 39 tests pass across test_bugfixes.py, test_blend.py, test_phase1_gates.py
  (was 23 before Phase 1 work)
- Pre-existing failures in test_optimizer.py, test_portfolio_optimizer.py,
  test_news_service.py are unrelated to Phase 1 scope
- Status: COMPLETE

### 2026-03-15 — Cerebro literature briefing for Vol-Scaled Momentum
- Full briefing compiled: supporting evidence (8 papers), contradicting evidence (6 papers), alpha decay analysis, book references, known failure modes, suggested approaches
- Key findings: DeMiguel et al. (2024 JoF) validates multifactor vol management OOS (+13% Sharpe); Cederburg et al. (2020 JFE) is primary OOS challenge; 2024 crowding risk elevated
- Saved to: research/strategies/vol_scaled_momentum_2026-03-13_conditional/cerebro_briefing.md
- Files modified: research/STRATEGY_TRACKER.md, cerebro_briefing.md (created)
- Status: COMPLETE

### 2026-03-15 — Fix rebalance_frequency passthrough in builder.py (Dev)
- Bug: `backtest()` else branch hardcoded `resample("M")`, ignoring configured `rebalance_frequency` for any non-daily, non-weekly value
- Fix: added explicit `"monthly"` branch; else branch now passes the configured string directly to `resample()` (supports "2M", "Q", "BQ", etc.)
- Added `TestBug10RebalanceFreqPassthrough` (2 tests): verifies "2M" produces fewer rebalance dates than "M" and returns a valid result dict
- Note: pandas 2.1.x (installed) uses "M"/"2M" — "ME"/"2ME" aliases require pandas >= 2.2
- Files modified: `backtests/builder.py:461-472`, `tests/unit/test_bugfixes.py`
- Status: COMPLETE

### 2026-03-15 — Add target_vol parameter to PortfolioBuilder.backtest() (Dev)
- New parameter: `target_vol=None` (float or None). At each rebalance date computes trailing 60-day realised portfolio vol, scales gross exposure by `min(1.0, target_vol / port_vol)`. Never levers up. No look-ahead.
- Falls back to no scaling for first 60 bars. target_vol=None preserves existing behaviour exactly (backward compatible).
- Added `TestBug11TargetVol` (3 tests): drawdown reduction verified, None is identity, result dict is finite.
- Files modified: `backtests/builder.py:418-526`, `tests/unit/test_bugfixes.py`, `.pre-commit-config.yaml`
- Status: COMPLETE

### 2026-03-15 — Vol-Scaled Momentum REJECTED after 3-round PM review
- 3 rounds of PM review completed (R1: code review, R2: executed notebook review, R3: vol targeting review)
- Final gate score: 7/11 PASS, 4/11 FAIL (worst regime -48.12%, max DD -32.00%, turnover 178%, MinBTL 26.4yr)
- Vol targeting (target_vol=0.12) proved ineffective: max DD unchanged (sudden crash, not gradual), worst regime improved only 9%, Sharpe decreased from 0.591 to 0.454
- Critical finding: negative alpha vs equal-weight benchmark (-3.32% annualized) — signal-driven optimization destroys value vs naive 1/N diversification
- Critical finding: fair-weather fund dynamics — high-VIX Sharpe -1.305, low-VIX Sharpe +2.255 — all returns from calm markets
- Root cause: mean-variance optimizer with binding max_weight=0.12 constraint is effectively equal-weight with noise; high turnover (178%) from shuffling which stocks hit the cap
- Lessons: (1) vol targeting doesn't fix crash risk for equity long-only, (2) benchmark against equal-weight from R1, (3) MVO with tight constraints adds noise not alpha, (4) IS/OOS split (0.516 vs 0.180) reveals decay that walk-forward (66.7% hit rate) masks
- Strategy folder renamed: `vol_scaled_momentum_2026-03-13_conditional/` -> `vol_scaled_momentum_2026-03-13_rejected/`
- Priority reallocation: FX Carry + Momentum (P2) moves to Priority 1 after data gaps closed
- Files modified: pm_review.md (3 rounds appended), STRATEGY_TRACKER.md
- Status: COMPLETE (REJECTED)

### 2026-03-15 — VIX Regime (VRP + Term Structure) REJECTED after 2-round PM review
- Joint submission: Elena (notebook, equity signals) + Marco (macro concerns, crowding risk)
- R1 identified catastrophic turnover (2430%/yr daily regime switching) — weekly resampling approved as R2 fix
- R2 results: 8/12 gates PASS, 3 FAIL, 1 FLAG
- Three structural failures with no fix path:
  - MinBTL = 3,968yr vs 12.6yr available (off by 315x — Sharpe indistinguishable from noise)
  - Spanning alpha t = -0.18 (zero independent alpha after controlling for SPY + momentum)
  - Dominated by simpler signals: trailing vol beats VRP on Sharpe (0.341 vs 0.299), MaxDD (-20% vs -32%), and turnover (187% vs 916%)
- Overlay test (Cell 15) was decisive: VRP overlay HURTS momentum Sharpe by -0.297 OOS while reducing drawdown by 11.6pp — expensive insurance, not alpha
- Signal genuinely detects crises (interaction t = -3.77) but doesn't translate to tradeable edge
- Lessons: (1) check head-to-head vs simple baselines in R1, (2) MinBTL as early filter, (3) drawdown reduction ≠ alpha, (4) VRP is a risk management input not a strategy signal
- Folder: `vix_regime_2026-03-15_rejected/`
- Files created: pm_review.md
- Status: COMPLETE (REJECTED)

### 2026-03-17 — Goldman Sachs Strategy Ideas Assessment (PM)
- Assessed 4 strategy ideas from Goldman Sachs Global Strategy Views (16 March 2026)
- **Strategy 1 (Defensive Sector Rotation):** REJECTED — no sector classification data, requires $5K+/yr Norgate or 6mo valuation pipeline build
- **Strategy 2 (HALO Factor):** REJECTED — no fundamental data pipeline, factor definition too vague
- **Strategy 3 (Geographic Rotation):** REJECTED — no international equity data, IBKR account lacks intl permissions
- **Strategy 4 (Quality + Safe-Haven Overlay):** APPROVED for research (Priority 2) — feasible with ETF proxies (QUAL/USMV + GLD/USO + JPY/CHF FX)
- Strategy 4 added to pipeline: Elena assigned, data requirements identified (QUAL, USMV, GLD, USO, VIX, HYG, LQD)
- FX Carry + Momentum priority elevated from P2 → P1 (after Vol-Scaled Momentum rejection)
- Files created: `research/goldman_sachs_strategy_assessment_2026-03-17.md`
- Status: COMPLETE

### 2026-03-17 — Quality + Safe-Haven Overlay Equity Quant Assessment (Elena)
- Completed full equity quant analysis of Goldman Sachs Quality + Safe-Haven strategy
- **Quality factor validation:** Academically sound (Asness QMJ Sharpe 0.5-0.6, FF5 RMW 3-4% alpha), but post-publication decay significant (expect 2-3% alpha in US large-cap due to QUAL/USMV crowding, $50B+ AUM)
- **Regime performance:** Quality works in SUSTAINED high-vol + rising-rate regimes (2008 +15% vs SPY, 2022 +8%), NOT all VIX > 20 periods. VIX > 20 trigger too coarse (occurs 30% of time) — recommend VIX > 25 + credit spread widening.
- **Safe-haven overlay analysis:** JPY/CHF ENHANCE (negative crisis correlation -0.4 to -0.5), Gold CONDITIONAL (regime-dependent, failed in 2022 rate hikes), Oil DILUTES (positive correlation +0.3 to +0.4, NOT a safe-haven). Recommendation: DROP Oil, keep JPY/CHF 15% each.
- **ETF proxy assessment:** QUAL/USMV acceptable for Phase 1 (fast implementation, no data pipeline), but crowding penalty -1% to -2% alpha. Upgrade to fundamental construction in 6-12mo for fresher signals (+1-2% alpha lift).
- **Implementation recommendation:** 70% Quality (QUAL or 50/50 QUAL+USMV blend) + 15% JPY + 15% CHF, rebalance monthly. Expected Sharpe 0.5-0.6, max DD -20% to -25% (vs -25% to -30% for Quality alone).
- **Key risks:** (1) Crowding (QUAL $20B AUM), (2) Short history (14yr, MinBTL borderline 12-18yr), (3) Position-sizing overlay may hurt Sharpe (Lesson L5 — must improve Sharpe +0.15 minimum, not just reduce drawdown), (4) FX carry not captured (spot rates only, missing 2-3% carry income)
- **4-week research plan:** Week 1 validate Quality factor, Week 2 test safe-haven overlay, Week 3 dynamic trigger logic, Week 4 full 16-cell notebook
- **Verdict:** APPROVED for research (Priority 2), status changed from PENDING to IN REVIEW
- Files created: `research/quality_safe_haven_assessment_2026-03-17.md` (12-section equity quant analysis)
- Files modified: `research/external_ideas.md` (updated Strategy 5.4 with Elena assessment summary), `research/STRATEGY_TRACKER.md` (status update)
- Status: COMPLETE (assessment), next step: message Cerebro for literature briefing

### 2026-03-18 — Quality + Safe-Haven Overlay Codex GPT-5.4 Audit
- Codex (GPT-5.4) completed independent audit of strategy entry before adding to research pool
- **Final recommendation:** REVISE (feasibility 3/5 — research-feasible, not production-ready)
- **Critical inconsistency identified:** Strategy description says "triggered overlay" but implementation shows static "70/15/15" allocation — these are fundamentally different strategies with different risk/return profiles
- **Signal quality issues:** (1) HYG-LQD duration mismatch (2.88y vs 8.00y) produces false credit stress signals during rate hikes — recommend OAS-based spread instead, (2) VIX > 25 trigger ambiguous (AND vs OR with credit spread? hysteresis? timing?)
- **Missing specifications:** (1) FX implementation unspecified (spot, forwards, futures, ETF proxies?), (2) Gold inclusion/exclusion unclear ("optionally Gold"), (3) Rebalancing frequency mismatch (monthly rebalance inconsistent with fast-moving VIX triggers)
- **Risk factors flagged:** (1) Base currency risk (USD can strengthen in crises, hedge fails), (2) Policy regime risk (BOJ/SNB intervention changes safe-haven behavior), (3) Factor purity confusion (QUAL+USMV blend is quality+minvol, not pure quality), (4) Crowding/valuation (QUAL P/E 27.84x, beta 0.97 — not low-beta defensive), (5) Whipsaw risk (hard VIX threshold, no hysteresis)
- **Recommended revisions:** (1) Resolve static vs dynamic allocation (recommend static 70/15/15 for Phase 1), (2) Fix credit spread signal (use FRED OAS: BAMLH0A0HYM2 - BAMLC0A0CM), (3) Specify FX implementation (recommend FXY/FXF ETFs for Phase 1), (4) Remove "optionally Gold" ambiguity (exclude for Phase 1), (5) Add hysteresis to trigger (enter VIX > 25, exit VIX < 20 for 5 days)
- **Agreement with Elena:** Quality factor sound ✅, JPY/CHF genuine safe havens ✅, Oil should be excluded ✅, Crowding risk real ✅, Short history concern ✅
- **Disagreement with Elena:** (1) Codex recommends VIX > 25 + hysteresis (Elena VIX > 20), (2) Codex flags HYG-LQD duration mismatch (Elena doesn't mention), (3) Codex flags static vs dynamic inconsistency (Elena proposes static as default), (4) Codex treats Sharpe/DD estimates as hypotheses (Elena presents as forecasts)
- **Next steps:** Revise strategy entry to resolve ambiguities, then proceed to Phase 1 research (4-week plan)
- Files created: `research/quality_safe_haven_codex_audit_2026-03-18.md` (9-section audit with 6 red flags)
- Status: COMPLETE (audit), awaiting revisions before Cerebro briefing

*Last updated: 2026-03-18*
