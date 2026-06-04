# FIRV Study Hypotheses

Study hypotheses for the main implementation chapters of *Fixed Income Relative Value Analysis (2nd ed.)* that can be explored from the current playground setup.

These are designed to be:

- concrete
- testable with currently available local Treasury data
- directly mappable into the existing notebooks:
  - `01_mean_reversion.ipynb`
  - `02_pca_yield_curve.ipynb`

## Data Available For These Hypotheses

Local Treasury/FRED curve series currently available in the study environment:

- `DGS2`, `DGS3`, `DGS5`, `DGS7`, `DGS10`, `DGS20`, `DGS30`
- `SOFR`, `DFEDTARU`
- `T10Y2Y`, `T10Y3M`

Primary working sample in the current lake:

- approximately `2024-02-26` to `2026-02-25`

## Chapter 2: Mean Reversion

### Hypothesis MR-1

**Name:** 2s5s10s butterfly mean reversion

**Hypothesis:**  
The Treasury `2s5s10s` butterfly,

`2 * DGS5 - DGS2 - DGS10`,

is mean reverting over the current sample, and extreme z-score states tend to decay over the following 5 to 20 trading days.

**Why it fits Chapter 2:**  
This is the cleanest local proxy for the book’s rates-butterfly mean-reversion examples.

**Data and construction:**
- Load `DGS2`, `DGS5`, `DGS10`
- Construct butterfly in yield terms
- Fit a discrete OU approximation
- Compute rolling z-scores, half-life, and conditional forward changes

**Test design:**
- Estimate OU parameters on an expanding or rolling basis
- Bucket current z-score into bands such as:
  - `z < -1.5`
  - `-1.5 <= z <= 1.5`
  - `z > 1.5`
- Measure average forward change in the spread over 5d, 10d, and 20d horizons
- Check whether positive z-scores are followed by negative spread changes and vice versa

**Evidence that would support the hypothesis:**
- positive mean-reversion speed estimate
- finite, economically plausible half-life
- sign-consistent forward reversals after extreme z-score states
- residual variance small enough that the expected move is not swamped immediately by noise

**Failure modes to watch:**
- structural drift rather than stable mean reversion
- regime instability across the sample
- reversals only showing up because of one short subperiod

### Hypothesis MR-2

**Name:** Front-end policy spread mean reversion

**Hypothesis:**  
The front-end spread between Treasury 2Y yields and short-rate/funding proxies,

for example `DGS2 - SOFR` or `DGS2 - DFEDTARU`,

mean reverts after extreme widening or tightening because the market repeatedly overshoots policy-path expectations.

**Why it fits Chapter 2:**  
It tests whether policy-sensitive rates dislocate and then normalize, which is a strong Chapter 2-style spread candidate.

**Data and construction:**
- Load `DGS2`, `SOFR`, `DFEDTARU`
- Build one or both spreads:
  - `DGS2 - SOFR`
  - `DGS2 - DFEDTARU`
- Fit OU-style dynamics separately for each spread

**Test design:**
- Compare OU parameter stability across the two spread definitions
- Evaluate whether spread extremes predict reversal in subsequent 5d/10d/20d windows
- Compare reversal strength before and after sharp policy repricing episodes in the sample

**Evidence that would support the hypothesis:**
- positive mean-reversion estimates in both definitions
- stronger reversal after unusually large front-end repricing episodes
- similar directional behavior across `SOFR` and `DFEDTARU` versions

**Failure modes to watch:**
- spread is dominated by a trend in the policy cycle
- one proxy behaves very differently from the other
- sample too short to distinguish mean reversion from simple noise

### Hypothesis MR-3

**Name:** Long-end versus intermediate-curve spread mean reversion

**Hypothesis:**  
The long-end richness/cheapness relationship,

for example `(DGS30 - DGS10)` or a long-end butterfly such as `DGS30 - 2 * DGS20 + DGS10`,

