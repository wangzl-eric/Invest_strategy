# Paper Notes: Term Premia and Interest Rate Forecasts in Affine Models

**Authors:** Gregory R. Duffee
**Year:** 2002
**Journal:** Journal of Finance, Vol. 57, No. 1, pp. 405–443
**Scores:** Credibility: 5 | Relevance: 4 | Actionability: 4

---

## Core Claim

Standard affine term structure models (Vasicek, CIR) produce poor out-of-sample
yield forecasts because their **market price of risk specification is too restrictive**.
In "completely affine" models, the risk premium must covary with volatility — forcing
a tight, counterfactual link between the level of rates and expected excess returns.
"Essentially affine" models break this link by allowing flexible, essentially
arbitrary risk premia without losing the affine tractability. The result:
**dramatically better yield forecasts and more realistic term premia dynamics**.

---

## The Problem with Standard Affine Models

### Completely Affine Models (Vasicek, CIR)

In these models, the market price of risk is:
$$\lambda(X_t) = \lambda_0 + \lambda_1 X_t$$
but with $\lambda_0 = 0$ — the risk premium is proportional to the state variable
(and thus to volatility in CIR, or to $r_t$ itself in Vasicek).

The problem: this forces the **sign and magnitude** of the risk premium to be
mechanically tied to the level of rates. When rates are high, risk premia must
be high. When rates are low (near zero), risk premia must be near zero.

Empirical fact: risk premia (term premia) are countercyclical — they are high
when rates are low (recessions, flight to safety). Completely affine models
cannot capture this.

### Essentially Affine Models

Duffee's fix: allow the full affine risk price:
$$\lambda(X_t) = \Sigma^{-1}(\lambda_0 + \lambda_1 X_t)$$
where $\Sigma$ is the diffusion matrix. Under $\mathbb{Q}$, the dynamics remain
affine. Under $\mathbb{P}$, the drift is modified by $\lambda_0 + \lambda_1 X_t$
without any constraint tying risk premia to volatility.

---

## Key Findings

### Forecasting Performance

Duffee compares three model classes on out-of-sample yield forecasts (1952–1994):
- **Completely affine** (Vasicek/CIR-style): poor — loses to random walk at 6M+ horizons
- **Essentially affine** (his proposal): substantially better — beats random walk at
  3M, 6M, and 12M for most maturities
- **Random walk benchmark**: outperforms completely affine at most horizons

The essentially affine model reduces RMSE by 15–30% vs. completely affine at
6–12M horizons. At 1M horizons, differences are small.

### Why Risk Premia Matter for Forecasting

Under completely affine models, the physical drift of yields is too tightly linked
to the risk-neutral drift — forecasts are essentially the expected path under $\mathbb{Q}$
rather than $\mathbb{P}$. Essentially affine models allow the $\mathbb{P}$ dynamics
to be estimated freely, capturing the empirical mean-reversion of yields more accurately.

### Term Premia Implications

- Term premia under essentially affine models are **countercyclical** — high when
  the level of rates is low (recessions) and low when rates are high.
- This matches the Fama-Bliss (1987) and Campbell-Shiller (1991) evidence that
  forward rates predict excess bond returns with time-varying risk premia.
- Completely affine models predict procyclical term premia — empirically wrong.

---

## Key Takeaways

1. **The physical measure matters for trading.** Practitioners care about $\mathbb{P}$
   (real-world expected returns), not just $\mathbb{Q}$ (risk-neutral pricing).
   A model that fits the yield curve perfectly under $\mathbb{Q}$ can still give
   terrible expected return forecasts under $\mathbb{P}$.

2. **Term premia are countercyclical.** When yields are low, investors demand more
   compensation for duration risk (uncertainty about rate normalization). This is
   the Kim-Wright (2005) finding in a closely related model.

3. **Essentially affine = free lunch in tractability.** The modification preserves
   the closed-form bond pricing of affine models while freeing the risk premium
   to be estimated empirically. There is no cost in model complexity.

4. **Implication for RV:** If term premia are currently compressed (Kim-Wright TP
   near historical lows), the ex ante Sharpe on long-duration bonds is low — even
   if the yield looks attractive. Ch9's analytic process should incorporate term
   premia as a regime overlay.

5. **Model selection test:** Duffee provides formal likelihood ratio tests comparing
   model classes — a template for practitioners who want to test which affine
   specification fits their data best.

---

## Caveats

- **Sample period ends 1994.** The model has not been validated through the 2008 ZLB
  period or the 2022 hiking cycle in its original form.
- **Latent factors.** The three factors are statistical (latent), not observable.
  Mapping them to observable macro variables requires additional structure
  (Diebold-Rudebusch-Aruoba 2006).
- **No-arb vs. forecasting trade-off.** Models optimized for forecasting under $\mathbb{P}$
  may fit the cross-section of yields under $\mathbb{Q}$ less well.

---

## Connection to FIRV Book Chapters

| Chapter | Connection |
|---------|------------|
| **Ch6 — Yield Curve Models** | Essentially affine models are the modern affine ATSM standard; Ch6's discussion of model selection directly reflects Duffee's findings |
| **Ch9 — Analytic Process** | The ex ante expected return calculation in Ch9 requires $\mathbb{P}$ dynamics; essentially affine models provide the correct framework |
| **Ch2 — Mean Reversion** | Duffee's result implies mean reversion parameters estimated under $\mathbb{Q}$ (from derivative prices) differ from $\mathbb{P}$ (from time-series) — a key calibration choice |

---

## Adjacent Papers to Read Next

- **Kim & Wright (2005)** — implements essentially affine 3-factor model; Fed publishes estimates daily
- **Cochrane & Piazzesi (2005)** — single factor from forward rates predicts excess bond returns; related evidence on time-varying risk premia
- **Joslin, Singleton & Zhu (2011)** — canonical essentially affine estimation with observable factors

---

*Cerebro — 2026-03-26 | FIRV study: Duffee (2002)*
