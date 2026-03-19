# Research Collaboration Model

> How the Zelin Investment Research team operates — from idea to implementation.

---

## Team Overview

| Agent | Model | Role |
|-------|-------|------|
| **Marco** | Opus 4.6 | Macro quant researcher — treasuries, commodities, FX |
| **Elena** | Opus 4.6 | Equity quant researcher — factors, sectors, indices |
| **PM** | Opus 4.6 | Portfolio manager & chief challenger — final gatekeeper |
| **Cerebro** | Opus 4.6 | Research intelligence — literature, contradictions, monitoring |
| **Dev** | Opus 4.6 | Quantitative developer — code review & production implementation |
| **Data** | Sonnet 4.6 | Data engineer — coverage gaps, pipeline builds, data quality |

**Utility agents** (invoked by slash commands, not standing sessions):
- **KB Curator** — validates and writes entries to domain knowledge bases (`/learn-verdict`, `/capture-finding`)

---

## Core Philosophy

Every strategy must prove itself through **executed backtests**, not just proposals.

- Researchers run actual code in Jupyter notebooks
- PM reviews quantitative evidence, not markdown narratives
- Cerebro actively feeds external knowledge into the loop
- **Data validates coverage before any code is written**
- Dev only implements after PM approval
- All work is organized by strategy folder with consistent naming
- Lessons from every strategy (approved or rejected) flow into the domain knowledge bases

---

## Strategy Folder Structure

Each strategy lives in a self-contained folder:

```
research/strategies/{main_idea}_{YYYY-MM-DD}_{verdict}/
  proposal.md          # Strategy hypothesis, literature, signal spec
  data_review.md       # Data agent's coverage & pipeline assessment
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
│  RESEARCHER          CEREBRO           PM              DEV       │
│      │                  │               │               │        │
│   [Phase 0: Data Coverage Check]        │               │        │
│      │──── coverage? ──>DATA            │               │        │
│      │<─── data_review.md ─────────────────────────────│        │
│      │                  │               │               │        │
│   [Phase 1: Literature Review]          │               │        │
│      │── briefing req ─>│               │               │        │
│      │<─ [CEREBRO BRIEFING] ────────────│               │        │
│      │                  │               │               │        │
│   [Phase 2: Notebook Execution]         │               │        │
│      │ (runs 16-cell template)          │               │        │
│      │── [ROUND 1 SUBMISSION] ──────────>               │        │
│      │                  │               │               │        │
│   [Phase 3: PM Round 1 Review]          │               │        │
│      │             contradiction req ──>│               │        │
│      │             [CEREBRO CONTRADICTION]              │        │
│      │<────────── [ROUND 1 REVIEW] ─────               │        │
│      │ (revises notebook → r2.ipynb)    │               │        │
│      │── [ROUND 2 SUBMISSION] ──────────>               │        │
│      │                  │               │               │        │
│   [Phase 4: PM Round 2 Review]          │               │        │
│      │                  │   (verifies fixes)            │        │
│      │                  │               │               │        │
│      │         [ROUND 3 only if unresolved CRITICAL]    │        │
│      │                  │               │               │        │
│      │                  │        VERDICT│               │        │
│      │                  │   APPROVED ───┼──────────────>│        │
│      │                  │   CONDITIONAL ┼──> loop       │        │
│      │                  │   REJECT ─────┼──> done       │        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase-by-Phase Breakdown

### Phase 0 — Data Coverage Check (Researcher + Data)

**Researcher** messages Data with the strategy's required instruments, frequency, and lookback *before requesting a Cerebro briefing*.

**Data** responds with `[DATA REVIEW]` saved to `data_review.md`:
- Required tickers / series and their availability in the data lake
- Coverage gaps (missing history, frequency mismatches, survivorship risk)
- Pipeline actions needed (new connectors, backfill scripts, derivation logic)
- **Data verdict:** READY / CONDITIONAL / BLOCKED

If verdict is BLOCKED, strategy is parked until pipeline is built. No research proceeds.

---

### Phase 1 — Literature Review (Researcher + Cerebro)

**Researcher** messages Cerebro with the strategy domain *before writing any code*.

**Cerebro** responds with `[CEREBRO BRIEFING]`:
- 3-5 supporting papers with relevance scores
- Contradicting evidence
- Book references (chapters from `books_and_papers/reading-list-summary.md`)
- Known failure modes for this strategy type
- Suggested signal construction approaches
- Relevant entries from domain knowledge bases (`memory/knowledge/`)

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
- Cell-level references (e.g., "Cell 9 output shows...")
- Specific quantitative concerns
- Optional: requests Dev code review (`[DEV REVIEW REQUEST]`)

---

### Phase 4 — PM Round 2 Review (PM)

Researcher revises notebook → `research_r2.ipynb`. PM verifies fixes with same 11-gate checklist.

A Round 3 is triggered only if a CRITICAL issue remains unresolved after Round 2.

---

### Phase 5 — Verdict & Knowledge Capture

**PM** issues one of three verdicts:
- `APPROVED` — passes all 11 gates; PM renames folder to `*_approved`, messages Dev with notebook path
- `CONDITIONAL` — minor gaps remain; researcher iterates in same loop
- `REJECTED` — fails a kill gate; folder renamed to `*_rejected`, lessons captured

**After any verdict**, KB Curator is triggered (via `/learn-verdict {folder}`) to extract lessons into the domain knowledge bases (`memory/knowledge/KNOWLEDGE_{FX|EQUITY|MACRO|VOL}.md`). This ensures rejected strategies teach future researchers.

---

## The 11-Gate PM Checklist

| # | Gate | Kill threshold |
|---|------|----------------|
| 1 | Annualised Sharpe (IS) | < 0.5 |
| 2 | Annualised Sharpe (OOS walk-forward) | < 0.3 |
| 3 | Max Drawdown | > −30% |
| 4 | PSR vs benchmark | < 95% confidence |
| 5 | Deflated Sharpe (multiple-testing corrected) | < 0 |
| 6 | IS/OOS Sharpe ratio | < 0.5 (overfitting proxy) |
| 7 | MinBTL (minimum backtest length) | Exceeds available history |
| 8 | Cost sensitivity (3× costs) | Sharpe < 0 |
| 9 | Spanning alpha t-stat | < 1.96 (vs existing strategies) |
| 10 | Capacity estimate | < AUM target |
| 11 | Economic rationale | No credible mechanism |

---

## Domain Knowledge Bases

Lessons from every strategy feed into four domain KB files:

| Domain | File | Topics |
|--------|------|--------|
| FX | `memory/knowledge/KNOWLEDGE_FX.md` | carry, momentum, real-exchange-rates, regime |
| Equity | `memory/knowledge/KNOWLEDGE_EQUITY.md` | momentum, quality, low-vol, sector-rotation, crowding |
| Macro | `memory/knowledge/KNOWLEDGE_MACRO.md` | yield-curve, commodity-momentum, inflation-regime, credit |
| Volatility | `memory/knowledge/KNOWLEDGE_VOL.md` | vrp, vix-regime, vol-targeting, realized-vs-implied |

**Skills for capturing knowledge:**
- `/learn-verdict {folder}` — extract lessons from a completed PM review
- `/capture-finding` — capture an insight from playground or reading
- `--learn-source` flag on `market-intelligence-synthesizer` — auto-extract from articles

All writes are proposed by **KB Curator** and require explicit user confirmation before writing.

---

## Playground (Hypothesis Generation)

Before formal research, ideas can be explored in `workstation/playground/` with no rigor gates:

- **No statistical thresholds** — explore freely
- **No PM review required** — learning-focused
- **Agents:** Tutor (educational), Explorer (hypothesis generation)
- **Migration path:** When a playground study shows promise → message Cerebro → create strategy folder → follow v2 workflow

Capture playground insights with `/capture-finding` so they flow into the knowledge bases.

---

## Agent-Deck Session Architecture

The team runs as isolated tmux sessions managed by agent-deck:

```bash
# Launch full team
./scripts/launch_research_team.sh <strategy_name> <researcher: elena|marco>

# Stop sessions (preserve worktrees)
./scripts/cleanup_research_team.sh

# Full teardown
./scripts/cleanup_research_team.sh --remove
```

| Session | Agent | Worktree | MCP |
|---------|-------|----------|-----|
| `research-elena` or `research-marco` | Researcher | `research/<name>` | filesystem |
| `research-cerebro` | Cerebro | main | exa, filesystem |
| `research-data` | Data | `research/data` | filesystem |
| `research-dev` | Dev | `research/dev` | filesystem |
| `research-pm` | PM | main | filesystem |
| `codex-runner` | Codex | — | — |

**Auto-sync:** When any `.claude/agents/*.md` file is edited, `scripts/sync_agents.sh` fires automatically (via `PostToolUse` hook) and sends a reload message to the matching live session.

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
1. Message Data: "coverage check for {strategy} — need {instruments} at {frequency}"
2. Message Cerebro: "literature briefing for {domain}"
3. Create folder: research/strategies/{name}_{date}_in_review/
4. Write proposal.md
5. Execute notebook template → save as research_r1.ipynb
6. Send path + summary to PM: "[ROUND 1 SUBMISSION]"

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
4. Run /learn-verdict {folder} to capture lessons in KB

# Capturing knowledge
/learn-verdict {strategy_folder}   # from PM verdict
/capture-finding                   # from playground or reading
```

---

*Last updated: 2026-03-20*
