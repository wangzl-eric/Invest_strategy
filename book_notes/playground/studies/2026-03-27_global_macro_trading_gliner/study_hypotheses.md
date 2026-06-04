# GMT Study Hypotheses

Testable hypotheses for *Global Macro Trading: Profiting in a New World Economy* by Greg Gliner.

These hypotheses are designed to:

- reflect the book's practitioner-style mental models
- connect global macro themes to the repo's existing quant infrastructure
- use data that is already available in the local FRED / market-data lake

## Material Score

| Dimension | Score | Reason |
|-----------|-------|--------|
| Credibility | 4/5 | Practitioner-oriented Wiley macro text with coherent trade-process framing |
| Relevance | 5/5 | Directly aligned with multi-asset, regime-based macro research |
| Actionability | 5/5 | Most ideas can be prototyped immediately with local FRED and market price data |

The book clears the `>= 3/5` threshold on all dimensions and warrants deeper follow-up.

## Local Data We Can Use Now

### FRED / Macro

- `SOFR`
- `DFEDTARU`
- `T10Y2Y`
- `T10Y3M`
- `T5YIE`
- `T10YIE`
- `UNRATE`
- `CPIAUCSL`
- `BAMLH0A0HYM2`
- `NFCI`

### Market / Price Proxies

- `^GSPC`, `^NDX`, `^RUT`, `^VIX`
- `DX-Y.NYB`
- `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`
- `GC=F`, `CL=F`

## Group A: Cross-Asset Signal Construction

### Hypothesis XA-1

**Name:** Cross-asset risk-on basket predicts equity breadth

**Hypothesis:**  
A simple cross-asset composite built from:

- curve steepening (`T10Y2Y`, `T10Y3M`)
- tighter financial conditions (`NFCI`)
- tighter credit spreads (`BAMLH0A0HYM2`)
- lower implied volatility (`^VIX`)

predicts subsequent 10d to 20d relative outperformance of:

- `^RUT` versus `^GSPC`
- `^NDX` versus `^GSPC`

depending on whether the regime is reflationary or disinflationary.

**Why it fits the book:**  
It operationalizes Gliner's “macro theme -> cleanest asset expression” framework across rates, credit, and equities.

**Test design:**
- standardize each input into z-scores
- build a daily risk-on composite
- test whether extreme composite readings predict forward relative returns

**Evidence that would support the hypothesis:**
- strongest risk-on signals are followed by broad beta leadership
- weakest risk-on signals are followed by defensive / large-cap leadership

### Hypothesis XA-2

**Name:** Inflation shock basket identifies cross-asset rotation

**Hypothesis:**  
When inflation expectations rise sharply and curve signals do not confirm growth fear, the cross-asset winners should be:

- `CL=F`
- `GC=F`
- `DX-Y.NYB` sensitivity depending on whether the inflation shock is USD-policy-led

while duration-sensitive equities and long-end bonds should lag.

**Why it fits the book:**  
It turns a broad macro “inflation shock” theme into a tractable cross-asset relative-value study.

**Test design:**
- define an inflation shock score from `T5YIE`, `T10YIE`, `SOFR`, and curve-slope controls
- test forward 5d / 10d performance of oil, gold, dollar, and equity proxies under high-score episodes

**Evidence that would support the hypothesis:**
- commodity and inflation-hedge assets outperform in top inflation-shock states
- the sign and magnitude of dollar response depend on whether the rate move is policy-tightening or growth-driven

## Group B: Macro Regime Indicators

### Hypothesis REG-1

**Name:** Four macro regimes improve signal conditioning

**Hypothesis:**  
A four-regime classification using:

- `SOFR`
- `DFEDTARU`
- `T10Y2Y`
- `T10Y3M`
- `T5YIE`
- `T10YIE`

can separate:

1. inflation shock
2. growth scare
3. stable carry
4. funding stress

and improve the hit rate of cross-asset macro signals relative to unconditional trading.

**Why it fits the book:**  
Gliner repeatedly emphasizes process and context rather than single-signal trading.

**Test design:**
- define rule-based regimes
- compare trade hit rates with and without regime gating
- evaluate which assets or signals behave best in each regime

**Evidence that would support the hypothesis:**
- materially different hit rates by regime
- fewer false positives when signals are only traded in the “right” backdrop

### Hypothesis REG-2

**Name:** Stable carry regime is the cleanest environment for systematic macro signals

**Hypothesis:**  
Signals based on trend, carry, and cross-asset relative moves perform best when:

- funding stress is absent
- inflation expectations are range-bound
- curve shape is not violently repricing

which is precisely the stable-carry regime.

**Why it fits the book:**  
This tests Gliner's practitioner intuition that some macro environments reward cleaner process-following while others are dominated by event shock.

