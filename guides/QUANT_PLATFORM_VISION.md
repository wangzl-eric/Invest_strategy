# The Optimal Quant Research Platform & Market Monitoring Stack

**A Macro Portfolio Manager's Blueprint**

*Last updated: February 2026*

---

## Preface

This document captures my working thesis on what the ideal quantitative research platform and market monitoring infrastructure looks like for a discretionary-systematic macro book. The goal is not a fully automated black box — it is a decision-support system that amplifies a PM's edge by compressing the time between signal, analysis, and action.

Every design choice below reflects a single principle: **reduce latency between the world changing and you understanding why it changed, what it implies, and what to do about it.**

---

## Table of Contents

- [I. Design Philosophy](#i-design-philosophy)
- [II. Market Monitoring Layer](#ii-market-monitoring-layer)
- [III. Quant Research Platform](#iii-quant-research-platform)
- [IV. Risk & Portfolio Construction](#iv-risk--portfolio-construction)
- [V. Execution Intelligence](#v-execution-intelligence)
- [VI. Data Architecture](#vi-data-architecture)
- [VII. Alerting & Notification](#vii-alerting--notification)
- [VIII. Technology Choices & Trade-offs](#viii-technology-choices--trade-offs)
- [IX. What Exists Today vs. Target State](#ix-what-exists-today-vs-target-state)
- [X. Sequencing & Priorities](#x-sequencing--priorities)

---

## I. Design Philosophy

### Core Tenets

1. **Cross-asset by default.** Macro means rates, FX, equities, credit, commodities, and vol — simultaneously. Every screen, every model, every alert must be multi-asset natively, not bolted on.

2. **Opinion-aware, not opinion-free.** The platform should encode your views (Black-Litterman priors, regime labels, directional biases) and show you where reality is confirming or diverging from those views. A neutral dashboard is useless to a PM with conviction.

3. **Research and production are the same code path.** The notebook where you discover an edge and the system that monitors it in production should share the same data layer, the same feature definitions, the same risk calculations. Drift between research and production is where alpha dies.

4. **Latency tiering.** Not everything needs to be real-time. Economic regime detection can run daily. Intraday momentum signals need sub-minute. PnL monitoring needs second-level. Central bank speech parsing needs minutes. Design each pipeline for the latency it actually requires — over-engineering latency burns money.

5. **Auditability.** Every trade thesis, signal, override, and risk exception should be logged with timestamps and attribution. When you're explaining a drawdown to yourself (or your investors), the system should be your memory.

---

## II. Market Monitoring Layer

This is the nerve center. The goal is a single-screen (or two-screen) view that tells you the "state of the world" within 10 seconds of sitting down.

### A. Cross-Asset Dashboard

The primary monitoring surface should display:

| Panel | Content | Refresh |
|-------|---------|---------|
| **Rates** | UST 2Y/5Y/10Y/30Y yields, 2s10s/5s30s spreads, SOFR/FF, real yields (TIPS breakevens), swap spreads | Real-time |
| **FX** | DXY, G10 spot + 1D change, EM barometer (EMFX index), vol (1M ATM), risk reversals on key pairs | Real-time |
| **Equities** | S&P 500, NDX, RTY, STOXX 600, Nikkei, CSI 300, sector performance heatmap, VIX term structure | Real-time |
| **Credit** | IG/HY CDX, iTraxx, IG/HY spread to worst, fallen angel watch | 15-min |
| **Commodities** | Crude (WTI/Brent), Nat Gas, Gold, Copper, Ags index, term structure (contango/backwardation) | Real-time |
| **Macro Pulse** | Today's data releases + surprise index, Citi EASI, Fed/ECB/BOJ implied policy paths, geopolitical risk index | Event-driven |

### B. The "What Changed" Feed

Most dashboards show levels. Levels are not actionable — changes are. The system should prominently surface:

- **Cross-asset movers**: anything that moved >1.5 sigma vs. its 20-day realized vol, ranked by z-score
- **Correlation breaks**: pairs that historically co-move but are diverging today (e.g., USD/JPY moving without a rates move)
- **Curve regime shifts**: yield curve steepening/flattening beyond recent range, credit curve inversion
- **Flow signals**: unusual ETF flows, futures OI changes, options skew shifts

### C. Central Bank & Policy Monitor

For a macro book this is arguably the most important layer:

- **Meeting countdown timers** for Fed, ECB, BOJ, BOE, RBA, PBOC with current market-implied probabilities (from OIS/FF futures)
- **Dot plot tracker** — current vs. last meeting, with market pricing overlaid
- **Speech/minutes NLP digest** — automated extraction of hawkish/dovish scoring from FOMC minutes, Fedspeak, ECB commentary. Not full NLP sentiment — just a structured summary: who spoke, key phrases, deviation from prior guidance
- **Policy rule dashboard** — Taylor rule variants, r-star estimates, financial conditions indices (Goldman FCI, Bloomberg FCI, Chicago Fed NFCI)

### D. Positioning & Sentiment

- **CFTC Commitments of Traders**: net spec positioning in major futures, percentile rank vs. 3Y history
- **Options market**: put/call ratios, skew indices, VIX term structure slope, MOVE index
- **Fund flow data**: EPFR-style equity/bond fund flows, money market fund balances
- **Survey data**: AAII, Investors Intelligence, Fund Manager Survey (BofA)

---

## III. Quant Research Platform

### A. Signal Research Workflow

The ideal research loop:

```
Hypothesis → Data Pull → Feature Engineering → Backtest → Statistical Validation → Production Signal
    ↑                                                                                      |
    └──────────────────── Performance Monitoring ← ─────────────────────────────────────────┘
```

Each step should live in a reproducible, versioned environment. Concretely:

1. **Hypothesis notebook**: Jupyter/Lab with DuckDB for fast SQL over Parquet, `pandas`/`polars` for transforms. The notebook should pull from the canonical data lake, not ad-hoc CSV downloads.

2. **Feature registry**: A shared definitions file where every derived feature (e.g., "12-1 momentum", "real yield spread", "credit impulse") is defined once, with its computation logic, data dependencies, and lookback windows. This is the single source of truth.

3. **Backtesting**: Two tiers:
   - **Vectorized** (fast iteration): for signal-level research where you need to test hundreds of parameter combos quickly. Acceptable to ignore transaction costs at first pass.
   - **Event-driven** (realistic): for final validation with fills, slippage, margin, and rebalancing logic. Run this on the 3-5 surviving signals from vectorized screening.

4. **Statistical rigor**: Every backtest should automatically output:
   - Sharpe, Sortino, Calmar, max drawdown, drawdown duration
   - Deflated Sharpe ratio (accounting for multiple testing)
   - Rolling performance windows (is the signal decaying?)
   - Regime-conditional performance (does it work in both risk-on and risk-off?)
   - Turnover and capacity estimates

5. **Experiment tracking**: MLflow (or similar) to log every research run with parameters, metrics, and artifacts. Three months from now you need to answer "why did I reject that signal?" — the tracking system is the answer.

### B. Macro Factor Models

A macro PM's research platform must have first-class support for:

- **Cross-asset factor decomposition**: PCA on a cross-asset universe to extract the dominant risk factors (typically: growth, rates, inflation, risk appetite, USD). Label them economically, not just "PC1".
- **Macro regime classification**: Hidden Markov Models or threshold-based rules to classify the current environment (e.g., Goldilocks, Reflation, Stagflation, Deflation). Every signal and every portfolio should be tagged with regime-conditional behavior.
- **Leading indicator composites**: Custom leading indicator indices combining PMIs, yield curve, credit conditions, labor market, housing — tailored to the economies you trade.
- **Carry, momentum, value, and defensive factors** across all asset classes with consistent definitions and regular rebalancing.

### C. Alternative Data Integration

Not all alternative data is useful. For a macro book, the highest-value alternative datasets are:

| Dataset | Signal Type | Latency |
|---------|-------------|---------|
| Satellite/shipping (AIS) | Global trade activity, commodity flows | Weekly |
| Credit card / consumer spending | Consumption tracking for GDP nowcasting | Weekly |
| NLP on central bank text | Policy stance shifts before market prices them | Minutes |
| News sentiment indices | Geopolitical risk, policy uncertainty | Daily |
| Electricity / mobility data | Real-time economic activity proxies | Daily |
| Job postings / layoff trackers | Labor market leading indicators | Weekly |

The platform should make it trivial to ingest a new dataset, align it to the canonical time index, and correlate it with existing factors.

---

## IV. Risk & Portfolio Construction

### A. Risk Framework

Risk for a macro book is multi-dimensional. A single VaR number is necessary but wildly insufficient.

**Required risk views:**

1. **Factor risk decomposition**: What percentage of portfolio risk comes from duration, credit spread, FX, equity beta, commodity beta, vol? If 80% of your risk is duration and you think you're running a diversified macro book, the system should make that painfully obvious.

2. **Scenario analysis**: Pre-defined and custom scenarios:
   - Historical: Taper Tantrum, COVID March 2020, SVB/regional bank stress, BOJ YCC exit, Trump tariffs
   - Hypothetical: +100bp parallel shift, USD +5%, oil +30%, EM crisis
   - Reverse stress test: "what scenario would cause a -5% portfolio drawdown?"

3. **Correlation regime risk**: Correlations are unstable. The system should show current realized correlation vs. long-term average, and flag when portfolio diversification assumptions are breaking down.

4. **Liquidity risk**: Estimated days-to-liquidate by position, market impact cost at various urgency levels. Illiquid positions should be penalized in optimization.

5. **Gross/net exposure tracking**: by asset class, geography, factor, and theme — with limits and breach alerts.

### B. Portfolio Construction

The optimization engine should support:

- **Mean-variance** (Markowitz) with robust covariance estimators (Ledoit-Wolf shrinkage, DCC-GARCH for time-varying correlations)
- **Black-Litterman** for blending market equilibrium with PM views — this is the most natural framework for a discretionary-systematic PM
- **Risk parity** and hierarchical risk parity (HRP) for the structural allocation layer
- **Regime-conditional allocation**: different target portfolios for different macro regimes, with smooth transitions
- **Constraint-aware optimization**: max position size, sector limits, turnover constraints, tracking error bounds, ESG exclusions

The optimizer should run nightly and present recommendations, but the PM always has final override. Every override should be logged.

### C. PnL Attribution

Daily PnL should be decomposed into:

- **Asset-level contribution**: which positions made/lost money
- **Factor contribution**: how much came from duration, credit, FX, equity, commodity, idiosyncratic
- **Decision attribution**: how much came from strategic allocation vs. tactical tilts vs. position sizing vs. timing
- **Benchmark-relative**: active return decomposition (if running against a benchmark)

---

## V. Execution Intelligence

### A. Pre-Trade Analytics

Before entering a trade, the system should provide:

- Expected market impact (using models like Almgren-Chriss or simpler heuristics for liquid markets)
- Optimal execution window (avoid illiquid periods, consider time zone overlaps for FX)
- Historical fill quality for the instrument
- Margin impact and what-if on portfolio risk

### B. Post-Trade Analysis

Transaction cost analysis (TCA) is not optional:

- Slippage vs. arrival price, VWAP, TWAP benchmarks
- Execution timing analysis — did we trade at the optimal time?
- Broker comparison (if using multiple execution venues)
- Monthly TCA summary with trends

### C. Order Management

For a macro book that trades across asset classes:

- Unified order blotter across rates, FX, equity, and commodity futures
- Staged orders: research → pre-trade risk check → PM approval → execution
- Netting across related positions (e.g., if you're adding duration via futures and bonds simultaneously)

---

## VI. Data Architecture

### A. Guiding Principles

1. **Parquet as the canonical format** for all time-series data. Column-oriented, compressed, portable, fast.
2. **DuckDB for interactive queries**. SQL over Parquet without ETL overhead. This has been a game-changer for research velocity.
3. **PostgreSQL + TimescaleDB for production state**. Positions, trades, alerts, audit logs — anything transactional goes here.
4. **Redis for ephemeral state**. Session caches, rate limits, real-time price buffers.
5. **No vendor lock-in on market data**. Abstract the data provider behind a clean interface. Today it's Polygon + Yahoo Finance; tomorrow it might be Databento or LSEG. Swap without rewriting research code.

### B. Data Taxonomy

```
data_lake/
├── market_data/
│   ├── equities/          # OHLCV, adjusted closes, corporate actions
│   ├── fixed_income/      # Yields, spreads, curves, total returns
│   ├── fx/                # Spot, forward points, vol surfaces
│   ├── commodities/       # Futures, spot, term structure
│   └── volatility/        # VIX, MOVE, implied vol surfaces
├── macro/
│   ├── economic_releases/ # GDP, CPI, NFP, PMI — with surprise component
│   ├── central_banks/     # Statements, minutes, dot plots, speeches
│   ├── financial_conditions/ # FCI indices, credit spreads, TED spread
│   └── positioning/       # COT, fund flows, options OI
├── alternative/
│   ├── news_sentiment/
│   ├── satellite/
│   └── consumer/
└── portfolio/
    ├── holdings/          # Daily snapshots
    ├── transactions/      # Trade log
    ├── pnl/               # Daily PnL with attribution
    └── risk/              # VaR, factor exposures, scenario results
```

### C. Data Quality

Garbage in, garbage out. The platform must enforce:

- **Schema validation** (pandera / Great Expectations) on every ingestion
- **Staleness detection**: alert if a data feed hasn't updated within expected SLA
- **Corporate action handling**: adjusted vs. unadjusted prices, split/dividend awareness
- **Point-in-time correctness**: research must use data-as-known-at-the-time, not revised data. This is the most common source of backtest overfitting.

---

## VII. Alerting & Notification

Alerts should be tiered by severity and channel:

| Severity | Examples | Channel |
|----------|----------|---------|
| **Critical** | Drawdown >2% daily, risk limit breach, data feed failure, margin call | SMS + Phone + Slack |
| **High** | Position P&L >1 sigma, correlation regime shift, new Fed statement | Push + Slack |
| **Medium** | Economic data surprise >1 sigma, COT positioning extreme, signal entry/exit | Slack + Email |
| **Low** | Overnight market recap, weekly risk report ready, backtest completed | Email digest |

### Smart Alert Principles

- **No alert fatigue**: if an alert fires every day, it's useless. Use adaptive thresholds that account for current vol regime.
- **Context-rich**: an alert that says "SPX down 2%" is noise. An alert that says "SPX -2%, largest move since Oct 2023, driven by tech sector, VIX +5 vols to 22, credit spreads widening 15bp, no obvious catalyst in news feed" is useful.
- **Actionable**: pair every alert with a suggested action or at minimum a link to the relevant dashboard/analysis.

---

## VIII. Technology Choices & Trade-offs

### What We Got Right

- **FastAPI + Plotly Dash**: lightweight, Python-native, fast to iterate on. For a 1-3 person team, this beats building a React frontend by a wide margin.
- **DuckDB + Parquet data lake**: research velocity is 10x what it would be with a traditional database. SQL over files is the right paradigm for quantitative research.
- **ib_insync for IBKR**: mature, well-maintained, async-capable. The right choice for an IBKR-centric workflow.
- **SQLAlchemy ORM**: clean separation of data models from business logic. Makes it easy to swap databases.
- **MLflow for experiment tracking**: low overhead, self-hosted, integrates with the existing Python stack.

### What Needs Improvement

- **Real-time data pipeline**: currently polling-based. For intraday macro trading, we need a proper streaming layer (WebSocket → Redis pub/sub → dashboard). Not Kafka — that's over-engineered for our scale. Redis Streams or a lightweight message broker is sufficient.
- **Multi-asset data normalization**: each asset class currently has slightly different schemas. Need a canonical `TimeSeriesBar` schema that works for equities, bonds, FX, and commodities with asset-class-specific extensions.
- **Central bank / macro event processing**: this is currently manual. Automating the ingestion and parsing of Fed communications, economic releases, and geopolitical events would be the highest-ROI improvement.
- **Mobile access**: a PM needs to check the book from their phone. A lightweight mobile-friendly dashboard or Telegram bot for key metrics would be valuable.

### Technology I Would Not Add

- **Kafka / Spark**: we are not a hedge fund with 500 signals and 10TB of tick data. These add operational complexity without proportional benefit at our scale.
- **Kubernetes**: Docker Compose on a single server (or 2-3 for redundancy) is sufficient. K8s is for when you have a platform team, not a PM who also codes.
- **Custom C++ execution engine**: we trade macro with holding periods of days to weeks. Microsecond latency is irrelevant. Python with proper async is fine.
- **LLM-powered trading signals**: LLMs are useful for text processing (central bank speeches, news), but they are not a replacement for well-defined quantitative signals. Use them as a feature input, not a decision-maker.

---

## IX. What Exists Today vs. Target State

| Capability | Current State | Target State | Priority |
|-----------|--------------|-------------|----------|
| IBKR data ingestion | Flex Query + live TWS | ✅ Sufficient | — |
| Cross-asset dashboard | ✅ Multi-asset: rates, FX, equities, commodities, curves, Fed QE/QT monitor, macro pulse | ✅ Delivered | — |
| Historical sparklines | ✅ 30-day sparklines + 1W/1M change columns on all market panels, click-to-expand 1Y chart | ✅ Delivered | — |
| Market data lake | ✅ Parquet-based storage (yfinance OHLCV + FRED series), catalog.json, incremental updates | Production DuckDB query layer | **P1** |
| Data Manager UI | ✅ Data tab with catalog browser, pull form, data viewer/chart | Full data lineage + scheduling | **P2** |
| Central bank monitor | Fed QE/QT monitor + CB meeting tracker (FOMC countdown, policy rates, 2Y-FF implied path proxy) | Automated CB speech/minutes parsing + CME FedWatch probabilities | **P0** |
| Economic data integration | FRED macro indicators (CPI, GDP, NFCI, HY OAS) | Full economic calendar with surprise tracking | **P0** |
| Factor risk decomposition | Basic (equity factors) | Cross-asset macro factor model | **P1** |
| Regime detection | ML prototype | Production HMM with live classification | **P1** |
| Black-Litterman optimizer | Implemented | Add regime-conditional views + constraint UI | **P1** |
| PnL attribution | Asset-level | Factor-level + decision attribution | **P1** |
| Scenario analysis | Basic stress test | Historical + hypothetical + reverse stress | **P2** |
| Positioning data (COT) | None | Automated weekly ingestion + percentile dashboard | **P2** |
| NLP on central bank text | None | Hawkish/dovish scorer + summary extraction | **P2** |
| TCA | None | Post-trade slippage analysis | **P3** |
| Mobile dashboard | None | Responsive Dash or Telegram bot | **P3** |
| Alternative data pipeline | None | Modular ingestion framework | **P3** |

---

## X. Sequencing & Priorities

### Phase 1: Foundation (Q1 2026)

Get the monitoring right. A macro PM who can't see the full market is flying blind.

- [x] Extend the Dash dashboard to display rates, FX, and commodity panels alongside equities
- [x] Integrate a cross-asset "what changed" z-score ranker
- [x] Set up economic calendar integration (FRED API — CPI, GDP, NFCI, HY OAS, unemployment)
- [x] Build Fed QE/QT monitor (balance sheet, RRP, reserves, TGA, net liquidity)
- [x] Add yield curve, forward rates, and real yield (TIPS) charting
- [x] Add 30-day sparklines, 1W/1M change columns, and click-to-expand historical charts
- [x] Build Parquet data lake for persistent market data storage with Data Manager UI
- [x] Build central bank meeting tracker with OIS-implied rate paths

### Phase 2: Research Depth (Q2 2026)

Build the analytical toolkit that turns observations into trades.

- [ ] Implement canonical cross-asset factor model (PCA + economic labeling)
- [ ] Deploy production regime classifier (HMM on growth/inflation proxies)
- [ ] Build factor-level PnL attribution pipeline
- [ ] Create feature registry with shared signal definitions
- [ ] Enhance Black-Litterman with regime-conditional view blending

### Phase 3: Intelligence (Q3 2026)

Layer on the automated intelligence that makes the system proactive.

- [ ] NLP pipeline for Fed/ECB communications (hawkish/dovish scoring)
- [ ] CFTC COT data ingestion + positioning extremes dashboard
- [ ] Scenario analysis engine (historical replay + hypothetical)
- [ ] Context-rich alert system (alerts with market context, not just levels)

### Phase 4: Polish (Q4 2026)

Production hardening and quality of life.

- [ ] TCA module for post-trade analysis
- [ ] Mobile-friendly monitoring interface
- [ ] Alternative data ingestion framework
- [ ] Portfolio rebalancing workflow (optimizer → risk check → staged execution)
- [ ] Comprehensive backtesting of the full signal suite with deflated Sharpe

---

## Closing Thought

The best quant platform is not the one with the most features — it is the one you actually use every day. Every component described here should earn its place by making you faster, more informed, or more disciplined. If a module doesn't change how you trade, it's technical debt masquerading as infrastructure.

Build what you need. Measure whether it helps. Iterate.
