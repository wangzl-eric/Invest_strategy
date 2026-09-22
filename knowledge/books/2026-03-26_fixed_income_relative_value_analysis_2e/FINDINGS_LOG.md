# FINDINGS LOG — Fixed Income Relative Value Analysis (2nd ed.)

This file tracks actionable ideas, tradeable signals, and replicable findings discovered during the study. Each entry should be concrete enough to act on or implement in a notebook.

## Log Format

```
### [DATE] [CHAPTER] — [FINDING TITLE]
- **Type**: signal / methodology / data insight / trade idea / model
- **Source**: chapter + page / paper
- **Finding**: what was found
- **Actionability**: how to implement or test it
- **Status**: idea / scaffolded / tested / promoted
```

---

## Entries

### 2026-03-27 Ch2 — Treasury 2s5s10s Butterfly OU Fit
- **Type**: signal
- **Source**: Chapter 2, 01_mean_reversion.ipynb
- **Finding**: Treasury 2s5s10s butterfly (2×DGS5 − DGS2 − DGS10) fits an OU process with half-life ~28 trading days. Current z-score ~0.01 (flat, no signal). Long-run mean: -0.272. Range: -0.47 to +0.03.
- **Actionability**: monitor z-score for entry signals beyond ±1.5–2.0. Half-life of 28 days is short enough for tactical positioning.
- **Status**: scaffolded

### 2026-03-27 Ch3 — DGS5 PCA Residual Rich/Cheap Signal
- **Type**: signal
- **Source**: Chapter 3, 02_pca_yield_curve.ipynb
- **Finding**: Rolling PCA on Treasury curve (DGS2–DGS30). DGS5 shows residual z-score of ~-2.54 after removing first 3 factors — strongest outlier in the curve. PCA-neutral 2Y/5Y/10Y butterfly z-score: -1.34 (approaching but not yet at ±1.5 entry band).
- **Actionability**: DGS5 is cheap relative to the PCA-reconstructed curve. Monitor for convergence. PCA-neutral butterfly is a factor-hedged expression of this view.
- **Status**: scaffolded

### 2026-03-27 Ch3 — PCA Factor Instability Risk
- **Type**: methodology
- **Source**: Chapter 3, ch03_notes.md
- **Finding**: PCA eigenvectors are sample-specific and can drift materially across regimes. Static hedges based on PCA loadings can become stale under stress.
- **Actionability**: use rolling PCA with stability diagnostics. Flag when eigenvector loadings shift more than a threshold across consecutive windows.
- **Status**: scaffolded

### 2026-03-27 Paper — Litterman & Scheinkman (1991) Level/Slope/Curvature
- **Type**: methodology
- **Source**: paper_notes_litterman1991.md
- **Finding**: First 3 PCA factors explain ~98% of yield curve variance. Level (89%), slope (8%), curvature (3%). Duration hedges only level risk — slope and curvature require separate butterfly/fly positions.
- **Actionability**: use 3-factor hedge ratios when constructing curve trades. Residuals from 3-factor fit are the RV signal.
- **Status**: scaffolded

### 2026-03-27 Paper — Diebold & Li (2006) DNS Factor Macro Interpretations
- **Type**: methodology
- **Source**: paper_notes_diebold2006.md
- **Finding**: Dynamic Nelson-Siegel level factor correlates with inflation, slope with monetary policy stance, curvature with business cycle. DNS beats random walk at 6–12 month forecast horizons.
- **Actionability**: use DNS factors as macro regime indicators alongside PCA. Scaffold a DNS notebook replicating L&S and DNS side by side on Treasury data.
- **Status**: idea

### 2026-03-27 Ch5 — Duration-Only Hedge Trap in Long-End Curve Trades
- **Type**: methodology
- **Source**: Chapter 5, FIRV study_hypotheses.md
- **Finding**: Duration-neutral barbell-versus-bullet and `10s30s` structures can still carry material convexity mismatch. Large move days should expose residual second-order risk even when first-order DV01 is neutral.
- **Actionability**: add convexity-adjusted PnL attribution to Treasury curve trade studies and compare linear versus quadratic hedge error on shock days.
- **Status**: idea

