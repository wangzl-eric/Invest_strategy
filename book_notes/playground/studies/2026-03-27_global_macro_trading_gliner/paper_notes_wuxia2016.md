# Paper Notes: "Measuring the Macroeconomic Impact of Monetary Policy at the ZLB" — Wu & Xia (2016)

**Citation:** Wu, J., Xia, F. (2016). Measuring the Macroeconomic Impact of Monetary Policy at the Zero Lower Bound. *Journal of Money, Credit and Banking*, 48(2–3), 253–291.
**DOI:** 10.1111/jmcb.12300
**Scores:** C:5 / R:4 / A:4

---

## Core Thesis

When the policy rate hits the zero lower bound (ZLB), conventional rate measures fail to capture the true stance of monetary policy. The Wu-Xia shadow rate extends the effective fed funds rate into negative territory using a term structure model, providing a continuous measure of policy stance through unconventional policy periods.

---

## Key Findings

- **Shadow rate construction:** Uses a shadow-rate term structure model (Black 1995 framework) to back out the "effective" policy rate implied by the yield curve, even when the nominal rate is floored at zero.
- **ZLB period (2008–2015):** The shadow rate fell to approximately −3% at the peak of QE, indicating substantially easier monetary policy than the 0–0.25% nominal rate suggested.
- **Macro impact:** A 1% decline in the shadow rate has similar macroeconomic effects (output, inflation) as a 1% conventional rate cut — validating the use of QE as policy stimulus.
- **Cross-country:** Shadow rates for ECB, BOJ, and BOE can be estimated using the same methodology, enabling cross-country monetary policy comparisons even during ZLB periods.
- **Data availability:** Shadow rate series publicly available from Atlanta Fed website.

---

## Connection to Gliner (GMT)

- **Ch11 (central banks):** Shadow rate is the quantitative tool for measuring QE and forward guidance — directly operationalizes Gliner's discussion of non-standard monetary policy.
- **Ch7 (FX):** Cross-country shadow rate differentials extend interest rate carry analysis through ZLB periods when nominal differentials are compressed.
- **Ch9 (fixed income):** Shadow rate helps explain yield curve dynamics during QE — the term structure reflects more than the floored policy rate.

---

## Implementation Notes

- **Download:** Atlanta Fed publishes Wu-Xia shadow rate monthly at https://www.atlantafed.org/cqer/research/wu-xia-shadow-federal-funds-rate
- **Use as regime variable:** Shadow rate < −1% = deep QE regime; > 0% = conventional tightening. Use to condition carry and trend signals.
- **Cross-country carry:** Use shadow rate differentials (Fed vs ECB vs BOJ) for FX carry during ZLB periods instead of nominal short rates.

---

*Notes compiled 2026-03-28 | Global Macro Trading (Gliner) study*