# Paper Notes: An Arbitrage-Free Three-Factor Term Structure Model and the Recent Behavior of Long-Term Yields

**Authors:** Don H. Kim, Jonathan H. Wright
**Year:** 2005
**Source:** Federal Reserve Board Finance and Economics Discussion Series 2005-33
**Scores:** Credibility: 5 | Relevance: 4 | Actionability: 4

---

## Core Claim

Nominal Treasury yields can be decomposed into two conceptually distinct components:
**(1) expected future short rates** (the path of monetary policy priced into the
curve) and **(2) the term premium** (compensation for bearing duration/inflation
risk). The paper implements this decomposition using an **arbitrage-free
three-factor affine model** with latent factors, and shows that the low long-term
yields of the mid-2000s (Greenspan's "conundrum") were almost entirely due to
a compressed — and at times negative — term premium, not to expectations of
permanently lower policy rates.

The Federal Reserve publishes daily Kim-Wright term premium estimates on its
website. This makes the model directly usable as a **macro regime signal**
for fixed income RV research.

---

## 1. The Decomposition

### Yield = Expected Short Rates + Term Premium

For a $n$-period zero-coupon bond:

$$y_t^{(n)} = \underbrace{\frac{1}{n}\sum_{i=0}^{n-1} E_t[r_{t+i}]}_{\text{Expected short rate path}} + \underbrace{TP_t^{(n)}}_{\text{Term premium}}$$

where:
- **Expected short rate path** = what the market expects the overnight rate
  to average over the bond's life (pure monetary policy expectations)
- **Term premium** = extra yield required by investors for locking in
  duration; compensation for inflation uncertainty and interest rate risk

### Why the Decomposition Matters for RV

| Scenario | Expected Rates | Term Premium | RV Implication |
|----------|---------------|--------------|----------------|
| Normal | Moderate | +100–150bps | Bonds have cushion; RV trades have carry buffer |
| Compressed TP era (2014–19) | Low | Near zero or negative | Long bonds expensive; RV trades have no cushion; convergence risk high |
| Rate hike cycle (2022) | Rising fast | Volatile | Both components move; decomposition helps isolate the driver |
| Post-crisis ZLB | Very low | Low but positive | Model needs shadow rate extension (Wu-Xia) |


---

## 2. The Three-Factor Affine Model

### Model Structure

Kim-Wright use a **completely affine Gaussian three-factor model**:

$$X_t = \begin{pmatrix} X_1 \\ X_2 \\ X_3 \end{pmatrix}, \quad dX_t = K(\theta - X_t)dt + \Sigma dW_t^P$$

Under the risk-neutral measure:
$$dX_t = K^Q(\theta^Q - X_t)dt + \Sigma dW_t^Q$$

Yields are **affine** in the state vector:
$$y_t^{(n)} = A_n + B_n' X_t$$

where $A_n$ and $B_n$ are scalar/vector solutions to Riccati ODEs that enforce
no-arbitrage across all maturities simultaneously.

### Latent Factors

Unlike Diebold-Li, Kim-Wright's three factors are **latent** — they don't
correspond to directly observable yields. The factors are extracted from
the cross-section of yields using Kalman filtering (state-space estimation).

This means:
- The model always satisfies no-arbitrage across maturities
- Term premia estimates don't depend on any particular maturity
- But factors are harder to interpret than NS $\beta_1/\beta_2/\beta_3$

---

## 3. Term Premium Decomposition

### Federal Reserve Daily Estimates

The Fed publishes Kim-Wright term premium estimates at:
`https://www.federalreserve.gov/pubs/feds/2005/200533/200533abs.html`

Key series (downloadable from Fed website):
- `ACMTP10` — 10Y term premium (ACM model, alternative)
- Kim-Wright 10Y term premium — separate series
- Expected 10Y rate (= 10Y yield minus term premium)

### Empirical Behavior

| Period | 10Y Term Premium | Interpretation |
|--------|-----------------|----------------|
| 1990–2000 | +100–200bps | High inflation uncertainty; investors demanded large TP |
| 2004–2007 | +0–50bps | Greenspan "conundrum"; low TP compressed long yields |
| 2008–2013 | +0–100bps | QE compressed TP further; TP occasionally negative |
| 2014–2019 | -50–+50bps | Secular stagnation; TP near zero; long yields "too low" |
| 2022–2023 | +100–200bps | Rate shock; TP re-priced rapidly; long yields led the selloff |

---

## 4. Using Kim-Wright as a Regime Signal

### The Core Insight for RV Research

The term premium tells you **how much cushion** a fixed income RV trade has:

- **High term premium (> 100bps):** Long bonds are cheap on a risk-adjusted
  basis. RV spread trades that are long duration have a structural tailwind.
  Mean reversion trades have carry cushion — even if convergence is slow,
  term premium earns while waiting.

- **Low or negative term premium (< 0bps):** Long bonds are expensive.
  RV trades with long-duration exposure face a structural headwind. The
  trade needs fast convergence or it bleeds carry. This was the environment
  of 2015–2021 — most fixed income carry trades were structurally challenged.

- **Rising term premium:** Duration sells off faster than the front end.
  Curve steepeners are rewarded. Bund/UST spread may widen as global TP
  reprices unevenly.

### Regime Classification Framework

```python
def classify_tp_regime(tp_10y):
    """
    tp_10y: Kim-Wright 10Y term premium in percent (e.g. 0.50 = 50bps)
    Returns regime label for fixed income RV context.
    """
    if tp_10y < 0:
        return "COMPRESSED_NEGATIVE"   # Structural headwind; avoid long-duration RV
    elif tp_10y < 0.5:
        return "COMPRESSED_LOW"        # Weak cushion; require fast convergence
    elif tp_10y < 1.5:
        return "NORMAL"                # Standard RV conditions
    else:
        return "ELEVATED"              # Strong tailwind; duration longs have carry buffer
```

---

## 5. Key Findings from the Paper

1. **The "conundrum" was a term premium story.** Greenspan noted in 2005 that
   long yields weren't rising despite Fed hikes. Kim-Wright showed this was
   because the term premium collapsed from ~150bps in 2000 to near zero in
   2004–2005. Expected short rates did rise with the Fed; term premium fell
   to offset it entirely.

2. **Three factors explain >99% of yield curve variance.** Consistent with
   Litterman-Scheinkman (1991) and NS (1987); the affine structure imposes
   this efficiently.

3. **Term premium has a strong business cycle component.** TP tends to rise
   in recessions (uncertainty premium) and fall in expansions. It is also
   compressed by central bank QE (reduces duration supply in private hands).

4. **No-arbitrage discipline matters.** Unconstrained regression-based
   decompositions (e.g., simple forward rate regressions) produce unstable
   term premium estimates. The Riccati ODE constraints enforce consistency
   across maturities and improve out-of-sample stability.

---

## 6. Key Takeaways

1. **Use Kim-Wright TP as the first macro filter in any fixed income RV screen.**
   Before computing fitting residuals or carry, check the TP regime. In a
   compressed-TP environment, required convergence speed doubles.

2. **TP and yield slope are related but distinct.** The yield slope (10Y–2Y)
   conflates TP with expected rate path. Kim-Wright separates them: a steep
   curve can be driven by high TP or by expectations of future rate hikes —
   very different implications for positioning.

3. **The Fed publishes the data daily.** This is one of the few latent
   variable models where the output is freely available in real time.
   Download from the Fed website; use as a time-series feature in any
   rate strategy research.

4. **Rising TP regimes favor steepeners and duration shorts.** Falling TP
   regimes favor flatteners and carry trades. The TP trend is often more
   important than its level for medium-term positioning.

5. **ACM model (Adrian-Crump-Moench) is the alternative.** The Fed also
   publishes ACM term premia (`ACMTP10` on FRED). ACM uses a different
   identification approach (OLS principal components); Kim-Wright uses
   Kalman filter MLE. They track each other closely but diverge in stress.
   Use both as a cross-check.

---

## Caveats

- **Latent factor models require careful estimation.** Small sample changes
  can cause large shifts in estimated TP. The Fed periodically re-estimates
  the model, causing backward revisions.
- **Completely affine structure has known limitations.** Duffee (2002) showed
  that completely affine models (where risk prices are proportional to volatility)
  have poor forecasting properties. Kim-Wright's TP estimates may be biased
  in low-volatility regimes.
- **Model uncertainty is real.** ACM and Kim-Wright sometimes disagree by
  50–100bps on the level of TP. Treat TP estimates as regime indicators,
  not precise measurements.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch6 — Yield Curve Models** | Kim-Wright is a completely affine model; Ch6 discusses the same class; KW shows the practical output of the estimation pipeline |
| **Ch9 — Analytic Process** | TP regime is the macro context for the Ch9 process; compressed TP = raise the convergence speed bar |
| **Ch2 — Mean Reversion** | Expected short rate path (= yield minus TP) is the "true" mean reversion target for the short rate OU process |
| **Ch17 — Global RV** | Cross-country TP differentials drive cross-market ASW spreads; ECB and BoJ TP estimates contextualize EUR/JPY vs USD positioning |

---

## Adjacent Papers to Read Next

- **Adrian, Crump & Moench (2013)** — ACM model; alternative no-arb decomposition;
  `ACMTP10` published on FRED daily
- **Cochrane & Piazzesi (2005)** — single tent-shaped forward rate factor predicts
  bond excess returns; closely related to TP variation
- **Estrella & Hardouvelis (1991)** — yield slope as macro predictor; complements
  KW by linking TP to recession probability

---

*Cerebro — 2026-03-26 | FIRV study: Kim & Wright (2005)*