exhibits slower but still detectable mean reversion after large deviations.

**Why it fits Chapter 2:**  
It tests a different part of the curve where duration supply/demand imbalances may create temporary dislocations with longer half-lives.

**Data and construction:**
- Load `DGS10`, `DGS20`, `DGS30`
- Build:
  - spread version: `DGS30 - DGS10`
  - curvature version: `DGS30 - 2 * DGS20 + DGS10`

**Test design:**
- Fit OU-style models for both series
- Compare half-lives against the `2s5s10s` butterfly
- Evaluate whether larger entry thresholds are needed to compensate for slower reversion

**Evidence that would support the hypothesis:**
- positive but slower mean-reversion speed than the belly butterfly
- larger absolute dislocations are associated with stronger subsequent reversals
- curvature version gives cleaner reversion than the raw 30s10s spread

**Failure modes to watch:**
- no stable long-run mean
- sensitivity to small sample changes
- dominant trend effects from inflation or term-premium repricing

## Chapter 3: PCA-Based Trade Ideas

These hypotheses should use the rolling PCA implementation in `02_pca_yield_curve.ipynb`, including:

- rolling explained variance
- latest loadings
- tenor-level residuals
- PCA-neutral weight construction

### Hypothesis PCA-1

**Name:** Single-tenor residual snapback

**Hypothesis:**  
When a single Treasury tenor shows an unusually large rolling PCA residual z-score, that residual tends to partially normalize over the next 5 to 10 trading days.

**Why it fits Chapter 3:**  
This is the most direct use of PCA as a residual-screening device.

**Data and construction:**
- Use rolling PCA on daily changes in:
  - `DGS2`, `DGS3`, `DGS5`, `DGS7`, `DGS10`, `DGS20`, `DGS30`
- Reconstruct each day’s move from the first 3 factors
- Define residuals and residual z-scores by tenor

**Trade idea:**
- For the tenor with the most extreme positive residual z-score:
  - fade cheapening by going long that tenor versus a factor-matched hedge
- For the tenor with the most extreme negative residual z-score:
  - fade richness by going short that tenor versus the hedge

**Test design:**
- Rank residual z-scores each day
- Form a signal only when `|z| > 1.5` or `|z| > 2.0`
- Track subsequent residual mean reversion over 5d/10d horizons

**Evidence that would support the hypothesis:**
- extreme residuals decay materially faster than non-extreme residuals
- decay is not concentrated in only one tenor
- signal is stronger after factor-stable windows

### Hypothesis PCA-2

**Name:** PCA-neutral belly butterfly reversion

**Hypothesis:**  
A `2Y / 5Y / 10Y` butterfly that is neutral to the first two rolling PCA factors reverts more cleanly than the raw `2s5s10s` butterfly.

**Why it fits Chapter 3:**  
This is the natural Chapter 3 extension of Chapter 2: remove broad factor exposure first, then test the residual trade.

**Data and construction:**
- Use the notebook’s PCA-neutral weight solver with:
  - belly = `DGS5`
  - wings = `DGS2`, `DGS10`
  - factor neutrality = `PC1`, `PC2`
- Build the weighted trade spread and its rolling z-score

**Trade idea:**
- Enter short when trade z-score is high
- Enter long when trade z-score is low
- Compare realized reversion of:
  - raw `2s5s10s`
  - PCA-neutral `2Y/5Y/10Y`

**Test design:**
- Estimate rolling z-scores for both series
- Compare:
  - half-life
  - hit rate of sign-correct reversals after entry
  - stability across rolling windows

**Evidence that would support the hypothesis:**
- PCA-neutral structure has lower variance unexplained by factor shifts
- z-score extremes reverse more reliably than in the raw butterfly
- trade path is less contaminated by large level/slope shocks

### Hypothesis PCA-3

**Name:** Factor-instability regime filter for trade selection

