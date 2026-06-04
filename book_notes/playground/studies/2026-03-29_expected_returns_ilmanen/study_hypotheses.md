# ER Study Hypotheses

Testable hypotheses for *Expected Returns: An Investor's Guide to Harvesting Market Rewards* by Antti Ilmanen.

These hypotheses are designed to:

- reflect Ilmanen's core framing that expected returns are decomposable into persistent risk premia
- focus on hypotheses that can be prototyped with the current local FRED and market-data lake
- connect directly to the existing GMT and FIRV study infrastructure already built in this repo

## Material Score

| Dimension | Score | Reason |
|-----------|-------|--------|
| Credibility | 5/5 | Canonical cross-asset risk-premia book by Ilmanen, with strong academic and practitioner grounding |
| Relevance | 5/5 | Directly aligned with cross-asset expected-return research, tactical allocation, and factor harvesting |
| Actionability | 4/5 | Many ideas are immediately testable with local data, but some textbook implementations need richer valuation and options data |

The book clears the `>= 3/5` threshold on all dimensions and warrants deeper follow-up.

## Local Data We Can Use Now

### FRED / Rates / Macro

- `SOFR`
- `DFEDTARU`
- `DGS1`, `DGS2`, `DGS3`, `DGS5`, `DGS7`, `DGS10`, `DGS20`, `DGS30`
- `DFII5`, `DFII10`, `DFII30`
- `T10Y2Y`, `T10Y3M`
- `T5YIE`, `T10YIE`, `T5YIFR`
- `BAMLH0A0HYM2`
- `NFCI`
- `CPIAUCSL`
- `UNRATE`
- `UMCSENT`
- `WALCL`, `WRESBAL`, `RRPONTSYD`

### Market / Price Proxies

- `SPY`, `^GSPC`, `^NDX`, `^RUT`, `^STOXX`, `^N225`, `^VIX`
- `DX-Y.NYB`
- `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`, `USDCAD=X`, `AUDUSD=X`, `NZDUSD=X`, `USDCHF=X`, `USDNOK=X`, `USDSEK=X`
- `CL=F`, `BZ=F`, `GC=F`, `HG=F`, `NG=F`, `SI=F`
- `^IRX`, `^FVX`, `^TNX`, `^TYX`

### Existing Study Infrastructure We Can Reuse

- Current Ilmanen study folder:
  - `01_equity_risk_premium.ipynb`
  - `02_bond_risk_premium.ipynb`
  - `03_carry_strategies.ipynb`
  - `04_momentum.ipynb`
  - `05_volatility_risk_premium.ipynb`
  - `local_parquet.py`
- GMT study:
  - `01_cross_asset_overview.ipynb`
  - `02_fx_valuation.ipynb`
  - `03_macro_regime_indicators.ipynb`
  - `04_central_bank_policy.ipynb`
  - `05_commodities_macro.ipynb`
- FIRV study:
  - `01_mean_reversion.ipynb`
  - `02_pca_yield_curve.ipynb`
  - `08_macro_regime_panel.ipynb`

### Practical Sample Coverage

For most daily market and FRED panels in the current lake, the overlapping working sample is roughly:

- `2024-02-26` through `2026-02-27`

Important exceptions:

- monthly macro series such as `CPIAUCSL`, `UNRATE`, and `UMCSENT` start around `2024-02-01`
- some equity proxies have longer raw histories, but many of the cross-asset joins are still constrained by the shorter daily FRED sample

This makes the study suitable for hypothesis scaffolding and conditional diagnostics, but too short for strong claims about long-horizon premia magnitude.

## Local Data Gaps That Matter

The following are not yet cleanly available in the local lake:

- equity valuation series such as earnings yield, CAPE, book-to-price, or buyback yield
- investable credit total-return proxies such as `LQD`, `HYG`, or CDX / iTraxx histories
- foreign CPI and foreign real-yield panels for cleaner FX PPP and real-rate-differential models
- option-implied variance term structures beyond coarse volatility proxies like `^VIX`
- direct illiquidity-premia datasets for Chapter 19
- forward points, funding curves, and futures-curve term structures for cleaner cross-asset carry measurement

Because of those gaps, several hypotheses below use reduced-form local proxies rather than the full textbook implementation.

## Group A: Strategic Premia and Cross-Asset Interactions

### Hypothesis ERP-1

**Name:** Real-yield shocks dominate reduced-form equity risk premium timing

**Hypothesis:**  
Sharp increases in U.S. real yields,

- `DFII5`
- `DFII10`

that are not offset by tighter credit spreads or falling volatility predict weaker subsequent `SPY` excess returns over `SOFR` on 5d to 20d horizons.

**Why it fits the book:**  
It operationalizes Ilmanen's Chapter 7 argument that discount-rate variation is a major driver of tactical equity expected returns.

**Test design:**
- construct a daily real-yield shock score from changes in `DFII5` and `DFII10`
- condition the signal on `BAMLH0A0HYM2` and `^VIX`
- measure forward `SPY` excess return over `SOFR`
- compare top-decile shock days versus neutral days

**Evidence that would support the hypothesis:**
- large positive real-yield shocks are followed by weaker equity excess returns
- the effect is strongest when spreads are widening and volatility is rising