**Test design:**
- classify stable carry using the macro inputs above
- compare average forward returns of risk-on and carry-like signals inside versus outside the regime

**Evidence that would support the hypothesis:**
- higher hit rate and smoother half-life for signals during stable carry windows

## Group C: Central Bank Policy Signals

### Hypothesis CB-1

**Name:** Policy-gap shocks drive near-term cross-asset stress

**Hypothesis:**  
The gap between realized overnight funding and the policy target,

`SOFR - DFEDTARU`,

when elevated, predicts near-term:

- higher `^VIX`
- weaker equity performance
- stronger dollar pressure

because the market is under short-term funding strain.

**Why it fits the book:**  
This is a clean, process-driven central-bank transmission signal with clear multi-asset impact.

**Test design:**
- identify top-decile `SOFR - DFEDTARU` episodes
- measure 1d / 5d / 10d forward response in `^VIX`, `^GSPC`, `DX-Y.NYB`, `USDJPY=X`

**Evidence that would support the hypothesis:**
- elevated policy gap aligns with near-term volatility spikes and weaker risk assets

### Hypothesis CB-2

**Name:** Curve inversion plus policy tightness is a stronger growth-scare signal than either alone

**Hypothesis:**  
The combination of:

- inverted `T10Y2Y` or `T10Y3M`
- elevated short-rate stance (`SOFR`, `DFEDTARU`)

predicts stronger growth-scare behavior than either input alone.

**Why it fits the book:**  
It captures the interaction between central-bank stance and macro growth expectations.

**Test design:**
- compare forward cross-asset returns under:
  - inversion only
  - policy tightness only
  - both together
- focus on equities, dollar, and gold

**Evidence that would support the hypothesis:**
- the joint condition has stronger explanatory power for subsequent risk-off behavior

## Group D: FX Valuation Models

### Hypothesis FX-1

**Name:** Reduced-form USD valuation model improves DXY timing

**Hypothesis:**  
A reduced-form USD valuation score using:

- curve slope (`T10Y2Y`, `T10Y3M`)
- real/inflation expectations (`T5YIE`, `T10YIE`)
- funding stance (`SOFR`, `DFEDTARU`)

helps identify when `DX-Y.NYB` is rich or cheap versus macro conditions.

**Why it fits the book:**  
It operationalizes Gliner's FX-valuation framing using only local macro inputs and a liquid USD proxy.

**Test design:**
- regress or map DXY against macro factors
- define residual valuation gaps
- test whether large positive or negative residuals mean revert over 10d to 20d horizons

**Evidence that would support the hypothesis:**
- DXY residuals beyond threshold normalize more often than not
- valuation gap is more informative than simple trend alone in mixed macro regimes

### Hypothesis FX-2

**Name:** JPY acts as the cleanest growth-scare and funding-stress FX expression

**Hypothesis:**  
Among the locally available FX pairs, `USDJPY=X` should react most cleanly to:

- growth-scare signals from inversion
- funding-stress signals from `SOFR - DFEDTARU`

making it a stronger macro expression than `EURUSD=X` or `GBPUSD=X` in stress windows.

**Why it fits the book:**  
This is directly in line with discretionary macro heuristics about safe-haven currencies and clean trade expression.

**Test design:**
- rank growth-scare and funding-stress days
- compare forward 1d / 5d / 10d FX responses across:
  - `USDJPY=X`
  - `EURUSD=X`
  - `GBPUSD=X`

**Evidence that would support the hypothesis:**
- `USDJPY` shows the strongest and most consistent move under stress signals

### Hypothesis FX-3

**Name:** FX valuation and policy regime should be combined, not traded separately

**Hypothesis:**  
An FX valuation residual is more predictive when aligned with the macro regime:

- rich USD in growth scare -> stronger reversal odds
- rich USD in funding stress -> weaker reversal odds because structural stress can dominate valuation

**Why it fits the book:**  
This reflects the discretionary practitioner idea that valuation alone is rarely enough; regime tells you whether valuation matters now.

**Test design:**
- compute FX valuation residual from `FX-1`
- split by regime from `REG-1`
- compare reversal hit rates across regimes

**Evidence that would support the hypothesis:**
- valuation signals only work reliably in selected regimes rather than universally

## Suggested Build Order

1. `REG-1` — four macro regimes
2. `CB-1` — policy-gap stress response
3. `XA-1` — cross-asset risk-on composite
4. `FX-1` — reduced-form DXY valuation model
5. `FX-2` / `FX-3` — FX expression quality and regime alignment

## Immediate Next Steps

1. Create `study_hypotheses.md` notebooks or markdown-linked experiments for:
   - macro regime panel
   - cross-asset risk-on composite
   - USD valuation residual model
2. Add a small findings log entry whenever a hypothesis becomes scaffolded or tested.