**Hypothesis:**  
PCA-based RV trades work better when the rolling explained variance and eigenvector shapes are stable; performance deteriorates when factor structure shifts abruptly.

**Why it fits Chapter 3:**  
The book explicitly warns about eigenvector instability and factor correlation changing across subperiods.

**Data and construction:**
- Use rolling PCA outputs:
  - explained variance by PC
  - latest eigenvectors
  - PCA-neutral trade z-scores
- Define a simple factor-stability filter, for example:
  - rolling change in `PC1` explained variance below threshold
  - rolling correlation of current versus prior eigenvectors above threshold

**Trade idea:**
- Only allow PCA-neutral butterfly or single-tenor residual trades when factor structure is stable
- Skip entries when factor geometry is changing sharply

**Test design:**
- Split signals into:
  - stable-factor regime
  - unstable-factor regime
- Compare mean forward spread reversal or signal hit rate across the two groups

**Evidence that would support the hypothesis:**
- trades entered during stable-factor windows revert more cleanly
- unstable-factor periods show more false positives or weaker normalization
- filter reduces signal count but improves average quality

## Chapters 5 Through 12: Financial-Model and Market-Structure Hypotheses

These hypotheses extend the study from pure statistical dislocations into fixed-income mechanics, fitted curves, and spread-package logic. Some are directly testable with current Treasury data; others are concrete next studies contingent on ingesting additional market structure data.

## Chapter 5: Yield, Duration, and Convexity

### Hypothesis DVC-1

**Name:** Duration-neutral is not risk-neutral in long-end curve trades

**Hypothesis:**  
A Treasury barbell-versus-bullet trade that is neutral on first-order duration alone still exhibits systematic PnL asymmetry on large curve-move days because convexity mismatch becomes economically meaningful.

**Why it fits Chapter 5:**  
The chapter warns against treating duration neutrality as complete risk neutrality.

**Data and construction:**
- Use `DGS5`, `DGS10`, `DGS20`, `DGS30`
- Approximate zero-coupon modified duration and convexity from maturity and yield
- Build a duration-matched barbell/bullet structure, for example:
  - long 5Y and 30Y barbell
  - short 10Y or 20Y bullet

**Test design:**
- Compute hedge weights using duration only
- Compare predicted daily PnL from:
  - linear duration approximation
  - duration + convexity approximation
- Focus on large-move days, for example top decile of absolute `DGS10` changes

**Evidence that would support the hypothesis:**
- convexity-adjusted PnL explains realized move impact better than linear-only PnL
- duration-only hedges show persistent residual exposure on shock days
- long-end structures show stronger convexity sensitivity than belly structures

**Failure modes to watch:**
- sample too calm for convexity effects to separate clearly
- constant-maturity yields too coarse to mimic true bond-package PnL

### Hypothesis DVC-2

**Name:** Convexity mismatch contaminates curve-flattener signals

**Hypothesis:**  
Apparent relative-value signals in duration-matched steepeners/flatteners are partially false positives when convexity mismatch is ignored, especially for `10s30s` structures.

**Why it fits Chapter 5:**  
This tests a specific misapplication trap: interpreting a curve trade as “hedged” when the second-order risk is still large.

**Data and construction:**
- Use `DGS10` and `DGS30`
- Build a duration-matched `10s30s` flattener/steepener
- Compute approximate convexity-adjusted exposure

**Test design:**
- Compare signal quality with and without convexity adjustment
- Measure whether extreme `10s30s` z-scores still imply the same trade direction after convexity correction
- Track realized forward returns after entry in both frameworks

**Evidence that would support the hypothesis:**
- convexity-adjusted entry rules reduce false positives
- large `10s30s` moves are less attractive once second-order risk is included

**Failure modes to watch:**
- convexity correction too small to matter in this sample
- signal dominated by macro trend rather than hedging error

## Chapter 6: Yield Curve Model Regime Caution

### Hypothesis YC-1

**Name:** Event-day curve moves are too heavy-tailed for naive Gaussian RV sizing

