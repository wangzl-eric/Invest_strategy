# Next-Gen Investment Plan

## Goal

Refine the current quant research infrastructure into a **scalable, rigorous, and robust**
system that supports the full investment cycle: research → deployment → monitoring → feedback.
The end state is a standalone application that runs the complete investment lifecycle:

```
Data ──► Research ──► Deployment (optimization + execution) ──► Monitoring ──► (feeds back to) Data / Research
```

## Architecture at a glance

The repo is a **three-layer DAG**: a shared infrastructure package at the bottom, then
the product components on top.

| Layer / Component | Path | Role |
|-------------------|------|------|
| **Core infrastructure** | `core/` | Config, DB/persistence, IBKR client, market-data platform, Flex ingestion, LLM plumbing. Imports nothing internal. |
| **Alpha research** | `alpha_research/` | Research + backtest framework (signals, backtests, portfolio, execution, quant_data, cerebro). |
| **Dashboard** | `dashboard/` | Monitoring + control app (FastAPI backend + Dash frontend). |
| **Book notes** | `book_notes/` | Reading / learning material (playground studies, papers). |

Data is **not** a separate top-level component today — it spans `core/` (the FRED/yfinance
market-data platform and Parquet store) and `alpha_research/quant_data/` (vendor connectors,
DuckDB research lake). It is the weakest link: connectors exist (Stooq, Polygon, Binance, ECB
FX, yfinance/FRED) but there is **no paid data subscription yet**, so coverage and depth are
limited. Treating data as a first-class component — with a clean contract into research — is a
prerequisite for everything downstream.

## Constraints & success criteria

The fixed inputs the plan is sequenced against (confirmed 2026-06-12):

| Input | Value | Implication |
|-------|-------|-------------|
| **Capital band** | $25k–$100k | Sweet spot for a multi-strat micro-futures CTA + cross-sectional equity + ETF book. Use **micro futures** (MES, MNQ, MYM, M2K, MCL, MGC) for diversification; full-size only in the most liquid contracts at the top of the range. |
| **IBKR permissions** | Futures + margin enabled | All three tracks unblocked: CTA on futures, equity L/S with shorting, ETF. No application gate. |
| **Data budget** | $0 in Phase I; ~$78/mo (Norgate) before the CTA track; hard ceiling ~$150/mo | Build the harness on free equity/ETF/macro data; buy roll-adjusted continuous futures + survivorship-bias-free equity universe only when the CTA track starts. |
| **Time / operating** | ~8–15 hrs/wk, milestone-gated (not calendar), agent team amplifies, solo go/no-go | Each phase ships a usable increment; no big-bang. Researcher is the bottleneck on review and promotion decisions. |

**Definition of "fully fledged":**

