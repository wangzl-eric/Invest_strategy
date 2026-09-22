# Reading Queue — Advances in Financial Machine Learning

Follow-ups surfaced while reading, scored on Credibility / Relevance / Actionability
(1–5). Only items ≥3 on all three are kept here.

| Next | Why | C | R | A |
|------|-----|:-:|:-:|:-:|
| **Ch. 12 — Backtesting through Cross-Validation (CPCV)** | Direct parent of our `cpcv_split`; extends Ch.7 purge/embargo to the backtest itself. | 5 | 5 | 5 |
| **Ch. 11 — The Dangers of Backtesting** | The *second* leakage mode (multiple testing / selection bias) Ch.7 defers; pairs with `stats/multiple_testing.py`, `minimum_backtest.py`. | 5 | 5 | 4 |
| **Ch. 4 — Sample Weights / Uniqueness** (re-read) | Defines the label-overlap "concurrency" that purging removes; grounds `max_samples` = avg uniqueness. | 5 | 4 | 4 |
| **Ch. 8 — Feature Importance** | "Marcos' First Law: Backtesting is not a research tool, feature importance is." Reframes the research workflow away from the backtest-cycle. | 5 | 4 | 3 |
| Bailey & López de Prado — *The Deflated Sharpe Ratio* (2014) | Quantifies the multiple-testing problem; underpins our DSR gate in the review pipeline. | 5 | 5 | 4 |