### Hypothesis ERP-2

**Name:** Tight financial conditions stack is a stronger ERP timing signal than any single input

**Hypothesis:**  
The combination of:

- rising `NFCI`
- widening `BAMLH0A0HYM2`
- rising `DFII5` or `DFII10`

predicts materially weaker forward `SPY` excess returns than any one of those inputs in isolation.

**Why it fits the book:**  
This captures Ilmanen's broader point that expected returns are driven by stacked discount-rate and risk-aversion forces, not by one indicator at a time.

**Test design:**
- z-score the three inputs above
- build a daily tightness composite
- compare forward `SPY` excess return over `SOFR` across composite deciles
- test whether the joint score outperforms single-variable forecasts

**Evidence that would support the hypothesis:**
- the composite has stronger monotonic forecasting power than any one input
- worst decile composite readings align with the weakest forward equity outcomes

### Hypothesis ERP-3

**Name:** Cash hurdle plus curve inversion is a forward-looking ERP headwind

**Hypothesis:**  
When the cash hurdle to owning equities is high, as proxied by:

- elevated `SOFR`
- low or falling `T10YIE`
- flat or inverted `T10Y2Y` / `T10Y3M`

subsequent `SPY` excess returns over cash are weaker than average.

**Why it fits the book:**  
Ilmanen's Chapter 7 is explicitly about forward-looking ERP indicators. This translates that logic into a local reduced-form “cash versus risk asset” hurdle measure.

**Test design:**
- define a daily ERP headwind score from `SOFR`, `T10YIE`, `T10Y2Y`, and `T10Y3M`
- compare forward `SPY` excess return over `SOFR` across score quantiles
- test whether the headwind score adds information beyond real yields alone

**Evidence that would support the hypothesis:**
- the highest-hurdle states have the weakest forward equity excess returns
- the joint score outperforms any single short-rate or curve input

### Hypothesis ERP-4

**Name:** Stagflation-risk state has the lowest forward ERP

**Hypothesis:**  
Forward equity excess returns are weakest when both:

- real yields are rising
- inflation expectations are also rising

because equities face simultaneous discount-rate pressure and macro-margin pressure.

**Why it fits the book:**  
This is a forward-looking Chapter 7 state-variable hypothesis, using only the local market-implied inflation and real-rate proxies we already have.

**Test design:**
- classify days by the sign or quantile of:
  - changes in `DFII5` or `DFII10`
  - changes in `T10YIE` or `T5YIE`
- compare forward `SPY` excess return over `SOFR` across the four quadrants

**Evidence that would support the hypothesis:**
- the “real yields up + breakevens up” quadrant has the weakest subsequent equity excess returns
- other quadrants are materially less negative

### Hypothesis ERP-5

**Name:** Liquidity impulse predicts forward ERP

**Hypothesis:**  
Improving liquidity conditions, as proxied by:

- rising `WALCL`
- rising `WRESBAL`
- falling `RRPONTSYD`

predict stronger forward equity excess returns, especially when `NFCI` is also easing.

**Why it fits the book:**  
It extends Ilmanen's ERP discussion from pure discount-rate logic into practical balance-sheet and liquidity channels that matter for realized premia.

**Test design:**
- build a 13-week liquidity-impulse composite from `WALCL`, `WRESBAL`, and inverse `RRPONTSYD`
- combine it with `NFCI`
- compare forward 20d and 60d `SPY` excess returns across liquidity-impulse quantiles

**Evidence that would support the hypothesis:**
- strongest liquidity-impulse readings align with better forward equity excess returns
- the signal is stronger when financial conditions are already improving

### Hypothesis BE-1

**Name:** Bond-equity correlation flips with inflation-expectation regime

**Hypothesis:**  
The rolling correlation between:

- `SPY` returns
- changes in `DGS10`

is more negative when inflation expectations are anchored and funding stress is low, but becomes less negative or positive when:

- `T10YIE` and `T5YIE` are elevated or rising
- the macro regime is inflation shock rather than growth scare

**Why it fits the book:**  
This is the cleanest local expression of Chapter 8's bond-equity interaction argument.

**Test design:**
- compute rolling stock-bond correlation using `SPY` and `DGS10`
- define inflation-expectation states from `T5YIE` and `T10YIE`
- reuse `macro_regime_daily.parquet` from the GMT regime notebook as an additional conditioning layer
- compare average rolling correlation across:
  - low-inflation / stable-carry windows
  - high-inflation / inflation-shock windows

**Evidence that would support the hypothesis:**
- materially more negative stock-bond correlation in anchored-inflation regimes
- meaningful breakdown of diversification during inflation repricing windows

### Hypothesis BE-2

**Name:** Funding stress compresses diversification across risky assets

**Hypothesis:**  
In funding-stress windows defined by combinations of:

- high `SOFR - DFEDTARU`
- wider `BAMLH0A0HYM2`
- worse `NFCI`

correlations rise across risky assets such as:

- `SPY`
- oil proxy `CL=F`
- credit-spread moves

while traditional diversifiers become less reliable.