**Hypothesis:**  
Daily Treasury curve changes contain enough event-day tail risk that RV signals based on normal-noise assumptions should be downweighted or filtered on shock days.

**Why it fits Chapter 6:**  
The chapter’s model discussion implies that richer dynamics than simple Gaussian curve shocks may matter in practice.

**Data and construction:**
- Use daily changes in `DGS2`, `DGS5`, `DGS10`, `DGS30`
- Compare empirical tail frequencies against Gaussian benchmarks

**Test design:**
- Standardize daily changes by rolling volatility
- Count exceedances beyond `2σ` and `3σ`
- Check whether residual-based signals entered on shock days mean revert less reliably

**Evidence that would support the hypothesis:**
- empirical tails exceed Gaussian expectations materially
- trade outcomes deteriorate when entered during shock regimes

## Chapter 7: Bond Futures Cheapest-to-Deliver Dynamics

### Hypothesis CTD-1

**Name:** CTD richness signals are strongest when delivery basket ranking is stable

**Hypothesis:**  
Within a Treasury futures delivery basket, relative richness/cheapness between candidate deliverables should be more predictive when the cheapest-to-deliver ranking is stable and switch risk is low.

**Why it fits Chapter 7:**  
This connects fitted-value or richness signals to the delivery-option mechanics of bond futures.

**Data required beyond current local lake:**
- deliverable bond basket
- conversion factors
- futures prices
- repo / financing inputs
- bond cash prices and accrued interest

**Test design once data is available:**
- estimate net basis and identify CTD
- rank candidate bonds by fitted-curve residual
- split observations into:
  - stable CTD windows
  - near-switch windows
- compare richness-signal decay across the two groups

**Evidence that would support the hypothesis:**
- fitted richness/cheapness has cleaner predictive content in stable-CTD windows
- near-switch windows show more noise because delivery option dominates

### Hypothesis CTD-2

**Name:** CTD switch probability rises when candidate richness gaps compress

**Hypothesis:**  
CTD switches are more likely when the richness/cheapness gap between adjacent delivery candidates narrows and the curve level approaches historical switch boundaries.

**Why it fits Chapter 7:**  
This turns the delivery-option logic into a regime-detection study.

**Data required beyond current local lake:**
- same as CTD-1

**Test design once data is available:**
- estimate fitted richness for top CTD candidates
- monitor relative residual compression
- classify pre-switch versus non-switch windows

**Evidence that would support the hypothesis:**
- switch episodes are preceded by compression in candidate residual gaps
- switch risk correlates with curve-level or slope shifts

## Chapter 8: Fitted Curve Richness and Cheapness

### Hypothesis FC-1

**Name:** Fitted-curve residuals mean revert more cleanly than raw slope spreads

**Hypothesis:**  
Residuals from a fitted Treasury curve provide a cleaner richness/cheapness signal than raw pairwise or slope spreads because they isolate local mispricing from broad curve shape.

**Why it fits Chapter 8:**  
This is the core fitted-curve RV idea.

**Data and construction:**
- Use current Treasury constant-maturity curve
- Fit a Nelson-Siegel-style curve daily or at regular intervals
- Define residuals by tenor

**Test design:**
- compare residual z-score reversion against:
  - `10s2s`
  - `30s10s`
  - `2s5s10s`
- measure 5d/10d forward normalization

**Evidence that would support the hypothesis:**
- fitted residuals show faster and more stable decay than raw spread signals
- richest/cheapest tenor ranking is more informative than raw curve-slope rank

### Hypothesis FC-2

**Name:** Belly tenors generate the most persistent fitted-curve dislocations

**Hypothesis:**  
Intermediate maturities such as `5Y` and `7Y` generate more repeatable richness/cheapness dislocations than the front end or long end because they are influenced by both macro factor moves and maturity-selection effects.

**Why it fits Chapter 8:**  
It tests where fitted-curve RV should be concentrated.

