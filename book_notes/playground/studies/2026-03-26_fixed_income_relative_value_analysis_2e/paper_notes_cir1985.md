# Paper Notes: A Theory of the Term Structure of Interest Rates

**Authors:** John C. Cox, Jonathan E. Ingersoll Jr., Stephen A. Ross
**Year:** 1985
**Journal:** Econometrica, Vol. 53, No. 2, pp. 385–408
**Scores:** Credibility: 5 | Relevance: 5 | Actionability: 4

---

## Core Claim

Using a general equilibrium framework (not just no-arbitrage), if the short rate follows
a **square-root diffusion process**, the entire term structure is determined analytically.
The model guarantees non-negative interest rates (unlike Vasicek's Gaussian process),
produces a richer volatility structure (vol scales with $\sqrt{r}$), and derives bond
prices and derivative prices in closed form. This is the **CIR model**.

---

## The Model

### Short Rate Dynamics

$$dr_t = \kappa(\theta - r_t)\,dt + \sigma\sqrt{r_t}\,dW_t$$

Key difference from Vasicek: the diffusion term is $\sigma\sqrt{r_t}$ (not $\sigma$).

Properties:
- **Mean-reverting:** Same OU drift as Vasicek — $\kappa$ pulls $r$ toward $\theta$
- **Non-negative:** If $2\kappa\theta \geq \sigma^2$ (Feller condition), $r_t > 0$ always
- **Heteroskedastic:** Volatility $= \sigma\sqrt{r_t}$ rises when rates are high,
  falls near zero — consistent with observed rate vol behavior
- **Non-Gaussian:** $r_t$ follows a non-central chi-squared distribution

### Risk Premium

CIR specifies a **market price of risk proportional to $\sqrt{r_t}$**:
$$\lambda(r_t) = \lambda\sqrt{r_t}$$
This preserves the affine structure under the risk-neutral measure.

Under $\mathbb{Q}$, the short rate follows:
$$dr_t = \kappa^*(\theta^* - r_t)\,dt + \sigma\sqrt{r_t}\,d\tilde{W}_t$$
where $\kappa^* = \kappa + \lambda\sigma$ and $\theta^* = \kappa\theta/(\kappa + \lambda\sigma)$.

### Bond Pricing Formula

Zero-coupon bond price under CIR:

$$P(t,T) = A(t,T)\,e^{-B(t,T)\,r_t}$$

where $\tau = T-t$, $\gamma = \sqrt{(\kappa^*)^2 + 2\sigma^2}$, and:

$$B(t,T) = \frac{2(e^{\gamma\tau}-1)}{(\gamma+\kappa^*)(e^{\gamma\tau}-1)+2\gamma}$$

$$A(t,T) = \left[\frac{2\gamma\,e^{(\kappa^*+\gamma)\tau/2}}{(\gamma+\kappa^*)(e^{\gamma\tau}-1)+2\gamma}\right]^{2\kappa\theta/\sigma^2}$$

Yields are again **affine** in $r_t$ — the CIR model is a member of the affine family.

---

## Key Findings

1. **Non-negative rates guaranteed** (Feller condition: $2\kappa\theta \geq \sigma^2$).
   This is the primary practical advantage over Vasicek.

2. **Volatility scales with $\sqrt{r_t}$.** Rate volatility is higher in high-rate
   environments, consistent with empirical evidence from the 1980s.

3. **General equilibrium derivation.** Unlike Vasicek (no-arbitrage only), CIR
   derives the term structure from investors' optimal consumption/investment decisions.
   The market price of risk is endogenous, not assumed.

4. **Non-central chi-squared transition density.** The exact conditional distribution
   of $r_{t+h}|r_t$ is non-central $\chi^2$, enabling maximum likelihood estimation.

---

## Key Takeaways

1. **Use CIR when rates are near zero.** The Feller condition prevents $r_t < 0$,
   making CIR the safer choice for USD short rates during 2009–2015 or EUR rates
   during the negative rate era (where CIR breaks — shadow rate models needed).

2. **Calibration is harder than Vasicek.** No closed-form OLS; requires MLE on the
   non-central chi-squared transition density or GMM. Practically, many desks use
   Vasicek for speed and CIR as a robustness check.

3. **CIR underpins cap/floor pricing in normal regimes.** The Jamshidian (1989)
   decomposition of a swaption into a portfolio of caplets works under both
   Vasicek and CIR — but CIR gives non-zero probability floor at zero.

4. **Multi-factor CIR.** Duffie & Kan (1996) generalize CIR to $N$ factors —
   each factor follows a square-root process. This is the canonical affine
   multi-factor model used in practice.

---

## Caveats

- **Negative rates still possible in multi-factor versions** if cross-correlations
  are not constrained. The Feller condition must hold for each factor independently.
- **Empirical fit is poor at short end.** The sqrt-diffusion implies rate vol
  proportional to $\sqrt{r}$ — but empirically, short-rate vol does not go to zero
  when rates approach zero (the 2010s showed rates near zero with non-trivial vol).
- **Shadow rate models supersede CIR at ZLB.** Wu-Xia (2016) and Black (1995) shadow
  rate models are now preferred for ZLB regimes.
- **Estimation requires MLE or GMM**, not simple OLS — a practical barrier vs Vasicek.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch2 — Mean Reversion** | CIR is the positive-rate alternative to Ch2's OU/Vasicek; the book discusses both in the context of nonparametric drift estimation |
| **Ch6 — Yield Curve Models** | CIR is the ancestor of the affine multi-factor models covered in Ch6; shadow rate models referenced there are responses to CIR's ZLB failure |
| **Ch19 — Options** | Cap/floor pricing under CIR uses the non-central chi-squared CDF — produces different vol smiles than Gaussian Vasicek |

---

## Adjacent Papers to Read Next

- **Vasicek (1977)** — simpler predecessor; read first if not already done
- **Hull & White (1990)** — extended Vasicek that fits the current curve exactly
- **Duffie & Kan (1996)** — multi-factor generalization of CIR (canonical affine ATSMs)
- **Wu & Xia (2016)** — shadow rate fix for ZLB regime

---

*Cerebro — 2026-03-26 | FIRV study: Cox, Ingersoll & Ross (1985)*
