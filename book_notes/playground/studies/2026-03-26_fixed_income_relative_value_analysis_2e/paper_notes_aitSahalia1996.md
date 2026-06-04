# Paper Notes: Testing Continuous-Time Models of the Spot Interest Rate

**Authors:** Yacine Aït-Sahalia
**Year:** 1996
**Journal:** Review of Financial Studies, Vol. 9, No. 2, pp. 385–426
**Scores:** Credibility: 5 | Relevance: 4 | Actionability: 3

---

## Core Claim

Standard parametric models of the short rate — Vasicek, CIR, and their
generalizations — are **statistically rejected by the data**. Using a
nonparametric specification test based on the transition density of the
short rate, Aït-Sahalia shows that the failure is concentrated in the
**tails of the rate distribution**: at very low and very high rate levels,
the drift function is strongly nonlinear in ways that constant-parameter
OU/CIR models cannot capture. The paper is the canonical empirical critique
of affine short rate models and motivates the nonparametric and regime-
switching extensions discussed in Ch2 and Ch6 of FIRV.

---

## 1. The Testing Framework

### Nonparametric Transition Density Test

Aït-Sahalia's approach:
1. Estimate the **transition density** $p(r_{t+h} | r_t)$ of the short
   rate nonparametrically (using kernel density estimation)
2. Compute the transition density implied by a parametric model (Vasicek, CIR)
3. Test whether the parametric density equals the nonparametric estimate
   using an $L^2$ distance statistic

The test is powerful because it targets the **full shape** of the transition
density — not just the first two moments (mean and variance) that OLS-based
OU calibration focuses on.

### Data

- US federal funds rate and 3-month T-bill rate, 1963–1993 (monthly)
- 360 observations — large enough for nonparametric estimation
- Sample includes the Volcker shock (1979–1982) with rates up to 20%

---

## 2. Key Findings

### The Drift is Nonlinear at the Tails

The nonparametric drift estimate $\hat{\mu}(r)$ shows:

| Rate Level | Parametric (Vasicek) Drift | Nonparametric Drift | Implication |
|------------|--------------------------|--------------------|--------------|
| Very low (< 3%) | Moderate positive (pulls toward $\theta$) | **Strongly positive** (strong upward pull) | Rates don't stay near zero; strong reverting force |
| Normal (4–8%) | Moderate mean-reversion | Approximately linear | Vasicek adequate in this range |
| Very high (> 15%) | Moderate negative | **Strongly negative** (strong downward pull) | Rates quickly revert from extremes |

**The tails are where models break.** In the normal range (where most
data points lie), Vasicek and CIR fit well. At the extremes — the 1979–82
Volcker shock and the ZLB — the nonparametric drift is far more powerful
than any constant-$\kappa$ model predicts.

### Diffusion is Also Nonlinear

The nonparametric diffusion (volatility) function $\hat{\sigma}(r)$ also
shows nonlinearity:
- At low rates: $\sigma(r)$ falls faster than $\sqrt{r}$ (CIR prediction)
- At high rates: $\sigma(r)$ rises faster than $\sqrt{r}$
- Overall: neither Vasicek ($\sigma$ constant) nor CIR ($\sigma \propto \sqrt{r}$)
  captures the empirical diffusion well

### All Standard Parametric Models Are Rejected

| Model | Test Statistic | Rejection at 5%? |
|-------|---------------|------------------|
| Vasicek | High | Yes |
| CIR | High | Yes |
| CKLS (Chan et al.) | Moderate | Yes |
| General affine | Moderate | Yes |

---

## 3. Implications for FIRV Research

### Why This Matters for OU Calibration

Ch2 of FIRV uses constant-parameter OU calibration:
$$dr_t = \kappa(\theta - r_t)dt + \sigma dW_t$$

Aït-Sahalia's critique implies:
- The $\kappa$ estimated from OLS is a **local average** of a nonlinear drift
- In normal rate regimes, the OLS $\kappa$ is a reasonable approximation
- In tail regimes (ZLB, Volcker-style spikes), the true mean reversion is
  much stronger — the OU model will **underestimate** convergence speed

**Practical response:** Use OU calibration as a baseline but recognize
that it may underestimate convergence speed at extreme levels. At the ZLB,
the Wu-Xia shadow rate framework (paper #19) provides a complementary
correction. For high-rate regimes, widen confidence intervals around $\kappa$.

### Regime-Switching as a Response

The nonlinearity in both drift and diffusion motivates **regime-switching
models** (e.g., Hamilton 1989 applied to rates):
- Estimate separate $\kappa_1$, $\theta_1$, $\sigma_1$ for normal regime
- Estimate separate $\kappa_2$, $\theta_2$, $\sigma_2$ for stress regime
- Transition probabilities govern regime switches

This approach captures the tail nonlinearity without the full nonparametric
complexity — and is more tractable for RV signal calibration.

---

## 4. Key Takeaways

1. **Constant-parameter OU is adequate in normal rate regimes.** For the
   typical rate range (2–8%), Vasicek-style calibration produces reasonable
   half-life and mean estimates. Don't over-correct based on Aït-Sahalia.

2. **Tail behavior is not captured.** At ZLB or stress spike levels,
   mean reversion is stronger than the model predicts — positions at
   extremes converge faster in practice than the model implies.

3. **Don't use constant-$\sigma$ in high-vol regimes.** CIR's $\sqrt{r}$
   diffusion is a better approximation than Vasicek's constant $\sigma$
   when rates are elevated (2022 hiking cycle). Use CIR-based vol scaling
   for position sizing at high rate levels.

4. **Nonparametric testing is the gold standard.** When calibrating any
   mean reversion model, compare model-implied transition densities against
   kernel density estimates — not just RMSE of the mean. A model can have
   low RMSE but badly misspecify tail behavior.

---

## Caveats

- **Small sample in the tails.** Very few observations at rate extremes
  (< 3% or > 15%) — nonparametric estimates are noisy there.
- **Regime stationarity assumed.** The full 1963–1993 sample mixes multiple
  Fed regimes; nonparametric estimates average across them.
- **Monthly data only.** High-frequency (daily) short rate dynamics may
  differ — microstructure noise and policy announcement effects dominate.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch2 — Mean Reversion** | Aït-Sahalia is the empirical calibration check on Ch2's OU framework; motivates caution at rate extremes |
| **Ch6 — Yield Curve Models** | Shadow rate models (Wu-Xia) and regime-switching models are partly motivated by Aït-Sahalia's rejection of affine models |
| **Ch9 — Analytic Process** | Ex ante Sharpe calculations using OU parameters should be stress-tested at tail rate levels |

---

*Cerebro — 2026-03-26 | FIRV study: Aït-Sahalia (1996)*