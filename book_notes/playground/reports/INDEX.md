# Reports Library — Index

## Purpose of this section — read this first

**This is an idea accumulator that operates *before* validation.** Its sole job is to build a pool
of ideas and methodologies that make *initial* sense. Nothing here is validated, backtested, or
gated, and nothing here is a recommendation.

The intended sequence is:

```
  STAGE 1  (here)   read reports → record the essence → harvest transferable ideas → score them
                    ↓  accumulate until the pool is large enough to choose from
  STAGE 2           select the ideas that make the most economic sense
                    ↓
  STAGE 3           validate the selected pool — formal research, rigor gates, the strategy pool
                    (alpha_research/research/, python -m alpha_research.review)
```

Two rules follow from this, and they are the ones most easily got wrong:

- **Testability is a score, never a gate.** An idea that cannot be tested on this platform today is
  still a good idea and still belongs in the pool. The data gap is recorded and the idea stays.
- **Harvest the transferable mechanism, not the house call.** "GS is short the 10y JGB" is a
  position and is worthless once it expires. "Net issuance mix plus central-bank taper identifies
  *which* curve sector underperforms, because mandated buyers sit at one tenor and the calendar is
  public" is an idea — reusable in another market, another year, by someone who never read the note.

**[`IDEAS.md`](IDEAS.md) is the accumulating pool** — one scored entry per idea, and the essence of
every report. The digests below are the working papers behind it; `IDEAS.md` is the output that
carries into stage 2.

`LEARNING_ROADMAP.md` belongs to **stage 3**, not here — it concerns validating and scoring claims
against outcomes. Parked deliberately until the pool is worth selecting from.

---

## The digests

Digests of **industrial / industry research reports** (sell-side notes, sector & macro
outlooks, consulting decks, central-bank notes, white papers) produced by the
`/read-industrial-report` skill. Every digest follows the fixed three-part format:
a 3–5 sentence STAR-ordered executive summary (context · methodology · conclusion),
PEE blocks with arrow-linked causal chains dissecting the argument, and 5–10 study
keywords — plus a required *What to watch* table and *Connection to our platform*.

---

## Convention

```
reports/
├── INDEX.md
├── <YYYY>/<MM>/<tag>_<issuer>_<topic>_<YYYY-MM-DD>.md    # digest
│                <tag>_<issuer>_<topic>_<YYYY-MM-DD>.pdf   # source report, same stem
└── <YYYY>/<tag>_<issuer>_<topic>_<YYYY>.md               # undated classics (year only)
```

- **Folders are the report's own publication date, not the date it was read.** The library
  reads as a market timeline; the read date lives in each digest's `Read on:` field.
- **Source PDF shares the digest's stem**, so `ls` pairs them. A PDF *export of a digest*
  (as opposed to a source report) takes the `.digest.pdf` suffix.
- Undated practitioner classics (AQR 2013, Bridgewater 2012) get a year folder with no month.
- Genuine academic finance papers go to `../papers/` via `/read-to-learn` instead.

**Tag vocabulary** — exactly one per report:

| Tag | Scope |
|---|---|
| `macro` | Cross-market macro strategy and trade ideas (rates + FX + policy together) |
| `rates` | Rates-specific: curve, vol, swap spreads, duration |
| `economics` | Economic outlooks, forecasting, policy-path research |
| `equities` | Single-market or sector equity strategy |
| `crossasset` | Multi-asset allocation, risk appetite, portfolio positioning |
| `flows` | Positioning, flow, and demand-side analysis — CTA/systematic tracking, institutional allocation, ownership shifts |
| `factor` | Factor, risk-premia, and portfolio-construction method papers |
| `event` | Single-event notes (central-bank meetings, elections, shocks) |

---

## Digests (newest report first)