**Why it fits the book:**  
It extends Chapter 8 from stock-bond correlation into the broader cross-asset diversification question that matters for expected-return portfolios.

**Test design:**
- reuse the existing GMT or FIRV regime panel
- compute regime-specific correlation matrices using:
  - `SPY`
  - `DX-Y.NYB`
  - `GC=F`
  - `CL=F`
  - `DGS10` changes
  - `BAMLH0A0HYM2` changes
- compare risky-asset co-movement in funding stress versus stable carry

**Evidence that would support the hypothesis:**
- risky-asset correlations are materially higher in funding-stress windows
- diversification benefits are best in stable-carry or growth-scare states, not funding stress

### Hypothesis BRP-1

**Name:** Curve steepness forecasts positive bond risk premium

**Hypothesis:**  
When the Treasury curve is steep,

- `T10Y3M`
- `T10Y2Y`

future long-duration performance is stronger than when the curve is flat or inverted, as measured by:

- subsequent declines in `DGS10`
- or a simple duration PnL proxy such as `-D * delta_y`

**Why it fits the book:**  
This is the textbook Chapter 9 bond-risk-premium signal and extends directly from the FIRV curve work.

**Test design:**
- use `T10Y3M` and `T10Y2Y` as steepness measures
- proxy long-duration returns with yield changes in `DGS10` or `^TNX`
- test whether steeper starting curves are followed by lower subsequent long yields or stronger duration returns over 1m to 3m horizons

**Evidence that would support the hypothesis:**
- steeper curves predict better forward duration performance
- the relationship survives when split by macro regime

### Hypothesis BRP-2

**Name:** `T10Y3M` is a cleaner bond-risk-premium predictor than `T10Y2Y`

**Hypothesis:**  
The long-front curve slope measured by `T10Y3M` is a stronger predictor of subsequent duration performance than `T10Y2Y`, because it anchors the front end more directly to the cash rate.

**Why it fits the book:**  
It sharpens Chapter 9 into a predictor-comparison question rather than assuming all slope measures are equivalent.

**Test design:**
- estimate forward duration PnL or subsequent `DGS10` declines using both predictors
- compare monotonicity, t-stats, and hit rates across:
  - `T10Y3M`
  - `T10Y2Y`
- optionally test the predictors inside and outside inflation-shock windows

**Evidence that would support the hypothesis:**
- `T10Y3M` sorts have cleaner monotonic structure
- `T10Y3M` produces stronger forward duration timing than `T10Y2Y`

### Hypothesis BRP-3

**Name:** Curve steepness works best when real yields are already high

**Hypothesis:**  
A steep nominal curve is most informative for forward duration performance when starting real yields are also high, for example:

- `DFII10`
- `DFII5`

because the market has both carry and valuation cushion.

**Why it fits the book:**  
This turns Chapter 9 into an interaction hypothesis between slope and valuation rather than a one-variable predictor.

**Test design:**
- form 2D buckets on:
  - curve steepness (`T10Y3M` or `T10Y2Y`)
  - real-yield level (`DFII10` or `DFII5`)
- compare subsequent duration proxy returns across buckets

**Evidence that would support the hypothesis:**
- the best forward duration outcomes occur in steep-curve, high-real-yield states
- steep curve alone is weaker when starting real yields are already low

### Hypothesis BRP-4

**Name:** Curve curvature predicts forward duration PnL

**Hypothesis:**  
Extreme Treasury curve curvature, for example:

`2 * DGS5 - DGS2 - DGS10`,

predicts subsequent curve normalization and therefore helps forecast a simple long-end duration PnL proxy.

**Why it fits the book:**  
It broadens Chapter 9 from slope-only predictors to the richer yield-curve information already used in the FIRV study.

**Test design:**
- compute a curvature proxy from `DGS2`, `DGS5`, and `DGS10`
- z-score the curvature series
- test whether extreme curvature readings predict:
  - forward `DGS10` declines
  - or a duration PnL proxy such as `-D * delta_y`

**Evidence that would support the hypothesis:**
- curvature extremes predict forward curve normalization
- the signal adds information beyond slope alone

### Hypothesis BRP-5

**Name:** Inflation repricing weakens BRP even when the curve is steep

**Hypothesis:**  
A steep curve is a weaker bond-risk-premium signal when breakevens are rising sharply, because inflation repricing dominates the usual carry and rolldown logic.

**Why it fits the book:**  
It adds an inflation-conditioning layer to Chapter 9 using the exact breakeven series available locally.

**Test design:**
- condition the slope signal on:
  - high versus low `delta T10YIE`
  - or high versus low `delta T5YIE`
- compare forward duration proxy returns across slope-and-breakeven states

**Evidence that would support the hypothesis:**
- steep curves forecast stronger duration outcomes only when inflation repricing is muted
- steep plus rising breakevens produces weaker or opposite bond outcomes

### Hypothesis CRP-1

**Name:** Wide credit spreads with improving liquidity predict risk normalization

**Hypothesis:**  
Extremely wide `BAMLH0A0HYM2` spreads, when combined with improving liquidity or financial conditions,

- lower `NFCI`
- stabilizing `WALCL`
- falling `^VIX`

