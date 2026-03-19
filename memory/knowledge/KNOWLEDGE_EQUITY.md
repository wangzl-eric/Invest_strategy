# Knowledge Base: Equity
_Last updated: 2026-03-19_
_Entry tags: [AUTO] auto-extracted | [PLAYGROUND] from notebook | [BOOK/ARTICLE] from reading | [PM-VERDICT] from strategy review_
_All entries validated by kb-curator agent before write._

---

## Topic: momentum

### Market Facts & Structural Observations
- Cross-sectional equity momentum (12-1 month lookback) is one of the most replicated factors | robust across markets and time periods | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- Momentum crashes occur during sharp market reversals (post-crisis rebounds) | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- US large-cap equity is highly efficient; strategies claiming Sharpe > 1.0 require extraordinary evidence | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13

### Intermediate Findings
- Cross-Sectional Equity Momentum strategy is CONDITIONAL (Priority 3) — assigned to Elena | confidence: med | follow-up: full R1 with alphalens-reloaded | [AUTO: STRATEGY_TRACKER.md] | 2026-03-13
- Alphalens-reloaded installed for Elena's CS Momentum research | confidence: high | follow-up: use for factor analysis | [AUTO: LESSONS_LEARNED.md framework audit] | 2026-03-15

### Confirmed Signals
- (none fully approved — CS Momentum is CONDITIONAL pending research)

### Known Failure Modes
- Vol-scaled momentum (equity long-only): -3.32% alpha vs equal-weight, IS/OOS ratio 0.35, max DD -32% | REJECTED after 3 rounds | [PM-VERDICT: vol_scaled_momentum_2026-03-13 REJECTED] | 2026-03-13
- MVO with tight constraints adds noise not alpha for equity momentum; ranking-based allocation preferred | [PM-VERDICT: vol_scaled_momentum_2026-03-13 REJECTED] | 2026-03-13
- Always benchmark vs equal-weight from R1 — vol-scaled missed this until R3 | [AUTO: LESSONS_LEARNED.md] | 2026-03-15
- Vol targeting doesn't fix crash risk for equity long-only; backward-looking vol can't react to sudden shocks | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Key Papers & Concepts
- "Returns to Buying Winners and Selling Losers" | Jegadeesh & Titman | 1993 | relevance: 95/100 | original momentum paper; 12-1 month lookback | cited
- "Fact, Fiction, and Momentum Investing" | AQR | 2014 | relevance: 88/100 | momentum robustness and implementation | cited
- Jane Street 1st Place (Supervised Autoencoder + MLP) | Kaggle 2021 | relevance: 72/100 | denoising financial features via supervised autoencoder before signal generation | read
- Mitsui 3rd Place (Directional Trends over Volatility) | Kaggle | relevance: 80/100 | trend signals normalized by vol robust in commodity/equity/FX | read

---

## Topic: quality

### Market Facts & Structural Observations
- Quality factor (high ROE, low leverage, stable earnings) outperforms in defensive regimes | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- High valuations + deteriorating macro + geopolitical risks favor Quality stocks | [AUTO: goldman_sachs_strategy_assessment_2026-03-17.md] | 2026-03-17

### Intermediate Findings
- Quality + Safe-Haven Overlay is APPROVED for research (Priority 2) — feasible with ETF proxies (QUAL, USMV, GLD, JPY/CHF) | confidence: med | follow-up: Elena R1 notebook | [PM-VERDICT: quality_safe_haven APPROVED] | 2026-03-17
- Quality ETF proxies: QUAL (iShares MSCI USA Quality Factor), USMV (iShares MSCI USA Min Vol) | [AUTO: STRATEGY_TRACKER.md] | 2026-03-17

### Confirmed Signals
- (none — Quality + Safe-Haven in research, not yet approved)

### Known Failure Modes
- HALO Factor (High Asset, Low Obsolescence) rejected — no fundamental data pipeline, factor definition too vague | [PM-VERDICT: GS HALO REJECTED] | 2026-03-17
- Defensive Sector Rotation rejected — no sector classification data, requires expensive data subscription | [PM-VERDICT: GS Defensive Sector Rotation REJECTED] | 2026-03-17

### Key Papers & Concepts
- "Quality Minus Junk" | Asness, Frazzini, Pedersen | 2019 | relevance: 90/100 | QMJ factor; quality premium robust across markets | cited

---

## Topic: low-volatility

### Market Facts & Structural Observations
- Low-vol anomaly (low-beta stocks outperform on risk-adjusted basis) is well-documented | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- USMV (iShares MSCI USA Min Vol) as proxy for low-vol exposure in Quality overlay | [AUTO: STRATEGY_TRACKER.md] | 2026-03-17

### Intermediate Findings
- (none)

### Confirmed Signals
- (none)

### Known Failure Modes
- Vol targeting as standalone strategy doesn't add alpha beyond mechanical exposure reduction | [AUTO: LESSONS_LEARNED.md] | 2026-03-15

### Key Papers & Concepts
- "Betting Against Beta" | Frazzini & Pedersen | 2014 | relevance: 85/100 | BAB factor; low-vol premium from leverage constraints | cited

---

## Topic: sector-rotation

### Market Facts & Structural Observations
- Cyclicals vs Defensives valuation spread is a historically rare signal (GS March 2026 note) | [AUTO: external_ideas.md] | 2026-03-17

### Intermediate Findings
- Sector Rotation (Macro-Linked) is CONDITIONAL (Priority 4) — assigned to Elena | confidence: low | follow-up: data dependency on sector classification | [AUTO: STRATEGY_TRACKER.md] | 2026-03-13

### Confirmed Signals
- (none)

### Known Failure Modes
- Defensive Sector Rotation rejected — no sector classification data pipeline; requires $5K+/yr Norgate or 6-month valuation pipeline build | [PM-VERDICT: GS Defensive Sector Rotation REJECTED] | 2026-03-17

### Key Papers & Concepts
- (none yet)

---

## Topic: crowding

### Market Facts & Structural Observations
- Highly crowded factors can experience sharp drawdowns when hedge funds deleverage | [AUTO: BUSINESS_CONTEXT.md] | 2026-03-13
- Crowding analyses: "Is everyone running the same strategy?" is a mandatory Cerebro contradiction search question | [AUTO: cerebro.md] | 2026-03-13

### Intermediate Findings
- (none)

### Confirmed Signals
- (none)

### Known Failure Modes
- (none specific yet)

### Key Papers & Concepts
- (none yet)
