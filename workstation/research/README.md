# Zelin Investment Research

## Team

| Role | Agent | Model | Focus |
|------|-------|-------|-------|
| Macro Quant Researcher | Marco | Claude Opus 4.6 | Thesis, signal design, economic rationale (FX, commodities, rates) |
| Equity Quant Researcher | Elena | Claude Opus 4.6 | Factor research, signal design, cross-sectional analysis |
| Quantitative Developer | Dev | Claude Opus 4.6 | Framework integrity, code review, implementation |
| Portfolio Manager | PM | Claude Opus 4.6 | Strategy challenge, verdict authority, risk assessment |
| Research Intelligence | Cerebro | Claude Opus 4.6 | Literature briefing, contradiction search, monitoring |
| Execution Assistant | Codex | GPT-5.4 | Backtest execution, parameter sweeps, data pulls, code review |

**Design principle:** Opus agents focus on the hardest cognitive work. Codex handles mechanical execution.

## Teamwork Flow (v2 Challenge Loop)

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: HYPOTHESIS                          │
│                                                                 │
│  Researcher ──── "briefing request" ────► Cerebro               │
│                                                                 │
│  Cerebro ──── [CEREBRO BRIEFING] ────► Researcher               │
│    • Supporting evidence (2+ papers)                            │
│    • Contradicting evidence                                     │
│    • Book references (1+)                                       │
│    • Known failure modes                                        │
│    • Suggested approaches                                       │
│                                                                 │
│  Researcher writes proposal.md + designs notebook cells         │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2: EXECUTION                           │
│                                                                 │
│  Researcher ── "run cells 3-8" ──► Conductor ──► Codex          │
│                                                                 │
│  Codex executes:                                                │
│    • Data pulls                                                 │
│    • PortfolioBuilder.backtest()                                │
│    • WalkForwardAnalyzer.run()                                  │
│    • Statistical tests (PSR, Deflated Sharpe, MinBTL)           │
│    • Cost sensitivity (1x, 1.5x, 2x, 3x)                      │
│    • Parameter sensitivity (+/-20%, +/-40%)                     │
│    • Validation-engine checks (Backtrader first)                │
│    • QuantStats tear sheet generation                           │
│    • PyPortfolioOpt comparison for optimizer-heavy strategies   │
│                                                                 │
│  Codex ── results ──► Conductor ──► Researcher                  │
│                                                                 │
│  Researcher interprets results, designs next cells              │
│  Saves notebook as research_r1.ipynb (16 mode-driven sections)  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3: PM CHALLENGE (max 3 rounds)         │
│                                                                 │
│  Round 1:                                                       │
│  Researcher ── [ROUND 1 SUBMISSION] ──► Conductor ──► PM        │
│  PM ── "contradiction search" ──► Conductor ──► Cerebro         │
│  Cerebro ── [CEREBRO CONTRADICTION] ──► Conductor ──► PM        │
│  PM reads notebook code, checks metrics, reviews contradictions │
│  PM ── [ROUND 1 REVIEW] ──► Conductor ──► Researcher            │
│    • CRITICAL / HIGH / MEDIUM challenges                        │
│    • Required actions                                           │
│                                                                 │
│  Round 2:                                                       │
│  Researcher addresses challenges → research_r2.ipynb            │
│  (may request Codex re-run or Dev code review)                  │
│  PM ── [ROUND 2 REVIEW] ──► Conductor ──► Researcher            │
│                                                                 │
│  Round 3 (only if unresolved CRITICAL):                         │
│  Final opportunity → PM MUST issue verdict                      │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 4: VERDICT                              │
│                                                                 │
│  PM issues verdict (all 11 gates must pass for APPROVED):       │
│                                                                 │
│  ┌─ APPROVED ──► Dev begins Mode B implementation               │
│  │               Folder renamed: *_approved                     │
│  │                                                              │
│  ├─ CONDITIONAL ──► Specific improvements required              │
│  │                  Researcher re-enters loop                   │
│  │                                                              │
│  └─ REJECTED ──► Folder renamed: *_rejected                     │
│                  Archived, lessons logged                       │
└─────────────────────────────────────────────────────────────────┘
```

## Optional: Session Forking (A/B Research)

```
After PM Round 1 challenge:

  research-elena ──── fork ────► research-elena-alt-signal
       │                              │
       ▼                              ▼
  Approach A (original)         Approach B (alternative)
  research_r2.ipynb             research_r2_alt.ipynb
       │                              │
       └──────── compare ─────────────┘
                    │
              Better approach → submit to PM
              Losing fork → killed