predict subsequent spread compression and positive `SPY` returns.

**Why it fits the book:**  
It captures Ilmanen's Chapter 10 theme that carry-rich credit environments become attractive when stress starts to mean revert.

**Test design:**
- identify top-decile high-yield spread states
- split those states by whether `NFCI` or `^VIX` is improving
- measure forward change in `BAMLH0A0HYM2` and forward `SPY` return over 5d / 20d / 60d horizons

**Evidence that would support the hypothesis:**
- wide spreads alone are not enough
- wide spreads plus improving liquidity give the strongest compression and equity rebound

### Hypothesis CRP-2

**Name:** Spread widening is an equity tail-risk indicator

**Hypothesis:**  
Large positive daily changes in `BAMLH0A0HYM2` predict worse left-tail outcomes for `SPY` than unconditional days, even over short horizons such as 5d.

**Why it fits the book:**  
It makes Chapter 10 more precise by testing whether credit spreads are not just valuation measures but also near-term stress transmitters.

**Test design:**
- identify top-decile spread-widening days
- compare forward `SPY`:
  - average return
  - hit rate
  - 5d drawdown proxy
- benchmark against unconditional and low-spread-change days

**Evidence that would support the hypothesis:**
- spread-widening shocks coincide with worse subsequent equity downside
- the left-tail effect is stronger than what average returns alone imply

### Hypothesis CRP-3

**Name:** Funding-stress-driven spread widening mean reverts slower than growth-scare widening

**Hypothesis:**  
Credit spread widening caused by funding strain,

- high `SOFR - DFEDTARU`
- worsening `NFCI`

reverts more slowly than spread widening associated with ordinary growth scares.

**Why it fits the book:**  
It separates different drivers of credit premia, which is closer to Ilmanen's practitioner framing than treating all wide spreads as equivalent.

**Test design:**
- classify widening episodes by concurrent:
  - policy-gap stress
  - `NFCI`
  - macro regime
- compare subsequent spread compression speed and `SPY` recovery across episode types

**Evidence that would support the hypothesis:**
- funding-stress episodes show slower compression and weaker equity rebound
- non-funding growth scares normalize faster

### Hypothesis CRP-4

**Name:** Funding and policy tightness amplifies credit-stress transmission

**Hypothesis:**  
Credit spread widening transmits more strongly into equity weakness when short-rate plumbing is already tight, as proxied by:

- high `SOFR`
- high `SOFR - DFEDTARU`
- more inverted `T10Y2Y` or `T10Y3M`

**Why it fits the book:**  
This isolates a plausible driver of why some credit shocks remain contained while others become system-wide risk-off events.

**Test design:**
- identify top-decile `delta BAMLH0A0HYM2` days
- split those days into:
  - tight-plumbing states
  - non-tight-plumbing states
- compare forward `SPY` returns and `^VIX` changes

**Evidence that would support the hypothesis:**
- spread shocks are more damaging to equities when policy and funding are already tight
- the amplification is not explained by VIX alone

### Hypothesis CRP-5

**Name:** Real-yield shock plus credit shock is a stronger risk-off signal than either alone

**Hypothesis:**  
Days with both:

- rising real yields (`DFII5` or `DFII10`)
- widening `BAMLH0A0HYM2`

predict materially worse forward `SPY` returns than days with only one of those shocks.

**Why it fits the book:**  
It stacks discount-rate and credit-risk channels into one Chapter 10 expected-return signal.

**Test design:**
- form a 2x2 state table using the sign or z-score of:
  - `delta DFII5` or `delta DFII10`
  - `delta BAMLH0A0HYM2`
- compare forward 5d and 20d `SPY` returns and drawdowns across quadrants

**Evidence that would support the hypothesis:**
- the joint-shock state has the worst subsequent equity outcomes
- the interaction is stronger than the sum of standalone effects

## Group B: Commodity Risk Premia With Local Proxies

### Hypothesis COM-1

**Name:** Commodity basket premium is strongest in rising-breakeven, weaker-dollar states

**Hypothesis:**  
The CRB-equivalent commodity proxy already built in the GMT study earns its strongest forward returns when:

- `T10YIE` is rising
- `DX-Y.NYB` is weakening

which is a practical local proxy for reflationary commodity risk-premium states.

**Why it fits the book:**  
This is the cleanest local implementation of Chapter 11's commodity-premium discussion without access to full futures-curve carry data.

**Test design:**
- reuse the GMT commodity proxy panel
- define joint states from:
  - `T10YIE` change
  - `DX-Y.NYB` trend or return
- compare forward commodity-basket returns across states

**Evidence that would support the hypothesis:**
- reflation plus weaker-dollar states have the strongest forward commodity returns
- rising breakevens without dollar weakness are less powerful

### Hypothesis COM-2

**Name:** Energy and metals premia separate by macro regime

**Hypothesis:**  
The energy-heavy and metals-heavy commodity proxies already built in the GMT study behave differently across macro states:

- energy outperforms in growth / reflation regimes
- metals outperform in inflation-shock and funding-stress regimes

**Why it fits the book:**  
It recognizes that “commodity premium” is not one thing. Chapter 11 treats commodity exposure as structurally diverse, and the local proxy set is rich enough to test that.

