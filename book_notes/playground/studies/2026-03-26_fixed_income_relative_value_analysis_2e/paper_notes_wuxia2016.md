# Paper Notes: Measuring the Macroeconomic Impact of Monetary Policy at the Zero Lower Bound

**Authors:** Jing Cynthia Wu, Fan Dora Xia
**Year:** 2016
**Journal:** Journal of Money, Credit and Banking, Vol. 48, No. 2–3, pp. 253–291
**Scores:** Credibility: 5 | Relevance: 4 | Actionability: 4

---

## Core Claim

Standard short-rate models break at the **zero lower bound (ZLB)** because
they allow negative rates while the observed policy rate is constrained at zero.
Wu and Xia propose a **shadow rate model**: the true "latent" short rate can go
negative, but the observed short rate is floored at zero. The shadow rate
serves as a continuous summary of monetary policy stance even when the
nominal rate is stuck at the ZLB — it captures the effect of unconventional
policies (QE, forward guidance) as a negative shadow rate equivalent.

The Fed publishes Wu-Xia shadow rate estimates. This makes the model directly
usable as a **regime indicator** for any fixed income or macro strategy.

---

## 1. The Zero Lower Bound Problem

### Why Standard Affine Models Fail at the ZLB

Standard Gaussian affine models (Vasicek, Kim-Wright) assume:
$$r_t = \delta_0 + \delta_1' X_t$$

where $r_t$ can take any value — including negative. This is fine when rates
are well above zero but creates a fundamental inconsistency at the ZLB:
- The observed rate is floored at 0 (or slightly above)
- The model assigns positive probability to negative rates
- Yield curve fitting near the ZLB is distorted
- Term premium estimates become unreliable
- The model cannot distinguish between "rates at zero by policy constraint"
  and "rates near zero because the economy is weak"

### The Shadow Rate Solution

Black (1995) proposed the key insight: treat the short rate as an option:

$$r_t = \max(s_t, 0)$$

where $s_t$ is the **shadow rate** — the rate that *would* prevail if there
were no ZLB constraint. $s_t$ can go negative; $r_t$ cannot.

Wu-Xia implement this with an efficient approximation that makes the
otherwise computationally intractable shadow rate model fast to estimate.

---

## 2. The Wu-Xia Approximation

### The Key Formula

For a three-factor Gaussian model, Wu-Xia show that the shadow short rate
can be approximated as:

