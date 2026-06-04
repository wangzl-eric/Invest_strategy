# Paper Notes: Bond Risk Premia
**Authors:** Cochrane, Piazzesi | **Year:** 2005 | **Journal:** American Economic Review
**Date Read:** 2026-03-29 | **Scores:** Credibility 5 | Relevance 5 | Actionability 4

---

## Core Thesis

A single linear combination of forward rates — the "CP factor" — predicts excess bond returns across all maturities with striking power. Contrary to the expectations hypothesis (which posits that bond returns are unpredictable beyond a constant term premium), Cochrane and Piazzesi show that a tent-shaped combination of the 1-year yield and the 2- through 5-year forward rates explains up to 44% of the variation in annual excess returns on 2- to 5-year bonds. The same factor that forecasts 2-year returns also forecasts 3-, 4-, and 5-year returns (up to a scalar multiple), implying a one-factor structure in expected bond risk premia. This is the strongest evidence produced at the time that bond risk premia are time-varying and large.

---

## Key Findings

1. **R² up to 44%** for 5-year bond excess returns (annual horizon, 1964–2003), versus ~18% for the yield spread (slope) alone.
2. **Single-factor structure:** Forecasting regressions across maturities collapse to $\mathbb{E}_t[rx^{(n)}_{t+1}] = b_n \cdot cp_t$, where $cp_t$ is the common CP factor and $b_n$ is a maturity-specific loading.
3. **Tent-shaped coefficients:** Weights on forward rates are negative at the short end ($f^{(1)}$), peak around $f^{(3)}$, then turn negative again at $f^{(5)}$.
4. **Dominates Fama-Bliss:** The Fama-Bliss (1987) forward-spread predictor is a restricted special case. The unrestricted CP factor adds substantial explanatory power.
5. **Sample stability:** Forecasting power is present in both pre- and post-1980 subsamples, though somewhat weaker post-1980.
6. **Unspanned component:** The CP factor contains a component not spanned by the first three PCA factors (level, slope, curvature), which carries the bulk of predictive power.

---

## Methodology

- **Data:** Fama-Bliss unsmoothed zero-coupon yield data, 1964–2003, annual frequency. Five annually compounded zero yields: $y^{(1)}_t, \ldots, y^{(5)}_t$.
- **Forward rates:** $f^{(n)}_t = n \cdot y^{(n)}_t - (n-1) \cdot y^{(n-1)}_t$. So $f^{(1)}_t = y^{(1)}_t$, $f^{(2)}_t = 2y^{(2)}_t - y^{(1)}_t$, etc.
- **Excess returns:** $rx^{(n)}_{t+1} = r^{(n)}_{t+1} - y^{(1)}_t$, where $r^{(n)}_{t+1}$ is the log holding-period return on an $n$-year zero-coupon bond held for one year.
- **Step 1:** Regress the average excess return $\bar{rx}_{t+1} = \frac{1}{4}\sum_{n=2}^{5} rx^{(n)}_{t+1}$ on all five forward rates. The fitted value is $cp_t$.
- **Step 2:** Regress each $rx^{(n)}_{t+1}$ on $cp_t$ alone to get maturity-specific loadings $b_n$.
- OLS throughout; main results use non-overlapping annual returns so standard errors are conventional.
- No out-of-sample or walk-forward analysis presented in the original paper.


---

## The CP Factor (Signal Construction)

The CP factor is the fitted value from regressing the average excess bond return on all five forward rates:

$$cp_t = \hat{\gamma}_0 + \hat{\gamma}_1 f^{(1)}_t + \hat{\gamma}_2 f^{(2)}_t + \hat{\gamma}_3 f^{(3)}_t + \hat{\gamma}_4 f^{(4)}_t + \hat{\gamma}_5 f^{(5)}_t$$

**Tent-shaped coefficient vector** $\hat{\gamma}$ (approximate values from the paper):

| Forward Rate | Coefficient (approx.) |
|---|---|
| $f^{(1)}$ (1-yr yield / short rate) | $-2.14$ |
| $f^{(2)}$ (2-yr forward) | $0.81$ |
| $f^{(3)}$ (3-yr forward) | $3.00$ |
| $f^{(4)}$ (4-yr forward) | $0.80$ |
| $f^{(5)}$ (5-yr forward) | $-2.08$ |
| Intercept | $-4.68$ |