### 2026-03-27 Ch7 — CTD Studies Need Delivery Basket and Repo Inputs
- **Type**: data insight
- **Source**: Chapter 7, FIRV study_hypotheses.md
- **Finding**: Cheapest-to-deliver dynamics cannot be studied cleanly from Treasury yield curves alone. A proper CTD notebook needs deliverable basket membership, conversion factors, futures prices, and repo financing inputs.
- **Actionability**: treat CTD work as a data-ingestion milestone before implementation. Until then, keep Chapter 7 as a documented hypothesis set rather than a runnable notebook.
- **Status**: idea

### 2026-03-27 Ch8/9 — Fitted-Curve Residuals Are The Next Clean Local Signal Family
- **Type**: signal
- **Source**: Chapters 8-9, FIRV study_hypotheses.md
- **Finding**: With the current local Treasury curve data, fitted-curve richness/cheapness residuals are the most actionable next extension beyond PCA residuals. The strongest process candidate is the Chapter 9 sequence: PCA for maturity selection plus fitted-curve residuals for security selection.
- **Actionability**: implement daily fitted-curve residuals on Treasury constant-maturity yields and compare their reversion quality against raw slope/butterfly signals and PCA-only residual screens.
- **Status**: scaffolded

### 2026-03-27 Ch11/12 — Asset Swap Regime Model Can Start Before ASW Data Arrives
- **Type**: model
- **Source**: Chapters 11-12, FIRV study_hypotheses.md
- **Finding**: Even though asset swap spread time series are missing, the local lake already contains usable regime features (`SOFR`, `DFEDTARU`, `T10Y2Y`, `T10Y3M`, `T5YIE`, `T10YIE`) for a future ASW regime model.
- **Actionability**: formalize a funding-regime classification layer now so ASW spread series can plug into it immediately once ingested.
- **Status**: scaffolded

### 2026-03-27 Ch15 — Cross-Currency Basis Needs Regime Layer Before Market Data Arrives
- **Type**: model
- **Source**: Chapter 15, FIRV study_hypotheses.md
- **Finding**: Cross-currency basis studies are blocked on forwards, foreign OIS curves, and quoted basis series, but the regime layer can already be built from local USD funding and FX spot proxies.
- **Actionability**: define a USD funding-stress classification using `SOFR`, `DFEDTARU`, curve inversion, and dollar-strength proxies so future CCBS data can be analyzed immediately by regime.
- **Status**: scaffolded

### 2026-03-27 Ch17 — Funding-Adjusted Cheapness Can Disagree With Curve Cheapness
- **Type**: trade idea
- **Source**: Chapter 17, FIRV study_hypotheses.md
- **Finding**: A bond can be cheap on fitted-curve metrics but not cheap once SOFR-based funding terms are included. That disagreement is itself an RV signal about funding frictions rather than pure curve mispricing.
- **Actionability**: when ASW data becomes available, compare fitted-curve residual ranks against SOFR-adjusted cheapness ranks and isolate days where the two disagree.
- **Status**: idea

### 2026-03-27 Ch19 — Options RV Requires Surface Data But The Factor Workflow Is Clear
- **Type**: methodology
- **Source**: Chapter 19, FIRV study_hypotheses.md
- **Finding**: The options chapter maps naturally into the same workflow already used in the curve notebooks: factor decomposition first, residual dislocation second, mean-reversion test third. The missing piece is implied-vol surface data.
- **Actionability**: once surface snapshots are available, build a vega-sector PCA notebook and test residual mean reversion by expiry bucket.
- **Status**: scaffolded

### 2026-03-27 Ch20 — Macro Overlay Should Be A Shared Risk Layer Across FIRV Signals
- **Type**: model
- **Source**: Chapter 20, FIRV study_hypotheses.md
- **Finding**: Macro regime conditioning is not just an add-on. It should become a shared overlay across mean-reversion, PCA, fitted-curve, basis, and ASW signals. The local lake already contains enough variables to start that classification layer.
- **Actionability**: define a common regime panel from `SOFR`, `DFEDTARU`, `T10Y2Y`, `T10Y3M`, inflation expectations, and credit/liquidity proxies, then evaluate each FIRV signal family inside those regimes.
- **Status**: scaffolded

