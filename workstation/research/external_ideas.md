# External Research Ideas — Quant Finance

*Compiled: 2026-03-13*

---

## 1. Kaggle Competition Insights

### 1.1 Jane Street Market Prediction — 1st Place (Supervised Autoencoder + MLP)

**Source:** [Yirun's 1st Place Writeup](https://www.kaggle.com/competitions/jane-street-market-prediction/writeups/cats-trading-yirun-s-solution-1st-place-training-s)

**Architecture:**
- **Step 1:** Train a Supervised Autoencoder — the autoencoder learns compressed representations of 130 anonymized features while simultaneously predicting the target (binary trade/no-trade)
- **Step 2:** Lock the encoder weights and feed the encoded representation into an MLP for final prediction
- Optimizer: Adam (lr=0.005), MSE loss for reconstruction + BCE for label
- Skip connections in the MLP's first layer
- Median ensembling across folds for robustness

**Key Takeaways for Us:**
- Autoencoders for denoising financial features before signal generation — could apply to our factor zoo
- Supervised training objective forces the latent space to be predictive, not just reconstructive
- High dropout rates (0.35–0.45 increasing by layer) were critical for regularization
- Mixup augmentation (blending data points) helped fill sparse regions of feature space

**Applicability:** Feature extraction pipeline for cross-sectional signals. Could denoise our factor inputs before feeding into momentum/value models.

---

### 1.2 Mitsui Commodity Prediction Challenge — 3rd Place (Directional Trends over Volatility)

**Source:** [3rd Place Writeup](https://www.kaggle.com/competitions/mitsui-commodity-prediction-challenge/writeups/3-rd-place-solution-directional-trends-over-vola)

**Competition Setup:**
- Predict commodity prices (LME metals, JPX, US stocks, FX) with both accuracy AND stability
- Metric: Sharpe-variant — mean Spearman correlation / std of correlation across time
- $100K prize pool

**Key Concept (from title):**
- "Directional Trends over Volatility" — suggests the winning approach emphasized trend-following signals normalized by volatility, which aligns directly with vol-scaled momentum (our Priority 1 strategy)
- Stability of predictions mattered as much as accuracy (Sharpe-based metric)

**Applicability:** Directly relevant to our vol-scaled momentum strategy. Validates the idea that trend signals / vol is a robust approach even in commodity markets.

---

### 1.3 Hull Tactical — Market Prediction (Ongoing, ends June 2026)

**Source:** [Hull Tactical Competition](https://www.kaggle.com/competitions/hull-tactical-market-prediction)

**Setup:**
- Predict S&P 500 excess returns while managing volatility
- Metric: Modified Sharpe ratio penalizing excess volatility
- Data: Public market data + Hull Tactical proprietary signals
- 16K+ entrants, $100K prize pool

**Key Insight:** Associated paper ["Micro Alphas"](https://www.kaggle.com/competitions/hull-tactical-market-prediction/discussion/614618) by Hull Tactical discusses combining many weak alpha signals — directly relevant to our signal blending framework.

**Action:** Monitor for solution writeups after June 2026.

---

### 1.4 Jane Street Real-Time Market Data Forecasting (2024-2025)

**Source:** [Competition Page](https://www.kaggle.com/competitions/jane-street-real-time-market-data-forecasting)

**Key Challenges:**
- Real-time inference (16ms per prediction)
- Non-stationary feature-target relationships
- Low signal-to-noise ratio with multicollinearity
- Different volatility regimes require different strategies

**Common Approaches:**
- Autoencoder + MLP (dominant architecture)
- Regime-aware models
- Feature engineering focused on rolling statistics and cross-asset correlations

---

## 2. Academic Papers — SSRN

### 2.1 CRITICAL: Bryan Kelly (Yale / AQR) — ML for Asset Pricing

**"Empirical Asset Pricing via Machine Learning"** (Gu, Kelly, Xiu)
- [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3159577) | 3,200+ citations
- Trees and neural networks outperform linear models for cross-sectional return prediction
- Nonlinear predictor interactions (missed by OLS) drive the gains
- **Key finding:** ML methods can double the Sharpe ratio vs. traditional regression-based strategies

**"Artificial Intelligence Asset Pricing Models"** (Kelly, Kuznetsov, Malamud, Xu, Jan 2025)
- [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5089371)
- Transformer-based stochastic discount factor
- Cross-asset information sharing via attention mechanism
- "Many factors" conjecture: returns driven by large number of factors, not a few

**"Financial Machine Learning"** (Kelly, Xiu, 2023) — 160-page survey
- [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4501707)
- Comprehensive survey bridging ML and finance

**"Factor Models, Machine Learning, and Asset Pricing"** (Giglio, Kelly, Xiu)
- [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3943284)
- Methodological review: estimating expected returns, factors, risk exposures, risk premia, SDF

### 2.2 Momentum Factor Research (2025)

**"Momentum Factor Investing: Evidence and Evolution"** (van Vliet, Baltussen, Dom, Vidojevic, Aug 2025)
- [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5561720)
- Comprehensive review of momentum factor empirical evidence

**"The Lazy Man's Momentum Strategy"** (Estrada, Oct 2025)
- [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5644131)
- Simplified momentum with long track record across countries and asset classes

**"Revisiting Factor Momentum: A One-month Lag Perspective"** (Rönkkö, Holmi, Jul 2025)
- [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5333744)
- Questions whether factor momentum profitability is driven by static tilt toward historically positive factors

**"Improvements to Intraday Momentum Strategies"** (Maróy, Jan 2025)
- [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349)
- Parameter optimization + exit strategies for intraday momentum

### 2.3 Advanced Factor Construction

**"Scaled Factor Portfolio"** (Jiang, Li, Ning, Xue, Aug 2025)
- [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5392547)
- Scale each factor by its Sharpe ratio, then extract PCA components
- Across 50 anomalies: **12–19% annual alpha, Sharpe ratios up to 2.0**
- Directly applicable to our multi-factor portfolio construction

**"Forest through the Trees: Building Cross-Sections of Stock Returns"** (Bryzgalova, Pelger, Zhu)
- [NUS Working Paper](https://fass.nus.edu.sg/ecs/wp-content/uploads/sites/4/2020/09/Forest-Through-the-Trees-Bryzgalova-Pelger-and-Zhu.pdf)
- Asset Pricing Trees (AP-Trees) capture nonlinear interactions in characteristics
- Up to 3x higher Sharpe ratios vs. conventional sorting
- Value effect strongest for small stocks; accruals show inverted U-shape for small/mid
- Regularized mean-variance optimization with trading friction constraints

### 2.4 FX Momentum Enhancement

**"FX Momentum"** (Liu, 2025 via QuantSeeker roundup)
- Double-sort currencies on 6-month returns AND higher-moment risks
- Avoiding skewed, crash-prone currencies improves returns and reduces drawdowns
- Relevant to our FX Carry + Momentum strategy (Priority 2)

---

## 3. Actionable Ideas Mapped to Our Strategy Pipeline

| Idea | Source | Maps To | Priority |
|------|--------|---------|----------|
| Vol-scaled trend signals | Mitsui 3rd place | Vol-Scaled Momentum | REJECTED |
| Autoencoder for feature denoising | Jane Street 1st place | Factor preprocessing | New |
| Sharpe-scaled PCA for factor combination | Jiang et al. 2025 | Multi-factor blending | P1 |
| Nonlinear factor interactions (trees/NN) | Kelly et al. | Signal generation | New |
| AP-Trees for portfolio sorting | Bryzgalova et al. | Portfolio construction | New |
| Higher-moment FX filtering | Liu 2025 | FX Carry strategy | P1 |
| Micro alphas blending | Hull Tactical | Signal blending framework | P1 |
| Regime-aware models | Jane Street RTMDF | All strategies | New |
| Mixup augmentation for training | Jane Street 1st | ML training pipeline | New |
| Quality + Safe-Haven Overlay | Goldman Sachs 2026 | Multi-asset regime strategy | P2 |

---

## 4. Reading List — Priority Order

1. **Gu, Kelly, Xiu — "Empirical Asset Pricing via ML"** (foundational, most cited)
2. **Jiang et al. — "Scaled Factor Portfolio"** (directly applicable to our factor pipeline)
3. **Bryzgalova et al. — "Forest through the Trees"** (nonlinear factor interactions)
4. **Kelly et al. — "AI Asset Pricing Models"** (transformer SDF, cutting edge)
5. **van Vliet et al. — "Momentum Factor Investing"** (momentum evidence review)
6. **Estrada — "Lazy Man's Momentum"** (simple, robust baseline)
7. **Rönkkö & Holmi — "Revisiting Factor Momentum"** (important critique)
8. **Liu — FX Momentum enhancement** (for FX Carry strategy)

---

## 5. Goldman Sachs Global Strategy Views (16 March 2026)

### 5.1 Defensive Sector Rotation
**Thesis:** Cyclicals now as expensive as Defensives (rare historically)
**Position:** Long Defensives (Utilities, Staples, Healthcare), Short/Underweight Cyclicals (Industrials, Materials)
**PM Assessment:** REJECTED — no sector classification data, requires $5K+/yr Norgate or 6mo valuation pipeline build
**Details:** See `research/goldman_sachs_strategy_assessment_2026-03-17.md`

### 5.2 HALO Factor (High Asset, Low Obsolescence)
**Thesis:** World under-invested in physical assets, AI capex driving demand
**Position:** Long physical assets, infrastructure, industrial capacity, power infrastructure
**PM Assessment:** REJECTED — no fundamental data pipeline, factor definition too vague
**Details:** See `research/goldman_sachs_strategy_assessment_2026-03-17.md`

### 5.3 Geographic Rotation
**Thesis:** "New economy" growth favors non-US, asset-heavy businesses
**Position:** Overweight Europe, Japan, EM; Underweight US
**PM Assessment:** REJECTED — no international equity data, IBKR account lacks intl permissions
**Details:** See `research/goldman_sachs_strategy_assessment_2026-03-17.md`

### 5.4 Quality + Safe-Haven Overlay
**Thesis:** High valuations + deteriorating macro + geopolitical risks
**Position:** Long Quality stocks + JPY/CHF as geopolitical hedge
**PM Assessment:** APPROVED for research (Priority 2) — feasible with ETF proxies
**Implementation (Revised after Codex audit):**
- 70% Quality (QUAL or 50/50 QUAL+USMV blend)
- 15% JPY (FXY ETF proxy)
- 15% CHF (FXF ETF proxy)
- Static allocation (no dynamic trigger in Phase 1)
- Rebalance: Monthly
**Assigned:** Elena
**Data Requirements:** QUAL, USMV, FXY, FXF, SPY (benchmark)

**Elena Assessment (2026-03-17):** Quality factor academically sound (Asness QMJ, FF5 RMW), expect 2-3% alpha post-crowding. JPY/CHF overlay enhances (negative crisis correlation), Oil dilutes (positive correlation). Recommended: 70% Quality + 15% JPY + 15% CHF, drop Oil. VIX > 20 trigger too coarse, refine to VIX > 25 + credit spread widening. ETF proxy acceptable for Phase 1, upgrade to fundamental construction in 6-12mo. Main risks: crowding (QUAL $20B AUM), short history (14yr, MinBTL borderline), position-sizing overlay may hurt Sharpe (Lesson L5). 4-week research plan: validate Quality → test overlay → dynamic triggers → full notebook.

**Codex Audit (2026-03-18, GPT-5.4):** REVISE before proceeding. Critical issues identified:
1. **Static vs dynamic confusion** — description says "triggered overlay" but implementation shows permanent 70/15/15 allocation. Resolved: use static allocation for Phase 1.
2. **HYG-LQD duration mismatch** (2.88y vs 8.00y) produces false signals during rate hikes. Resolved: use FRED OAS spread (BAMLH0A0HYM2 - BAMLC0A0CM) if dynamic trigger added in Phase 2.
3. **FX implementation unspecified** — spot, forwards, futures, or ETF? Resolved: use FXY/FXF ETF proxies for Phase 1.
4. **Gold excluded** — "optionally Gold" creates ambiguity. Resolved: exclude gold in Phase 1, test separately later.
5. **Oil dropped** — positive correlation (+0.4), not a safe-haven.
6. **Feasibility rating: 3/5** (research-feasible, not production-ready). Requires 4-week validation before PM Round 1.

**Status:** Awaiting revisions, then Cerebro literature briefing before Phase 1 research begins.

**Details:**
- `research/quality_safe_haven_assessment_2026-03-17.md` (Elena equity quant analysis, 470 lines)
- `research/quality_safe_haven_codex_audit_2026-03-18.md` (Codex GPT-5.4 audit, 392 lines)

---

## 6. Next Steps

- [ ] Deep-read top 3 papers and extract implementable methodology
- [ ] Prototype autoencoder-based feature extraction on our factor data
- [ ] Implement Sharpe-scaled PCA for factor combination (Jiang et al.)
- [ ] Test AP-Trees approach on our equity universe
- [ ] Monitor Hull Tactical competition for solutions (post June 2026)
- [ ] Check Mitsui competition for full 3rd place writeup details
- [x] Assess Goldman Sachs strategy ideas (2026-03-17) — Strategy 4 approved for research

---

## 6. Book Summary — Advances in Financial Machine Learning (López de Prado, 2018)

*Summarized: 2026-03-13*

### Core Thesis

Standard ML applied naively to finance **will lose money**. Finance is uniquely difficult: low signal-to-noise, non-IID data, trivially easy overfitting. The solution is an **industrial, team-based "meta-strategy paradigm"** — a research factory with specialized roles (data curators, feature analysts, strategists, backtesters, deployment, portfolio oversight).

---

### Part 1: Data Analysis

#### Ch. 2 — Financial Data Structures
**Don't use time bars (daily OHLCV)** — poor statistical properties (serial correlation, fat tails, heteroskedasticity).

Better bar types:
| Bar Type | Sampled when... | Why better |
|---|---|---|
| Tick bars | N transactions occur | More stationary volatility |
| Volume bars | N units traded | Better independence |
| **Dollar bars** | $N in value traded | **Best overall** — normalizes for price changes, closest to normal returns |
| Imbalance bars | signed flow imbalances exceed threshold | Fastest at detecting informed trading |

**ETF trick:** Construct a synthetic series from a basket with allocation weights — models spread as a single series for multi-asset strategies.

#### Ch. 3 — Labeling
**Triple-Barrier Method** (replace fixed-time labels):
- 3 barriers: upper (profit-take), lower (stop-loss), vertical (max holding time)
- Label = +1 if upper hit first, −1 if lower hit first, 0 if vertical hit
- Barriers set dynamically using rolling volatility: `threshold = h * σ_t`

**Meta-Labeling** (two-stage classification):
1. Primary model generates side (long/short)
2. Meta-model learns "is this bet worth taking?" → outputs bet size
- Separates direction prediction from confidence/sizing
- Improves F1 score and precision without hurting recall

#### Ch. 4 — Sample Weights
Financial observations overlap → NOT independent. Treating them as IID inflates effective sample size and causes overfitting.
- **Uniqueness weighting:** weight each observation by proportion of non-overlapping returns
- **Sequential bootstrapping:** draw samples weighted by uniqueness (not uniformly)
- **Time decay:** exponential decay so older labels matter less
- **Class weights:** correct imbalance by upweighting rare events

#### Ch. 5 — Fractional Differentiation
**The dilemma:** Returns are stationary but memoryless. Prices carry memory but are non-stationary. Integer differencing (`d=1`) throws away all memory.

**Solution:** Find minimum `d` (typically 0.3–0.45) such that the series passes ADF stationarity test. Preserves long-range memory while achieving stationarity — a major edge over competitors using raw prices or plain returns.

---

### Part 2: Modelling

#### Ch. 6 — Ensemble Methods
- **Bagging > Boosting for finance**: bagging is more robust to mislabeled samples (unavoidable in finance); boosting overfits easily on noisy labels
- Random Forests preferred; apply sequential bootstrapping (Ch. 4) when building trees

#### Ch. 7 — Cross-Validation in Finance
**Standard K-Fold CV is broken in finance** — training data leaks via overlapping labels + serial correlation.

**Purged K-Fold CV:**
1. After train/test split, **purge** train observations whose outcomes overlap with test period
2. Add **embargo** gap (k observations) after each test fold
- Standard `sklearn.cross_validate` on time-series gives optimistically biased scores

#### Ch. 8 — Feature Importance
- **MDI (Mean Decrease Impurity):** fast, biased toward high-cardinality features
- **MDA (Mean Decrease Accuracy):** permute feature, measure accuracy drop — more robust
- Most financial features are useless. Aggressively prune before fitting.
- Stack importances across CV folds; rank by mean, filter by std

#### Ch. 9 — Hyper-Parameter Tuning
- Use **Randomized Search CV** (not Grid Search) for high-dimensional spaces
- **Nested CV**: outer loop for model selection, inner loop for tuning — prevents leakage
- Scoring: use **negative log loss** for classifiers; **Sharpe ratio** for sized bet strategies

---

### Part 3: Backtesting

#### Ch. 10 — Bet Sizing
- Size from predicted probabilities: `m = 2*N(p) - 1` (inverse normal CDF)
- Or Kelly criterion: `f = (p*(b+1) - 1) / b`
- **Concave sizing**: never go all-in; size proportional to prediction confidence

#### Ch. 11 — The Dangers of Backtesting
**Backtesting is NOT a research tool.** Using it iteratively = p-hacking.

Rules:
- Form a theory first; test it once
- Never mine data to generate hypotheses
- Backtest results shared only with management, never fed back to researchers
- Historical path is one realization of a stochastic process

#### Ch. 12 — Backtesting through Cross-Validation
Three paradigms:
1. Walk-forward (historical): most common, most overfitted
2. **Combinatorial Purged CV (CPCV):** splits data into N groups, combines C(N,k) train/test sets → multiple paths → estimates **distribution** of Sharpe ratios
3. Synthetic data: simulate paths from estimated process parameters

**Probability of Backtest Overfitting (PBO):** if median Sharpe in test folds < 0 more than 50% of the time, strategy is likely overfit.

#### Ch. 14 — Backtest Statistics
Key stats beyond Sharpe:
- **Deflated Sharpe Ratio (DSR):** adjusts for number of trials and sample length — a Sharpe of 2.0 found after 100 tries ≈ Sharpe of 0.5 found on first try
- Max Drawdown + Duration, Hit Rate, Avg Profit/Loss Ratio, Calmar, Skewness, IC

#### Ch. 15 — Strategy Risk
- Compute probability that OOS Sharpe < 0 given known strategy parameters
- **Asymmetric payoff strategies** (short volatility, carry): high apparent Sharpe but catastrophic tail risk — must be explicitly assessed

#### Ch. 16 — Hierarchical Risk Parity (HRP)
**Problem with Markowitz:** inversion of covariance matrix is unstable; error-maximizing; breaks when N > T.

**HRP algorithm (3 steps):**
1. **Tree Clustering:** cluster assets by correlation → dendogram
2. **Quasi-Diagonalization:** reorder covariance matrix so similar assets are adjacent
3. **Recursive Bisection:** allocate risk top-down through dendogram using inverse-variance weights

HRP significantly outperforms Markowitz, CLA, and equal-weight allocations OOS (Monte Carlo verified). No matrix inversion needed.

---

### Part 4: Useful Financial Features

#### Ch. 17 — Structural Breaks
- **CUSUM tests:** detect shifts in process mean/variance
- **SADF (Supremum ADF):** rolling explosiveness test — detects bubbles before they burst

#### Ch. 18 — Entropy Features
- Discretize returns into symbols → compute Lempel-Ziv complexity or Shannon entropy
- Low entropy = predictable market (opportunities); high entropy = random (avoid)
- VPIN: entropy-based measure of informed trading toxicity in order flow

#### Ch. 19 — Microstructure Features
- **Roll model:** estimate effective spread from serial covariance of returns
- **Kyle's lambda:** price impact per unit volume (measure of illiquidity)
- **Amihud illiquidity:** |return| / volume
- **PIN / VPIN:** probability of informed trading from order flow imbalance
- Order flow imbalance, cancellation/replacement ratios, queue depth, trade size distribution

---

### Actionable Takeaways for This Platform

| Current issue in our framework | Book's solution |
|---|---|
| Using daily time bars | Switch to **dollar bars** |
| Fixed-time labels in backtests | Implement **triple-barrier method** |
| K-fold CV on time series | Use **purged K-fold CV** |
| Walk-forward as only backtest | Add **CPCV** for PBO estimation |
| Markowitz allocation | Implement **HRP** |
| Integer differencing for stationarity | Use **fractional differentiation (d~0.35)** |
| Reporting raw Sharpe ratios | Report **Deflated Sharpe Ratio** |
| Treating all samples equally | Apply **uniqueness weights + time decay** |

---

## 6. Recent Academic Papers — Alpha Decay & Momentum Crowding (2024-2025)

### 6.1 "Modeling, Measuring, and Trading on Alpha Decay" (arXiv 2512.11913, Dec 2024)

**Authors:** Not specified in search results
**Source:** [arXiv:2512.11913](https://arxiv.org/abs/2512.11913)

**Key Findings:**
- Out-of-sample validation (2001-2024) shows crowded reversal factors have 1.7-1.8x higher crash probability (bottom decile returns)
- Crowded momentum shows 0.38x LOWER crash risk vs crowded reversal (p=0.006)
- Crowding predicts tail risk but affects momentum and reversal asymmetrically
- Momentum is more robust to crowding than mean-reversion strategies

**Relevance to Our Platform:** 95/100
- Directly addresses momentum crowding concerns for Vol-Scaled Momentum (rejected) and CS Momentum (conditional)
- Validates momentum as lower-risk factor even when crowded
- Suggests our rejection of Vol-Scaled Momentum may have been correct (high crowding in 2024-2025)

**Applicability:** Add crowding metrics to `backtests/stats/decay_analysis.py` — track factor popularity via ETF flows, mutual fund holdings

---

### 6.2 "A Re-Examination" by Gao, Li, Yuan, Zhou (SSRN 5057525, 2025)

**Authors:** Cheng Gao, Sophia Zhengzi Li, Peixuan Yuan, Guofu Zhou
**Source:** [SSRN 5057525](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5057525)

**Key Findings:**
- Momentum factor exhibits significant alpha after adding betting-against-systematic factor
- IPCA (Instrumented PCA) model fails to fully explain momentum returns
- Momentum remains an independent alpha source even after controlling for systematic factors

**Relevance to Our Platform:** 88/100
- Counters our VIX Regime spanning alpha failure (t=-0.18) — momentum IS independent
- Validates momentum as core strategy (CS Momentum Priority 3, FX Carry + Momentum Priority 1)
- Suggests our framework's spanning tests (controlling for SPY + momentum) are correctly identifying independent alpha

**Applicability:** Use as academic backing for momentum strategies in PM reviews

---

### 6.3 "LLM-Driven Alpha Mining with Regularized Exploration" (arXiv 2502.16789, Feb 2025)

**Authors:** Not specified in search results
**Source:** [arXiv:2502.16789](https://arxiv.org/html/2502.16789v1)

**Key Findings:**
- Traditional genetic programming faces rapid alpha decay from overfitting and complexity
- LLM-driven approaches with regularized exploration counteract alpha decay
- Regularization techniques prevent overfitting in automated signal generation

**Relevance to Our Platform:** 75/100
- Directly relevant to Cerebro signal generation pipeline (`cerebro/signal_generator.py`)
- Suggests our LLM-based signal generation needs explicit regularization (e.g., complexity penalties, cross-validation)
- Validates the Cerebro approach but warns of overfitting risk

**Applicability:** Add regularization to `cerebro/signal_generator.py` — penalize complex signals, require OOS validation before proposal

---

## 7. HALO Factor (Goldman Sachs 2026)

### 7.1 Concept Definition

**HALO = High Asset, Low Obsolescence**

**Characteristics:**
- Substantial physical capital with high barriers to replication (cost, regulation, time to build, engineering complexity)
- Long-lived economic relevance (not subject to rapid technological obsolescence)
- Examples: utilities, industrials, materials, energy infrastructure, railroads, pipelines, data centers

**Source:** Goldman Sachs Global Strategy Views (March 2026)
**Academic Precedent:** Repackaging of Quality factor (Asness et al. QMJ), Buffett's "moat" investing, Fama-French profitability

### 7.2 Academic Backing

**Supporting Research:**
- [AI-resistant 'halo' stocks drive UK and EU markets to record highs](https://www.theguardian.com/business/2026/mar/01/investment-ai-resistant-halo-companies-uk-eu-markets-goldman-sachs) — HALO businesses pair substantial physical capital with long-lived economic relevance
- [A Historical Lens on the Physical Asset Rotation](https://www.ainvest.com/news/testing-halo-trade-historical-lens-physical-asset-rotation-2603/) — Capital-intensive stocks as "tangible havens" from AI disruption

**Contradicting Evidence:**
- [The HALO trade is powering a market rotation](https://www.aol.com/articles/halo-trade-powering-market-rotation-104501884.html) — "Wall Street is getting it wrong" — suggests crowding risk
- Automation and AI could disrupt labor-intensive infrastructure (logistics, utilities) just as much as software

### 7.3 Implementation Approach

**Do NOT create standalone HALO strategy** — it's a factor tilt, not an alpha source.

**Recommended Implementation:**
- Add HALO as a **quality sub-factor** in `backtests/strategies/signals.py`
- Define HALO score = f(CapEx intensity, asset tangibility, regulatory moat, low R&D/Sales ratio)
- Test as a **tilt** in Elena's Cross-Sectional Momentum strategy (Priority 3)

**Feature Engineering:**
```python
# Pseudo-code for HALO score
halo_score = (
    0.4 * zscore(capex_to_sales)  # High capital intensity
    + 0.3 * zscore(ppe_to_assets)  # High tangible assets
    + 0.2 * (1 - zscore(rd_to_sales))  # Low R&D (not tech-driven)
    + 0.1 * regulatory_moat_dummy  # Regulated industries (utilities, pipelines)
)
```

**Expected Sharpe Lift:** +0.1 to +0.2 (quality factor typically adds modest alpha with significant drawdown reduction)

**Blocker:** Requires fundamental data (CapEx, PPE, R&D) — not available in current platform. Defer until fundamental data pipeline is built.

---

*Last updated: 2026-03-17*