- **~4–5 live strategies, pairwise low-correlation** — not per class. Target mix: 1–2 CTA (trend + carry/momentum on futures), 1–2 equity (cross-sectional factor tilt or L/S), 1 ETF tactical/macro rotation.
- **Net targets:** per-strategy Sharpe **0.4–0.8**, blended portfolio **0.8–1.2** (net of costs — anything above ~1.5 net for retail systematic is treated as a red flag for overfitting).
- **Risk budget:** ~**10% annualized portfolio vol**, designed for **15–20% expected max drawdown**, survivable to 25–30%. This is the target the optimizer (capability #4) manages to.
- **Promotion bar:** production-quality **paper platform that can go live**; real capital is gated behind a **3–6 month forward paper-trading record** (uses existing forward-pass tracking as the gate).

## Asset-class tracks

The three classes share the harness (R1–R3) but differ where execution lives. The plan forks
research by track:

| Track | Signal family | Data need | Tradability @ $25–100k | Repo support today |
|-------|---------------|-----------|------------------------|--------------------|
| **CTA** | Cross-asset trend following + time-series momentum / carry on futures | **Roll-adjusted continuous futures** (the long pole — needs Norgate or equivalent); macro via FRED | Micro futures (MES/MNQ/MYM/M2K/MCL/MGC) give diversification at this size; full-size only in ES/CL at top of range | Engines + stats exist; **no futures data, no roll/cost model for futures** — the main build |
| **Equity** | Cross-sectional factors (momentum, value, low-vol), L/S or long-tilt | Survivorship-bias-free universe (Norgate); fundamentals optional later | L/S enabled (margin + shorting on); start US large-cap, ~100+ names | `strategies/signals.py`, cross-sectional momentum proposal already drafted; needs clean universe |
| **ETF** | Tactical asset allocation / macro rotation across liquid ETFs | Free daily OHLCV (yfinance/Stooq) + FRED macro — **fully covered free** | Works at any size; lowest-friction track to ship first | Data fully available; signal/rotation logic to build |

**Sequencing implication:** the **ETF track is the cheapest to ship first** (free data, no
permissions gate, simplest costs) — it's the ideal vehicle to prove the end-to-end Phase I loop.
**CTA is gated on the Norgate purchase** and a futures roll/cost model, so it comes after the
harness is validated. Equity sits in between.

## Target capabilities (full lifecycle)

Mapped against what the repo already supports, so the plan separates *build* from *have*:

| # | Capability | Status today | Where it lives / what's missing |
|---|------------|--------------|----------------------------------|
| 1 | **Ingest ideas** — read reports & academic papers to extract modelling techniques and investment ideas | Partial | `alpha_research/cerebro/` (arXiv/SSRN/blog discovery, scoring, proposals) + `book_notes/playground/`. Experimental; not wired into a reliable queue. |
| 2 | **Research** — turn an idea into a tradable expression; backtest & validate rigorously with strict anti-overfitting / anti-p-hacking discipline (AFML first-principles) | Have (strong) | `backtests/` engines + `backtests/stats/` (PSR, deflated Sharpe, CPCV, purged k-fold, MinBTL, White's reality check, FDR/Bonferroni, decay/capacity). v2 Challenge Loop (Cerebro→Researcher→PM) enforces rigor. |
| 3 | **Register & scale** — register strategies/experiments to a tracked **strategy pool** (MLflow-style) for paper-trading, production, and monitoring | Partial | `backtests/run_manager.py` (run tracking + git commit + metrics + artifacts), MLflow hooks (`/api/research/backtest/mlflow`), feature registry. No unified *strategy pool* with lifecycle states (candidate → paper → live → retired). |
| 4 | **Optimize** — construct portfolios under risk constraints (target vol, VaR, drawdown) | Have | `alpha_research/portfolio/` (cvxpy mean-variance, risk parity, Black-Litterman, min-var), `risk.py` / `risk_analytics.py` (Ledoit-Wolf, VaR/CVaR, stress). |
| 5 | **Execute** — alert via SMS now; auto-route IBKR orders later | Partial | `alpha_research/execution/` (runner, pre-trade risk, sim broker, IBKR broker, audit) + `notifications.py` (SMS/Slack/email). Wiring research → execution is manual. |
| 6 | **Monitor** — IBKR connection for returns & position monitoring | Have | `dashboard/` + `core/ibkr_client.py`, WebSocket live PnL/positions, attribution. |
| 7 | **Rebalance** — driven by PnL and active strategies | Partial | `portfolio/rebalancer.py` (drift threshold, intervals, dry-run). Not closed-loop with live PnL. |
| 8 | **Refine** — improve existing strategies based on realized PnL | To build | Forward-pass tracking + LLM attribution exist; no systematic refinement loop feeding research. |

## Current focus: the Research component

This is the right stage to invest in **now** — data is good enough to iterate, and we are
upstream of onboarding strategies to production. The research component has three sub-goals.

### R1 — Rigorous backtest infrastructure

Integrate a **proprietary + third-party** backtesting stack so every research idea is tested
the same disciplined way.

- **Have:** in-house engines (vectorized `builder.py`, `walkforward.py`, canonical
  `event_driven/backtest_engine.py`), cost/slippage models, and the full `stats/` suite.
- **Have:** Backtrader compatibility layer (`strategies/backtrader_compat.py`) as a
  cross-validation engine; QuantStats tear sheets and PyPortfolioOpt comparison via
  `backtests/reporting/review.py`.
- **To firm up:** a single `ReviewConfig`-driven entry point so *every* strategy runs the same
  battery (primary engine + ≥1 validation engine, cost sensitivity 1×–3×, parameter
  sensitivity ±20/40%, PSR/DSR/MinBTL gates) and emits a standard artifact set. The
  scaffolding exists in `reporting/review.py` and `run_manager.py` — the gap is making it the
  **mandatory, one-call** path rather than an optional one.

### R2 — Standard strategy registration contract

Every strategy/model accepted into the pool must return a fixed, machine-readable bundle:

1. **Model spec** — signal construction, universe, rebalancing, sizing, params (the structured
   half of today's `proposal.md` + `strategies/metadata.py`).
2. **Model documentation** — economic rationale, references, PM challenges, verdict
   (today's `research/strategies/<name>/proposal.md`).
3. **Strategy implementation** — the signal/runner code (`strategies/signals.py`,
   `backtests/runners/`).
4. **Backtest report directory** — standard metrics (already produced) that **updates easily**
   on re-run, keyed by `run_id` so results are reproducible and comparable.

> The pieces exist but are scattered across `research/strategies/`, `run_manager.py`, and the
> reporting layer. R2 is about **codifying one schema** (a "strategy manifest") that ties them
> together and is the unit of registration into the pool.

### R3 — On-the-fly strategy analytics

Given a registered strategy, the infrastructure should pick up its details and render
analysis/statistics to a dashboard for reference — no manual notebook step.

- **Have:** `dashboard/backend/api/research_routes.py` (feature registry, MLflow-backed
  backtest endpoint), and the Dash frontend.
- **To build:** a strategy-pool view that reads the R2 manifest + latest `run_id` artifacts and
  renders the standard tear sheet, rolling Sharpe/decay, regime-conditional stats, and pool
  lifecycle state on demand.

## Roadmap

Four milestone-gated phases (no calendar dates — each ships a usable increment and gates the
next). The asset-class order is **ETF → CTA → equity**, driven by cost and data readiness.

## Phase I — Reproducible research loop + a real strategy pool

**Theme: make the research loop reproducible and the strategy pool real.** (ETF track, free data.)

Scope (research-only; no production execution):

1. **Strategy manifest schema (R2).** Define one `strategy.yaml`/JSON contract covering spec,
   doc pointer, implementation entry point, and backtest-report directory. Build the reference
   strategy on the **ETF rotation track** — it runs on free data with no permissions gate, so it
   proves the loop end-to-end at zero cost before any data spend or the CTA build.
2. **One-call review pipeline (R1).** Wrap `ReviewConfig` + `run_manager` so a single command
   takes a manifest and produces the full rigor battery + standard artifacts, registered under a
   `run_id`.
3. **Strategy pool registry (R3, part 1).** A lightweight pool index (lifecycle states:
   `candidate → paper → live → retired`) backed by `run_manager` / MLflow, queryable via the
   research API.
4. **Pool dashboard (R3, part 2).** A read-only Dash view listing pooled strategies with their
   latest metrics and one-click tear sheet.

**Exit criteria:** one ETF strategy flows end-to-end — manifest → one-call review → pool entry →
dashboard tile — with reproducible `run_id`s and no manual notebook steps. Zero data spend.

## Phase II — Data foundation + multi-track research

**Theme: buy the data that unblocks CTA and equity, and stand up both tracks on the validated harness.**

Gated on Phase I (don't pay for data until the loop is proven). Scope:

1. **Acquire futures + clean equity data.** Subscribe to Norgate (~$78/mo); wire it into
   `alpha_research/quant_data/` as a connector → Parquet/DuckDB, alongside the existing free
   sources. Deliver **roll-adjusted continuous futures** and a **survivorship-bias-free equity
   universe**.
2. **Futures roll & cost model (the main CTA build).** Add a futures-aware cost/slippage model
   under `backtests/costs/` (contract specs, tick value, roll cost, commission) — the piece the
   repo lacks today. Without it, CTA backtests are not trustworthy.
3. **Stand up the CTA track.** Trend following + time-series momentum / carry on liquid futures
   (micro contracts: MES/MNQ/MYM/M2K/MCL/MGC). Register ≥1 CTA strategy via the Phase I manifest
   + one-call review pipeline.
4. **Stand up the equity track.** Cross-sectional factor strategy (the drafted
   `equity_momentum` proposal, now on a clean 100+ name universe). Register ≥1 equity strategy.

**Exit criteria:** ≥3 candidate strategies in the pool (ETF + CTA + equity), each with the full
rigor battery (PSR/DSR/MinBTL, cost & parameter sensitivity, ≥1 validation engine), and a
**pairwise-correlation matrix** computed across the pool.

## Phase III — Portfolio construction + paper deployment

**Theme: combine the pool into one risk-managed book and run it on paper.**

Gated on Phase II (need ≥2–3 low-correlation candidates worth combining). Scope:

1. **Pool → optimizer.** Wire the strategy pool into `alpha_research/portfolio/` to build a
   blended book under the risk budget: **~10% target vol**, VaR / max-drawdown constraints,
   turnover penalty. Compare allocators (risk parity vs mean-variance vs min-var).
2. **Paper deployment path.** Connect optimizer output → `alpha_research/execution/` runner →
   IBKR **paper** account (port 7497) with pre-trade risk checks and the order audit trail.
3. **Forward-pass on every position.** Record signal context at entry (existing forward-pass
   infra) so the paper record is later comparable to realized PnL.
4. **Closed-loop rebalancer.** Drive `portfolio/rebalancer.py` from live paper PnL + drift
   thresholds.

**Exit criteria:** a blended multi-strat **paper portfolio running live on IBKR paper**,
forward-tracked, managed to the ~10% vol budget — and the **3–6 month promotion clock started**.

## Phase IV — Monitoring, go-live, and the refinement loop

**Theme: close the lifecycle — monitor the book, promote what works to real capital, feed PnL back into research.**

Gated on a paper track record from Phase III. Scope:

1. **Monitoring dashboard.** Extend `dashboard/` for the live/paper book: returns, per-strategy
   attribution, realized vs design vol/drawdown, regime flags.
2. **Promotion gate.** Strategies that clear the rigor gates **and** the 3–6 month paper record
   get promoted `candidate → paper → live`; size live positions to the risk budget. Real capital
   deployed on promoted strategies only.
3. **Refinement loop (capability #8).** Realized PnL + LLM attribution feed back into research:
   degraded strategies are flagged, re-researched, or retired; the loop reopens at Phase II for
   the next idea.

**Exit criteria:** the full lifecycle closes — **Data → Research → Deploy → Monitor → (back to)
Research** — with at least the first strategy promoted to live capital and a documented
feedback path for refinement.

## Open decisions (cross-cutting)

Genuine design calls, not gaps — decide as Phase I forces the question:

- **Strategy pool store:** extend `run_manager`'s on-disk format, lean fully on MLflow, or both?
- **Manifest source of truth:** the manifest as canonical vs. generated from `metadata.py` +
  `proposal.md`?
- **Promotion thresholds:** which `stats/` gates (DSR > ?, PSR > ?, MinBTL satisfied?) are
  required for `candidate → paper`, and what paper-record bar for `paper → live`?
- **Futures cost model fidelity:** per-contract specs vs. a simplified tick/commission
  approximation for Phase II — how much precision before it's good enough?