**Test design:**
- reuse the GMT:
  - `energy_proxy`
  - `metals_proxy`
  - macro regime panel
- compare forward energy-minus-metals performance by regime

**Evidence that would support the hypothesis:**
- energy leadership clusters in reflation or risk-on regimes
- metals leadership is stronger when inflation hedging or stress protection dominates

### Hypothesis COM-3

**Name:** Dollar strength is a headwind for commodity premia, especially outside gold

**Hypothesis:**  
A stronger `DX-Y.NYB` is a stronger headwind for:

- energy proxies
- industrial commodity proxies

than for gold, which should behave more like a real-rate hedge than a pure dollar-beta asset.

**Why it fits the book:**  
This separates commodity risk premia into invoicing and macro-sensitivity channels rather than treating all commodities the same.

**Test design:**
- compare rolling and regime-split correlations between `DX-Y.NYB` and:
  - energy proxy
  - metals proxy
  - `GC=F`
- test forward commodity returns after strong positive dollar moves

**Evidence that would support the hypothesis:**
- dollar strength is a more consistent negative predictor for energy and industrial commodities than for gold
- gold's response is weaker or more state-dependent

## Group C: Alternative Premia With Current Local Proxies

### Hypothesis ALT-1

**Name:** Gold is a real-rate hedge, not just a generic risk-off asset

**Hypothesis:**  
`GC=F` returns are negatively related to changes in U.S. real yields,

- `DFII5`
- `DFII10`

and that relationship is strongest in:

- growth-scare regimes
- funding-stress regimes

rather than uniformly across all macro states.

**Why it fits the book:**  
This is the cleanest local expression of Chapter 11's alternative-premia discussion using a liquid alternative asset proxy already in the lake.

**Test design:**
- regress or bucket `GC=F` returns on daily changes in real yields
- split the sample by the existing macro regime panel
- compare gold sensitivity across regimes

**Evidence that would support the hypothesis:**
- gold performs best when real yields fall
- the negative gold-real-yield relationship is materially stronger in stress regimes

### Hypothesis ALT-2

**Name:** Commodity basket tracks inflation repricing more than equity beta

**Hypothesis:**  
The CRB-equivalent commodity proxy already built in the GMT study is more tightly linked to:

- changes in `T10YIE`

than to:

- `SPY` returns

during inflation-shock regimes.

**Why it fits the book:**  
It turns Chapter 11's alternative-premia discussion into a direct cross-asset inflation-sensitivity test.

**Test design:**
- reuse the GMT commodity proxy panel
- compare the correlation of commodity returns with:
  - `T10YIE` changes
  - `SPY` returns
- split by regime using the existing GMT macro panel

**Evidence that would support the hypothesis:**
- commodity returns are more aligned with inflation repricing than with equity beta in inflation-shock windows

### Hypothesis ALT-3

**Name:** Liquidity expansion supports alternative-asset proxy performance

**Hypothesis:**  
When central-bank liquidity is expanding, as proxied by combinations of:

- rising `WALCL`
- rising `WRESBAL`
- falling `RRPONTSYD`

forward returns on local alternative-asset proxies such as:

- `GC=F`
- the GMT commodity basket

are stronger than in liquidity-withdrawal states.

**Why it fits the book:**  
It is a pragmatic Chapter 11 proxy for broader alternative-asset financing conditions in the absence of direct real-estate, private-equity, or hedge-fund datasets.

**Test design:**
- build a simple liquidity-expansion composite from the Fed balance-sheet variables
- compare forward returns of gold and the commodity basket across composite quantiles
- optionally intersect with `NFCI` and macro regime labels

**Evidence that would support the hypothesis:**
- liquidity expansion aligns with stronger forward alternative-proxy returns
- the relationship is strongest when financial conditions are also easing

## Group D: Value Factor Construction

### Hypothesis VAL-1

**Name:** Slow-moving anchor residuals are better value signals than raw levels

**Hypothesis:**  
Value signals work better when defined as residuals versus slow-moving anchors, not as raw price levels. The most feasible local anchors are:

- `DX-Y.NYB` versus PPP-style / real-yield fair value
- duration versus real-yield history
- commodity basket versus breakeven and dollar backdrop

**Why it fits the book:**  
This is the most practical local implementation of Chapter 12 without full textbook fundamental valuation series such as CAPE or earnings yield.

**Test design:**
- build residual-based value signals for DXY, duration, and the GMT commodity proxy
- compare forward returns after extreme residual states versus raw-price z-scores
- standardize signals so the sleeves are comparable

**Evidence that would support the hypothesis:**
- anchor-residual signals mean revert more reliably than raw-price-level signals
- residual-based value signals are less noisy across assets than naive raw levels

### Hypothesis VAL-2

**Name:** Cross-asset value dispersion basket mean reverts better than single-asset value

**Hypothesis:**  
A standardized basket of “rich versus cheap” residuals across:

- DXY
- duration
- commodity proxy

mean reverts more cleanly than any one sleeve alone, because idiosyncratic noise diversifies away.

**Why it fits the book:**  
Ilmanen repeatedly argues that expected-return harvesting works best when premia are diversified rather than concentrated.