| Tag | Digest | Report | Issuer / type | Published | C/R/A | Learning |
|---|---|---|---|---|:--:|:--:|
| `macro` | [em-trader](2026/07/macro_gs_em-trader_2026-07-30.md) | The EM Trader: Curves, Chips, Crude and Carry | Goldman Sachs — GIR EM strategy (Trivedi, Koul, Suwanapruti et al.) | 2026-07-30 | 4/4/3 | **direct** · useful <br><sub>rank 2/10</sub> |
| `crossasset` | [goal-kickstart](2026/07/crossasset_gs_goal-kickstart_2026-07-27.md) | GOAL Kickstart: Tracking Micro and Macro Risks into the Summer Holidays | Goldman Sachs — sell-side cross-asset strategy (Portfolio Strategy Research) | 2026-07-27 | 5/5/4 | **direct** · limited <br><sub>rank 7/10</sub> |
| `flows` | [japan-savings-jgb-demand](2026/07/flows_gs_japan-savings-jgb-demand_2026-07-20.md) | Global Markets Daily: Can Japanese Savings Boost JGBs? | Goldman Sachs — GIR Economics Research (Cole, Rosenberg) | 2026-07-20 | 4/4/2 | **direct** · useful <br><sub>rank 5/10</sub> |
| `flows` | [cta-bond-futures](2026/06/flows_gs_cta-bond-futures_2026-06-09.md) | 【GS先物】CTA グローバル債券先物 週次アップデート (CTA Global Bond Futures Weekly) | Goldman Sachs — FICC Futures Sales desk color (not GIR) | 2026-06-09 *(re-digested in place 2026-08-11 and 2026-08-15)* | 3/4/3 | **direct** · limited <br><sub>rank 10/10</sub> |
| `macro` | [jpy-macro-trading](2026/04/macro_gs_jpy-macro-trading_2026-04-07.md) | 2026 Q2 Trade Ideas from JPY Macro Trading **+** 2026 Top Trades from JPY Macro Trading — digested as a pair | Goldman Sachs Japan — FICC & Equities desk color, six JPY desks (not GIR) | 2026-04-07 *(pairs with [2025-12-26](2025/12/macro_gs_jpy-macro-trading_2025-12-26.pdf))* | 3/4/4 | **direct** · useful <br><sub>rank 1/10</sub> |
| `rates` | [fed-balance-sheet](2026/05/rates_gs_fed-balance-sheet_2026-05-21.md) | Global Markets Analyst: Revisiting the Outlook for the Fed's Balance Sheet | Goldman Sachs — GIR Economics Research (William Marshall) | 2026-05-21 | 5/4/3 | **direct** · useful <br><sub>rank 4/10</sub> |
| `economics` | [japan-outlook](2026/01/economics_gs_japan-outlook_2026-01-06.md) | 2026 Japan Economic Outlook: Steady Fundamentals, Policy Risks Ahead | Goldman Sachs — sell-side macro research (GIR, Japan Economics Analyst) | 2026-01-06 | 5/4/3 | **direct** · limited <br><sub>rank 6/10</sub> |
| `rates` | [vol-strategies](2025/11/rates_gs_vol-strategies_2025-11-13.md) | A Macro User's Guide to Interest Rates Volatility Strategies | Goldman Sachs — GIR sell-side research (Global Interest Rates Strategy) | 2025-11-13 | 5/4/3 | **direct** · limited <br><sub>rank 8/10</sub> |
| `factor` | [aqr-managed-futures](2013/factor_aqr_managed-futures_2013.md) | Demystifying Managed Futures | AQR — practitioner note | 2013 | 5/5/5 | **indirect** · useful <br><sub>rank 3/10</sub> |
| `factor` | [bridgewater-risk-parity](2012/factor_bridgewater_risk-parity_2012.md) | Risk Parity Is about Balance | Bridgewater — buy-side note | 2012 | 4/5/5 | **indirect** · limited <br><sub>rank 9/10</sub> |

*10 digests covering 11 reports.*

**On the paired digest:** `macro_gs_jpy-macro-trading` covers two notes in one file because the
April note is the mark-to-market and revision of the December note — the delta between them
(terminal rate 1.5% → 1.75%, a dropped FX section, a trade retained after ten months of not
working) is the analytical content, and splitting them would have duplicated ~80% of the text.
It is filed under the later report; the December source PDF sits in `2025/12/`.

---

## Reading threads

Several of these are best read together rather than as standalone notes:

- **Japan rates & the yen — six digests now touch this thread.** `economics_gs_japan-outlook`
  (GIR house view) vs `macro_gs_jpy-macro-trading` (the trading desks): they contradict each other
  on the JGB 10y and USD/JPY, and as of 2026-08 the desks are winning both.
  `flows_gs_cta-bond-futures` adds the positioning/crowding layer on the same JGB short;
  `flows_gs_japan-savings-jgb-demand` supplies the **demand** side against the desks' **supply**
  side, and the two disagree about what would kill the trade (GIR: a BoJ pause; desks: an
  issuance-calendar change); `crossasset_gs_goal-kickstart` (long JPY calls, 27-Jul) and
  `macro_gs_em-trader` (JPY as third-choice G10 funder, 30-Jul) contradict each other on the yen
  **three days apart from the same firm**.
- **Volatility** — `rates_gs_vol-strategies` (GIR: condition on macro fair value, not raw IV)
  and the JPY desks' receiver trades in `macro_gs_jpy-macro-trading` (condition on a realized-vol
  regime) reach the same principle from research and trading sides respectively.
- **Central-bank balance sheets & swap spreads** — `rates_gs_fed-balance-sheet` quantifies the
  Fed's UST **ownership share** (≈14% of outstanding), while `flows_gs_japan-savings-jgb-demand`
  supplies the **transfer function** (≈1bp on 30y swap spreads per 1ppt of free float). Neither
  note makes the composition; together they price balance-sheet policy in swap-spread terms.
- **Portfolio construction** — `factor_bridgewater_risk-parity` and `factor_aqr_managed-futures`
  are the method backbone; `crossasset_gs_goal-kickstart` is the applied allocation view — and it
  carries the +0.4 to +0.7 stock/bond correlation reading that the Bridgewater digest explicitly
  asked to be measured.

Each thread above has a counterpart in the pool, where the same material is grouped by *mechanism*
rather than by report: the threads follow the market story, the families follow the transferable idea.
Where a thread names a contradiction between two notes, the pool usually resolves it as one idea with
two sources — an independent arrival, which is itself evidence.

| Thread | Where it lands in the pool |
|---|---|
| Japan rates & the yen | [IDEA-005](IDEAS.md#idea-005) issuance mix · [IDEA-006](IDEAS.md#idea-006) mandate rebalancing · [IDEA-011](IDEAS.md#idea-011) official FX reaction · [IDEA-030](IDEAS.md#idea-030) WAM drift · [IDEA-042](IDEAS.md#idea-042) free float |
| Volatility | [IDEA-031](IDEAS.md#idea-031) direction of travel *(the merge of both halves)* · [IDEA-033](IDEAS.md#idea-033) fair-value residual · [IDEA-020](IDEAS.md#idea-020) convexity inside the factor · [IDEA-045](IDEAS.md#idea-045) priced dispersion |
| Central-bank balance sheets & swap spreads | [IDEA-014](IDEAS.md#idea-014) reserve satiation · [IDEA-016](IDEAS.md#idea-016) flat is tightening · [IDEA-039](IDEAS.md#idea-039) backstop censors the tail · [IDEA-042](IDEAS.md#idea-042) free-float denominator |
| Portfolio construction | [IDEA-001](IDEAS.md#idea-001) the correlation position · [IDEA-004](IDEAS.md#idea-004) risk vs capital weights · [IDEA-008](IDEAS.md#idea-008) leverage aversion · [IDEA-025](IDEAS.md#idea-025) where the Sharpe gain is not · [IDEA-037](IDEAS.md#idea-037) TSMOM |

**Navigating the library.** [`IDEAS.md`](IDEAS.md) is the pool and the entry point; its
[How the pool interconnects](IDEAS.md#how-the-pool-interconnects) section carries the six idea
families, the six hubs and the edge vocabulary. Every idea links to the digest it came from, every
digest links back to the ideas it produced, and ideas link outward to the paper notes in
[`../papers/`](../papers/INDEX.md), the book studies in `../studies/` and the strategy or code in
`alpha_research/` they bear on. Run `python3 scripts/check_ideas_integrity.py` after editing any of
it — it fails on a dead link, a broken reciprocal edge, or an ID that resolves but points at the
wrong entry.