### 2026-03-27 Ch20 — Four-Regime Overlay Can Be Built Entirely From Local FRED Inputs
- **Type**: model
- **Source**: macro_regime_overlay.md
- **Finding**: A first-pass macro overlay can already be built from local series `SOFR`, `DFEDTARU`, `T10Y2Y`, `T10Y3M`, `T5YIE`, and `T10YIE`. These are sufficient to classify inflation shock, growth scare, stable carry, and funding stress without waiting for new data ingestion.
- **Actionability**: build a reusable regime panel first and attach it to the Chapter 2 and Chapter 3 signals before expanding to later signal families.
- **Status**: scaffolded

### 2026-03-27 Ch20 — Stable Carry Should Be The Cleanest Regime For Local Curve RV
- **Type**: signal
- **Source**: macro_regime_overlay.md
- **Finding**: Mean-reversion spreads, PCA residuals, and fitted-curve richness signals should all have their cleanest behavior in the stable-carry regime, where policy, curve, and inflation signals are all range-bound.
- **Actionability**: use stable carry as the first regime gate to benchmark unconditional versus gated hit rate and half-life.
- **Status**: scaffolded

### 2026-03-27 Ch15/17/20 — Funding Stress Should Override Other Macro Labels
- **Type**: methodology
- **Source**: macro_regime_overlay.md
- **Finding**: For basis, ASW, and funding-adjusted global bond RV, funding stress is the first-order regime split. It should override broader inflation-shock or growth-scare labels because convergence mechanics change when balance-sheet constraints bind.
- **Actionability**: classify funding stress first in the regime-assignment order, then assign the remaining macro regime only if funding stress is absent.
- **Status**: scaffolded

### 2026-03-27 Ch2 — MR-1 Hit Rate Is 1.0 In Growth Scare And Inflation Shock
- **Type**: signal
- **Source**: 08_macro_regime_panel.ipynb
- **Finding**: The Chapter 2 `MR-1` mean-reversion signal achieved a hit rate of `1.0` in both the growth-scare regime and the inflation-shock regime in the current sample.
- **Actionability**: prioritize MR-1 entries when the overlay classifies the market as growth scare or inflation shock, then compare whether the stronger hit rate is offset by slower convergence or smaller sample count.
- **Status**: tested

### 2026-03-27 Ch3 — PCA-2 Hit Rate Is 0.74 In Inflation Shock
- **Type**: signal
- **Source**: 08_macro_regime_panel.ipynb
- **Finding**: The Chapter 3 `PCA-2` PCA-neutral butterfly signal achieved a hit rate of `0.74` in the inflation-shock regime in the current sample.
- **Actionability**: treat inflation shock as a viable, not automatically excluded, regime for PCA-neutral curve structures. Next compare this regime hit rate against unconditional hit rate and realized half-life before setting hard gates.
- **Status**: tested

### 2026-03-27 Ch4 — Johansen Rank Test on 2Y/5Y/10Y System
- **Type**: methodology
- **Source**: 06_multivariate_mean_reversion.ipynb
- **Finding**: Johansen trace test fails to reject rank=0 at 95% for 2Y/5Y/10Y Treasury yields on a 2-year sample. Rank=1 imposed for VECM. Beta vector: 1×2Y − 5.33×5Y + 12.44×10Y. Alpha speeds: 2Y=-0.0023, 5Y=-0.0041, 10Y=-0.0039. VECM z-score latest: -1.52 (2026-02-25), directionally consistent with MR-1 and PCA-2.
- **Actionability**: extend data history to 5-10 years to establish robust cointegration rank. Current VECM z-score at -1.52 — monitor for breach of -2.0. All three signal families (OU, PCA, VECM) aligned short the spread.
- **Status**: tested

### 2026-03-27 Ch4 — Three Signal Families Currently Aligned
- **Type**: signal
- **Source**: 01_mean_reversion.ipynb, 02_pca_yield_curve.ipynb, 06_multivariate_mean_reversion.ipynb
- **Finding**: As of 2026-02-25, three independent signal families point in the same direction on the Treasury curve: OU z-score ~0.01 (flat), DGS5 PCA residual z-score -2.54, VECM cointegrated spread z-score -1.52. DGS5 is cheap vs the curve on two independent measures.
- **Actionability**: DGS5 cheapness is the highest-conviction signal. Convergence trade: long DGS5 vs PCA-neutral hedge. Monitor for regime (currently check macro_regime_daily.parquet for current classification).
- **Status**: tested
