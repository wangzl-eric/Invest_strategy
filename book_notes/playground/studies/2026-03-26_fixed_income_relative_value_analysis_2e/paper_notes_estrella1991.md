# Paper Notes: The Term Structure as a Predictor of Real Economic Activity

**Authors:** Arturo Estrella, Gikas A. Hardouvelis
**Year:** 1991
**Journal:** Journal of Finance, Vol. 46, No. 2, pp. 555–576
**Scores:** Credibility: 5 | Relevance: 4 | Actionability: 4

---

## Core Claim

The **slope of the yield curve** — measured as the spread between the
10-year Treasury yield and the 3-month T-bill rate — is a powerful and
statistically robust predictor of **real economic activity** 4–8 quarters
ahead. An inverted yield curve (negative slope) reliably predicts recessions;
a steep curve predicts expansions. This relationship holds out-of-sample,
survives controlling for other leading indicators, and has been one of the
most replicated empirical results in macroeconomics.

For fixed income RV, the yield slope is the primary **macro regime
indicator**: it determines whether RV carry trades have a structural
tailwind or headwind, and whether duration risk is being compensated.

---

## 1. The Core Finding

### The Regression

Estrella and Hardouvelis run:

$$\Delta_h \text{GDP}_{t+h} = \alpha + \beta \cdot (y_{10} - y_{3m})_t + \varepsilon_{t+h}$$

where $h$ = 1 to 8 quarters ahead. Key results:

| Horizon (quarters ahead) | $\beta$ | $R^2$ |
|--------------------------|---------|-------|
| 1 | positive | ~15% |
| 4 | **strongest** | **~30%** |
| 8 | still significant | ~20% |

The 4-quarter horizon has the highest predictive power — the curve slope
today predicts GDP growth one year from now better than most alternatives.

### Recession Prediction

The paper also shows (extended in later work by Estrella & Mishkin 1998):
- **Slope < 0** (inverted): recession probability > 30% within 4 quarters
- **Slope < -100bps**: recession probability > 70%
- **Slope > +150bps**: recession probability < 5%

The 2s10s spread (a more common practitioner version) performs similarly.

---

## 2. Why the Yield Slope Predicts the Economy

### Three Mechanisms

1. **Monetary policy expectations:** An inverted curve means the market
   expects rates to fall — which happens when the Fed cuts in response
   to a weakening economy. The curve inverts *in anticipation* of recession.

2. **Term premium compression:** When the term premium is compressed
   (investors willing to hold long bonds cheaply), long yields fall below
   short yields. Compressed TP itself signals low growth expectations.
   (Kim-Wright separates these two channels.)

3. **Real economic transmission:** A flat/inverted curve directly tightens
   bank lending margins (borrow short, lend long). Banks pull back on credit;
   investment falls; recession follows with a 4–8 quarter lag.

### The Slope vs. Other Leading Indicators

Estrella and Hardouvelis show the yield slope **dominates** other standard
leading indicators in forecasting GDP:

| Indicator | Predictive Power (4Q ahead) |
|-----------|----------------------------|
| Yield slope (10Y–3M) | **Highest** |
| Leading index (Conference Board) | Moderate |
| Money supply (M2 growth) | Low |
| Stock market returns | Low–moderate |

The slope is particularly powerful because it aggregates market expectations
of monetary policy, growth, and inflation simultaneously.

---

## 3. Macro Regime Classification for Fixed Income RV

### The Regime Matrix

Combining yield slope with Kim-Wright term premium:

| Slope | Term Premium | Regime | FI RV Implication |
|-------|-------------|--------|-------------------|
| Steep (>150bps) | Normal/High | **EXPANSION** | Duration carry works; RV trades have cushion |
| Flat (0–100bps) | Compressed | **LATE CYCLE** | Carry compressed; tighten stops on duration longs |
| Inverted (<0bps) | Rising | **RECESSION RISK** | Avoid long-duration RV; favor short-end carry |
| Steep (>200bps) | High | **RECOVERY** | Best entry for duration carry; curve steepeners |

### Python Regime Classifier

```python
def classify_yield_curve_regime(slope_10y_3m, tp_10y):
    """
    slope_10y_3m: 10Y yield minus 3M yield in percent
    tp_10y: Kim-Wright 10Y term premium in percent
    Returns macro regime label.
    """
    if slope_10y_3m < 0:
        return "RECESSION_RISK"      # Inverted: recession signal; reduce duration exposure
    elif slope_10y_3m < 1.0:
        if tp_10y < 0.5:
            return "LATE_CYCLE"      # Flat + compressed TP: most dangerous for carry
        else:
            return "TIGHTENING"      # Flat but TP still positive
    elif slope_10y_3m < 2.0:
        return "NORMAL"              # Standard conditions
    else:
        if tp_10y > 1.0:
            return "RECOVERY"        # Steep + high TP: best for duration carry
        else:
            return "STEEPENING"      # Steep but TP low: expect-path driven
```