**Test design:**
- reuse:
  - `02_dxy_valuation_panel.csv`
  - a duration value proxy from `DFII10` and `DGS10`
  - GMT commodity proxy outputs
- z-score each value sleeve
- form a cross-asset dispersion basket and compare its forward reversion to the standalone sleeves

**Evidence that would support the hypothesis:**
- the basket has a higher hit rate than any single-asset value proxy
- dispersion shrinks more reliably after extreme basket readings

### Hypothesis FXC-1

**Name:** Reduced-form DXY valuation residual mean reverts

**Hypothesis:**  
A reduced-form DXY fair-value model using:

- U.S. 5Y real yield proxy `DFII5`
- a synthetic USD basket from local FX pairs
- a U.S.-CPI-deflated PPP-style anchor

produces a valuation residual that mean reverts over 10d to 20d horizons.

**Why it fits the book:**  
It is a practical Chapter 13 carry and valuation expression built from the exact data currently available in the repo.

**Proxy caveat:**  
The real-rate input is a U.S.-centric real-yield-versus-history proxy, not a true cross-country real-rate differential. A cleaner FX carry and valuation implementation requires foreign CPI and foreign rate curves.

**Test design:**
- reuse `02_dxy_valuation_panel.csv` from the GMT study or rerun `02_fx_valuation.ipynb`
- define rich and cheap DXY residual bands
- test forward normalization of `DX-Y.NYB`
- compare valuation residual signals versus simple DXY trend alone

**Evidence that would support the hypothesis:**
- extreme positive residuals are followed by weaker DXY returns
- extreme negative residuals are followed by stronger DXY returns
- residual-based timing is more informative than raw trend during mixed macro regimes

## Group E: Carry Across Assets

### Hypothesis CARRY-1

**Name:** Bond carry proxy works only when funding stress is absent

**Hypothesis:**  
Bond carry and rolldown proxies are most effective when:

- the curve is steep
- `SOFR - DFEDTARU` is not elevated
- financial conditions are not deteriorating

Even attractive curve carry should be impaired during funding stress.

**Why it fits the book:**  
This is the cleanest local Chapter 13 carry hypothesis for a data lake that has Treasury slopes but not full bond-index carry series.

**Test design:**
- use `T10Y3M` and `T10Y2Y` as carry / rolldown proxies
- define funding stress from `SOFR - DFEDTARU` and `NFCI`
- compare forward duration proxy returns in:
  - steep curve / low stress
  - steep curve / high stress

**Evidence that would support the hypothesis:**
- curve carry works materially better when short-rate plumbing is orderly
- slope alone is not enough in funding-stress windows

### Hypothesis CARRY-2

**Name:** Credit carry is a level-plus-stability signal, not a pure spread-level signal

**Hypothesis:**  
High `BAMLH0A0HYM2` is attractive carry only when default and liquidity stress are no longer worsening. Wide spreads with unstable stress conditions are not reliably harvestable.

**Why it fits the book:**  
It turns the broad Chapter 13 carry idea into an implementable local credit-carry proxy using spread level plus stability.

**Test design:**
- define high-carry states from elevated `BAMLH0A0HYM2`
- split those states by:
  - falling versus rising `NFCI`
  - falling versus rising `^VIX`
- compare forward spread compression and `SPY` performance

**Evidence that would support the hypothesis:**
- wide-but-stabilizing credit outperforms wide-and-worsening credit
- the stability filter adds more value than spread level alone

### Hypothesis CARRY-3

**Name:** Universal carry proxy is fragile in FX because foreign rates are missing

**Hypothesis:**  
A partial local cross-asset carry sleeve can be approximated from:

- bond slope carry
- credit spread carry
- commodity macro-carry surrogate from inflation and dollar backdrop

but the FX sleeve remains the weakest and noisiest until foreign short rates or forward points are ingested.

**Why it fits the book:**  
It makes Chapter 13 explicit about what is and is not testable from the current repo.

**Test design:**
- construct a partial carry basket from bonds, credit, and commodities
- compare it against any reduced-form FX carry surrogate based on:
  - `DFEDTARU`
  - `SOFR`
  - `DX-Y.NYB`
- document signal stability rather than forcing a false “universal carry” claim

**Evidence that would support the hypothesis:**
- non-FX carry sleeves are more stable than FX carry surrogates
- FX carry contributes the most noise to the cross-asset basket

## Group F: Momentum, Crashes, Scaling, and VRP Harvesting

### Hypothesis MOM-1

**Name:** Time-series momentum survives across the local cross-asset basket

**Hypothesis:**  
Simple 1m to 3m time-series momentum signals on:

- `SPY`
- `DX-Y.NYB`
- `GC=F`
- `CL=F`
- long-duration rate proxies

continue to predict same-sign forward returns, especially outside funding-stress windows.

**Why it fits the book:**  
This is the most direct local implementation of Chapter 14.

**Test design:**
- construct 21d, 63d, and 126d trend signals
- test forward 21d returns by signal sign
- condition results on the existing macro regime classification from the GMT and FIRV studies

