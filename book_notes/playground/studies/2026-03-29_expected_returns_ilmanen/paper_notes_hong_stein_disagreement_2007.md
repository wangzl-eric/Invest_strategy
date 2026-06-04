# Paper Notes: Disagreement and the Stock Market

**Authors:** Harrison Hong, Jeremy C. Stein
**Year:** 2007
**Journal:** Journal of Economic Perspectives, Vol. 21 No. 2, pp. 109–128
**Date Read:** 2026-03-30
**Scores:** Credibility 4 | Relevance 4 | Actionability 3
**Type:** JEP survey — accessible synthesis, not primary empirics

---

## Core Thesis

A single unified behavioral model — built on two types of boundedly-rational agents and the gradual diffusion of private information — can simultaneously explain:

1. **Short-horizon momentum** (underreaction / slow information diffusion)
2. **Long-horizon reversal / crashes** (overreaction when short-sale constraints lift)

The paper argues these two seemingly contradictory phenomena share a common root: disagreement among investors, combined with constraints on short-selling, causes prices to systematically deviate from fundamentals in predictable, pattern-forming ways.

---

## Key Findings

- Momentum and long-run reversal are not separate anomalies requiring separate explanations — they are two phases of the same mispricing cycle.
- Short-sale constraints cause stocks with high dispersion of opinion to be **systematically overpriced** (only optimists hold; pessimists are sidelined).
- Stocks with **low analyst coverage** (slower information diffusion) show **stronger momentum** — consistent with the gradual-diffusion mechanism.
- Momentum is stronger following **low-volume** periods: less trading implies slower diffusion of news.
- Crashes (sharp reversals) occur when previously constrained pessimistic information finally enters the market.
- The model naturally produces **negative skewness** in individual stock returns: long buildups punctuated by sudden sharp declines.


---

## The Two Mechanisms

### 1. Gradual Information Diffusion → Momentum

Private signals do not instantaneously reach all investors. Each "newswatcher" observes a different slice of the total information set, and signals diffuse across the population slowly over time. At any point, the marginal price-setter has not yet processed all available information. This creates **serial positive autocorrelation** in returns — the classic momentum pattern.

The key driver is *heterogeneous information arrival*, not irrationality per se. Each agent is Bayesian given what they see, but the aggregate market underreacts because no single agent sees everything at once. The bounded rationality is that newswatchers ignore prices as a sufficient statistic for others' signals.

### 2. Overreaction When Constraints Lift → Crashes

Momentum traders observe the initial price drift (caused by diffusion) and extrapolate it. Their demand pushes prices **beyond fundamentals**. When the accumulated overpricing unwinds — triggered by negative news that can no longer be suppressed, or by short-sellers entering — the correction is abrupt and large relative to the original shock.

This produces the **long-run reversal** signature (DeBondt & Thaler 1985) and contributes to crash risk. The two phases are causally linked: the same diffusion that creates momentum also seeds the conditions for the eventual correction.


---

## Short-Sale Constraint Model (Miller 1977 Foundation)

Miller (1977): when investors disagree and short selling is costly or prohibited, the **marginal buyer is the most optimistic** investor. Pessimists cannot express negative views, so they are excluded from price formation. Result: **prices reflect the upper tail of the belief distribution**, not the mean. The more dispersed the beliefs, the greater the overpricing.

Hong & Stein extend this dynamically: as price rises (momentum phase), more pessimists accumulate unexpressed negative views on the sidelines. When the price peaks and turns, the release of this latent pessimism amplifies the decline — creating **asymmetric crash risk** (left tail fat).

**Key pricing implications:**

| Signal | Direction | Mechanism |
|--------|-----------|----------|
| High analyst forecast dispersion | Overpriced → underperform | High disagreement, constraint binding |
| High short interest | Overpriced → underperform | Pessimist constraint currently binding |
| High dispersion + high short interest | Strongest overpricing signal | Both conditions simultaneously |
| Low analyst coverage | Stronger momentum | Slower diffusion of private signals |
| Low recent volume | Stronger momentum | Less trading → slower diffusion |


---

## Heterogeneous Agents

### Newswatchers
- Receive **private signals** about fundamentals (analyst updates, channel checks, guidance)
- Each sees only a subset of the total signal population
- Signals diffuse gradually — not all newswatchers receive information simultaneously
- Do **not** condition on price history — they ignore momentum entirely
- This is the bounded rationality: a fully rational agent would update on price as a sufficient statistic for others' signals

### Momentum Traders
- Observe **past price changes** and extrapolate them forward
- Simple trend-following rule: buy winners, sell losers
- Also boundedly rational: ignore fundamentals entirely, trade only on price history
- Their demand amplifies the initial drift, pushing prices past fair value
- They are the mechanism by which underreaction transitions into overreaction

**The interaction dynamic:** Newswatchers cause underreaction (prices adjust too slowly to private information). Momentum traders, responding to that underreaction, eventually cause overreaction. Neither agent is irrational relative to their information set in isolation — market-level mispricing is an emergent property of their interaction.


---

## Unified Behavioral Framework

The elegance of Hong-Stein is that a single parsimonious model produces **both** major documented anomalies from one set of assumptions:

