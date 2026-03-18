# Research Collaboration Model

> How the Zelin Investment Research team operates — from idea to implementation.

---

## Team Overview

| Agent | Model | Role |
|-------|-------|------|
| **Marco** | Opus 4.6 | Macro quant researcher — treasuries, commodities, FX |
| **Elena** | Opus 4.6 | Equity quant researcher — factors, sectors, indices |
| **PM** | Opus 4.6 | Portfolio manager & chief challenger — final gatekeeper |
| **Cerebro** | Sonnet 4.6 | Research intelligence — literature, contradictions, monitoring |
| **Dev** | Sonnet 4.6 | Quantitative developer — code review & production implementation |

---

## Core Philosophy

Every strategy must prove itself through **executed backtests**, not just proposals.

- Researchers run actual code in Jupyter notebooks
- PM reviews quantitative evidence, not markdown narratives
- Cerebro actively feeds external knowledge into the loop
- Dev only implements after PM approval
- All work is organized by strategy folder with consistent naming

---

## Strategy Folder Structure

Each strategy lives in a self-contained folder:

```
research/strategies/{main_idea}_{YYYY-MM-DD}_{verdict}/
  proposal.md          # Strategy hypothesis, literature, signal spec
  cerebro_briefing.md  # Cerebro's literature briefing (audit trail)
  research_r1.ipynb    # Researcher's Round 1 notebook (executed)
  research_r2.ipynb    # Revised notebook after PM Round 1 challenges
  research_r3.ipynb    # Final revision (if Round 3 needed)
  pm_review.md         # PM's structured challenges and verdict
  dev_review.md        # Dev's code review notes (if requested)
```

**Naming examples:**
```
vol_scaled_momentum_2026-03-15_conditional/
fx_carry_momentum_2026-03-16_approved/
yield_curve_2026-03-13_rejected/
```

When verdict changes, the folder is renamed (e.g., `_conditional` → `_approved`).

---

## The Multi-Round Challenge Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                     RESEARCH CYCLE                              │
│                                                                 │
│  RESEARCHER                 CEREBRO                  PM         │
│      │                         │                     │         │
│      │── "literature scan" ───>│                     │         │
│      │<── [CEREBRO BRIEFING] ──│                     │         │
│      │                         │                     │         │
│      │  (builds notebook)      │                     │         │
│      │                         │                     │         │
│      │── [ROUND 1 SUBMISSION] ──────────────────────>│         │
│      │                         │<── "contradiction" ─│         │
│      │                         │── [CEREBRO CONTRA] >│         │
│      │                         │                     │         │
│      │<────────── [ROUND 1 REVIEW] ─────────────────│         │
│      │       (challenges with cell references)       │         │
│      │                         │          │          │         │
│      │                         │     (optionally)    │         │
│      │                         │          │──> DEV   │         │
│      │                         │          │<── [DEV CODE REVIEW]│
│      │                         │                     │         │
│      │  (revises notebook)     │                     │         │
│      │                         │                     │         │
│      │── [ROUND 2 SUBMISSION] ──────────────────────>│         │
│      │<────────── [ROUND 2 REVIEW] ─────────────────│         │
│      │           (verifies fixes)                    │         │
│      │                         │                     │         │
│      │         [ROUND 3 only if unresolved CRITICAL] │         │
│      │                         │                     │         │
│      │                         │              VERDICT│         │
│      │                         │         APPROVED ───┼──> DEV  │
│      │                         │         CONDITIONAL ┼──> loop │
│      │                         │         REJECT ─────┼──> done │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase-by-Phase Breakdown

### Phase 1 — Literature Review (Researcher + Cerebro)

**Researcher** messages Cerebro with the strategy domain *before writing any code*.

**Cerebro** responds with `[CEREBRO BRIEFING]`:
- 3-5 supporting papers with relevance scores
- Contradicting evidence
- Book references (chapters from `books_and_papers/reading-list-summary.md`)
- Known failure modes for this strategy type
- Suggested signal construction approaches

