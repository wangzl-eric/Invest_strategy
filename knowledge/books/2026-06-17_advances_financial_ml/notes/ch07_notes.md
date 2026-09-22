# Advances in Financial Machine Learning (López de Prado, 2018) — Chapter 7 Notes: Cross-Validation in Finance

- **Read on:** 2026-06-17
- **Source:** `knowledge/sources/advances-in-financial-machine-learning.pdf`, pp. 146–159 (print Ch. 7)
- **Place in the arc:** Part 2 (Modelling). Chapter 4 established *sample uniqueness* and overlapping labels; Chapter 6 established bagging/early-stopping as overfitting controls. Chapter 7 is where those two ideas collide with model evaluation: it shows that the standard tool for estimating generalization error — k-fold CV — is *structurally broken* on financial data, and supplies the fix (purging + embargo). It sets up Chapters 11–13 (backtesting), where the *second* failure mode (multiple testing / selection bias) is addressed.

## Central claim (one sentence)
Standard k-fold CV almost always reports inflated, wrong performance in finance because observations are **not IID** — overlapping labels plus serially correlated features leak test-set information into the training set — and the remedy is **Purged K-Fold CV**: purge training observations whose label-outcome interval overlaps the test interval, and **embargo** a small fraction of observations immediately after each test fold.

**Decision it changes:** a practitioner stops trusting *any* CV or backtest number produced by vanilla `sklearn.KFold`/`cross_val_score`, re-runs evaluation with purging + embargo, and *expects and accepts a lower, more realistic* score. A drop after purging is evidence the original number was leaking — not a regression.

## Core concept
CV exists to estimate generalization error and thereby detect overfitting. But CV's validity rests on the IID assumption: every observation belongs to exactly one of train/test, and the two sets share no information. Financial labels violate this twice over:
- **Serial correlation in features:** $X_t \approx X_{t+1}$.
- **Overlapping labels:** a label $Y_t$ formed over a horizon (e.g. triple-barrier return from $t_{i,0}$ to $t_{i,1}$) overlaps the next label, so $Y_t \approx Y_{t+1}$.

When $t$ lands in train and $t{+}1$ in test, the classifier effectively "sees" the test answer through this overlap. It then scores well **even on irrelevant features** — the canonical signature of leakage. The danger is not leakage with a genuinely predictive feature (that only flatters an already-good strategy); it is leakage with *noise* features, which manufactures **false discoveries**.

## Author intent
De Prado is dismantling a specific, widespread false comfort: "my CV (even walk-forward OOS) looks good, therefore my model generalizes." His goal is to make the reader *distrust the number* and understand the mechanism of contamination well enough to fix it at the data-partition level, not paper over it. The chapter is deliberately mechanistic — he wants you to be able to implement the purge/embargo yourself, because (see 7.5) even the standard libraries get adjacent things wrong.

## Key technicalities

**Leakage condition.** Two observations $i,j$ leak into each other when their information sets overlap, $\Phi_i \cap \Phi_j \neq \varnothing$ — operationally, when their label intervals are *concurrent*. Label $Y_i = f[[t_{i,0}, t_{i,1}]]$ overlaps $Y_j$ if any of:
1. $t_{j,0} \le t_{i,0} \le t_{j,1}$
2. $t_{j,0} \le t_{i,1} \le t_{j,1}$
3. $t_{i,0} \le t_{j,0} \le t_{j,1} \le t_{i,1}$

**Purging.** For each test observation $j$, drop from the *training* set every observation $i$ whose label interval overlaps $j$'s. This requires knowing $t_1$ (label end / outcome time) for every observation — you cannot purge without it. (Repo equivalent: the `label_end_times` argument.)

**Embargo.** Purging handles overlap on *both sides* of the test fold, but serial correlation can leak through training observations that begin *just after* the test set ends. Embargo drops a small block of $h \approx 0.01\,T$ observations immediately following each test fold (only the post-test side needs it; pre-test training labels already ended before the test began). The diagnostic that $h$ is large enough: performance no longer rises monotonically as $k \to T$.

**The $k \to T$ tell.** If reported performance keeps improving as you increase the number of folds $k$ toward $T$ (i.e. shrinking test sets, more recalibration), you are likely *profiting from leakage*. Past a sufficient $k^*$, a clean setup stops improving. This is a cheap, model-free leakage detector.

**`PurgedKFold` (Snippet 7.3).** Extends `sklearn._BaseKFold`, forces `shuffle=False` (test folds must be contiguous in time), takes `t1` (label end times) and `pctEmbargo`, and yields purged+embargoed train indices per fold. Works for both hyper-parameter tuning *and* backtesting.

**7.5 — the libraries are buggy too.** `sklearn`'s scoring loses `classes_` because it relies on numpy arrays not pandas (issue 6231), and `cross_val_score` passes sample weights to `fit` but not to `log_loss` (issue 9144). De Prado's maxim: **always read all the code you run** — the upside of open source is you can verify and patch it. Use his `cvScore` (Snippet 7.4), avoid `cross_val_score`.

## How it builds on prior chapters
- **Ch. 4 (Sample Weights / Uniqueness):** "concurrency" and label-overlap defined there are exactly the overlap that purging removes. Average uniqueness → `max_samples` for bagging; here the same overlap structure drives the train/test partition.
- **Ch. 3 (Labeling / triple-barrier):** supplies the $[t_{i,0}, t_{i,1}]$ intervals the purge logic operates on.
- **Ch. 6 (Bagging / early stopping):** offered as the *second line of defence* — even if some leakage survives, a non-overfit classifier (early stopping, bagging with `max_samples`=avg uniqueness, sequential bootstrap) can't exploit it.

