---
type: concept
id: CONCEPT-006
slug: point-in-time-information
domain: method
status: stable
sources: 2
---

# CONCEPT-006 · information date vs availability date

**Definition.** Every observation has two dates: the period it *describes* and the moment it *became
knowable*. Using the first where the second is required is look-ahead bias. The gap is not noise — it is
a publication lag, it is usually known, and revisions mean the value you see today may never have
existed on the date you are backtesting.

## The rule

$$\text{usable}_t = \{x_s : \text{availability}(x_s) \le t\} \quad\text{not}\quad \{x_s : s \le t\}$$

For macro series the two differ by weeks or months: GDP is quarterly with a lag and then revised twice;
Japan's long-yield series `IRLTLT01JPM156N` is monthly with a **~45-day** lag. Trading on the
information date rather than the availability date manufactures alpha that was never available.

## How this platform enforces it

**PIT shifting is default-on**, which is the single most important thing to know here:

| Mechanism | Where |
|---|---|
| `get_data(..., pit=True)` — the default | [`quant_data/api.py`](../../../alpha_research/quant_data/api.py) |
| Publication-lag table per series | [`quant_data/pit.py`](../../../alpha_research/quant_data/pit.py) |
| `pit=False` logs a look-ahead warning | never use it in a backtest |
| Weights contract: entrypoints return **unshifted** target weights; the review engine applies the execution shift | [`backtests/strategies/manifest.py`](../../../alpha_research/backtests/strategies/manifest.py) |

**Never pre-shift inside a strategy function.** Weights at date $t$ use only data $\le t$, and the
engine owns the execution convention. Double-shifting is as wrong as not shifting, and much harder to
see.

## The document-level analogue

The same error class applies to *claims*, not just series — and it runs in one direction. A vendor
strategy note's **publication date is the end of its in-sample period**, because publication is
asymmetrically selected: the firm publishes when the backtest looks good and never publishes the
version that failed.

Dating that from the artifact is where it goes wrong. A re-digest of the CTA note surfaced a PDF
carrying **two** dates — a dateline of 9 June 2026 and a portal sidebar stamped 30 July 2026, rendered
~7 weeks later. Filesystem mtimes are worse. The bias is **always the same direction** (artifacts are
created at or after the claim), so dating from the file ends the in-sample period *late* and quietly
counts genuinely out-of-sample months as in-sample.

**Rule: date from the dateline in the document body; treat every other timestamp as rendering
furniture.**

## Where it fails / what is missing

- `manifest.py` has `n_trials` but **no `publication_date` field** — the document-level version of PIT
  is not enforced anywhere, while the series-level version is. That asymmetry is the open gap.
- Revision history (ALFRED vintages) is not ingested, so "what did this print say on the day" is not
  answerable for most series — only "what does it say now, shifted".
- PIT protects against look-ahead in *data*. It does nothing about parameters chosen while looking at
  the full sample, which is the more common leak.

## What it underpins

[IDEA-010](../../reports/IDEAS.md#idea-010) — publication date ends the in-sample; haircut a reported
Sharpe by a third to a half absent post-publication evidence ·
[IDEA-028](../../reports/IDEAS.md#idea-028) — the PIT-shifted growth decomposition ·
[IDEA-043](../../reports/IDEAS.md#idea-043) — the per-publisher forecast ledger

## Related

[[CONCEPT-005-effective-sample-size]] — the other systematic inflator of the same reported statistic ·
[[CONCEPT-001-term-premium]]

## Sources

[`quant_data/pit.py`](../../../alpha_research/quant_data/pit.py) — the implemented lag table is the
authority on this platform · [hurst2013](../../papers/paper_notes_hurst2013.md) ·
[baltussen2021](../../papers/paper_notes_baltussen2021.md)

*The McLean–Pontiff post-publication-decay literature supplies the effect size and is cited in the
mechanism pool but has **no paper note yet** — a genuine gap in `../papers/`.*
