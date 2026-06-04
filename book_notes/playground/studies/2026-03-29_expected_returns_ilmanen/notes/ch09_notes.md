# ER Chapter 9 Notes: Bond Risk Premium

## Core Concept

The bond risk premium, or term premium, is the expected return advantage of holding long-duration government bonds instead of rolling short-term bills or short bonds. Ilmanen's core claim is that the yield curve mixes two distinct objects:

- expected future short-rate paths
- required compensation for duration risk

The practical problem is that curve steepness is observable but the true ex ante bond risk premium is not.

## Author Intent

Ilmanen wants the reader to disentangle bond carry from bond timing. The chapter is both conceptual and practitioner-facing: it lays out the identities connecting yields, expectations, and excess returns, then asks which proxies actually help duration timing in real time.

His own bias is clear. He views survey-anchored and real-yield-based BRP measures as underused and often more informative than naive yield-curve steepness.

## Key Technicalities

- Ilmanen distinguishes realized excess bond return from the ex ante BRP and from raw curve steepness.
- The near-horizon BRP identity is approximately:

$$
BRP_H \approx (Y_{10} - Y_1) - Duration_{10}\,E(\Delta Y_{10})
$$

- The yield-based decomposition is:

$$
Y_{10} \approx E(\overline{Y_1}) + BRP
$$

  and can be refined into expected inflation, expected real short rates, and BRP.
- Four BRP proxies dominate the chapter:
  - yield-curve steepness
  - Cochrane-Piazzesi forward-rate factor
  - term-structure-model estimates such as Kim-Wright
  - survey-based BRP
- Ilmanen's four main BRP drivers are:
  - level-dependent inflation uncertainty
  - safe-haven or stock-bond covariance effects
  - supply-demand effects
  - cyclical effects
- A central technical claim is that curve steepness can be a good predictor of near-term bond returns while still being a poor measure of long-run ex ante BRP, because mean-reverting rate expectations contaminate it.

## Historical Evidence, Theories, and Forward-Looking Indicators

- Long-run Treasury returns from `1952-2009` show a positive but nonlinear maturity risk-reward relation: excess return rises with duration, but Sharpe ratios fall with duration.
- Realized average excess bond return is around `1%`, but that number can be badly distorted when the sample contains large yield declines.
- Yield-curve steepness predicts near-term excess returns better than future long-yield changes, but it has weak power over multi-year horizons.
- Ilmanen argues that the main secular postwar driver of BRP was a level-dependent inflation premium, which rose into the early 1980s and later collapsed.
- Stock-bond correlation matters because Treasuries with negative equity beta can rationally earn a lower premium or even a negative one.
- The chapter is skeptical that all curve-based return predictability reflects rationally time-varying premia. Some of it may instead be systematic forecast error in short-rate expectations.
- Tactical duration signals in the chapter include:
  - a steep yield curve
  - high survey-based BRP
  - high ex ante real yield
  - weak growth or weak equity markets
  - bond-market momentum

## Chapter Connections

- This chapter is the fixed-income counterpart to [ch07_notes.md](/Users/zelin/Desktop/PA%20Investment/Invest_strategy/workstation/playground/studies/2026-03-29_expected_returns_ilmanen/ch07_notes.md) and depends heavily on the interaction logic summarized in [ch08_notes.md](/Users/zelin/Desktop/PA%20Investment/Invest_strategy/workstation/playground/studies/2026-03-29_expected_returns_ilmanen/ch08_notes.md).
- It also connects directly to the FIRV yield-curve work already present elsewhere in the repo.
- The predictive-signal framework here leads naturally into later carry and tactical-allocation chapters.

## What Seems Immediately Testable with Available Data

- Reuse `02_bond_risk_premium.ipynb`, `02_bond_risk_premium_regime_summary.csv`, `02_cp_forward_regression_quintiles.csv`, and `02_cp_forward_regression_weights.csv` to test whether local curve-shape and forward-rate factors already line up with stronger future duration returns.
- Replicate the textbook steep-curve signal using `T10Y3M` and `T10Y2Y`, then condition on breakevens to test Ilmanen's claim that inflation regime contaminates simple steepness.
- Compare yield-curve steepness with ex ante real-yield proxies based on `DFII5`, `DFII10`, and nominal Treasury yields.
- Test whether local duration performance is strongest when curve steepness coincides with muted inflation repricing, consistent with `BRP-1` and `BRP-2` in `study_hypotheses.md`.

## What Likely Requires External or Harder-to-Source Data

- Long-horizon survey forecasts of future short rates.
- Full Kim-Wright style term-premium estimates or a richer macro-finance term-structure model.
- Better bond total-return histories across maturities and countries for robust long-run replication.

## Material Score

- Credibility: 5/5. This is one of the book's strongest practitioner chapters and is tightly grounded in fixed-income theory and evidence.
- Relevance: 5/5. It maps directly to existing local notebooks and to the repo's broader yield-curve work.
- Actionability: 5/5. Even reduced-form versions of the chapter's timing signals are immediately testable with local rate and FRED data.

## Open Questions and Things to Verify Empirically

- Does curve steepness in the current local sample mainly reflect expected policy normalization or genuine term premium?
- Are real-yield and survey-like proxies better duration signals than raw steepness once inflation regimes are accounted for?
- How stable is the Cochrane-Piazzesi style signal in a short modern sample relative to the original long U.S. sample?
- If bonds lose safe-haven status in an inflation shock, how quickly do standard duration-timing signals fail?
