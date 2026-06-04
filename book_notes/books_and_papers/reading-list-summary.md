# Reading List — Tier Summary & Project Value

## How the List is Structured
- **Tiers = sequence** (start at Tier 0 and climb)
- **Modules** group by discipline
- **Core → Depth → References** within each module

---

## Tier 0 — Orientation & Macro Mindset
**Purpose:** Build intuition for how global macro drives asset prices and risk.
**Key books:** Ilmanen *Expected Returns*, Pedersen *Efficiently Inefficient*, Harvey/Rattray/Van Hemert *Strategic Risk Management*
**Value to project:** Foundation for the signal research and strategy selection in `research/strategies/`. Ilmanen and Harvey directly inform the risk-adjusted return framework, position sizing philosophy, and the `backtests/stats/` statistical rigor module. Pedersen's framework maps to the cross-sectional momentum and carry strategies already in `research/STRATEGY_TRACKER.md`.

---

## Tier 1 — Macro Economics & Policy Backbone
**Purpose:** Understand central bank mechanics, fiscal cycles, inflation regimes, and geopolitical structural forces.
**Key books:** Bernanke *21st Century Monetary Policy*, Wang *Central Banking 101*, Reinhart/Rogoff *This Time Is Different*, Dalio *Changing World Order*
**Value to project:** Powers the macro regime detection layer — directly relevant to the `RegimeAnalyzer` in `backtests/` and the Vol-Scaled Momentum strategy (Priority 1 in `STRATEGY_TRACKER.md`). FRED data series in `backend/market_data_service.py` and `quant_data/connectors/` draw directly from these macro frameworks.

---

## Tier 2 — Time Series, Econometrics & Forecasting
**Purpose:** Rigorous statistical modeling of financial time series: stationarity, cointegration, ARIMA, state space models, forecasting.
**Key books:** Hamilton *Time Series Analysis*, Tsay *Analysis of Financial Time Series*, Durbin/Koopman *State Space Methods*, Hyndman *Forecasting Principles and Practice*
**Value to project:** Direct technical foundation for `research/features.py`, `backtests/strategies/signals.py`, and the signal generation pipeline. Walk-forward analysis in `backtests/walkforward.py` is grounded in these methods. Critical for avoiding spurious regressions in factor research.

---