**Data and construction:**
- use daily fitted-curve residuals for `DGS2`, `DGS3`, `DGS5`, `DGS7`, `DGS10`, `DGS20`, `DGS30`

**Test design:**
- compute residual z-score excursions by tenor
- compare reversion strength and half-life across tenor buckets

**Evidence that would support the hypothesis:**
- `5Y` and `7Y` residuals mean revert more consistently than front-end or long-end residuals
- belly residuals produce more stable signal hit rates

## Chapter 9: Analytic Process for Government Bond Markets

### Hypothesis GBP-1

**Name:** PCA maturity selection plus fitted-curve residuals beats either method alone

**Hypothesis:**  
The Chapter 9 process,

1. PCA for maturity/trade structure selection  
2. fitted-curve residuals for security selection,

produces cleaner signals than using either PCA residuals alone or fitted-curve residuals alone.

**Why it fits Chapter 9:**  
This is the chapter’s core integrated workflow.

**Data and construction:**
- use the rolling PCA notebook outputs
- fit a curve and compute tenor-level fitted residuals
- only act on fitted residuals in maturities that PCA already highlights as locally dislocated

**Test design:**
- compare three variants:
  - PCA-only residual screen
  - fitted-curve-only residual screen
  - Chapter 9 combined process
- evaluate forward residual normalization

**Evidence that would support the hypothesis:**
- combined screen yields fewer but higher-quality entries
- average forward reversion is stronger after combined filtering

## Chapter 11: Reference Rate Regime Conditioning

### Hypothesis RR-1

**Name:** Funding regime should condition swap-spread and ASW signals

**Hypothesis:**  
Relative-value signals connected to swap spreads or asset swaps should be segmented by funding regime, proxied locally by `SOFR`, `DFEDTARU`, `T10Y2Y`, and inflation-expectation measures such as `T5YIE` and `T10YIE`.

**Why it fits Chapter 11:**  
The chapter argues that reference-rate spreads are not neutral background variables; they are a core driver of relative value.

**Data and construction:**
- use local series:
  - `SOFR`
  - `DFEDTARU`
  - `T10Y2Y`
  - `T10Y3M`
  - `T5YIE`
  - `T10YIE`

**Test design:**
- define regime buckets such as:
  - SOFR above / below policy target
  - steep / flat / inverted curve
  - rising / falling inflation expectations
- test whether later asset-swap or fitted-curve signals behave differently across these buckets

**Evidence that would support the hypothesis:**
- signal quality differs materially by funding regime
- the same richness measure has different persistence depending on the reference-rate backdrop

## Chapter 12: Asset Swap Spread Regime Analysis

### Hypothesis ASW-1

**Name:** Asset swap spread reversion is regime-dependent

**Hypothesis:**  
Asset swap spreads mean revert within stable funding regimes but become trend-like across funding regime breaks.

**Why it fits Chapter 12:**  
It directly tests the cyclicality and driver decomposition emphasized in the chapter.

**Data required beyond current local lake:**
- asset swap spread history by tenor
- cash bond pricing inputs
- swap curve inputs

**Locally available regime features already usable:**
- `SOFR`
- `DFEDTARU`
- `T10Y2Y`, `T10Y3M`
- `T5YIE`, `T10YIE`
- optional macro/credit stress proxies from the broader FRED lake

**Test design once ASW data is ingested:**
- estimate simple mean-reversion diagnostics for ASW spreads by tenor
- segment observations by funding regime
- compare half-life, signal hit rate, and false-positive rate across regimes

**Evidence that would support the hypothesis:**
- ASW reversion is materially stronger in stable regimes than in transition regimes
- unconditional reversion estimates hide meaningful regime dependence

### Hypothesis ASW-2

**Name:** Belly asset swap spreads are the most cyclically informative

**Hypothesis:**  
`5Y` to `10Y` asset swap spreads contain more cyclical and regime-sensitive relative-value information than the front end or long end.

