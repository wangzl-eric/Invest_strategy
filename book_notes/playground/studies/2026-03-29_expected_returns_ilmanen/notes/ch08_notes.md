# ER Chapter 8 Notes: Bond-Equity Interactions

## Core Concept

The study briefing defines Chapter 8 as `Bond-equity interactions`, but the source 2011 PDF has no standalone chapter with that title. This note is therefore a sourced thematic synthesis built mainly from the stock-bond correlation and safe-haven material embedded in actual PDF Chapter 9, with supporting context from the equity-bond premium discussion in actual PDF Chapter 8.

The core idea is that bond-equity interaction is regime-dependent, not structural. Government bonds can be excellent diversifiers when inflation is anchored and flight-to-quality behavior dominates, but they can fail badly when inflation shocks and supply-side stress make stocks and bonds sell off together.

## Author Intent

Ilmanen's practical aim is to stop the reader from treating stock-bond diversification as a constant portfolio law. He wants investors to understand that:

- bond valuations partly reflect safe-haven value
- the stock-bond correlation is a state variable
- inflation regime and macro shock type drive whether bonds hedge or amplify equity risk

This thematic material also explains why relative valuation measures such as earnings yield versus Treasury yield can become misleading across secular regime shifts.

## Key Technicalities

- The most important state variable is stock-bond correlation, $\rho_{S,B}$.
- When inflation expectations are well anchored and demand shocks dominate, nominal Treasuries tend to hedge recession risk and $\rho_{S,B}$ can be negative.
- When supply shocks and inflation surprises dominate, stock and bond returns can move together and $\rho_{S,B}$ can turn positive.
- The bond safe-haven premium and the bond risk premium are linked:
  - a more negative stock-bond correlation raises the hedging value of Treasuries
  - that can justify a lower or even negative required bond risk premium
- On the equity side, the relative valuation shorthand is the equity-bond premium, often proxied using earnings yield versus Treasury yield. That shorthand is only stable within a regime because the underlying riskiness of bonds changes.
- Ilmanen explicitly warns of a "triple-whammy" bond problem in an inflation upswing:
  - higher expected inflation lifts nominal yields directly
  - inflation uncertainty raises required bond premia
  - bonds can lose safe-haven value as stock-bond correlation turns less negative or positive

## Historical Evidence, Theories, and Forward-Looking Indicators

- Over long history, average stock-bond correlation is only mildly positive, but the sign changes materially across regimes.
- Ilmanen highlights `1965-1997` as a period of especially positive stock-bond correlation because inflation expectations drove both markets.
- He also highlights the late 1990s and 2000s as a period when the correlation flipped deeply negative and Treasuries became unusually strong safe havens.
- The source material also ties the 1930s, parts of the 1950s and early 1960s, and crisis episodes such as `1987`, `1998`, `2002`, and `2008` to stronger hedging behavior from Treasuries.
- On the equity side, the earnings-yield/Treasury-yield relation is historically tight, but Ilmanen stresses that this relation partly reflects changing bond risk and changing inflation regimes, not just static relative valuation.
- The main forward-looking indicators suggested by the source are:
  - inflation level and inflation-expectation stability
  - stock-bond correlation itself
  - equity-bond valuation gaps such as earnings yield versus Treasury yield
  - macro-shock type, especially demand-shock versus supply-shock environments

## Chapter Connections

- This note bridges [ch07_notes.md](/Users/zelin/Desktop/PA%20Investment/Invest_strategy/workstation/playground/studies/2026-03-29_expected_returns_ilmanen/ch07_notes.md) and [ch09_notes.md](/Users/zelin/Desktop/PA%20Investment/Invest_strategy/workstation/playground/studies/2026-03-29_expected_returns_ilmanen/ch09_notes.md): ERP and BRP cannot be interpreted cleanly without understanding how stock and bond risks interact.
- It also anticipates the book's later emphasis on regime dependence, crisis alpha, and cross-asset strategy design.
- Within this repo, it fits directly with the existing GMT macro-regime work and the bond-risk-premium notebook already built in this study folder.

## What Seems Immediately Testable with Available Data

- Reuse the local hypothesis scaffold `BE-1` in `study_hypotheses.md` to test whether rolling correlation between `SPY` and changes in `DGS10` becomes more negative when `T5YIE` and `T10YIE` are subdued.
- Reuse `01_equity_risk_premium.ipynb` and `02_bond_risk_premium.ipynb` to examine whether equity and duration signals change sign or strength across inflation-regime labels.
- Build regime-specific correlation matrices for `SPY`, `DGS10` changes, `GC=F`, `CL=F`, and `BAMLH0A0HYM2` changes, consistent with the `BE-2` hypothesis already documented in the study folder.
- Track whether local bond-equity diversification weakens when breakevens rise or when `NFCI` and funding-stress proxies worsen.

## What Likely Requires External or Harder-to-Source Data

- Longer stock-bond correlation histories with consistent inflation-expectation measures.
- Cleaner decomposition of demand-shock versus supply-shock macro regimes.
- Institutional flow data to measure safe-haven demand directly rather than via market prices.

## Material Score

- Credibility: 4/5. The topic is strongly grounded in the source chapters, even though this note is a study-briefing synthesis rather than a standalone book chapter.
- Relevance: 5/5. Bond-equity interaction is central to portfolio construction and directly affects how ERP and BRP should be interpreted.
- Actionability: 5/5. The repo already contains enough macro, rate, and market data to test the main regime and correlation claims in reduced form.

## Open Questions and Things to Verify Empirically

- Does the recent local sample preserve Ilmanen's stock-bond correlation regime logic, or is it too short and post-QE-specific?
- Is inflation expectation level, inflation uncertainty, or funding stress the best practical trigger for diversification breakdown?
- When the earnings-yield/Treasury-yield gap widens, how much is true ERP versus a change in bond hedging value?
- Can stock-bond correlation itself be treated as a tradable state variable for allocation timing, or is it too unstable out of sample?
