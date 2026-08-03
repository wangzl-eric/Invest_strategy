# Report Digest: Goldman Sachs — The EM Trader: Curves, Chips, Crude and Carry (30 Jul 2026)

- **Source:** `book_notes/playground/reports/2026/07/macro_gs_em-trader_2026-07-30.pdf` — 30 July 2026, 3:00PM BST; the note states "market values in the exhibits that follow are as of 29 July, unless otherwise stated" (caption to the *Macro forecasts and outlook* section — the front-half exhibits carry no such date stamp, and the sovereign-credit valuation columns are explicitly 1 June)
- **Type / issuer:** Goldman Sachs **Global Investment Research** (Economics Research), EM Strategy — Kamakshya Trivedi, Sunil Koul, Danny Suwanapruti, Teresa Alves, Tarun Lalwani CFA, Victor Engel, Lexi Kanter, Mambuna Njie across four GS entities, plus a disclosed contribution from two Markets-team interns. Reg AC certified. Marked "For the exclusive use of ZELIN.WANG@GS.COM" — client-distributed, **not** desk color.
- **Read on:** 2026-08-03
- **One-line claim:** The July Iran re-escalation moved EM FX in the *same rank order* as February at *half the magnitude*, and a frozen-beta 4-factor model (S&P 500, oil, copper, US 10y real yields) explains almost all of the cross-section — so the trade is in the residual, not the shock; with the "disruptive Fed hike tail… curtailed for now" (GS's phrase, resting on its economists' soft-inflation call — the 29-Jul FOMC held but its three dissents to hike, GS says, "will likely keep market expectations for hikes… very much alive"), GS argues EM carry is still harvestable **provided you rank by carry-to-vol rather than raw carry and choose funders deliberately** (COP > BRL, then MXN > INR > ZAR; funders THB/PLN/ILS/CLP in EM, CHF/EUR/JPY/CAD in G10).
- **Decision it changes:** Three concrete ones.
  1. **The selection metric for an FX carry book** — rank by $C^{12m}/\sigma^{3m}$, not by the raw rate differential. This directly contradicts the signal spec written into `alpha_research/research/strategies/fx_carry_2026-03-13_conditional/proposal.md`.
  2. **Funder choice becomes a first-class decision variable.** Carry-to-vol vs EUR exceeds carry-to-vol vs USD for **all nine** of the crosses legible in the note's Exhibit 8 (which plots 16), and by **2.07×** for MXN — inside the note's ~3% carry cohort, which leg you short moves the ex-ante Sharpe of an identical long by more than which long you pick (MXN → BRL is only 1.79×).
  3. **How much weight to put on a GIR trade list vs the same note's forecast table.** On GS's own published 3-month forecasts the recommended book earns **+0.90% over 3m (+3.6% annualised)**, and its flagship preference ("prefer COP longs over BRL here") picks the leg GS forecasts to *lose* **2.33%** over the leg it forecasts to *make* **6.11%**. Executing the trade list is not executing the forecast table.
- **Scores (1–5):** **Credibility 4** · **Relevance 4** · **Actionability 3**
  - *Credibility 4* — GIR with Reg AC, two genuinely specified models (estimator, sample period, variable list all disclosed), and arithmetic that reconciles to ±0.1pp everywhere I could check it. Deducted a full point for: **zero error bands on either model**, a specification-searched issuance regression with no out-of-sample $R^2$ and no confidence band on its headline \$209bn, a sovereign-credit valuation table dated **1 June** presented alongside 29-July spreads without flagging the mismatch, and a recommendation list that contradicts the firm's own forecast table in four places without acknowledgement.
  - *Relevance 4* — the carry-to-vol rule and the funder decomposition land directly on a live CONDITIONAL proposal in this repo; the Exhibit 18 term-premium channel independently confirms the Japan thread already running through this library. Deducted one point because the specific trades are unexecutable here.
  - *Actionability 3* — honestly split. The **method** is a small concrete change (swap one ranking line; add ~15 registry entries). The **trades** are not actionable at all: `get_data` cannot resolve a single EM currency, and there are no EM forwards and no EM local IRS anywhere in the platform. Copper — one of the four inputs to GS's own FX model — is **not reachable through `get_data`** (raises `ValueError`), though `HG=F` does sit in `data/market_data/prices/commodities.parquet` and would resolve with a one-line registry entry.

---

## 1. Executive summary

Goldman Sachs Global Investment Research published this EM strategy note on 30 July 2026 to tell institutional clients how to position EM FX, local rates, equities and sovereign credit into the second half, one day after an FOMC that held with three dissents to hike and three weeks into the second oil shock of the Iran war. The method is four modelled exercises plus a descriptive equity attribution, all hung on one policy/commodity spine: an event study of EM FX over the 6→23 July window against the identical 13-trading-day window from 27 February, benchmarked to a four-factor model (S&P 500, oil, copper, US 10y real yields) whose betas are frozen on the five years to 27 February 2026 and applied out-of-sample; a cross-sectional screen of 12-month carry against 3-month annualised realised vol vs both USD and EUR; a reaction-function read of EM central banks scored on ex-ante real policy-rate buffers, plus a rolling regression of 16 EM 10y local rates on decomposed UST 10y; and a monthly OLS issuance model whose four regressors were chosen by maximising in-sample $R^2$ across combinations of four from an undisclosed candidate set. GS argues that the July move was a smaller repeat of February in rank order, that the residuals now identify local policy news rather than energy beta, and that relative-value carry is still harvestable if longs and funders are both selected on carry-to-vol — favouring COP over BRL, MXN within the ~3% cohort, and funding in THB, PLN, ILS and CLP; it also argues the 12% MSCI EM drawdown is a crowded North-Asia tech unwind rather than an energy shock (EM ex-tech **−1%** since 6 July against **−8%** in the February analogue), and forecasts full-year EM sovereign USD issuance at **~\$209bn** against **\$126bn** realised in H1. Confidence is asserted, not quantified: neither estimated model reports an $R^2$, a standard error, or a residual distribution, and GS concedes in its own text that the \$209bn forecast "appear[s] consistent with a bullish risk-on scenario that is not our baseline" and is "notably higher than out-of-sample model predictions based on the current values of market variables" — a current-conditions path GS never quantifies, while the downside path it *does* quantify is **~\$150bn**.

---

## 2. Methodology & reasoning

Five pillars. Pillars 1–2 are the FX call and carry the note; pillar 3 is EM local rates; pillar 4 is EM equities; pillar 5 is sovereign issuance. Pillar 2 is where the note breaks against itself.

### Pillar 1 — The shock is now a residual problem, not a directional one