**Researcher** also reads `research/external_ideas.md` and cites minimum:
- 2 academic papers
- 1 book reference

Answers two required questions before writing any code:
1. **"Who loses money?"** — identifies the counterparty
2. **"What is the economic mechanism?"** — why does this edge persist?

---

### Phase 2 — Notebook Construction (Researcher)

Researcher creates the strategy folder and executes the **16-cell research notebook**
(`notebooks/templates/strategy_research_template.ipynb`).

| Cell | Section | Framework Used |
|------|---------|----------------|
| 1 | Title & Metadata | — |
| 2 | Hypothesis & Literature (with citations) | — |
| 3 | Setup & pre-committed config | `sys`, `pandas`, `numpy` |
| 4 | Data Loading & Inspection | `yfinance`, `quant_data.duckdb_store` |
| 5 | Signal Construction | `backtests.strategies.signals` |
| 6 | Signal-to-Position Mapping (pre-committed weights) | `SignalBlender` |
| 7 | In-Sample Backtest with costs | `PortfolioBuilder`, `ProportionalCostModel` |
| 8 | Walk-Forward Analysis (2yr train / 3mo test) | `WalkForwardAnalyzer` |
| 9 | Statistical Tests | `probabilistic_sharpe_ratio`, `deflated_sharpe_ratio`, `block_bootstrap`, `minimum_backtest_length` |
| 10 | Regime Analysis | `RegimeAnalyzer` |
| 11 | Cost Sensitivity (1x–3x costs) | `CostSensitivityAnalyzer` |
| 12 | Parameter Sensitivity (±20%, ±40%) | `ParallelBacktester` |
| 13 | Decay & Capacity Analysis | `rolling_sharpe`, `strategy_half_life`, `correlation_with_existing` |
| 14 | LLM Verdict | `backend.llm_verdict.verdict` |
| 15 | Save Run | `RunManager` |
| 16 | **Summary Gate Table** (pass/fail for PM) | — |

> **Critical rule:** Signal weights are pre-committed in Cell 6 and NEVER changed after seeing backtest results. Changing weights after the fact is data mining.

Saved as `research_r1.ipynb` in the strategy folder.

---

### Phase 3 — PM Round 1 Review (PM + Cerebro)

Triggered when researcher sends folder path + 5-line summary to PM.

