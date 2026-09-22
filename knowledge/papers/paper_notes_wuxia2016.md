# Paper Notes: Measuring the Macroeconomic Impact of Monetary Policy at the Zero Lower Bound

**Authors:** Jing Cynthia Wu, Fan Dora Xia
**Year:** 2016 | **Journal:** Journal of Money, Credit and Banking, 48(2–3), 253–291
**DOI:** 10.1111/jmcb.12300
**Scores:** Credibility 5 | Relevance 4 | Actionability 4

> **Canonical merged note.** Surfaced while studying *Fixed Income Relative Value
> Analysis* (Darbyshire) and *Global Macro Trading* (Gliner). Per-book connection
> tables preserved under **Cross-Book Context**. Linked from each book's `reading_queue.md`.

---

## Core Claim

Standard short-rate models break at the **zero lower bound (ZLB)** because they allow
negative rates while the observed policy rate is floored at zero. Wu and Xia propose a
**shadow rate model**: the true latent short rate can go negative, but the observed rate
is $r_t = \max(s_t, 0)$. The shadow rate $s_t$ is a continuous summary of policy stance
even when the nominal rate is pinned at the ZLB — it captures unconventional policy (QE,
forward guidance) as a negative shadow-rate equivalent. The Fed (Atlanta) publishes the
series monthly, making it directly usable as a **regime indicator**.

---

## 1. The ZLB Problem

Standard Gaussian affine models (Vasicek, Kim-Wright) assume $r_t = \delta_0 + \delta_1' X_t$,
where $r_t$ can be negative. Near the ZLB this is inconsistent: observed rate floored at 0,
model assigns positive probability to negative rates, curve fitting is distorted, term-premium
estimates become unreliable, and the model cannot distinguish "rates at zero by policy
constraint" from "rates near zero because the economy is weak."

**Black (1995) solution:** treat the short rate as an option, $r_t = \max(s_t, 0)$, where
$s_t$ is the shadow rate that would prevail absent the ZLB. Wu-Xia provide an efficient
analytic approximation that makes the otherwise intractable shadow-rate model fast to estimate.

## 2. The Wu-Xia Approximation

For a three-factor Gaussian model the shadow short rate is approximated as

$$s_t \approx -\frac{1}{T^*}\left[A(T^*) + B(T^*)' X_t\right]$$

with $T^*$ a short maturity and $A, B$ the standard affine yield coefficients — replacing
Black's expensive integration over a truncated normal with an analytic expression. When
$s_t > 0$ the shadow rate ≈ the standard affine short rate; when $s_t < 0$ it captures the
effective easing from QE and forward guidance.

**US shadow-rate estimates:**

| Period | Fed Funds | Wu-Xia Shadow | Interpretation |
|--------|-----------|---------------|----------------|
| 2009 Q1 | 0.25% | ~0% | ZLB binding but shallow |
| 2012–2013 | 0.25% | **−2% to −3%** | QE3 + guidance ≈ −250bps |
| 2014–2015 | 0.25% | −1% to 0% | Taper; shadow rising before liftoff |
| 2016–2018 | 0.5–2.5% | = policy rate | Above ZLB; shadow = observed |
| 2020 Q2 | 0.25% | **−5% to −6%** | COVID QE + guidance; deepest |

## 3. Macroeconomic Impact (from GMT reading)

A **1% decline in the shadow rate has similar macro effects (output, inflation) as a 1%
conventional rate cut** — validating QE as policy stimulus quantifiable on the same scale
as conventional policy. This is the paper's headline macro contribution and what makes the
shadow rate usable as a single continuous policy-stance variable across conventional and
unconventional regimes.

## 4. Why It Matters for Fixed-Income RV

Near the ZLB, Kim-Wright / standard affine models are misspecified: term-premium estimates
are upward biased, model-implied expected returns are wrong, and OU short-rate calibration is
distorted ($\theta$ cannot be negative in standard form). **Carry P&L still uses the actual
SOFR/policy rate**; the shadow rate is used only for model-implied expected paths.

```python
def classify_shadow_rate_regime(shadow_rate, policy_rate):
    """Regime label for fixed-income RV / signal conditioning."""
    zlb_binding = policy_rate < 0.50
    if not zlb_binding:        return "NORMAL"        # standard affine valid
    elif shadow_rate > -1.0:   return "ZLB_SHALLOW"
    elif shadow_rate > -3.0:   return "ZLB_MODERATE"  # significant QE
    else:                      return "ZLB_DEEP"      # heavy QE + guidance
```

## 5. Europe & Japan

- **ECB negative rates ≠ ZLB.** ECB went below zero in 2014 (deposit to −0.50% by 2019);
  observed rate IS negative, so no ZLB binding — standard affine models work if calibrated to
  negative-rate data, but switch lognormal (Black) → **normal vol (Bachelier)** for swaptions.
- **BoJ YCC** (2016, 10Y peg 0% → ±0.25/0.50%) is a third distinct regime: the target-maturity
  yield is not market-determined, term premium is suppressed by fiat, Kim-Wright/Wu-Xia JGB
  estimates are unreliable — treat the 10Y peg as a structural constraint, not a mean-reverting spread.

## 6. Key Takeaways

1. Use the shadow rate as a ZLB regime indicator; substitute it for the policy rate in any
   short-rate-as-state-variable model for expected returns.
2. Standard affine carry P&L is still correct — finance at observed SOFR/repo.
3. ECB negatives and BoJ YCC are separate regimes requiring separate treatment.
4. Fed (Atlanta) publishes Wu-Xia monthly:
   https://www.atlantafed.org/cqer/research/wu-xia-shadow-federal-funds-rate
5. Shadow-rate rise **precedes** liftoff (rose −3% → 0% in 2014–2015 before the first hike) —
   an early-warning tightening signal while the policy rate is still pinned.
6. Cross-country shadow-rate differentials (Fed vs ECB vs BoJ) extend FX carry through ZLB
   periods when nominal differentials are compressed.

---

## Cross-Book Context

**Connections to FIRV (Darbyshire) chapters**

| Chapter | Connection |
|---------|------------|
| Ch6 — Yield Curve Models | Shadow-rate models are the ZLB extension; Wu-Xia is the standard implementation |
| Ch2 — Mean Reversion | OU short-rate calibration must use shadow rate in ZLB regimes ($\theta$ can't be negative in standard form) |
| Ch11 — SOFR | SOFR at the ELB (2020–2021) had complex dynamics the shadow rate contextualizes |
| Ch9 — Analytic Process | Kim-Wright TP at the ZLB is distorted; shadow rate corrects regime classification |

**Connections to Global Macro Trading (Gliner) chapters**

| Chapter | Connection |
|---------|------------|
| Ch11 — Central banks | Shadow rate quantifies QE + forward guidance; operationalizes Gliner's non-standard policy discussion |
| Ch7 — FX | Cross-country shadow-rate differentials extend rate-carry analysis through ZLB |
| Ch9 — Fixed income | Shadow rate explains yield-curve dynamics during QE beyond the floored policy rate |

---

## Adjacent Papers

Black (1995) — interest rates as options on the shadow rate · Kim & Singleton (2012) —
shadow-rate model for JGBs · Krippner (2012) — alternative shadow-rate implementation,
widely used for cross-country ZLB comparison.

## Citation

Wu, J. C., & Xia, F. D. (2016). Measuring the Macroeconomic Impact of Monetary Policy at the
Zero Lower Bound. *Journal of Money, Credit and Banking*, 48(2–3), 253–291.