**Why it fits Chapter 12:**  
The chapter stresses term-structure and cyclicality, which often express most cleanly in the belly.

**Data required beyond current local lake:**
- tenor-level asset swap spread history

**Test design once ASW data is ingested:**
- compare regime-conditioned mean reversion across:
  - front end
  - belly
  - long end
- relate regime differences to funding and inflation variables

**Evidence that would support the hypothesis:**
- belly tenors show larger and more tradable cyclical swings
- long-end ASW spreads are more trend-sensitive and less cleanly mean reverting

## Chapters 13 Through 20: Cross-Market, Options, and Macro Overlay Hypotheses

These hypotheses extend FIRV into credit-spread systems, basis relationships, options RV, and top-down regime conditioning. Most require additional market data, but the regime logic and test structure can already be specified.

## Chapter 13: Credit Default Swaps

### Hypothesis CDS-1

**Name:** CDS curve residuals and risk-free curve residuals diverge most during sovereign stress

**Hypothesis:**  
If sovereign or credit-default-swap curves are decomposed with PCA, their residual dislocations should co-move with risk-free curve residuals in calm regimes but decouple sharply in credit-stress episodes.

**Why it fits Chapter 13:**  
The chapter explicitly pairs CDS curve structure with PCA and comparisons to risk-free bond yields.

**Data required beyond current local lake:**
- CDS term structures or sovereign CDS quotes by tenor
- matching risk-free yield curves

**Test design once data is available:**
- fit rolling PCA on CDS curves and risk-free curves separately
- define tenor residual z-scores in both spaces
- compare residual co-movement across calm versus stress regimes

**Evidence that would support the hypothesis:**
- residual co-movement weakens materially during stress
- CDS residuals lead or amplify sovereign-risk episodes

## Chapter 14: Intra-Currency Basis Swaps

### Hypothesis ICBS-1

**Name:** Intra-currency basis dislocations mean revert within reference-rate regime buckets

**Hypothesis:**  
Intra-currency basis spreads should show cleaner mean reversion when analyzed within stable reference-rate regimes rather than across the full sample.

**Why it fits Chapter 14:**  
Basis is a structural building block, and the book treats it as a spread system shaped by reference-rate mechanics.

**Data required beyond current local lake:**
- intra-currency basis swap quotes by tenor
- relevant domestic reference-rate curves

**Test design once data is available:**
- define basis spreads by tenor
- bucket observations by reference-rate regime
- compare half-life and forward reversal across buckets

**Evidence that would support the hypothesis:**
- within-regime mean reversion is materially stronger than unconditional mean reversion

## Chapter 15: Cross-Currency Basis Regime Dynamics

### Hypothesis CCBS-1

**Name:** Dollar funding stress widens cross-currency basis dislocations

**Hypothesis:**  
Cross-currency basis dislocations should be most extreme when USD funding stress rises, proxied by combinations of `SOFR`, `DFEDTARU`, curve inversion, and broad dollar strength.

**Why it fits Chapter 15:**  
The chapter frames cross-currency basis as a funding and hedging relationship, not a static spread.

**Data currently available locally for regime conditioning:**
- `SOFR`
- `DFEDTARU`
- `T10Y2Y`, `T10Y3M`
- FX spot proxies: `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`, `USDCAD=X`, `DX-Y.NYB`

**Missing direct market inputs:**
- FX forward points
- foreign OIS curves
- quoted cross-currency basis swap spreads

**Test design once CCBS data is available:**
- define funding-stress regimes from local USD proxies
- compare basis level, persistence, and reversal speed across regimes
- evaluate whether basis dislocations are largest when USD funding and dollar strength rise together

**Evidence that would support the hypothesis:**
- wider and more persistent basis dislocations in USD-stress regimes
- smaller or faster-closing dislocations in calm funding regimes

### Hypothesis CCBS-2

**Name:** FX-hedged foreign bond attractiveness is regime-dependent