| Horizon | Phenomenon | Mechanism |
|---------|------------|----------|
| 3–12 months | **Momentum** | Gradual diffusion; newswatchers haven't all priced in the signal |
| 3–5 years | **Long-run reversal** | Momentum traders pushed price past fundamentals; eventual mean-reversion |
| Event-time | **Crash risk / negative skew** | Accumulated pessimist overhang releases suddenly |

Contrast with BSV (1998), which requires *two distinct biases* (conservatism for underreaction, representativeness for overreaction) in a single agent to explain the same facts. Hong-Stein achieves the same explanatory scope with one mechanism (gradual diffusion) and two agent types.

**Cross-sectional implications:** Stocks that diffuse information more slowly — small-cap, low institutional ownership, low analyst coverage — should show:
- Stronger momentum at 3–12 month horizon
- Stronger eventual reversal at 3–5 year horizon
- More negative return skewness (greater crash risk)

All three predictions are empirically confirmed (see Predictions section).


---

## Predictions & Tests

| Prediction | Empirical Status | Key Reference |
|-----------|-----------------|---------------|
| Momentum stronger in low-analyst-coverage stocks | Confirmed | Hong, Lim & Stein (2000, JF) |
| Momentum stronger after low-volume periods | Confirmed | Lee & Swaminathan (2000, JF) |
| High short-interest stocks underperform | Confirmed | Asquith, Pathak & Ritter (2005) |
| High analyst forecast dispersion → future underperformance | Confirmed | Diether, Malloy & Scherbina (2002, JF) |
| Individual stocks show negative skewness / crash risk | Confirmed | Chen, Hong & Stein (2001, JFE) |
| Stocks with high past runup show greater crash risk | Confirmed | Chen, Hong & Stein (2001, JFE) |
| Aggregate momentum at short run; reversal at long run | Confirmed | Jegadeesh & Titman (1993); DeBondt & Thaler (1985) |

All core quantitative predictions have empirical support. This is an unusually clean track record for a behavioral model.

---

## Limitations

1. **Survey paper — no new empirics.** The primary model is in Hong-Stein (1999, JF). The 2007 JEP paper is a synthesis and adds no new data or tests.
2. **Gradual diffusion is assumed, not micro-founded.** Why can't newswatchers read prices as sufficient statistics? The bounded rationality is imposed exogenously.
3. **Momentum trader rule is ad hoc.** The extrapolation rule is specified without evolutionary justification — why do these traders persist if they are eventually wrong?
4. **Short-sale constraints treated as binary.** In practice, borrowing costs vary continuously. The model is sharpest at the constraint boundary.
5. **No factor structure.** The model is firm-level; it does not explain why disagreement co-moves across stocks in ways that generate priced systematic factors.
6. **Diffusion speed not directly observable.** Analyst coverage and volume are used as proxies — these may capture other phenomena unrelated to information diffusion.

---

## Connection to Ilmanen — Expected Returns

### Ch. 6 (Behavioral Finance)
Hong-Stein sits squarely in Ilmanen's behavioral category of **investor irrationality as a source of return premium**. Ilmanen treats disagreement/dispersion as a behavioral source of mispricing. The short-sale constraint mechanism maps directly to Ilmanen's treatment of constraints-based overpricing: when pessimists are sidelined, optimist-dominated prices embed a "disagreement premium" that does not compensate for fundamental risk.

Ilmanen distinguishes premia that compensate for *bearing risk* from those that exploit *systematic mispricing*. Hong-Stein falls in the latter camp: the momentum premium is not a risk premium in the traditional sense — it is compensation for exploiting the slow diffusion of private information.

### Ch. 14 (Momentum)
Ilmanen's momentum chapter echoes Hong-Stein's two-phase structure directly:
- **Underreaction phase** (0–12 months): price adjusts too slowly to news → trend-following works
- **Overreaction phase** (12–60 months): accumulated extrapolation unwinds → contrarian works

Ilmanen's empirical observation that momentum is stronger for smaller, less-covered stocks is a direct confirmation of Hong-Stein's diffusion-speed prediction. The volume-momentum interaction (Lee & Swaminathan 2000) is also flagged by Ilmanen as a useful conditioning variable for momentum strategies.

---

## Codebase Check

### signals.py — No Behavioral Signals Present
`backtests/strategies/signals.py` contains: `MomentumSignal`, `CarrySignal`, `MeanReversionSignal`, `VolatilitySignal`, `ATRSignal`, `RSISignal`, `MACDSignal`, `BollingerPositionSignal`, `SMACrossoverSignal`, `VolumeSignal`, `SignalBlender`.

**No sentiment, analyst dispersion, short-interest, or disagreement signals exist.** The `MomentumSignal` (12-1 month lookback) is a pure price-based implementation — it captures the momentum anomaly Hong-Stein explains but embeds none of the conditioning variables the theory predicts should strengthen it.