The tent shape: large negative at $f^{(1)}$, rising to a peak near $f^{(3)}$, declining and turning negative at $f^{(5)}$. The factor is high when the intermediate forward curve is humped relative to both ends.

**Individual maturity forecasting equation:**
$$\mathbb{E}_t[rx^{(n)}_{t+1}] = b_n \cdot cp_t$$

Maturity loadings $b_n$ rise roughly linearly: $b_2 \approx 0.44$, $b_3 \approx 0.85$, $b_4 \approx 1.27$, $b_5 \approx 1.45$. Longer bonds load more heavily on the common factor, consistent with greater duration risk.


---

## Forecasting Performance

| Maturity | $R^2$ — CP factor | $R^2$ — yield slope only |
|---|---|---|
| 2-year | ~15% | ~8% |
| 3-year | ~28% | ~14% |
| 4-year | ~35% | ~16% |
| 5-year | ~44% | ~18% |
| Average (Step 1) | ~35% | ~17% |

- CP factor roughly doubles the $R^2$ of the yield slope at every maturity.
- Improvement is monotonically increasing with maturity — longer bonds are more exposed to the common risk factor.
- The Fama-Bliss forward spread and the yield curve slope are both nested within the CP specification and are strictly dominated by it.
- Results hold at annual frequency; monthly regressions (with overlapping returns) show qualitatively similar patterns but require Hansen-Hodrick or Newey-West corrections.

---

## Economic Interpretation

**Why tent-shaped?** The tent captures curvature information about the forward curve that neither slope nor level alone provides. A humped forward curve — elevated intermediate forwards relative to both ends — historically signals that investors require extra compensation for duration risk. The short rate ($f^{(1)}$) enters negatively because a high short rate mechanically compresses term premia (the Fed is tight, carry is eroded). The long forward ($f^{(5)}$) enters negatively because it partially reflects the expectations hypothesis component. The middle of the curve, stripped of these two effects, isolates the pure risk premium signal.

**Time-varying risk premia:** The factor is interpreted as the time-varying market price of interest rate risk. When $cp_t$ is high, investors demand more compensation per unit of duration — either because risk aversion has risen or because bond supply/demand imbalances have widened. Empirically, $cp_t$ is elevated during early recovery phases (post-recession), after Fed tightening cycles, and during credit stress episodes.

**Habit formation:** Cochrane and Piazzesi note qualitative consistency with Campbell-Cochrane (1999) external habit formation. When the surplus consumption ratio is low (bad times), risk aversion spikes and investors demand higher premia across all risky assets including bonds. The single-factor structure also maps to a one-factor SDF with a time-varying price of risk, consistent with habit dynamics.

**Not the expectations hypothesis:** The EH predicts $R^2 = 0$ for excess returns. The magnitude of predictability found here (up to 44%) is far beyond sampling error and directly falsifies the EH over this sample.


---

## Connection to Term Structure Models

**Fama-Bliss (1987):** The classic result is that the forward-spot spread $f^{(n)}_t - y^{(1)}_t$ predicts excess returns on $n$-year bonds with $R^2 \approx 10$–$18\%$. The CP regression nests Fama-Bliss: imposing the restriction that only the spread $f^{(n)} - f^{(1)}$ enters (ignoring the other forwards) recovers approximately the Fama-Bliss result. Relaxing this restriction to the full five-forward vector yields a factor that dominates strictly.

**Affine term structure models (ATSMs):** Standard Gaussian affine models (Vasicek, CIR) with constant market prices of risk $\lambda$ imply the expectations hypothesis at all horizons — no excess return predictability. The CP results require time-varying $\lambda_t$, which is the hallmark of "essentially affine" models (Duffee 2002) and "completely affine" models. The tent-shaped factor is not spanned by the standard three-factor PCA decomposition (level, slope, curvature), which is why simpler models miss it entirely.

**Unspanned risk factors:** The paper shows that the CP factor has a component orthogonal to the first three PCs of yields. This unspanned component carries the bulk of the predictive power for returns, even though it contributes little to explaining the cross-section of yield levels. This finding motivated the Joslin-Priebsch-Singleton (2014) class of models with unspanned macro risk and Duffee's (2011) "hidden factor" literature.