**Evidence that would support the hypothesis:**
- positive past returns predict positive future returns on average
- signal strength is weaker in funding-stress windows than in stable-carry windows

### Hypothesis MOM-2

**Name:** Value-momentum alignment is stronger than either signal alone

**Hypothesis:**  
When a local value proxy and momentum agree on direction, subsequent returns are stronger than when:

- value says cheap but momentum is negative
- value says rich but momentum is positive

This is most testable first in:

- `DX-Y.NYB`
- long-duration bond proxies

where we already have workable reduced-form value anchors.

**Why it fits the book:**  
It links Chapters 12, 14, and 17 in the way Ilmanen typically does: individual premia matter, but combinations matter more.

**Test design:**
- use valuation residuals from `FXC-1` for DXY
- use curve or term-premium-style proxies for duration valuation
- compute 1m to 3m momentum
- compare forward returns when value and momentum are:
  - aligned
  - neutral
  - in conflict

**Evidence that would support the hypothesis:**
- aligned signals have higher hit rate and better average forward return
- conflicting signals show lower conviction and more noise

### Hypothesis MOM-3

**Name:** Momentum crashes after fast risk-off reversal

**Hypothesis:**  
Cross-asset momentum is most vulnerable after abrupt reversals in prior risk-off trends, especially when:

- `^VIX` falls sharply
- `BAMLH0A0HYM2` compresses quickly
- `SPY` rebounds while `DX-Y.NYB` and `GC=F` reverse

**Why it fits the book:**  
This is the closest local proxy to Ilmanen's Chapter 14 discussion of momentum crashes and reversal episodes.

**Test design:**
- define momentum signals on:
  - `SPY`
  - `DX-Y.NYB`
  - `GC=F`
  - `CL=F`
  - duration proxy
- isolate fast reversal windows using `^VIX`, `BAMLH0A0HYM2`, and asset returns
- compare momentum performance inside and outside those windows

**Evidence that would support the hypothesis:**
- momentum drawdowns cluster in fast reversal episodes
- normal trend periods have much better momentum hit rates

### Hypothesis MOM-4

**Name:** Vol-scaled momentum outperforms raw momentum

**Hypothesis:**  
Volatility-scaled 1m to 3m momentum signals produce:

- smaller drawdowns
- better risk-adjusted returns
- less sensitivity to crisis whipsaws

than raw equal-notional momentum.

**Why it fits the book:**  
This is the cleanest local test of Chapter 14's implementation question: whether scaling improves momentum robustness.

**Test design:**
- compute raw and realized-vol-scaled momentum on the local cross-asset basket
- compare:
  - drawdown
  - Sharpe ratio
  - hit rate
- evaluate especially around stress windows

**Evidence that would support the hypothesis:**
- vol scaling reduces drawdowns materially
- any loss in raw return is offset by stronger risk-adjusted performance

### Hypothesis MOM-5

**Name:** Momentum works best outside funding stress and inflation shock

**Hypothesis:**  
Momentum should work best in:

- stable carry
- ordinary growth-scare regimes

and degrade in:

- funding stress
- inflation shock

because those regimes are more reversal-prone and less orderly.

**Why it fits the book:**  
It gives the existing momentum hypotheses a macro conditioning layer consistent with the rest of the expected-returns framework.

**Test design:**
- reuse `macro_regime_daily.parquet`
- split cross-asset momentum results by regime
- compare forward hit rates and drawdowns by regime

**Evidence that would support the hypothesis:**
- stable-carry windows have the cleanest momentum signal quality
- funding stress and inflation shock have more false positives and larger reversals

### Hypothesis VRP-1

**Name:** Implied-minus-realized vol spread is a harvestable local VRP proxy

**Hypothesis:**  
When `^VIX` is materially above trailing realized `SPY` volatility, subsequent volatility is overpaid relative to realized outcomes, creating a practical local proxy for VRP harvesting.

**Why it fits the book:**  
This is the most defensible Chapter 15 test available without direct option or variance-swap data.

**Test design:**
- compute trailing realized volatility from `SPY` returns
- define a local VRP proxy as:
  - `^VIX - realized_vol`
- test whether high proxy readings predict:
  - lower subsequent realized volatility
  - stronger equity returns
  - VIX normalization

**Evidence that would support the hypothesis:**
- high implied-minus-realized spreads are followed by calmer realized vol and better risk assets
- the proxy behaves like a harvestable premium rather than a one-off fear spike

### Hypothesis VRP-2

**Name:** VRP harvesting works only outside acute stress transitions

**Hypothesis:**  
The implied-realized vol spread is most harvestable when:

- `^VIX` is elevated but stabilizing
- `BAMLH0A0HYM2` is not still widening
- `NFCI` is not deteriorating rapidly

Short-vol style harvesting is weakest during stress transitions, even if the implied-minus-realized spread looks large.

**Why it fits the book:**  
It keeps Chapter 15 honest by distinguishing rich vol from dangerous vol.

**Test design:**
- interact the local VRP proxy with:
  - `delta BAMLH0A0HYM2`
  - `NFCI`
  - macro regime labels
- compare subsequent outcomes in:
  - high-VRP but stabilizing stress
  - high-VRP and worsening stress