**Hypothesis:**  
The relative attractiveness of buying foreign bonds and hedging back to USD should vary systematically with cross-currency basis regime, so the same nominal yield advantage is not equally valuable across funding states.

**Why it fits Chapter 15:**  
The chapter emphasizes issuing and investing in foreign bonds without FX exposure.

**Data required beyond current local lake:**
- foreign sovereign or high-grade bond yields
- FX forwards / hedging costs
- CCBS or equivalent hedging basis data

**Test design once data is available:**
- compute FX-hedged yield pickup by market
- compare pickup stability across funding regimes
- isolate when hedged foreign carry survives basis costs

**Evidence that would support the hypothesis:**
- hedged pickup compresses or disappears in stressed basis regimes
- stable basis regimes preserve more of the nominal pickup

## Chapter 16: Interactions Between Asset, Basis, and CDS Spreads

### Hypothesis INT-1

**Name:** Spread-system inconsistencies are strongest during balance-sheet stress

**Hypothesis:**  
Violations or distortions of the equilibrium relationships between asset swaps, basis swaps, and CDS should be most visible during periods when dealer balance-sheet constraints are binding.

**Why it fits Chapter 16:**  
This chapter is about the joint equilibrium and its breakdowns.

**Data required beyond current local lake:**
- asset swap spreads
- cross-currency basis spreads
- CDS spreads
- balance-sheet or funding stress proxies

**Test design once data is available:**
- construct theoretical parity gaps across spread systems
- compare gap size and persistence across funding/liquidity regimes

**Evidence that would support the hypothesis:**
- parity gaps widen during funding stress and shrink in calm regimes
- gaps cluster in specific tenor buckets or issuer groups

## Chapter 17: Global Bond RV via Fitted Curves and SOFR Asset Swap Spreads

### Hypothesis GLB-1

**Name:** Fitted-curve cheapness and SOFR-adjusted cheapness diverge most in funding stress

**Hypothesis:**  
A bond can appear cheap on fitted-curve metrics but not on SOFR-adjusted asset-swap metrics, and that divergence should be largest when funding conditions are tight.

**Why it fits Chapter 17:**  
The chapter explicitly combines fitted curves and SOFR asset-swap spreads into a global RV lens.

**Data required beyond current local lake:**
- fitted-curve residuals from local or ingested bond data
- SOFR asset-swap spreads
- bond-level market inputs

**Test design once data is available:**
- compute both cheapness measures for the same bonds
- classify days by funding regime
- measure how often the two signals agree versus diverge

**Evidence that would support the hypothesis:**
- stronger disagreement in stressed funding regimes
- cleaner convergence when both signals point the same way

## Chapter 18: Haircuts, Margins, and Regulation

### Hypothesis REG-1

**Name:** Funding-constraint regimes increase persistence of RV dislocations

**Hypothesis:**  
When collateral and margin conditions are effectively tighter, relative-value dislocations should persist longer because arbitrage capital is slower to engage.

**Why it fits Chapter 18:**  
The chapter frames haircuts and regulation as real constraints on spread convergence.

**Data currently usable as rough regime proxies:**
- `SOFR`
- `DFEDTARU`
- curve inversion variables
- credit/liquidity proxies from the broader FRED lake when needed

**Missing direct inputs:**
- haircut schedules over time
- margin requirement series
- dealer balance-sheet stress measures mapped to instrument set

**Test design once spread data is available:**
- split signal episodes by funding-constraint proxy regime
- compare half-life and convergence probability

**Evidence that would support the hypothesis:**
- convergence slows materially in tighter funding regimes
- signal tails become fatter when funding constraints bite

## Chapter 19: Options Implied Vol Surface RV

### Hypothesis VOL-1

**Name:** Implied-vol surface residuals mean revert after factor removal

**Hypothesis:**  
Residual dislocations in an implied-vol surface, after removing the dominant level/slope/term-structure factors, should mean revert over short to medium horizons.