### forward_pass/comparison.py — News Sentiment Field (Weak)
`backtests/forward_pass/comparison.py` lines 43, 221–232: a `news_sentiment` field (`Optional[str]`, values `"positive"` / `"negative"`) is tracked on forward-pass comparisons and accuracy is scored against actual returns. This is a stub-level implementation — binary categorical, not a continuous dispersion measure. It does not connect to any signal generation pipeline and is not used in backtesting.

**Flag:** This field is the closest existing hook to behavioral sentiment data. It could be extended to carry analyst forecast dispersion or short-interest data if those sources were ingested.

### KNOWLEDGE_EQUITY.md — No Behavioral / Dispersion Entries
The equity knowledge base has entries for momentum, quality, low-volatility, sector-rotation, and crowding. No entries exist for behavioral finance, analyst dispersion, short interest, or disagreement-based signals. Hong-Stein's findings are new to the KB.

### external_ideas.md — No Sentiment-Based Ideas
No sentiment, dispersion, or short-interest strategy ideas are present. The GS HALO strategy (section 7) touches on quality factors but is fundamental-data-gated and unrelated to disagreement.

### Summary Table

| Component | Relevant? | Notes |
|-----------|-----------|-------|
| `backtests/strategies/signals.py` | Partial | `MomentumSignal` exists; no dispersion/sentiment signals |
| `backtests/forward_pass/comparison.py:43` | Weak | Binary `news_sentiment` stub; not wired to signal pipeline |
| `memory/knowledge/KNOWLEDGE_EQUITY.md` | No | No behavioral or dispersion entries |
| `research/external_ideas.md` | No | No disagreement-based strategy ideas |

---

## Implementability

### What Is Not Available Locally
- **Short-interest data:** Requires FINRA, Quandl/Nasdaq, or S3 short-interest feeds. Not in current data lake. Cost: ~$500–2,000/yr for clean daily short interest by ticker.
- **Analyst forecast dispersion:** Requires I/B/E/S, FactSet, or Refinitiv consensus estimates. Not in current pipeline. Proxied imperfectly by realized return volatility.
- **Analyst coverage count:** Could be approximated via free sources (Yahoo Finance analyst count, Quandl) but not systematic.

### What Can Be Proxied Today
- **Dispersion proxy:** Realized return volatility (`VolatilitySignal`) is a crude but available proxy for disagreement. Higher vol → more disagreement → potentially overpriced under Miller 1977.
- **Diffusion speed proxy:** Market cap (small-cap = slower diffusion). Available via price * shares or ETF proxy baskets.
- **Volume conditioning:** `VolumeSignal` exists. Hong-Stein predicts momentum should be stronger in low-recent-volume stocks — this interaction is testable today with existing signals.

### Actionable Near-Term Test
Condition `MomentumSignal` on lagged volume: split the cross-section into high-volume and low-volume terciles, run separate momentum backtests. If Hong-Stein holds, the low-volume tercile should show materially stronger momentum IC. This requires no new data — only a `SignalBlender` or conditional wrapper around existing signals.

### Longer-Term (Data-Gated)
- Build analyst dispersion signal from IBES once fundamental data pipeline exists
- Build short-interest signal from FINRA short-volume data (free, daily, but noisy)
- Combine into a `DisagreementSignal` that overweights momentum in low-dispersion stocks and fades it in high-dispersion stocks

---

## Key Quotes

> "When there is heterogeneity of opinion, and short-selling is restricted, the most optimistic investors set prices. If optimism is not justified by fundamentals, stocks will be overvalued."

> "The interaction of gradual information flow with momentum trading can generate the full range of under- and overreaction patterns observed in the data."

> "Stocks with low analyst coverage — which we take to be a proxy for slow information diffusion — display significantly stronger return continuation."

> "Our model suggests that momentum and crashes are two sides of the same coin: the underreaction that creates momentum is the same mechanism that, once amplified by trend-chasers, creates the overpricing that eventually crashes."

---

## Follow-Up Papers

| Paper | Authors | Year | Journal | Why Read |
|-------|---------|------|---------|----------|
| A Unified Theory of Underreaction, Momentum Trading and Overreaction in Asset Markets | Hong & Stein | 1999 | Journal of Finance | Primary model — full formal derivation of the two-agent framework |
| Differences of Opinion, Short-Sales Constraints, and Market Crashes | Hong & Stein | 2003 | Review of Financial Studies | Crash risk extension; negative skewness predictions |
| Differences of Opinion and the Cross-Section of Stock Returns | Diether, Malloy & Scherbina | 2002 | Journal of Finance | Analyst forecast dispersion as disagreement proxy; underperformance result |
| Risk, Uncertainty, and Divergence of Opinion | Miller | 1977 | Journal of Finance | Foundational short-sale constraint + disagreement = overpricing argument |
| Overconfidence, Arbitrage, and Equilibrium Asset Pricing | Scheinkman & Xiong | 2003 | Journal of Political Economy | Speculative bubble extension; resale option value under heterogeneous beliefs |
| Do Industries Explain Momentum? | Moskowitz & Grinblatt | 1999 | Journal of Finance | Industry-level momentum — tests diffusion speed at sector level |
| Price Momentum and Trading Volume | Lee & Swaminathan | 2000 | Journal of Finance | Volume as diffusion-speed proxy; volume-momentum interaction |