**Evidence that would support the hypothesis:**
- the local VRP proxy only works reliably when the stress regime is no longer worsening
- the worst outcomes cluster in high-VRP but worsening-stress windows

## Group G: Combining Premia

### Hypothesis COMBO-1

**Name:** Composite carry-value-momentum beats standalone sleeves

**Hypothesis:**  
An equal-risk composite that combines:

- value proxies
- carry proxies
- momentum proxies

across the locally available asset set produces better risk-adjusted performance than any single sleeve alone.

**Why it fits the book:**  
This is the natural Chapter 17 synthesis and probably the most important portfolio-level claim in the book.

**Test design:**
- define a small local universe:
  - equities via `SPY`
  - rates via duration proxy from `DGS10`
  - FX via `DX-Y.NYB`
  - commodities via the GMT CRB-equivalent proxy
- build one simple value, carry, and momentum signal per sleeve
- volatility-scale each sleeve
- compare standalone versus combined signal portfolios

**Evidence that would support the hypothesis:**
- higher Sharpe ratio for the combination
- smaller drawdowns than the best standalone sleeve
- lower signal correlation across value, carry, and momentum

### Hypothesis COMBO-2

**Name:** Macro-regime gating improves multi-premia portfolios

**Hypothesis:**  
The composite portfolio in `COMBO-1` performs better when signals are gated by macro regime:

- stable carry favors carry and momentum
- growth scare favors duration and defensive quality proxies
- inflation shock favors commodities and selected USD expressions
- funding stress reduces carry exposure

**Why it fits the book:**  
Ilmanen is less discretionary than Gliner, but the expected-return framework still depends on knowing when a premium is structurally rewarded versus temporarily impaired.

**Test design:**
- reuse the existing GMT and FIRV macro regime panels
- run standalone and regime-gated versions of the combined portfolio
- compare hit rate, drawdown, and turnover-adjusted Sharpe

**Evidence that would support the hypothesis:**
- regime gating reduces false positives
- the improvement is largest for carry-oriented signals

## Group H: Tail Risk and Crisis Alpha

### Hypothesis TAIL-1

**Name:** Long USD plus gold plus duration is the cleanest local crisis-alpha basket

**Hypothesis:**  
During acute stress defined by:

- rising `^VIX`
- widening `BAMLH0A0HYM2`
- worsening `NFCI`

a basket long:

- `DX-Y.NYB`
- `GC=F`
- duration proxy from `DGS10`

outperforms risky assets such as `SPY` and high-beta commodities.

**Why it fits the book:**  
This is the cleanest local implementation of Chapter 18.

**Test design:**
- define stress windows using joint thresholds on `^VIX`, `BAMLH0A0HYM2`, and `NFCI`
- compare forward returns of:
  - crisis basket
  - `SPY`
  - oil proxy `CL=F`
- test both equal-weight and volatility-scaled versions

**Evidence that would support the hypothesis:**
- crisis basket has positive average forward return during stress windows
- risky assets underperform materially at the same time

### Hypothesis TAIL-2

**Name:** Momentum is more robust than carry in funding-stress regimes

**Hypothesis:**  
In funding-stress states, momentum signals should degrade less than carry signals because:

- carry depends on orderly financing and mean reversion
- momentum can continue to work when dislocations trend rather than normalize

**Why it fits the book:**  
It is a direct comparison of premium fragility under Chapter 18-style stress.

**Test design:**
- define simple local carry and momentum proxies across DXY, duration, and commodities
- split results by:
  - funding stress
  - non-stress regimes
- compare hit rates and average forward returns

**Evidence that would support the hypothesis:**
- carry hit rate falls sharply in funding stress
- momentum deteriorates less, or even improves, in the same windows

## Suggested Build Order

1. Reuse the existing Ilmanen study notebooks before building new scaffolds.
2. `FXC-1` - extend the already-built DXY valuation scaffold
3. `BE-1` - condition stock-bond correlation on the already-persisted GMT regime panel
4. `BRP-1` - bond risk premium proxy study
5. `CARRY-1` / `CARRY-2` - carry proxy studies in the existing carry notebook
6. `MOM-1` / `MOM-4` - momentum baseline and vol scaling
7. `VRP-1` / `VRP-2` - local volatility risk premium proxy tests
8. `COMBO-1` / `COMBO-2` - combined premia portfolio
9. `TAIL-1` / `TAIL-2` - crisis-alpha and premium fragility tests

## Immediate Next Steps

1. Create markdown-linked notebooks for:
   - bond-equity correlation regime study
   - bond risk premium proxy study
   - value residual basket study
   - cross-asset carry proxy study
   - cross-asset momentum sleeve
   - local VRP proxy study
   - combined value-carry-momentum portfolio
2. Reuse:
   - GMT `macro_regime_daily.parquet`
   - GMT `02_dxy_valuation_panel.csv`
   - GMT commodity proxy outputs
   - existing Ilmanen `03_carry_strategies.ipynb`
   - existing Ilmanen `05_volatility_risk_premium.ipynb`
   rather than rebuilding those inputs from scratch.
3. Add findings-log entries whenever one of the hypotheses above becomes scaffolded or tested.