**Why it fits Chapter 19:**  
The chapter generalizes RV logic to option structures and factor models in the vega sector.

**Data required beyond current local lake:**
- option implied-vol surface snapshots by maturity and strike or delta
- consistent surface normalization

**Test design once data is available:**
- fit PCA or factor model on the surface
- compute residuals by node or sector
- test whether large residual z-scores normalize over 1d/5d/10d horizons

**Evidence that would support the hypothesis:**
- residual surface distortions decay faster than raw implied-vol changes
- signal quality improves when trades are factor-neutralized

### Hypothesis VOL-2

**Name:** Vega-sector mean reversion is strongest in intermediate expiries

**Hypothesis:**  
After decomposing the vega sector into factors, intermediate-expiry residuals should mean revert more reliably than very short-dated or very long-dated residuals.

**Why it fits Chapter 19:**  
This is the options analogue of fitted-curve and PCA residual concentration in the belly.

**Data required beyond current local lake:**
- options surface / vega sector data

**Test design once data is available:**
- build vega-bucket factors
- compare residual z-score reversion by expiry bucket

**Evidence that would support the hypothesis:**
- mid-expiry residuals show better hit rate and cleaner decay
- front-end residuals are noisier and more event-sensitive

## Chapter 20: Macro Regime Overlay for RV Signals

### Hypothesis MACRO-1

**Name:** RV signals should be gated by macro regime

**Hypothesis:**  
The same RV signal has different persistence and false-positive behavior across macro regimes, so a simple regime overlay should improve signal quality relative to unconditional trading.

**Why it fits Chapter 20:**  
The chapter broadens RV into a macro/system context rather than treating trades as isolated statistical objects.

**Locally available regime features:**
- `SOFR`, `DFEDTARU`
- `T10Y2Y`, `T10Y3M`
- `T5YIE`, `T10YIE`
- `UNRATE`, `BAMLH0A0HYM2`, `NFCI` where needed from the FRED macro lake

**Test design:**
- create macro regimes such as:
  - inflation shock
  - growth scare / flight-to-quality
  - stable carry regime
  - funding stress regime
- compare signal hit rate and half-life across:
  - Chapter 2 mean-reversion trades
  - Chapter 3 PCA residual trades
  - fitted-curve residual trades

**Evidence that would support the hypothesis:**
- signal performance differs materially across macro buckets
- regime-conditioned trades reduce false positives and improve average reversal quality

### Hypothesis MACRO-2

**Name:** Macro overlays matter most for cross-market and funding-linked RV

**Hypothesis:**  
Macro regime overlays should add more value to cross-market and funding-linked trades (basis, asset swaps, global bond RV) than to simple local curve dislocations.

**Why it fits Chapter 20:**  
It tests where top-down conditioning is most necessary.

**Test design:**
- compare regime overlay improvement across:
  - local curve butterflies
  - PCA residual tenor trades
  - fitted-curve cheapness
  - basis / ASW / global-RV signals once data exists

**Evidence that would support the hypothesis:**
- larger uplift from regime conditioning for funding-linked and cross-market trades than for local curve trades

## Recommended Execution Order

1. Test `MR-1` first
   - it is the cleanest and most directly scaffolded study
2. Test `PCA-2` next
   - it is the strongest bridge from Chapter 2 to Chapter 3
3. Then add `PCA-1`
   - tenor-level residual screen
4. Finally test `MR-2`, `MR-3`, and `PCA-3`
   - more regime-sensitive and sample-sensitive

## Minimal Deliverables For The Next Study Pass

- `01_mean_reversion.ipynb`
  - implement forward-return diagnostics for `MR-1` and `MR-2`
- `02_pca_yield_curve.ipynb`
  - compute rolling residual z-score snapshots
  - backfill simple signal tables for `PCA-1` and `PCA-2`
  - add a factor-stability metric for `PCA-3`