## Methodology & mindset extracted
*(lenses from `.claude/skills/read-to-learn/references/methodology-lenses.md`)*

- **Problem framing:** This is a *measurement-validity* problem, not a return problem. Before asking "does my signal work?", de Prado asks "is my instrument for answering that question even unbiased?" Mindset: **fix the ruler before you measure.**
- **Evidence standard:** He treats a *good* CV score as a red flag to investigate, not a result to celebrate. The asymmetry — leakage helps irrelevant features most — means impressive numbers on weak features are *expected* under contamination. "Almost certain those results are wrong" about published k-fold-in-finance evidence.
- **Economic mechanism:** Purging/embargo has no economic story — it's a *statistical hygiene* step. The economic content lives downstream; this chapter guarantees the downstream test is honest. Lesson: separate "is the test clean?" from "is the edge real?" — conflating them is how people fool themselves.
- **Implementation reality:** The fix *lowers* reported performance and *costs* you the $t_1$ bookkeeping. A practitioner who refuses to pay that cost is choosing a flattering lie. Embargo size is a tunable with a built-in validation diagnostic ($k \to T$ monotonicity).
- **Practitioner heuristics (durable):**
  1. *Non-IID by default* — never assume financial observations are independent; prove it or partition around it.
  2. *A performance jump after a methodology "improvement" that adds information access is usually leakage, not skill.*
  3. *Read all the code you run* — even canonical libraries (sklearn) are wrong on the details that matter here.
  4. *Lower-but-honest beats higher-but-leaking* — purging should reduce your Sharpe; welcome it.

## Connection to our platform (required)
*(Updated 2026-06-17 after tracing the call graph — see Resolved verification below.)*

**Partial VALIDATION — the CV module implements the chapter; the review pipeline does not use it.**
- `alpha_research/backtests/stats/cross_validation.py` exposes `purged_kfold_split(..., embargo_pct=0.01, label_end_times=...)` whose docstring mirrors the chapter precisely (purge = drop train obs whose label outcome overlaps the test period; embargo = drop the next block after each fold). The **1% default embargo equals the book's $h \approx 0.01T$.** It also exposes `cpcv_split` (Ch. 12's Combinatorial Purged CV) and `walk_forward_split`. Where this is *used* — the ML/signal path, `signals.py:723` fed a real `t1` series from `labeling.py.label_end_times()` — purging is wired **correctly** (no silent no-op).
- **The weights-contract review pipeline (`alpha_research/review`) still does not use *purged* CV** — by design (see below). Its walk-forward *was* `np.array_split(returns, 4)` (contiguous-segment Sharpe over the whole series, including lookback-starved early bars). **Updated 2026-06-17:** it now runs **expanding-window walk-forward OOS** — `walk_forward_split(..., expanding=True)` reserves a ~40% in-sample anchor and evaluates 6 non-overlapping OOS windows marching forward, reporting per-window Sharpe, mean OOS Sharpe, and positive-window count (`walkforward_method="expanding_oos"`). This is a *stability* diagnostic over the realized (already-causal) return path, **not** a leakage control. The `WalkForward`/`use_purged_cv` class remains dormant.
- This is **defensible by design, not a bug:** the review path is a position→returns backtest, not an ML-classifier CV, so there are no overlapping triple-barrier labels to purge. Look-ahead there is controlled by a *different* mechanism — the **execution-convention shift** ("weights at date $t$ use only data ≤ $t$", per the Weights Contract in CLAUDE.md) plus **PIT-shifted macro** (`quant_data/pit.py`). Ch. 7's leakage and the weights-contract's look-ahead are two distinct contamination channels guarded by two distinct controls.

**Resolved verification (was an open question):**
- Q: *Does `alpha_research/review` pass real `label_end_times` into `purged_kfold_split`?*
  **A: It never calls `purged_kfold_split`, so the question is moot for review.** Confirmed via call-graph trace: `review/pipeline.py` + `review/engine.py` contain no purged/CPCV/WalkForward usage. The only live purged-CV caller is `signals.py` (ML path), and it *does* supply a real `t1`.

**Lesson for me (mindset):** I initially read "the repo has `purged_kfold_split`" as "the review battery is leakage-controlled à la de Prado." Wrong inference — *implemented* ≠ *invoked on the path I care about*. Always trace the call graph before crediting a guarantee.

## Open questions & testable ideas
- Does increasing $k$ in our `purged_kfold_split` on a *known-noise* feature stop improving past some $k^*$? A quick synthetic check (random features + overlapping labels) would let us *demonstrate* the leakage detector on our own code — a strong playground study, and a regression test for the CV module. → candidate for `study_hypotheses.md`.
- How sensitive are our pooled strategies' reported metrics to `embargo_pct` (0% vs 1% vs 5%)? Large sensitivity = thin, possibly-leaking edge.

## What to do next
- [ ] Read **Ch. 12 "Backtesting through Cross-Validation"** (CPCV) next — it extends this to the backtest itself and is the direct parent of our `cpcv_split`.
- [ ] Read **Ch. 11 "The Dangers of Backtesting"** for the *second* failure mode (multiple testing / selection bias) this chapter defers — pairs with our `stats/multiple_testing.py` and `minimum_backtest.py`.
- [ ] Trace whether `alpha_research/review` passes real `label_end_times` into `purged_kfold_split`; if not, open a documentation/issue note (do not assume a bug).
- [ ] Optional (ask first): replicate the $k \to T$ leakage detector on `purged_kfold_split` with synthetic overlapping labels via `/get-market-data` + a notebook in this study folder.