**PM simultaneously:**
1. Reads the actual notebook file (verifies it's executed, checks outputs)
2. Messages Cerebro for a contradiction search

**Cerebro** responds with `[CEREBRO CONTRADICTION]`:
- Alpha decay evidence
- Documented failure cases
- Crowding risk
- Implementation traps
- Each rated HIGH/MEDIUM/LOW severity

**PM** issues structured challenges tagged `[ROUND 1 REVIEW]` with:
- CRITICAL / HIGH / MEDIUM severity per challenge
- Cell number references
- Required actions

**PM optionally messages Dev** if code-level concerns are found (look-ahead, API misuse). Dev responds with `[DEV CODE REVIEW]` before PM issues Round 2.

---

### Phase 4 — Researcher Revision (Researcher)

Researcher addresses each PM challenge:
- References specific cell numbers and metric values
- Adds new cells to the notebook if additional analysis is needed
- Saves as `research_r2.ipynb` (never overwrites Round 1)
- Tags reply message `[ROUND 2 SUBMISSION]`

---

### Phase 5 — PM Round 2 Review (PM)

PM verifies:
- Each Round 1 challenge was addressed with quantitative evidence
- No regression introduced (fixing one issue didn't break another)

If all CRITICAL/HIGH challenges resolved → issues **VERDICT**.
If unresolved CRITICAL remain → **Round 3** (final).

Maximum **3 rounds**. PM must issue a verdict after Round 3.

---

## Quantitative Verdict Gates

A strategy **cannot** receive APPROVED unless ALL gates pass:

| Gate | Threshold | Why |
|------|-----------|-----|
| Deflated Sharpe Ratio | > 0 | Adjusts for number of parameter combos tested |
| Walk-forward hit rate | > 55% | OOS performance is consistent, not lucky |
| Survives 2x realistic costs | Sharpe > 0 | Edge survives realistic execution |
| PSR (Probabilistic Sharpe) | > 0.80 | Statistical significance beyond noise |
| Worst regime annual loss | > -15% | Strategy doesn't blow up in any regime |
| LLM verdict | != ABANDON | Hybrid rule + LLM sanity check |
| Strategy half-life | > 2 years | Edge hasn't fully decayed |
| MinBTL | < available data | Enough data for the claimed Sharpe |

### Verdict Definitions

| Verdict | Meaning | Action |
|---------|---------|--------|
| **APPROVED** | All gates pass, economic rationale sound | Dev implements → paper trading |
| **CONDITIONAL** | 1-2 borderline gates, specific fixes identified | Re-enter loop after addressing |
| **REJECT** | Fundamental flaw, multiple gate failures | Archive, move on |

---

## Dev's Dual Role

**Mode A — Code Review During Research**

PM or researchers can request a targeted code review at any point in the loop. Dev checks for:
- Look-ahead bias (signals using future data)
- SignalBlender full-sample normalization (should be expanding-window)
- Off-by-one errors in signal shifts
- Incorrect cost model configuration
- Data alignment / timezone issues

Responds with `[DEV CODE REVIEW]`, saved as `dev_review.md` in the strategy folder.

**Mode B — Production Implementation (after APPROVED only)**

Dev extracts signal logic from the final notebook and:
1. Implements as `BaseSignal` subclass in `backtests/strategies/signals.py`
2. Writes unit tests in `tests/unit/`
3. Configures `RunManager` for paper trading
4. Wires into `execution/runner.py`

Dev does **not** write the researcher's notebook, propose strategies, or implement pre-approval code.

---

## Cerebro's Three Functions

| Function | Trigger | Output Tag | Purpose |
|----------|---------|-----------|---------|
| Literature Briefing | Researcher requests | `[CEREBRO BRIEFING]` | Supporting + contradicting evidence before coding |
| Contradiction Search | PM requests | `[CEREBRO CONTRADICTION]` | Devil's advocate — reasons strategy might fail |
| Active Monitoring | Continuous | `[CEREBRO ALERT]` | Proactive alerts for active strategies |

Cerebro **never** recommends APPROVE or REJECT — it provides evidence, PM decides.

---

## Capital Policy

**ZERO capital** until:
1. ~~Framework bugs fixed~~ ✅ Done (2026-03-13)
2. Strategy completes 3+ months paper trading
3. Walk-forward shows positive OOS Sharpe

**Risk limits per strategy (when approved):**
- Max allocation: 20% of portfolio
- Aggregate gross leverage: 2.0x
- Per-strategy drawdown stop: -15%
- Portfolio drawdown stop: -10%

---

## Quick Reference

```bash
# Researcher starting a new strategy
1. Message Cerebro: "literature briefing for {domain}"
2. Create folder: research/strategies/{name}_{date}_in_review/
3. Write proposal.md
4. Execute notebook template → save as research_r1.ipynb
5. Send path + summary to PM: "[ROUND 1 SUBMISSION]"

# PM reviewing
1. Read research_r{N}.ipynb (not just the message)
2. Message Cerebro: "contradiction search for {strategy}"
3. Issue [ROUND N REVIEW] with cell references
4. Optionally: message Dev for code review

# Dev code review
1. Read cited cells in notebook
2. Check for look-ahead, cost errors, API misuse
3. Save [DEV CODE REVIEW] to dev_review.md in strategy folder

# After APPROVED verdict
1. PM renames folder: *_conditional → *_approved
2. PM messages Dev with approval + notebook path
3. Dev extracts logic, implements, tests, wires into execution
```

---

*Last updated: 2026-03-14*