---

## 4. Connection to Term Premium (Kim-Wright)

### Slope = Expected Rates + Term Premium

The yield slope conflates two distinct signals:

$$y_{10} - y_{3m} = \underbrace{(E[r]_{10Y} - r_{3m})}_{\text{Expected rate path}} + \underbrace{TP_{10Y}}_{\text{Term premium}}$$

This means an inverted curve can be driven by:
- **High short rates** (Fed tightening aggressively above neutral) — monetary
  policy signal; recession risk from overtightening
- **Low long rates** (compressed term premium) — risk-off demand; not
  necessarily a recession signal if TP is structural

Kim-Wright separates these. **The cleanest recession signal** is:
- Slope inverted **AND** expected rate path component is negative
  (market pricing large rate cuts)
- Not just compressed TP pulling long yields down

**Practical implication:** Use slope for the first-order regime screen;
use Kim-Wright decomposition to verify the signal is expectation-driven
not TP-driven before acting on the recession call.

---

## 5. Historical Performance of the Signal

| Yield Curve Inversion Date | Subsequent Recession | Lead Time |
|---------------------------|--------------------|-----------|
| 1978–1980 | 1980 recession | ~6 months |
| 1988–1989 | 1990–91 recession | ~12 months |
| 2000 | 2001 recession | ~12 months |
| 2006–2007 | 2008–09 GFC | ~18 months |
| 2019 | 2020 (COVID) | ~6 months (confounded) |
| 2022–2023 | No recession yet (as of 2026) | Still pending |

The 2022–2023 inversion is the deepest since 1981 (peak inversion -180bps
on 10Y–3M) but has not produced a recession as of the current date —
possibly reflecting the unusual post-COVID cycle dynamics and strong labor market.

---

## 6. Key Takeaways

1. **The yield slope (10Y–3M) is the single most reliable macro leading
   indicator for fixed income.** Sharpe ratios on duration strategies
   are significantly higher in steep curve regimes than flat/inverted ones.
   Use it as the primary macro filter before entering any duration RV trade.

2. **Inversion is a warning, not a trigger.** Average lead time to recession
   is 12–18 months. Do not exit duration trades the day the curve inverts;
   do begin tightening stops and reducing duration exposure.

3. **Combine with Kim-Wright TP for signal quality.** Slope inversion driven
   by expected rate cuts (Kim-Wright: expected path component negative) is a
   stronger recession signal than inversion driven by compressed TP.

4. **Steep curve = carry tailwind.** In steep curve environments (>150bps),
   bond carry strategies earn roll-down in addition to coupon income. This is
   the structural carry environment for fixed income RV. The Koijen et al.
   (2018) bond carry framework implicitly assumes normal/steep curve conditions.

5. **The 2022–2023 failure is a regime warning.** The unprecedented
   post-COVID labor market resilience may have altered the slope-to-recession
   transmission. Apply the signal with increased uncertainty in novel regimes.

---

## Caveats

- **Long lead times create implementation challenges.** 12–18 month leads
  mean a trading strategy cannot mechanically time entries/exits on slope alone.
- **The signal is well-known and may be priced.** After Estrella-Mishkin
  (1998) and widespread adoption, markets price the recession probability
  into the curve more quickly — lead times may shorten.
- **2023 false signal risk.** The 2022–23 inversion without recession weakens
  the signal's unconditional credibility; use it as context, not as alpha.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch9 — Analytic Process** | Macro regime (slope) is the outer context for the Ch9 process; inverted curve = raise convergence speed bar |
| **Ch20 — Macro Perspective** | Ch20's framework for distinguishing transient vs. structural dislocations uses the macro cycle; slope is the primary cycle indicator |
| **Ch2 — Mean Reversion** | OU mean reversion speed of yield spreads is higher in steep curve regimes (more carry supports faster convergence) |
| **Ch12 — Asset Swaps** | ASW carry is positive in steep curves (roll-down large); negative in flat/inverted (roll-down small or negative) |

---

## Adjacent Papers to Read Next

- **Estrella & Mishkin (1998)** — extends this paper with probit recession
  probability model; provides calibrated probability estimates by slope level
- **Kim & Wright (2005)** — already read; decomposes slope into expected
  path and TP; refines the signal quality
- **Fama & Bliss (1987)** — forward rates predict excess bond returns;
  closely related to the slope-as-predictor literature

---

*Cerebro — 2026-03-26 | FIRV study: Estrella & Hardouvelis (1991)*