## Tier 3 — Probability, Statistics & Causal Thinking
**Purpose:** Rigorous probability theory, Bayesian inference, causal reasoning, and high-dimensional statistics.
**Key books:** Wasserman *All of Statistics*, Gelman *Bayesian Data Analysis*, Peters/Janzing/Schölkopf *Elements of Causal Inference*
**Value to project:** Underpins the `backtests/stats/` module — especially `sharpe_tests.py` (PSR, Deflated Sharpe), `multiple_testing.py` (BH-FDR, White's Reality Check), and `cross_validation.py` (CPCV). Causal inference is critical for distinguishing genuine alpha from data-mining artifacts in the Cerebro pipeline.

---

## Tier 4 — Machine Learning
**Purpose:** Full ML toolkit from classical methods through deep learning, with finance-specific applications.
**Key books:** López de Prado *Advances in Financial Machine Learning* + *ML for Asset Managers*, Hastie/Tibshirani/Friedman *Elements of Statistical Learning*, Jansen *ML for Algorithmic Trading*, Coqueret *ML for Factor Investing*
**Value to project:** Directly feeds the Cerebro `cerebro/scoring/` relevance/quality scoring, `backtests/strategies/auto_signals/` LLM-generated signals, and the `backend/llm_verdict.py` module. López de Prado is the primary reference for `backtests/stats/minimum_backtest.py` (MinBTL) and purged cross-validation. This is the highest-leverage tier for the current platform.

---

## Tier 5 — Optimization & Numerical Methods
**Purpose:** Convex optimization theory, numerical methods, robust optimization, and linear algebra fundamentals.
**Key books:** Boyd *Convex Optimization*, Nocedal/Wright *Numerical Optimization*, Ben-Tal/Nemirovski *Robust Optimization*, MOSEK *Portfolio Cookbook*
**Value to project:** Direct foundation for `portfolio/optimizer.py` (CVXPY mean-variance and risk parity). The MOSEK Portfolio Cookbook is especially practical — maps 1:1 to the optimization formulations in the codebase. Robust optimization (Ben-Tal) is relevant for improving the optimizer under estimation error.

---

## Tier 6 — Asset Class Modules
**Purpose:** Deep practitioner knowledge of Rates, FX, Commodities, Equity/CTA, and Credit instruments.

| Sub-module | Key Book | Project Relevance |
|---|---|---|
| **Rates & Inflation** | Tuckman *Fixed Income Securities* | FRED rate data, yield curve regime signals |
| **FX & Cross-Currency** | Weithers *Foreign Exchange*, Wystup *FX Options* | FX Carry + Momentum strategy (Priority 2) |
| **Commodities** | Bouchouev *Virtual Barrels*, Clenow *Following the Trend* | Commodity momentum (rejected — no futures infra yet) |
| **Equity/CTA** | Clenow *Following the Trend*, Greyserman/Kaminski *Trend Following*, Ang *Asset Management* | Cross-sectional and Vol-Scaled Momentum strategies |
| **Credit** | Dor et al. *Systematic Investing in Credit* | Future expansion |

**Value to project:** The equity/CTA and FX modules are immediately actionable for the 4 conditional strategies in `STRATEGY_TRACKER.md`.

---

## Tier 7 — Derivatives, Volatility & Microstructure
**Purpose:** Options pricing, volatility surface modeling, and market microstructure/execution science.
**Key books:** Gatheral *The Volatility Surface*, Natenberg *Option Volatility and Pricing*, Harris *Trading and Exchanges*, Bouchaud et al. *Trades, Quotes and Prices*
**Value to project:** Microstructure knowledge directly improves `execution/sim_broker.py` and the `backtests/costs/` market impact models. Volatility books support the Vol-Scaled Momentum strategy's position sizing. Relevant to the `backend/market_data_service.py` VIX/volatility data.

---

## Tier 8 — Portfolio Construction, Risk & Attribution
**Purpose:** Systematic portfolio construction, risk budgeting, factor exposure management, and performance attribution.
**Key books:** Meucci *Risk and Asset Allocation*, Grinold/Kahn *Active Portfolio Management*, Scherer *Portfolio Construction and Risk Budgeting*, Paleologo *Advanced Portfolio Management*
**Value to project:** Core reference tier for `portfolio/optimizer.py`, `portfolio/risk_analytics.py`, `portfolio/rebalancer.py`, and `backend/attribution_engine.py`. Grinold/Kahn's IC-IR-BR framework should inform signal evaluation in `research/strategies/`. Meucci's full probability approach is the theoretical foundation for the entire portfolio layer.

---

## Tier 9 — Systematic Trading
**Purpose:** End-to-end systematic strategy development — from alpha research through execution and live trading operations.
**Key books:** Chan *Algorithmic Trading*, Pardo *Evaluation and Optimization of Trading Strategies*, Carver *Systematic Trading*, Kakushadze *151 Trading Strategies*, Tulchinsky *Finding Alphas*
**Value to project:** The most directly operational tier. Pardo maps to walk-forward methodology in `backtests/walkforward.py`. Carver's position sizing approach is directly applicable to `execution/risk.py`. Chan is the foundational reference for the vectorized backtest engine in `backtests/builder.py`. Kakushadze feeds the Cerebro alpha discovery pipeline.

---

## Tier 10 — Data Engineering & Software
**Purpose:** Scalable data systems, software architecture, Python performance, and quantitative data pipelines.
**Key books:** Kleppmann *Designing Data-Intensive Applications*, Reis/Housley *Fundamentals of Data Engineering*, Ramalho *Fluent Python*, Gorelick *High Performance Python*
**Value to project:** Directly applicable to `quant_data/` architecture (DuckDB + Parquet), `backtests/parallel.py` (ProcessPoolExecutor), `backtests/cache.py` (Parquet-backed signal cache), and the overall FastAPI backend design. Kleppmann is the architectural reference for the time-series database decisions in `backend/timeseries_db.py`.

---

## Tier 11 — Math Foundations
**Purpose:** Deep mathematical foundations — measure theory, stochastic calculus, information theory, random matrices.
**Key books:** Karatzas/Shreve *Brownian Motion and Stochastic Calculus*, Øksendal *SDEs*, Cover/Thomas *Elements of Information Theory*, Tao *Random Matrix Theory*
**Value to project:** Long-term theoretical foundation. Immediately relevant: stochastic calculus for volatility modeling and SDE-based option pricing; information theory for feature selection in `research/features.py` (mutual information, entropy). Random matrix theory is the theoretical basis for the covariance cleaning technique referenced in `backtests/stats/`.

---

## Priority Recommendation for This Project

| Priority | Tier | Reason |
|---|---|---|
| **Immediate** | T4 (ML), T8 (Portfolio), T9 (Systematic) | Active development areas |
| **Next 30 days** | T2 (Time Series), T3 (Stats), T5 (Optimization) | Underpins backtesting rigor |
| **Next 90 days** | T0 (Macro Mindset), T6-FX/Equity, T7 (Vol/Micro) | Strategy expansion |
| **Long-term** | T1 (Macro Econ), T11 (Math), T10 (Data Eng) | Deepening foundations |

> **Single highest-ROI book for this project right now:**
> **López de Prado — *Advances in Financial Machine Learning***
> It directly addresses the look-ahead bias, multiple testing, and walk-forward methodology that are the critical blocking issues identified in `research/framework_audit/backtesting_audit.md`.