**Cochrane-Piazzesi (2008):** A follow-up paper embeds the CP factor in a formal no-arbitrage ATSM, showing that the tent-shaped factor can be reconciled with no-arbitrage pricing if the market price of risk loads on a combination of forward rates rather than just the standard level/slope/curvature PCs.

---

## Failure Modes & Limitations

1. **In-sample overfit:** The CP factor is estimated on the full 1964–2003 sample with five free coefficients. Subsequent OOS studies (Thornton-Valente 2012; Duffee 2011) find dramatically lower or even negative OOS $R^2$, suggesting substantial in-sample overfit from the unrestricted five-variable regression.
2. **Parameter instability:** The tent-shaped coefficients are not stable across subsamples. Post-1980 estimates look different from pre-1980, and post-2003 evidence is mixed. Real-time replication requires recursive estimation, which degrades performance further.
3. **Data revision and availability:** Fama-Bliss unsmoothed yields are constructed from CRSP bond data with specific filters. Exact replication requires access to the original dataset; approximations using Gurkaynak-Sack-Wright (GSW) or FRED constant-maturity yields produce similar but not identical factors.
4. **Transaction costs and liquidity:** The paper is entirely theoretical/empirical — no implementation costs are considered. Actual trading on the CP signal requires Treasury futures or cash bonds, where bid-ask spreads and financing costs matter, especially for shorter maturities.
5. **Annual frequency:** Results are at annual horizon. Monthly replication requires overlapping returns and produces noisier estimates. The factor is a slow-moving (low-turnover) signal by construction.
6. **Forward rate measurement:** Small errors in zero-coupon yield bootstrapping amplify into larger errors in forward rates (especially at the 4- and 5-year point), which may introduce noise into the high-maturity CP coefficients.
7. **Post-2008 regime:** Zero lower bound, QE, and forward guidance fundamentally altered term structure dynamics post-GFC. The CP factor constructed on post-2008 data shows substantially weaker predictive power.


---

## Connection to Ilmanen Expected Returns Ch9 (Bond Risk Premium)

Ilmanen Chapter 9 treats the CP factor as one of three primary carry-based predictors of bond returns, alongside the yield curve slope (Fama-Bliss) and the real yield level. Key connections:

- **CP as the "forward rate factor":** Ilmanen situates CP within the broader framework that bond risk premia are driven by investor risk appetite, supply/demand for duration, and the business cycle. The tent shape is consistent with his view that the middle of the forward curve captures "pure" term premium, stripped of policy expectations at the short end and convexity at the long end.
- **Time-varying premia = the central theme of Ch9:** Ilmanen's chapter argues that the bond risk premium fluctuates between near-zero (late 1990s, early 2000s) and large positive values (early 1980s, post-GFC normalization). CP is his primary empirical exhibit for this claim.
- **Multi-predictor framework:** Ilmanen recommends combining CP with the real yield (TIPS-based or inflation-adjusted nominal yield) and the yield curve slope for a more robust composite predictor. No single factor dominates in all periods.
- **Practical signal construction:** Ilmanen explicitly discusses using the CP factor with recursive (expanding-window) estimation to avoid look-ahead bias, acknowledging that real-time $R^2$ is lower than the in-sample 44%.
- **Connection to carry:** The CP factor is related to bond carry (yield minus financing cost), but it is not identical. High CP regimes often but not always coincide with steep carry environments, particularly when curvature is high.
- **Macro regime overlay:** Ch9 argues that the CP factor is strongest as a predictor when combined with a macro regime signal (e.g., recession indicator, ISM momentum). Standalone CP is a necessary but not sufficient condition for a high-conviction bond overweight.

---

## Implementability for This Team

**FRED data needed:**

| Series | FRED ID | Description |
|---|---|---|
| 1-year Treasury CMT | `GS1` | Constant maturity, annual |
| 2-year Treasury CMT | `GS2` | Constant maturity, annual |
| 3-year Treasury CMT | `GS3` | Constant maturity, annual |
| 5-year Treasury CMT | `GS5` | Constant maturity, annual |
| 7-year Treasury CMT | `GS7` | Proxy for 4-yr interpolation |
| 10-year Treasury CMT | `GS10` | For context / longer end |