```

## Orchestration Modes

**Both paths use the same agent definitions, same workflow, same 11 gates. Never run both simultaneously for the same strategy.**

### Path A: Claude Code Teams

```
You ◄──► Claude Code session (team lead)
              │
              ├── Agent: Marco (Opus) ── executes cells directly
              ├── Agent: Elena (Opus) ── executes cells directly
              ├── Agent: Dev (Opus)   ── code review + implementation
              ├── Agent: PM (Opus)    ── challenge + verdict
              └── Agent: Cerebro (Opus) ── literature + contradictions

Orchestration: TeamCreate + SendMessage (in-process)
Codex: available via /codex skill (on-demand, not always-on)
Worktrees: none (all on main branch)
Best for: hands-on steering, real-time interaction
```

### Path B: Agent-Deck

```
You ◄──► agent-deck TUI / web UI
              │
              ├── Conductor (Claude session) ── autonomous routing
              │     └── routes messages per v2 challenge loop
              ├── research-marco   [worktree]  ── writes cells, Codex executes
              ├── research-elena   [worktree]  ── writes cells, Codex executes
              ├── research-dev     [worktree]  ── code review + implementation
              ├── research-pm      [main]      ── challenge + verdict
              ├── research-cerebro [main]      ── literature + contradictions
              └── codex-runner     [main]      ── backtest execution, sweeps

Orchestration: Conductor + agent-deck session send (tmux)
Codex: always-on codex-runner session, routed via Conductor
Worktrees: researchers + dev get isolated branches
Best for: background sprint, parallel exploration, session forking
```

### Agents auto-detect which path they're in
- **Path A detected:** `SendMessage` tool available, spawned via `Agent` tool
- **Path B detected:** initial message mentions "Conductor" or agent-deck

## Agent-Deck Session Architecture

```
agent-deck TUI
  │
  ├── Conductor: research (persistent Claude session)
  │     ├── Heartbeat (15 min)
  │     ├── Message routing (v2 challenge loop)
  │     ├── Periodic monitoring (5 min cron)
  │     └── Fork tracking
  │
  ├── Group: research
  │     ├── research-marco    [worktree: .worktrees/research-marco]   Opus
  │     ├── research-elena    [worktree: .worktrees/research-elena]   Opus
  │     ├── research-dev      [worktree: .worktrees/research-dev]     Opus
  │     ├── research-pm       [main branch]                           Opus
  │     ├── research-cerebro  [main branch]                           Opus
  │     └── codex-runner      [main branch]                           GPT-5.4
  │
  ├── MCP Socket Pool (shared via Unix sockets)
  │     ├── exa (web search)
  │     ├── filesystem
  │     └── context7 (library docs)
  │
  └── On-demand forks
```

## Quantitative Verdict Gates (11 required for APPROVED)

| # | Gate | Threshold |
|---|------|-----------|
| 1 | Deflated Sharpe Ratio | > 0 |
| 2 | Walk-forward hit rate | > 55% |
| 3 | Survives 2x realistic costs | Sharpe > 0 |
| 4 | PSR (Probabilistic Sharpe) | > 0.80 |
| 5 | Worst regime annual loss | > -15% |
| 6 | LLM verdict | != ABANDON |
| 7 | Strategy half-life | > 2 years |
| 8 | MinBTL | < available data length |
| 9 | Max Drawdown | > -25% |
| 10 | IS Sharpe | varies |
| 11 | OOS Sharpe | > 0 |

## Directory Structure

```
research/
  STRATEGY_TRACKER.md           # Master tracker: status, verdicts, priorities
  README.md                     # This file
  external_ideas.md             # Academic papers, Kaggle insights
  pm_review.md                  # Legacy PM verdicts
  strategies/
    {name}_{date}_{verdict}/    # Per-strategy folder
      proposal.md               # Strategy proposal
      cerebro_briefing.md       # Cerebro literature briefing
      research_r1.ipynb         # Round 1 notebook (16 cells)
      research_r2.ipynb         # Round 2 notebook (if needed)
      pm_review.md              # PM challenges + verdict
      dev_review.md             # Dev code review (if requested)
  framework_audit/
    backtesting_audit.md        # Full framework audit (24 issues)
    framework_comparison_*.md   # External framework comparisons
    pm_framework_advisory_*.md  # PM advisory reports
```

## Capital Policy

ZERO capital until:
1. All critical framework bugs fixed (DONE)
2. At least one strategy completes 3+ months paper trading
3. Walk-forward analysis shows positive OOS Sharpe