- **Point:** July repeats February in rank order at roughly half the magnitude, and a frozen-beta four-factor model explains enough of the cross-section that GS reads what is left over as identifiable policy news.
- **Evidence:**
  - Window: **6 July 2026** (US-Iran re-escalation) → **23 July 2026** (oil peak) = **13 trading days**; February analogue starts **27 Feb 2026**, same length.
  - Exhibit 1 FX spot returns vs USD span roughly **−6% (HUF, ZAR) to +5% (COP)** in July, against roughly **−10% to +4%** in February.
  - Exhibit 3 terms-of-trade changes span **−3.5% to +1.5%** since 27 Feb and are visibly compressed since 6 July; **CLP and PEN improve** because copper rose in July where it fell in March.
  - Model: weekly FX returns vs USD on S&P 500, oil, copper and US 10y real yields, estimated over the **5 years to 27 Feb 2026 (~260 weekly obs)**, applied out-of-sample.
  - Exhibit 6: most currencies sit **above** the 45° line (outperformed prediction), inverting February when most sat below. The note names exactly five outliers: largest positive **KRW (~+4% actual on ~−2% predicted)** and **COP (+5% on +1%)**; largest negative **ZAR (−3.5% on −1%)**, **CLP (−1.8% on 0%)** and **MXN**. (HUF is the worst *absolute* performer at ~−3%, but it is not on GS's underperformer list — on the chart it sits slightly above its own prediction.)
  - Live check from our own lake over the identical window (FRED pulled on reference dates, `pit=False`, to line up with GS's market-date window rather than the PIT publication lag): **USO 104.35 → 139.49 (+33.68%)**, **SPY 751.28 → 738.18 (−1.74%)**, **DGS10 4.48% → 4.71% (+23bp)**, real 10y (DGS10 − T10YIE) **2.24% → 2.43% (+19bp)**.
- **Chain:**
  - Same conflict, same transmission channel (energy terms of trade) → importers underperform, exporters outperform, exactly as in February
  - → but risk sentiment sold off far less (SPY only **−1.74%** over 13 sessions) **and** EM FX had never retraced the February move, so importers entered 6 July already near YTD lows
  - → a smaller starting cushion produces a smaller further move
  - → the four factors absorb nearly all cross-sectional dispersion
  - → the leftover residual is attributed to named local events: SARB's against-consensus hold (ZAR), leverage-curbing measures and reduced equity outflows (KRW), BanRep hike expectations plus post-election optimism (COP)
  - → **trade the residual, not the shock: fade CLP's underperformance, respect ZAR's.**
- **Read:** Inferential and load-bearing — this is the analytical spine and the justification for every subsequent RV pair. Two clean leaps.
  - **Frozen betas across a regime break.** The coefficients are estimated on a pre-war sample and applied to a war regime, in which oil, copper, the S&P and real yields are strongly collinear. The per-factor attribution bars in Exhibit 5 are therefore far less identified than the clean stacking implies — only the *total* predicted value is really estimated.
  - **A regression residual is being read as causal policy news** — a narrative laid over an error term. The tell is that GS applies it asymmetrically: **ZAR's residual gets a SARB story; CLP's same-sign residual gets "limited local developments… the move may have gone too far."** Residual-as-signal when it suits the trade, residual-as-noise when it doesn't. **No $R^2$, no standard errors, no residual distribution anywhere** — a reader cannot tell whether a 2% residual is 0.5σ or 3σ.

### Pillar 2 — Carry-to-vol is the stated selection metric, and it contradicts GS's own forecast table in four places

- **Point:** Rank by carry ÷ realised vol, not by raw carry — and fund deliberately. Applying that rule produces a recommended book at odds with the forecast table printed 20 pages later in the same document.
- **Evidence:**
  - **12m carry vs USD** — Exhibit 7 prints no numbers, so these are the carry column of the note's own forecast table, sorted descending: COP **9.2%**, BRL **8.1%**, INR 3.3%, IDR 3.0%, MXN **3.0%**, ZAR **3.0%**, PHP 1.6%, PEN 1.4%, HUF 0.9%, TWD 0.4%, PLN −0.1%, CLP −0.4%, CZK −0.4%, KRW −0.8%, MYR −0.9%, ILS −1.6%, THB **−2.0%**, CNY −2.6%. (Exhibit 7's bar order puts MYR ahead of KRW, which the table values reverse.)
  - **Exhibit 8, carry-to-vol (vs USD | vs EUR)** — chart reads, no values printed in the text; Exhibit 8 plots 16 crosses sorted on the *vs-EUR* ratio, of which these nine are legible: BRL 0.75 | 1.03, MXN 0.42 | **0.87**, COP 0.67 | 0.79, INR 0.46 | 0.74, IDR 0.47 | 0.72, PHP 0.28 | 0.62, PEN 0.21 | 0.51, ZAR 0.28 | 0.45, TWD 0.12 | 0.41.
  - **Recommended longs:** COP > BRL, then MXN > INR > ZAR, cautious on IDR. **EM funders:** THB, PLN, ILS, plus CLP "to neutralise broader risk exposures." **G10 funders:** CHF, EUR, JPY, CAD "in roughly that order."
  - **GS's own 12m total-return forecasts (spot 29 Jul):** MXN **+0.0%**, ZAR **+8.9%**, CLP **+8.2%**, COP +9.1%, BRL +10.0%, IDR +8.1%, MYR +9.6%, TRY +24.1%.
- **Chain:**
  - High raw carry is not investable if it comes with high vol → rank by $C/\sigma$
  - → BRL and COP lead on both raw carry (8.1%, 9.2%) and carry-to-vol (0.75, 0.67)
  - → within the ~3% cohort MXN (0.42) beats ZAR (0.28) because ZAR realised vol is far higher
  - → so prefer MXN carry and treat ZAR as an energy-relief *option* rather than a carry long
  - → pair the longs with genuinely low- or negative-carry funders (THB −2.0%, ILS −1.6%, CLP −0.4%)
  - → **a carry-to-vol-maximised RV book, not a directional EM long.**
- **Read:** Descriptive in its inputs, strongly inferential in its recommendation, and this is where the note breaks. Four contradictions with its own table, none flagged:
  - **(i) MXN vs ZAR.** Identical **3.0%** carry, but GS forecasts MXN's 12m total return at exactly **+0.0%** and ZAR's at **+8.9%**. No positive volatility number can make a 0.0% expected return Sharpe-dominate an 8.9% one.
  - **(ii) CLP.** Recommended as a funding **short** while the same table forecasts USD/CLP falling **933 → 860**, i.e. **+8.5% CLP spot appreciation and +8.2% total return**. Its **−19.4%** GSDEER/GSFEER undervaluation is never mentioned; the only nod is a tactical terms-of-trade aside.
  - **(iii) COP over BRL.** On GS's own **3-month** forecasts this picks **−2.33%** over **+6.11%** — an **8.43pp** expected-return sacrifice justified solely by Brazilian election vol, which is a Sharpe argument made without ever computing the Sharpe.
  - **(iv) The G10 funder list** (CHF > EUR > JPY > CAD) is the one ranking in the note where carry-to-vol is **never computed** — and on our own lake it inverts on the denominator. Three-month annualised realised vol vs USD over the 42 common trading days to 29 July 2026 (`USDCHF=X`, `EURUSD=X`, `USDJPY=X`, `USDCAD=X`): **JPY 3.39% < CAD 3.65% < EUR 4.48% < CHF 5.88%**. GS's *first* choice is the highest-vol of the four and its *third* the lowest — an exact reversal. And the very next session made the point the other way: JPY's low measured vol was a pre-intervention artefact, and on 30 July it printed a 5.74-yen range.

#### The arithmetic the note does not do — I. Implied vols and the funder decomposition

Exhibit 8 publishes the ratio and Exhibit 7 the numerator, so the vols invert directly, $\sigma = C/\mathrm{CtV}$. **The note never prints them.**

| Pair | 12m carry vs USD | CtV vs USD | **Implied $\sigma^{3m}$ vs USD** | CtV vs EUR | **Implied $\sigma^{3m}$ vs EUR** | EUR-funded vol vs USD-funded |
|---|--:|--:|--:|--:|--:|--:|
| BRL | 8.1% | 0.75 | **10.8%** | 1.03 | 9.3% | −14% |
| COP | 9.2% | 0.67 | **13.7%** | 0.79 | 13.5% | −2% |
| ZAR | 3.0% | 0.28 | **10.7%** | 0.45 | 9.9% | −8% |
| INR | 3.3% | 0.46 | **7.2%** | 0.74 | 6.4% | −10% |
| **MXN** | **3.0%** | **0.42** | **7.1%** | **0.87** | **5.1%** | **−28%** |
| IDR | 3.0% | 0.47 | 6.4% | 0.72 | 6.2% | −3% |
| PEN | 1.4% | 0.21 | 6.7% | 0.51 | 5.6% | −16% |
| PHP | 1.6% | 0.28 | 5.7% | 0.62 | 4.9% | −14% |
| TWD | 0.4% | 0.12 | 3.3% | 0.41 | 4.5% | **+36%** |

**ZAR vol is 1.50× MXN vol at identical 3.0% carry.** That ratio, not the carry, is the entire MXN-over-ZAR argument.

The EUR column needs one input the note also never states: the implied 12m USD–EUR rate differential. It falls straight out of the five currencies quoted against *both* funders, since $C^{(EUR)}-C^{(USD)}=r_{USD}-r_{EUR}$ must hold for every one of them — **CZK 1.5pp, HUF 1.4pp, PLN 1.4pp, RON 1.4pp, RUB 1.6pp; mean Δ = 1.46pp, dispersion 0.2pp.** Five independent quotes agreeing is a genuine internal cross-check that the two funding conventions are consistent.

Decomposing the MXN case GS asserts but never derives: carry vs EUR $=3.0+1.46=4.46\%$, and $\mathrm{CtV}=0.87$ implies $\sigma(\text{EUR/MXN})=5.13\%$ against $\sigma(\text{USD/MXN})=7.14\%$. Check: $(4.46/3.00)\times(7.14/5.13)=1.487\times1.392=\mathbf{2.07}=0.87/0.42$ ✓. So the uplift is **~1.49× more carry × ~1.39× less vol**. Repeating across the table, **EUR-funded vol is lower than USD-funded vol for 8 of 9 currencies** — the dollar is the dominant common factor in EM FX vol, and funding in EUR strips part of it out *and* pays 1.46pp more carry. TWD is the sole exception (+36%).

#### The arithmetic the note does not do — II. The recommended book, marked to GS's own 3-month forecasts

$R^{3m}=\left(S_0/\hat S_{3m}-1\right)+C^{12m}/4$, using the note's own Exhibit-page forecast table.

| Leg | Spot (29 Jul) | GS 3m fcst | Spot leg | Carry (¼ of 12m) | **3m total** |
|---|--:|--:|--:|--:|--:|
| **Longs** | | | | | |
| BRL | 5.10 | 4.90 | +4.08% | +2.03% | **+6.11%** |
| INR | 95.8 | 94.0 | +1.91% | +0.83% | **+2.74%** |
| ZAR | 16.69 | 16.50 | +1.15% | +0.75% | **+1.90%** |
| MXN | 17.45 | 17.75 | −1.69% | +0.75% | **−0.94%** |
| COP | 3195 | 3350 | −4.63% | +2.30% | **−2.33%** |
| *long-leg mean* | | | | | **+1.50%** |
| **Funders (paid away)** | | | | | |
| ILS | 3.08 | 3.00 | +2.67% | −0.40% | **+2.27%** |
| CLP | 933 | 920 | +1.41% | −0.10% | **+1.31%** |
| PLN | 3.80 | 3.77 | +0.80% | −0.03% | **+0.77%** |
| THB | 33.50 | 34.00 | −1.47% | −0.50% | **−1.97%** |
| *funder-leg mean* | | | | | **+0.59%** |
| **Net book** | | | | | **+0.90% / 3m = +3.60% ann.** |

Two things follow that the note never says. First, **the flagship preference is the single worst leg in the book on GS's own numbers** — COP at −2.33% chosen over BRL at +6.11%. Second, **+3.6% annualised is what the entire recommended structure earns on the firm's own forecasts**, before any transaction cost, against a book whose implied vols run 5–14%.

#### The arithmetic the note does not do — III. Breakevens and the valuation drag on the flagship pair

Carry breakeven, $S^{BE}=S_0/(1-C^{12m})$ — the spot at which being long carry for 12 months stops paying:

| Pair | Spot | **Breakeven** | Depreciation tolerance | GS 12m forecast |
|---|--:|--:|--:|--:|
| USD/BRL | 5.10 | 5.55 | 8.8% | 5.00 |
| USD/COP | 3195 | 3518.7 | 10.1% | 3200 |
| USD/INR | 95.8 | 99.07 | 3.4% | 96.0 |
| **USD/MXN** | **17.45** | **17.99** | **3.1%** | **18.00** ← *lands on the breakeven* |
| USD/ZAR | 16.69 | 17.21 | 3.1% | 15.75 |
| USD/IDR | 18072 | 18631 | 3.1% | 17200 |
| USD/TRY | 47.38 | 74.50 | 57.2% | 54.00 |
| EUR/HUF | 366 | 374.6 | 2.4% | 345 |

**GS's own 12m USD/MXN forecast (18.00) sits exactly on the carry breakeven (17.99)** — which is the arithmetic behind the +0.0% total return, and the reason MXN has literally zero cushion against Fed repricing.

The headline pair, **long COP / short CLP**, is a **9.6pp carry pickup** (9.2 − (−0.4)) against a **37.1pp valuation spread running the wrong way** (COP **+17.7%** overvalued vs CLP **−19.4%** undervalued on GS's own 60/40 GSDEER/GSFEER). At PPP half-lives of 3/4/5 years the annual reversion drag is **7.65 / 5.90 / 4.80pp**, and GS's own 12m forecasts make the pair worth only **+0.9%** (COP +9.1% − CLP +8.2%) — so on a 4-year half-life the pair nets roughly **−5.0%/yr**. In fairness: the *full* book is valuation-neutral (long-leg mean −0.26%, funder-leg mean −0.05%, spread −0.21pp) because INR/ZAR/BRL are undervalued. **It is the flagship pair specifically, not the book, that fights valuation.**

Finally, **expected-return composition** — carry as a share of GS's own 12m total: COP **101%**, INR 110%, BRL 81%, IDR 37%, ZAR **34%**, HUF/EUR 28%, CLP −5%, MXN n/a (total = 0.0%). GS writes that "HUF longs are increasingly more of a spot than a carry trade"; quantified, that is **72% spot / 28% carry**. Its preferred MXN is **100% carry with zero expected return**, while the highest-forecast names in the same cohort (ZAR, IDR) are **63–66% spot**. Across the **21** vs-USD currencies the table quotes with both a carry and a total (ex-TRY), the correlation between carry and GS's forecast total return is only **+0.11** (Spearman +0.19); even after also dropping the two capital-controlled war currencies whose carry is unharvestable (RUB 11.6% carry → 0.4% total, UAH 10.6% → −3.1%) it reaches only **+0.54** (Spearman +0.47). **Carry-to-vol is not a proxy for GS's own expected return, and the note never checks whether it is.**

### Pillar 3 — EM local rates split on real-policy-rate buffer, not on oil exposure

- **Point:** High-yielders entered the shock with enough real-rate buffer to absorb it (some are cutting); EM Asia low-yielders have none and must rebuild. The buffer is the sort key — but the buffer number itself is convention-sensitive in exactly the market GS recommends.
- **Evidence:**
  - Exhibit 12: since March, EM central banks moved **far less than the market priced in March**; **Hungary, Brazil and Mexico actually cut.**
  - Surprises: **SARB held at a meeting fully priced for a hike** (Exhibit 13: ZAR 1m-forward market-implied policy rate collapses from ~7.25% back to ~7.00%); **Bank Indonesia held** against hike expectations; **NBP signalled a September cut** while PLN 12m pricing still carries **~+30bp of hikes**.
  - **FOMC 29 July: held, with three dissents to raise.**
  - Exhibit 18: 3-year rolling weekly OLS of **16 EM 10y local rates** on decomposed UST 10y — **median $t$ on the term-premium component ≈ 6–8 vs ≈ 2 on the risk-neutral component.**
  - **Ex-ante real policy rates I recomputed** from the report's own forecast table (current policy − GS 2026 CPI), which the note shows only as a chart, for all 20 countries in that table: Brazil **+9.0%**, Russia +8.1%, Turkey +6.4%, Colombia +5.4%, Hungary +4.1%, India +4.1%, South Africa +2.9%, Indonesia +2.5%, Mexico +2.3%, Israel +1.8%, Czechia +1.8%, Poland +1.0%, Malaysia +0.8%, Chile +0.6%, China +0.4%, Peru +0.3%, Korea +0.1%, Philippines **−0.3%**, Thailand **−1.0%**, Romania **−1.6%**. (Exhibit 14's own chart drops Russia, Turkey and Malaysia and adds USD and EUR, so it is not the same 20 names.)
  - **GS-vs-consensus 2027 policy gaps** (every non-zero gap in the table): Hungary **−2.0pp** (GS 3.0 vs cons 5.0), Russia −0.8, Romania −0.7, South Africa −0.5, Czechia −0.5, Peru −0.3, Chile −0.2, Thailand −0.2, China −0.1, Malaysia −0.1, Mexico −0.1, India +0.2, Philippines +0.6, Colombia +0.7, Indonesia +0.7, Turkey +1.3.
- **Chain:**
  - Real policy rates entered the war restrictive in the high-yield complex and accommodative in EM Asia
  - → a supply-driven inflation shock is absorbable by BRL/COP/ZAR/HUF (hold, or even cut) but forces KRW/PHP to hike to rebuild buffer
  - → positioning also cleaned out after the February consensus-receiver washout (HUF, BRL, ZAR, GBP hit hardest), so the adverse tail in EM front-ends is trimmed even as oil re-spiked
  - → receive where rates backed up **and** the central bank leans dovish (**PLN, HUF, ILS**); stay out of MXN (rate differential to the US "notably lower than most EMs" — though Exhibit 17 puts PEN and CNY lower still — combined with the highest 2y beta to US 2y SOFR in that chart)
  - → separately, EM 10y local rates load on UST **term premium** ~3× more strongly than on risk-neutral rates, and AI capex plus defence/infrastructure fiscal keeps term premium bid
  - → **no broad EM long-end compression; only INR, ZAR and possibly COP, on improving fiscal paths and still-wide local spreads.**
- **Read:** Mostly descriptive on the reaction-function evidence (observed decisions, not model output), inferential on the buffer→behaviour mapping, corroborating rather than load-bearing for the FX call. Three flags:
  - **The India inconsistency.** GS's own table gives India policy **6.3%** and FY2026 CPI **2.2%**, implying a **+4.1%** real buffer that would rank India joint-5th of the 20 countries in that table — yet Exhibit 14 places INR near the **bottom** of the ranking. That reconciles only on FY2027 CPI (4.9%), giving **+1.4%**. **India's real policy rate swings 2.7pp on a fiscal-year convention choice**, and INR is one of only two names GS nominates for long-end compression.
  - **The Philippines is internally odd:** GS forecasts 2026 inflation *below* consensus (5.1% vs 5.9%) yet the policy rate *above* consensus (5.5% vs 5.2%) — defensible as buffer-rebuilding, but never stated as such.
  - **The Hungary call is quietly the largest-EV rates trade in the note and is ranked second.** A **200bp** GS-vs-consensus gap at the 2027 point is the largest in the table — **1.5×** the next-largest gap of any sign (Turkey +1.3pp) and **2.5×** the next-largest dovish one (Russia −0.8pp); with the 2026 gap already −1.4pp, a 2y HUF receiver capturing an average ~170bp path differential at duration ~1.9 is worth **~3.2% of notional** if GS is right.

### Pillar 4 — The "12% EM correction" is a Korea/Taiwan semiconductor unwind wearing an EM index costume

- **Point:** Not an EM event and not an energy event. GS's "broadening" conclusion, however, is a forecast that its own YTD table currently contradicts.
- **Evidence:**
  - MSCI EM **−12%** from its 22 June peak, "reversing about half" of 1H gains; **MSCI EM ex-tech −1% since 6 July vs −8%** over the equivalent late-February window, and **+2% MTD** in July.
  - **GSPRHIMO** (GS US high-beta momentum pair) **−40% in 5 weeks**, erasing all YTD gains; EM Momentum factor **M1EFMMT −25%+** from the late-June peak; **SOX −25%** from 22 June; **KOSPI ~−40%** after a **>100%** 1H rally.
  - Index weights from the note's own table: **Taiwan 26.0%, China 22.7%, Korea 18.0%, India 12.3%** (top four = 79.0%; **Korea + Taiwan = 44.0%**).
  - MSCI EM current **1560**, NTM P/E **9.7x**, YTD USD **+11.1%**, 2026E EPS growth 66%, 2027E **25%**, 12m GS target **2000**. KOSPI current **5663**, NTM P/E **4.4x**, NTM EPS revised **+345.7%** over 12m local, GS 12m target **12000**.
  - Leveraged-ETF AUM in US tech and Korea/Taiwan "meaningfully reset from highs but not fully cleared" (Exhibit 27); 2Q results tracking ahead of consensus, beats outpacing misses.
- **Chain:**
  - Crowded AI/memory positioning unwinds globally → Korea and Taiwan are **44%** of MSCI EM and are the EM expression of that trade
  - → the cap-weighted index falls 12%, but ex-tech EM falls only 1% because oil-sensitive markets (ASEAN, India, South Africa) never retraced February and so started cheap, rate-sensitive pockets (Brazil, South Africa) were spared repricing when SARB held, and 2Q earnings are beating
  - → so the energy shock is **not** what is hitting EM equities
  - → if oil and rates vol stay contained, earnings accrual plus the diversification bid should broaden performance away from North Asia, as in every US TMT drawdown since the early 2000s
  - → **prefer balanced / equal-weighted EM allocations over the cap-weighted index.**
- **Read:** Descriptive and well-evidenced on the attribution; the broadening conclusion is inferential and **currently unsupported by the note's own numbers**.
  - **Drawdown attribution, computed.** With Korea (18.0%) at −40% and ex-tech EM at −1%, Taiwan (26.0%) at −15% / −20% / −25% yields an index move of **−11.7% / −13.0% / −14.3%**, bracketing the reported −12%. **Korea + Taiwan account for 95–96% of the entire drawdown.** Caveat on my own arithmetic: the note dates the −40% and the −12% from the 22 June peak but the −1% ex-tech from 6 July, so this splices two windows — it is an order-of-magnitude decomposition, not an exact one, and the true Taiwan number is unpublished.
  - **Consistency check on the reported figures.** Peak $=1560/0.88=1772.7$, YTD start $=1560/1.111=1404.1$ → the peak was **+26.3% YTD**, and the current +11.1% means **57.7% of the gain has been retraced**. "About half" is really 58%. KOSPI cross-check: 5663 at +49.8% YTD, −40% from peak ⇒ peak = 9438 = **+149.7% YTD**, consistent with ">100% rally in 1H."
  - **Where it leaps — the equal-weight claim.** Averaging the report's own **23-country YTD USD returns** gives **mean +9.44%, median +8.50%**, against cap-weighted MSCI EM at **+11.1%**. The equal-weighted basket is **1.7pp behind**; excluding Korea and Taiwan it is **+6.07%**, meaning **North Asia concentration *added* ~5.0pp to the index YTD**. Exhibit 28 is captioned "the equal-weighted EM index has remained resilient" and presented as observation; on the note's own table, broadening is a **prediction**.
  - **The 12m target, decomposed** (the note gives the target, never the decomposition). NTM EPS $=1560/9.7=160.8$ index points; in 12 months NTM rolls to 2027 at +25% → **201.0**; a 2000 target therefore implies a forward P/E of **9.95x**, i.e. **+2.6% re-rating**. So **+28.2% upside = 25pp of EPS growth × 2.6pp of multiple** — a pure earnings call with essentially no re-rating assumed. Note the mechanics: **the same 2000 target at the 22 June peak of 1773 was only +12.8% upside** — the "+28%" is manufactured entirely by the drawdown. **KOSPI 12000 vs 5663 is +111.9% on a 4.4x NTM P/E whose denominator has been revised up 345.7% in 12 months** — the most extreme number in the report, and the text never mentions it.

### Pillar 5 — The \$209bn issuance forecast sits 28% above the only model path GS quantifies, and 30% of the implied H2 supply is three GCC sovereigns

- **Point:** Record H1 supply absorbed with no spread impact justifies raising the full-year forecast — but the raise overrides the model rather than following it.
- **Evidence:**
  - H1 2026 gross EM sovereign USD issuance **\$126bn**: IG **~\$79bn (62.7%**, stated "~63%"**)**, HY **~\$47bn**. Both IG and HY at their **second-highest H1 levels in a decade**.
  - Full-year forecast **~\$209bn** = IG **~\$138bn (66%)** + HY **~\$72bn (34%)**, raised from **~\$190bn** at the start of the year. Stated H2 remainder: **~\$58bn IG + ~\$25bn HY**.
  - Model: monthly OLS of issuance **levels** on **four** global market variables plus **monthly seasonal dummies** (the note says "monthly dummy variables" without a count — 11 if an intercept is kept, which the formula below assumes), sample **Jan-2010 → Dec-2025 (192 monthly obs)**, with the four variables chosen by **searching combinations of four from a larger candidate set to maximise $R^2$** — winners: **EMBI Global Diversified spreads, MOVE, Brent, S&P 500**. Realised cumulative issuance exceeded model predictions in **each of the first six months**.
  - GS's own text: the forecast "appear[s] consistent with a bullish risk-on scenario that is **not our baseline**" — EM spreads **−100bp**, MOVE **−40pts**, Brent **−15%**, US equities **+20%** — and is "notably higher than out-of-sample model predictions based on the **current values** of market variables," a number GS never prints. The only alternative path it does quantify is the **downside** one (moderate spread widening, higher-for-longer oil, renewed rate vol): **~\$150bn**.
  - Country detail: **Kuwait FY \$15bn vs \$8bn issued; Saudi Arabia \$25bn vs \$11.5bn; Qatar \$7bn vs \$3bn.** Net supply forecast to a multi-year-high **~\$150bn** on a 12m rolling basis.
- **Chain:**
  - Spreads retraced the March war-widening back to historically tight levels → issuance terms attractive from the sovereign's side
  - → primary demand strong enough that median IG new issues **outperform** the IG index two weeks post-print (Exhibit 33) while HY prints in line (Exhibit 34)
  - → the market absorbed record supply with no spread impact
  - → GCC sovereigns additionally need to fund reconstruction, security infrastructure and choke-point-bypassing capex — an idiosyncratic driver the model cannot see
  - → **override the model to the upside**
  - → elevated **net** supply is a technical headwind
  - → **moderate (not sharp) EM spread widening over 12 months.**
- **Read:** Inferential and the most methodologically exposed section in the note.
  - **The arithmetic ties.** \$209 − \$126 = **\$83bn** H2, and the stated \$58bn IG + \$25bn HY = **\$83bn exactly**; IG \$138 + HY \$72 = \$210 vs the stated \$209 (a \$1bn rounding residual); IG share 138/209 = **66.0%**, HY **34.4%**, both as stated. Gross \$209bn against net ~\$150bn implies **~\$59bn of principal and interest payments** (Exhibit 36 defines net as gross less both).
  - **Two things the note never says.** (1) Its own forecast implies H2 gross running at **\$13.8bn/month against H1's \$21.0bn/month — 34% *below* the H1 pace**, so the section header "Robust in H1, With More to Come in H2" actually describes a forecast **slowdown**; the downside case implies **\$4.0bn/month, 81% below**. (2) The GCC remainder (Kuwait \$7bn + Saudi \$13.5bn + Qatar \$4bn = **\$24.5bn**) is **42% of all H2 IG and 30% of all H2 EM sovereign gross supply from three issuers** — a concentration figure never computed.
  - **Where it leaps hardest is the model itself.** Choosing the best 4-variable subset by in-sample $R^2$ from an undisclosed candidate set $\mathcal{C}$ searches $\binom{|\mathcal{C}|}{4}$ specifications with **zero multiplicity correction** — 210 for $|\mathcal{C}|=10$, 1365 for $|\mathcal{C}|=15$. At a nominal $\alpha=0.05$ over 210 models the family-wise false-positive probability is $1-0.95^{210}\approx 99.998\%$; an honest Bonferroni threshold is $p<2.4\times10^{-4}$. **No $R^2$, no out-of-sample $R^2$, no standard errors, no confidence band on \$209bn** — and GS then puts its forecast **\$59bn = 28% of the forecast** above the only model path it quantifies (the ~\$150bn downside case), on a risk-on scenario it explicitly does not believe in, while conceding the current-conditions model prediction is lower too without ever printing it.

### Load-bearing formulas

The note's selection metric — an ex-ante Sharpe ratio under an *assumed zero expected spot drift*, which is exactly the assumption the note's own forecast table violates:

$$\mathrm{CtV}_i^{(f)}=\frac{C_i^{(f),12m}}{\sigma_i^{(f),3m}},\qquad C_i^{(f)}=\frac{S_i^{(f)}}{F_i^{(f),12m}}-1\;\approx\;r_i-r_f$$

with $S$ the spot of currency $i$ versus funder $f$, $F$ the 12m outright forward, $r$ the 12m money-market rate, $\sigma^{3m}$ the 3-month annualised realised vol of the spot cross.

The 12m total-return identity — **verified to tie across all 27 quoted lines** (22 vs USD + 5 vs EUR): the spot leg reproduces to ±0.13pp and total = spot + carry to ±0.10pp on the table's own printed components, and it is **additive, not compounded** (compounding BRL would give 10.26%, not the printed 10.0%):

$$R_i^{tot}=\underbrace{\left(\frac{S_{i,0}}{\hat S_{i,12m}}-1\right)}_{\text{spot leg}}+\underbrace{C_i^{12m}}_{\text{carry leg}},\qquad S_i^{BE}=\frac{S_{i,0}}{1-C_i^{12m}}$$

The **funder-switch identity** (my derivation, not the note's) — why "which leg you short" is a first-order decision:

$$C_i^{(EUR)}-C_i^{(USD)}=r_{USD}-r_{EUR}\equiv\Delta\;\;\forall i,\qquad \frac{\mathrm{CtV}_i^{(EUR)}}{\mathrm{CtV}_i^{(USD)}}=\underbrace{\frac{C_i^{(USD)}+\Delta}{C_i^{(USD)}}}_{\text{carry gain}}\times\underbrace{\frac{\sigma_i^{(USD)}}{\sigma_i^{(EUR)}}}_{\text{vol gain}}$$

with $\Delta=1.46\,\text{pp}$ implied by the note's own CZK/HUF/PLN/RON/RUB dual quotes.

GS's EM FX attribution model (Exhibits 5–6) — $\beta$ frozen on the 5 years to 27-Feb-2026, applied out-of-sample 6→23 Jul; $\varepsilon$ is what GS reads as policy news:

$$r_{i,t}=\alpha_i+\beta_i^{SPX}r_t^{SPX}+\beta_i^{oil}r_t^{oil}+\beta_i^{Cu}r_t^{Cu}+\beta_i^{ry}\Delta y_t^{r,10}+\varepsilon_{i,t}$$

GS's EM sovereign issuance model (Exhibit 35), with the specification search made explicit:

$$I_m=\alpha+\sum_{k=1}^{4}\beta_k X_{k,m}+\sum_{j=1}^{11}\gamma_j D_{j,m}+\varepsilon_m,\qquad X^\star=\arg\max_{X\subset\mathcal{C},\,|X|=4}R^2$$

EM long-end sensitivity decomposition (Exhibit 18) — weekly, 3-year rolling OLS across 16 EMs; median $t(b^{TP})\approx6\text{–}8$ vs median $t(b^{RN})\approx2$:

$$\Delta y_{i,t}^{10y,\,loc}=a_i+b_i^{TP}\,\Delta TP_t^{UST,10y}+b_i^{RN}\,\Delta RN_t^{UST,10y}+u_{i,t}$$

And the valuation-reversion drag I applied to the flagship COP/CLP pair, $h$ the PPP half-life in years:

$$\mathrm{drag}_{\text{ann}}=(\text{valuation gap})\times\left(1-2^{-1/h}\right)$$

At $h=4$ and a 37.1pp gap this is **5.90pp/yr against the trade**.

**Weakest link (across all five pillars):** **the note's stated selection metric systematically selects against its own forecast table, and it never notices.** Carry-to-vol is computed on the carry leg *alone* — it structurally discards the spot forecast occupying the other half of the same report. Run both rankings side by side and they disagree in the four places that matter: MXN over ZAR (forecast-Sharpe **0.00 vs 0.83** on GS's own inputs); CLP shorted while forecast to return **+8.2%**; COP over BRL at a **−2.33% vs +6.11%** 3-month sacrifice; and a G10 funder list where the ratio is never computed at all. Underneath all four sits the deeper defect: **carry-to-vol is a mean-variance statistic applied to the canonical negatively-skewed crash-risk premium.** FX carry's entire economic justification (Brunnermeier–Nagel–Pedersen 2008, cited in our own `fx_carry` proposal) is that the excess return compensates for crash risk — so a ratio built from the first two moments is precisely the statistic least able to separate a good EM carry trade from a bad one. **No skew, no kurtosis, no drawdown appears anywhere in the note.** That is the *identical* weakness this library already flagged in `book_notes/playground/reports/2025/11/rates_gs_vol-strategies_2025-11-13.md` nine months earlier and one desk over. Two GIR notes with the same blind spot is a house methodology, not an oversight — and it is the specific reason a book earning **+3.6% annualised on GS's own 3-month forecasts** is not compensating anyone for the tail it carries.

---

## 3. Keywords

`carry-to-vol selection`, `funder-leg choice / EUR vs USD funding`, `frozen-beta factor attribution`, `residual-as-policy-news`, `ex-ante real policy rate buffer`, `UST term-premium beta of EM local rates`, `GSDEER/GSFEER valuation gap`, `specification-search R² maximisation`, `EM sovereign gross vs net supply`, `North Asia concentration in MSCI EM`

---

## Mark-to-market as of 2026-08-03 (added on read — not in the report)

The note is timestamped **30 July 2026, 3:00PM BST** with exhibit values "as of 29 July" — i.e. struck at **USD/JPY 163.86, the exact 2026 peak close**. Its third-ranked G10 funder can therefore be marked immediately, from `USDJPY=X` in our own lake:

| Date | High | Low | Close | Daily range |
|---|--:|--:|--:|--:|
| 2026-07-29 (note's exhibit date) | 163.88 | 163.29 | **163.86** | 0.59 |
| **2026-07-30** (note published) | 163.73 | **157.99** | 163.30 | **5.74** |
| 2026-07-31 | 160.84 | 158.67 | **160.18** | 2.17 |
| 2026-08-02 (indicative, Sunday stub — unconfirmed) | — | — | *157.40* | — |

A short-JPY funding leg lost **−2.25% by the 31-Jul close** (−3.94% on the indicative print). Against the note's own carry numbers that is **9.0 months of MXN carry (3.0%/yr), 8.2 months of INR carry, and 2.9 months of COP carry — burned in two sessions**; on the indicative print, **15.8 months of MXN carry**. The single highest-cost recommendation in the note, made on the day the MoF intervened.

This is also the **third** time in this library that GS FICC desk color has beaten GS GIR research. The December-2025 JPY desk note (`book_notes/playground/reports/2026/04/macro_gs_jpy-macro-trading_2026-04-07.md`) published an explicit rule — *"when the daily RSI exceeds 80, the risk of intervention increases, so long positions should be avoided"* — and `USDJPY=X` RSI(14) hit **80.5 on 1 July 2026**, four weeks before GIR nominated JPY as a funder.

---

## What to watch

| Observable | Series | Latest print available on 2026-08-03 | Confirms if | Breaks if |
|---|---|---|---|---|
| **Oil level** — the note's master variable ("the easiest way to resolve these risks is a sustained path to lower energy prices") | `USO` (registered WTI-ETF proxy). **GAP:** Brent `BZ=F` sits in `data/market_data/prices/commodities.parquet` but is **absent from `alpha_research/quant_data/ticker_map.py`**, so `get_data` raises `ValueError` | **129.17** (31-Jul), −7.4% off the 23-Jul peak of 139.49, still **+23.79% vs the 6-Jul level of 104.35** | USO sustains **below ~110** (full retrace of the July re-escalation) → unlocks importer FX (ZAR, HUF, PLN, INR, THB) and lets EM front-ends rally — the note's own stated resolution path | USO closes **above 139.49** (new post-war high) → the entire "milder this time" framing rests on July < February, and a new high forces the frozen-beta model's importer bars wider than March |
| **US 10y real yield** — the vulnerability GS names for its own two best carry longs, and the Exhibit 18 channel | `DGS10` − `T10YIE` (both registered). **GAP:** direct series `DFII10` is in the FRED parquet store but absent from `ticker_map.py` | **2.41%** (30-Jul reference date — DGS10 for 31-Jul not yet published); +19bp over GS's 6→23 Jul window — **83% of the 23bp DGS10 move was real, not breakeven** | Stalls or falls **below ~2.25%** → EM long-end compression in INR/ZAR/COP becomes viable and the BRL/COP high-beta carry longs keep their main risk contained | Pushes **above ~2.60%** → the note explicitly names "a continued selloff in the long-end" as the live risk, and it hits COP and BRL hardest — the two names carrying the whole FX section |
| **US 2y yield** — the "disruptive Fed hike tail," re-armed by three dissents on 29-Jul, and the kill-switch for the preferred MXN long (Exhibit 17: notably low rate differential to the US, highest 2y beta to US 2y SOFR) | `DGS2` (registered) | **4.23%** (30-Jul reference date), −14bp off the 23-Jul high of 4.37%, still +10bp vs 6-Jul's 4.13% | Drifts back toward **~4.10%** → hike pricing bleeds out, MXN carry survives, GS's "no Fed hikes" base case holds into September | Clears **~4.45%** → MXN's 3.0% carry is consumed by differential compression (**breakeven USD/MXN 17.99, GS's own 12m forecast 18.00 — zero cushion**), and SARB is forced back to hiking at its September MPC |
| **USD/JPY** — mark-to-market on the note's third-ranked G10 funder, and the live GIR-vs-desk test | `USDJPY=X` (registered, daily) | **160.18** close (31-Jul) from the 163.86 peak close on 29-Jul; indicative 157.40 on 2-Aug is a weekend stub | Stabilises above **160** and grinds back toward 163–165 → intervention was a one-off vol event, not a level defence; the Dec desk note's "rebound ~1 month after intervention" rule dates that to **~30-Aug** | Sustains **below ~157** → MoF is defending a level, and a JPY-funded EM carry book bleeds faster than any EM long earns (the leg has already burned **9.0 months of MXN carry in two sessions**) |
| **10y breakeven inflation** — the hinge of "benign prints → central banks stay dovish → EM carry survives," which every section depends on | `T10YIE` (registered) | **2.28%** (31-Jul reference date); **+4bp over the 6→23 Jul window for a +33.7% oil move = 0.12bp of breakeven per 1% of oil** | Pass-through stays under **~0.3bp per 1% oil** on the next impulse → the supply shock is not becoming an expectations shock; the PLN/HUF/ILS receivers work | Breakevens clear **~2.45% on flat or falling oil** → second-round pass-through, re-arms the Fed dissents, and simultaneously kills the receivers, the INR/ZAR/COP long-end trade **and** the carry book — the one event that takes every recommendation down together |

**Data GAPs the note leans on that this platform cannot resolve at all** (no source, not a registry omission): EM local IRS curves, EMBI Global Diversified spreads, the MOVE index, EM policy rates, GS terms-of-trade indices, GSDEER/GSFEER fair values, MSCI EM / M1EFMMT / SOX / KOSPI. Copper is a *different* kind of gap: `HG=F` **is** in `data/market_data/prices/commodities.parquet`, it is simply unreachable through `get_data` (raises `ValueError`) — so the fourth input to GS's FX model is one registry line away, not missing. All FRED marks in this table are reference-date values (`pit=False`); `get_data`'s PIT default shifts them one publication day later.

---

## Connection to our platform

- **`alpha_research/research/strategies/fx_carry_2026-03-13_conditional/proposal.md`** — **CHALLENGES**, and the single most valuable connection in the read. The proposal's signal is `carry_rank = rate_diffs.rank(axis=1, pct=True)` — a raw carry ranking, exactly the construction this note argues against; the correct spec is `carry / realized_vol_3m`. On the note's own numbers the two rankings disagree materially: **MXN and ZAR carry identically at 3.0% but sit 2nd and 8th in Exhibit 8's ordering** (which sorts on the vs-EUR ratio; on the vs-USD ratio the gap is 0.42 vs 0.28), because ZAR realised vol is **1.50×** MXN's.
- **`alpha_research/research/strategies/fx_carry_2026-03-13_conditional/proposal.md` (funding leg)** — **COULD IMPROVE.** The proposal treats the funder as a residual; the note plus my $\Delta=1.46\,\text{pp}$ decomposition shows funder choice moves ex-ante Sharpe by up to **2.07×** for an identical long, with EUR-funded vol below USD-funded vol for **8 of the 9** crosses legible in Exhibit 8. `FXCarrySignal.compute` needs an explicit funder argument, not just a rate-differential matrix.
- **`alpha_research/research/strategies/fx_carry_2026-03-13_conditional/proposal.md` (PM Challenge #3)** — **CHALLENGES the challenge.** "EM pairs have wider bid-ask spreads (5–20bps) that eat into carry" is now quantifiable and much weaker than assumed: against **3–9%** EM carry, a 20bp spread is **2–7%** of the carry, versus a far larger fraction of G10's near-zero differentials. The transaction-cost argument for staying G10-only does not survive Exhibit 7.
- **`alpha_research/quant_data/ticker_map.py` vs `core/market_data_service.py`** — **hard GAP, and a specifically fixable one.** Thirteen EM crosses are already *defined* in **`FX_TICKERS`** in `core/market_data_service.py` — eleven vs USD (`USDBRL=X`, `USDMXN=X`, `USDZAR=X`, `USDINR=X`, `USDIDR=X`, `USDKRW=X`, `USDTHB=X`, `USDTWD=X`, `USDPHP=X`, `USDMYR=X`, `USDTRY=X`) plus `EURHUF=X` and `EURPLN=X`, which is exactly the quoting convention GS uses for those two. `BZ=F` / `HG=F` sit in `data/market_data/prices/commodities.parquet` and `DFII10` in `data/market_data/fred/treasury_yields.parquet`. None of them is in `_FX_ENTRIES` / `_ETF_ENTRIES` / `_FRED_ENTRIES`, so `get_data` raises `ValueError` on every one — and none of the EM crosses has ever been pulled either (`prices/fx.parquet` holds G10 + DXY only). **Defined for the dashboard, unreachable from the research API, and never fetched.** A ~15-line registry addition is enough — `get_data` falls back to yfinance on a cache miss (verified live) — and would give all four of GS's FX-model inputs end-to-end, upgrading the `USO` and `DGS10−T10YIE` proxies to exact Brent and DFII10 along the way. COP, CLP, PEN, CZK, ILS, RON are absent from both registries and are a genuine new-source gap.
- **`alpha_research/backtests/stats/multiple_testing.py` + `alpha_research/backtests/strategies/manifest.py` (`n_trials` → DSR gate)** — **CHALLENGES the note's method.** GS's issuance model selects the best 4-of-$\mathcal{C}$ variable subset by in-sample $R^2$ with no multiplicity correction, no out-of-sample $R^2$, and no confidence band on the \$209bn. Our own `_evaluate_gates` in `alpha_research/review/pipeline.py` would refuse it — a clean external example of exactly the failure mode the gate exists to catch, worth citing in `alpha_research/research/RESEARCH_PHILOSOPHY.md`.
- **`book_notes/playground/reports/2026/07/crossasset_gs_goal-kickstart_2026-07-27.md`** — **direct CONTRADICTION, three days apart, same firm.** GOAL Kickstart (27-Jul, GS Portfolio Strategy) recommends **long JPY calls** as its tail hedge; The EM Trader (30-Jul, GIR EM Strategy) names **JPY as its third-ranked G10 funder** — structurally short JPY. A reader holding both is on opposite sides of the yen.
- **`book_notes/playground/reports/2026/07/crossasset_gs_goal-kickstart_2026-07-27.md` (FOMC catalyst)** — **RESOLVES it, partially.** The Kickstart framed the 29-Jul FOMC as a days-away falsifiable catalyst; this note is the answer — hold, but **three dissents to hike** — and our `DGS2` shows the 2y at 4.23% after a 4.13% → 4.37% July run-up: **14bp of the 24bp given back, +10bp still priced**, i.e. the catalyst resolved only partially, exactly as "curtailed for now" implies.
- **`book_notes/playground/reports/2026/04/macro_gs_jpy-macro-trading_2026-04-07.md` and `book_notes/playground/reports/2026/06/flows_gs_cta-bond-futures_2026-06-09.md`** — **VALIDATES the mechanism, indicts the timing.** Exhibit 18 (EM 10y local rates load on UST **term premium** at median $t\approx6\text{–}8$ vs $\approx2$ risk-neutral) plus "AI buildout capital needs + defence/infrastructure fiscal add term premia" is independent GIR confirmation of the same global channel that drove JGB 10y **2.06% → 2.670%** and left CTAs net short JGB futures. But the JPY-funder call was published on the exact session the December desk's intervention playbook fired to spec (5.74-yen range, RSI 80.5 on 1-Jul, spot parked at 160.18).
- **`book_notes/playground/reports/2025/11/rates_gs_vol-strategies_2025-11-13.md`** — **VALIDATES a repeated house blind spot worth naming.** That digest's stated weakest link was that every return series is characterised only by return, vol and return-to-vol — never skew, kurtosis or max drawdown. The EM Trader commits the identical error one layer up, on FX carry, the canonical negatively-skewed premium. **Two GIR notes, nine months apart, different desks, same missing third and fourth moments** — which argues for making skew / kurtosis / max-DD mandatory columns in `alpha_research/backtests/reporting/professional_report.py` whenever the strategy family is carry-like.

---

## Commentary — value to our investment learning

**`direct` · `useful`**  ·  ranked **2 of 10** in the library by contribution to learning

> Ties for the pool's highest total and is the only source anywhere in the library that states a cross-market transmission channel with a ratio attached — EM 10y local rates load ~3x more on UST term premium than on the risk-neutral path — and it rewrites the ranking statistic in a live proposal in his own repo.

**Why.** 6 ideas, 71 points, tied first with the JPY desk; four exclusive ideas totalling 46, so it ties on volume and loses the originality comparison to the JPY note's 50. Its top line, IDEA-003 (14, pool #3), is both shared with the Nov-2025 rates-vol note and a critique — the note commits the moment mismatch, it does not name it, and the merge kept the EM half's mechanism while crediting the rates note's algebra. What redeems it from the negative-example verdict is IDEA-007 (13, econ 5 / dur 5): its own Exhibit 18 regression, sole-source, one of only nine econ-5s in 46 ideas, median t 6–8 vs 2 across 16 EMs. Add the funder-switch algebra — the note asserts the funder matters, the reader proved it — and a direct hit on fx_carry_2026-03-13_conditional/proposal.md line 69, verified to contain `carry_rank = rate_diffs.rank(axis=1, pct=True)`, the exact construction its Exhibit 8 argues against. It changes code, not just reading habits.

**Take.** (1) IDEA-007: decompose the driver before sizing a foreign long-end response — 25bp of UST move driven by term premium is a different event for EM and DM local 10y than the same 25bp from Fed-path repricing. This is the only place in the library that states the channel as a rule rather than an observation, and it converts the scattered Japan readings (JGB 2.06→2.67, CTA net-short) into a general transmission. (2) The funder-switch identity, CtV^EUR/CtV^USD = [(C+Δ)/C] × [σ_USD/σ_EUR], with Δ = 1.46pp pinned independently by the five currencies quoted against both funders (CZK/HUF/PLN/RON/RUB, dispersion 0.2pp), decomposing the 2.07x MXN uplift into 1.49x carry × 1.39x vol. Carry the identity, not the MXN number. (3) The platform work item: FXCarrySignal.compute needs an explicit funder argument, and the same proposal's PM Challenge #3 (bid-ask eats EM carry) collapses to 2–7% of a 3–9% differential. (4) A durable habit: mark any sell-side trade list against the same document's own forecast table, since the two come from different processes and are never reconciled — here the flagship COP-over-BRL preference picks −2.33% over +6.11%, and the whole book earns +3.6% annualised on GS's own numbers against constituent 3m implied vols of 5–14%.

**Ignore.** Everything downstream of the method. The 29-Jul-2026 trade list (COP/BRL/MXN/ZAR longs, THB/PLN/ILS/CLP funders) is already partly dead — the JPY funder leg lost 2.25% in two sessions, nine months of MXN carry. The \$209bn issuance forecast, MSCI EM 2000, KOSPI 12000, the GCC concentration arithmetic and the entire Iran-shock event-study window are perishable, and pillars 4 and 5 yielded nothing to the pool at all. Discount two of its six as evidence of THIS report's worth: IDEA-026 arrived three separate ways (JPY desk, GPIF flows, here), so the triple arrival is evidence the operation is real, not that this note taught it; IDEA-003's algebra came from the rates-vol note. Do not overweight IDEA-019 despite its 12 — econ 2, explicitly a research-process control with no counterparty. IDEA-029 is its own argument but rests on one episode with no base rate and testability 2. And the trades are unexecutable here (no EM crosses through get_data, no EM forwards, no local IRS, no EMBI/MOVE); the actionable residual is a ~15-line ticker_map patch, not a book.

**Second read.** Twice, for narrow reasons. When the fx_carry conditional proposal is picked back up: pillar 2 plus the three 'arithmetic the note does not do' tables are the working spec — carry-to-vol, the implied-vol inversion σ = C/CtV, the breakeven S/(1−C), and the funder decomposition. And when building a DM version of the term-premium test (ACM or THREEFYTP10 against JGB/Bund/Gilt via stooq): pillar 3 and the Exhibit 18 formula are the reference. Everything else is spent — the trade list, the forecast tables, the mark-to-market section. One residual worth extracting once: pillar 5's specification search (best 4-of-C by in-sample R², 210 models, no multiplicity correction, no OOS R², no band on \$209bn) is a clean external exhibit of exactly the failure the n_trials/DSR gate exists to catch — cite it in RESEARCH_PHILOSOPHY.md and be done.

*Axes are independent: `indirect` means it contributes through method or context rather than
directly investable content — not that it is weak. Verdicts were calibrated across all 10
digests together, ranked by exclusive idea-yield in [`IDEAS.md`](../../IDEAS.md) and by whether
the report's best contributions were its own argument or critiques of it.*