Note: FRED CMT yields are par yields, not zero-coupon yields. The Fama-Bliss dataset uses unsmoothed zero-coupon yields. For a practical approximation, the Gurkaynak-Sack-Wright (GSW) zero-coupon yield dataset is available from the Federal Reserve website (not FRED directly) and is the standard academic proxy.

**Forward rate construction from zero yields:**

Given zero-coupon yields $y^{(n)}_t$ (annually compounded), the $n$-year instantaneous forward rate is:
$$f^{(n)}_t = n \cdot y^{(n)}_t - (n-1) \cdot y^{(n-1)}_t$$

For CMT par yields, a bootstrap is required first to extract zero-coupon yields before applying this formula. The approximation error from using par yields directly is small for the 1- to 5-year range but non-negligible.

**Implementation steps:**
1. Pull GSW zero-coupon yields (or bootstrap from FRED CMT) at 1, 2, 3, 4, 5-year maturities, monthly frequency.
2. Compute forward rates $f^{(1)}$ through $f^{(5)}$ via the formula above.
3. Construct excess returns: use iShares/SPDR Treasury ETFs (SHY, IEI, IEF) as bond return proxies, or compute synthetic returns from yield changes with duration approximation.
4. Run Step 1 regression (average excess return on all five forwards) with expanding window to estimate $\hat{\gamma}_t$ recursively.
5. The CP signal at time $t$ is $cp_t = \hat{\gamma}_t' f_t$; use lagged $\hat{\gamma}$ to avoid look-ahead.
6. Use $cp_t$ as a timing signal for Treasury duration: overweight when $cp_t$ is in top tercile of its trailing distribution, underweight in bottom tercile.

**Existing infrastructure:** `quant_data/connectors/` already supports FRED pulls. The `backtests/` framework supports signal-based timing. The `02_bond_risk_premium.ipynb` notebook in this study folder already implements a version of the CP forward regression — check `02_cp_forward_regression_weights.csv` for computed coefficients.

**Realistic OOS expectation:** $R^2$ of 10–20% at monthly frequency with recursive estimation, versus the in-sample 35–44% annual figure. Sharpe ratio of a pure CP timing strategy on 10-year Treasuries: approximately 0.3–0.5 before costs in academic replications.


---

## Key Quotes

> "A single factor predicts excess returns on two- to five-year maturity bonds with $R^2$ up to 44 percent."

> "The single forecasting factor is a tent-shaped linear function of forward rates. It is high when the middle forward rates are high relative to the short and long forward rates."

> "Bond risk premia are strongly time-varying and are driven by this single factor that is not captured by the slope of the yield curve alone."

> "The return-forecasting factor has a component that is not spanned by the level, slope, and curvature factors that summarize most of the variation in yields."

> "Our results suggest that models with time-varying risk premia — such as habit formation models — are needed to explain bond return predictability."

---

## Follow-Up Papers

| Paper | Authors | Year | Why Relevant |
|---|---|---|---|
| Expectations Hypotheses Tests | Fama, Bliss | 1987 | Original forward-spread predictor; nested by CP |
| Essentially Affine Term Structure | Duffee | 2002 | ATSM framework with time-varying risk prices; makes CP consistent with no-arbitrage |
| Bond Risk Premia (no-arb version) | Cochrane, Piazzesi | 2008 | AER P&P; embeds CP factor in formal ATSM |
| Macro Factors in Bond Risk Premia | Ludvigson, Ng | 2009 | Adds macro factors to CP; combined $R^2$ rises to ~26% monthly |
| Forecasting Bond Returns OOS | Thornton, Valente | 2012 | Shows OOS $R^2$ of CP is near zero; challenges practical usefulness |
| Forecasting with Unspanned Risk | Duffee | 2011 | "Hidden factor" literature; unspanned macro risk |
| Unspanned Macro Risks | Joslin, Priebsch, Singleton | 2014 | Formal ATSM with unspanned factors; theoretical foundation for CP unspanned component |
| Yield Curve Predictors (survey) | Diebold, Rudebusch | 2013 | Book-length treatment; places CP in broader forecasting literature |
| Expected Returns | Ilmanen | 2011 | Ch9 integrates CP into multi-predictor bond risk premium framework |
| Return Predictability Across Asset Classes | Koijen, Moskowitz, Pedersen, Vrugt | 2018 | Generalizes carry concept; bond carry is related but distinct from CP |