$$s_t \approx -\frac{1}{T^*}\left[A(T^*) + B(T^*)' X_t\right]$$

where $T^*$ is a short maturity (e.g., 1 quarter), and $A$, $B$ are the
standard affine yield coefficients. The approximation replaces the
computationally expensive integration over the truncated normal distribution
(from Black's original formulation) with an analytic expression.

**Key property:** When $s_t > 0$, the shadow rate approximately equals the
standard affine short rate. When $s_t < 0$, it captures the effective
monetary easing beyond the ZLB from QE and forward guidance.

### Empirical Shadow Rate Estimates (US)

| Period | Fed Funds Rate | Wu-Xia Shadow Rate | Interpretation |
|--------|---------------|-------------------|----------------|
| 2009 Q1 | 0.25% | ~0% | ZLB binding but shallow |
| 2012–2013 | 0.25% | **-2% to -3%** | QE3 + forward guidance equivalent to -250bps |
| 2014–2015 | 0.25% | -1% to 0% | Taper; shadow rate rising before liftoff |
| 2016–2018 | 0.5%–2.5% | = policy rate | Above ZLB; shadow = observed |
| 2020 Q2 | 0.25% | **-5% to -6%** | COVID QE + forward guidance; deepest shadow rate |

---

## 3. Why the Shadow Rate Matters for Fixed Income RV

### Standard Affine Models Are Misspecified at ZLB

When using Kim-Wright or any standard affine model near the ZLB:
- Term premium estimates are upward biased (model attributes low long rates
  to low TP when part of it is ZLB distortion)
- Carry calculations using the short rate as funding cost are correct
  (you pay the actual SOFR/policy rate) but model-implied expected returns
  are wrong
- Mean reversion calibration of the short rate is distorted — the OU
  process cannot have $\theta < 0$ in standard form

### The Shadow Rate as a Regime Signal

```python
def classify_shadow_rate_regime(shadow_rate, policy_rate):
    """
    shadow_rate: Wu-Xia shadow rate in percent
    policy_rate: observed fed funds / policy rate in percent
    Returns regime label for fixed income RV.
    """
    zlb_binding = policy_rate < 0.50  # policy rate at effective lower bound
    if not zlb_binding:
        return "NORMAL"               # Standard affine models valid
    elif shadow_rate > -1.0:
        return "ZLB_SHALLOW"          # ZLB binding but mild unconventional policy
    elif shadow_rate > -3.0:
        return "ZLB_MODERATE"         # Significant QE; shadow rate -1% to -3%
    else:
        return "ZLB_DEEP"             # Heavy QE + forward guidance; shadow < -3%
```

**In ZLB regimes:** Replace the short rate in carry calculations with the
shadow rate *only* for model-implied expected return estimates. Use the
actual policy rate (SOFR/EFFR) for P&L carry calculations.

---

## 4. European and Japanese Context

### ECB Negative Rates

The ECB took rates negative in 2014 (deposit rate to -0.10%, eventually -0.50%
by 2019). This is **below** the ZLB — the shadow rate logic inverts:
- Observed rate IS negative; no ZLB binding
- Standard affine models can be used if calibrated to negative rate data
- BUT standard lognormal vol models (Black's cap/floor model) break —
  switch to normal vol (Bachelier) for swaption pricing
- Bund yields went negative out to 10Y+ — fitting residuals and carry
  calculations remain valid but intuition from positive-rate environments
  doesn't transfer

### Bank of Japan YCC

The BoJ implemented **Yield Curve Control (YCC)** in 2016 — pegging the
10Y JGB yield at 0% (later ±0.25%, ±0.50%). This is a different distortion:
- The yield at the target maturity is not determined by the market
- Term premium at 10Y is suppressed to near zero by fiat
- Kim-Wright / Wu-Xia estimates for JGBs are unreliable during YCC
- For global RV involving JGBs: treat the 10Y peg as a structural constraint,
  not a mean-reverting spread

---

## 5. Key Takeaways

1. **Use shadow rate as ZLB regime indicator.** When the Fed Funds rate is
   at the ELB, replace policy rate with Wu-Xia shadow rate in any model that
   uses the short rate as a state variable for expected returns.

2. **Standard affine carry is still correct.** The actual financing cost is
   the observed SOFR/repo rate — use that for P&L. Use shadow rate only
   for model-implied expected path of short rates.

3. **ECB negative rates ≠ ZLB.** ECB broke through zero; Wu-Xia ZLB
   correction not needed. But normal vol (Bachelier) required for options.
   BoJ YCC is a third distinct regime requiring separate treatment.

4. **Fed publishes the data.** Wu-Xia shadow rate series available from
   the Federal Reserve Bank of Atlanta website. Updated monthly.

5. **Shadow rate rise precedes rate liftoff.** In 2014–2015, the Wu-Xia
   shadow rate rose from -3% to 0% before the first Fed hike. It acts
   as an early warning signal for tightening even while the policy rate
   is still pinned.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch6 — Yield Curve Models** | Ch6 mentions shadow rate models as the ZLB extension; Wu-Xia is the standard implementation |
| **Ch2 — Mean Reversion** | OU short rate calibration must use shadow rate in ZLB regimes; $\theta$ cannot be negative in standard parameterization |
| **Ch11 — SOFR** | SOFR at ELB (2020–2021) had complex dynamics; shadow rate contextualizes the period |
| **Ch9 — Analytic Process** | Kim-Wright TP at ZLB is distorted; Wu-Xia shadow rate corrects the regime classification |

---

## Adjacent Papers to Read Next

- **Black (1995)** — original shadow rate idea; interest rates as options on
  the shadow rate
- **Kim & Singleton (2012)** — shadow rate model applied to JGBs during ZLB
- **Krippner (2012)** — alternative shadow rate implementation; widely used
  for cross-country ZLB comparisons

---

*Cerebro — 2026-03-26 | FIRV study: Wu & Xia (2016)*