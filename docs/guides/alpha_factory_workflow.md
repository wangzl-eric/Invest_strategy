# Alpha Factory — Goal-Oriented Agentic Research Pipeline (v1.0)

> Consolidated 2026-06-12. Build + operating spec for the automated quant research
> workflow: **data in, validated low-correlation strategies out**.
>
> **How this doc is consumed:** humans read this file; the Conductor and dispatch
> scripts read `alpha_research/research/factory/factory_config.yaml` — the single
> source of truth for every threshold, limit, and tunable named here. If this doc and
> the config disagree, the config wins; fix the doc. Changing either = tracker entry.
>
> Grounding: `alpha_research/research/RESEARCH_PHILOSOPHY.md` (**the constitution / single
> source of truth** — principles, rigor battery, 11-gate checklist, capital policy) ·
> `EXECUTION_PLAN.md` (D1–D8) · `.claude/agents/*.md` (agent protocols, source of truth) ·
> `docs/RESEARCH_TEAM_MODELS.md` (per-role models = per-stage cost lever).

---

## 0. Objective function

The factory does **not** maximize strategy count or backtest Sharpe. It maximizes:

```
marginal blended-portfolio Sharpe per unit of owner review time,
subject to: factory-wide false discovery control.
```

**Goal state** (the brief): 3–4 active streams, pairwise |ρ| < 0.4, blended net Sharpe
0.8–1.2 at ~10% vol, ≥1 promoted to live capital via the paper gate.

**Queue-ranking metric** — Diversification-Adjusted Contribution:

```
DAC = SR_net × √(1 − ρ̄²)        ρ̄ = mean |corr| vs active pool streams
```

DAC ranks; the |ρ| < 0.4 gate (and its stronger successor, the spanning-alpha test, §2 S5)
stays binary.

---

## 1. The control loop

The Conductor (owner in F-0, agent in F-1+) runs **SENSE → DIAGNOSE → DISPATCH → GATE →
LEARN**. Work is dispatched against the **binding constraint**, never on a calendar:

```
SENSE      pool state: active streams, ρ matrix, realized vol vs budget, decay
           stats, stage queue depths, trial-ledger totals
DIAGNOSE   binding constraint, strict priority:
             C1 pool risk broken (vol off-budget, drawdown breach, decay trigger)
             C2 diversification gap (correlation cluster > 0.4, or < 3 streams)
             C3 pipeline starvation (a stage empty while downstream has capacity)
             C4 validation backlog (candidates waiting on review/implementation)
DISPATCH   route work to the stage that relaxes the constraint; never exceed WIP
           limits (§5) — a full downstream queue blocks upstream dispatch
GATE       stage exits are machine-checked; promotion is decided by the owner
LEARN      outcomes → trial ledger + domain KBs; queue re-scored; losers retired
```

**C2 dispatch rule (the common case):** find the pool's dominant correlation cluster;
boost queue scores for hypothesis families with low *predicted* correlation to it
(equity-beta-heavy pool → boost CTA trend / defensive / carry). The factory hunts the
*missing* stream, not the best absolute one.

---

## 2. Stage specifications

Every stage block is self-contained: owner, inputs, artifacts, hard-stops, exit gate,
kill rule. Artifacts are files or DB rows — **chat is coordination, never storage**.
Once a hypothesis reaches S2 it gets a strategy folder
`research/strategies/{idea}_{YYYY-MM-DD}_{verdict}/` whose name carries the verdict and
is **renamed on verdict change** — the filesystem is the pipeline state display.

---

**S0 — Intake & scan** · *Owner: Cerebro + Data*
- **Sources:** literature (arXiv/SSRN/blogs); playground studies via `/capture-finding`;
  graveyard resurrections (§4.4, after cooling); S7 decay diagnostics ("X stopped
  working — why?" is a hypothesis); domain-KB open questions; owner ideas.
- **Output:** entry in `alpha_research/research/factory/hypothesis_queue.yaml` —
  `{id, family, asset_track, mechanism (one falsifiable sentence),
  predicted_correlation_family, data_readiness, evidence_score, status}`.
- **Data's role:** sets `data_readiness` (READY / CONDITIONAL / BLOCKED). BLOCKED parks
  the entry — visible, justifying future data spend, never silently rotting.
- **Exit:** queue score (§3) ≥ dispatch threshold AND data_readiness ≠ BLOCKED.
- **Kill:** mechanism cannot be stated in one falsifiable sentence → reject at intake.

**S1 — Briefing** · *Owner: Cerebro*
- **Output:** `cerebro_briefing.md` — ≥2 supporting papers, **≥1 contradicting study or
  known failure mode** (no briefing without contradicting evidence), post-publication
  decay estimate, crowding assessment, graveyard/KB prior art.
- **Exit:** Researcher accepts (→S2) or rejects (logged; queue re-scored).

**S2 — Proposal + pre-registration** · *Owner: Researcher (Elena/Marco)* · **the rigor anchor**
- **Entry requires** (before any code): Data's `data_review.md` verdict ≥ CONDITIONAL,
  and written answers to *"Who loses money?"* and *"What is the economic mechanism?"*
  with ≥2 papers + ≥1 book cited.
- **Output:** `proposal.md` — signal construction, universe, rebalance frequency, **all**
  parameter values with rationale, expected net Sharpe (PM priors: long-only tilts 1–2%
  alpha, L/S factors 2–4%), kill thresholds — plus completed `preflight_checklist.md`
  (lessons L1–L7 + domain-KB failure modes checked).
- **Pre-registration:** hash `(proposal.md + manifest params)` → trial ledger, version 1.
  Material changes = new version; **trial counts accumulate across versions** (§4.1).
- **Exit:** pre-registration hash recorded.

**S3 — Adversarial review (PM touchpoint 1: spec-level)** · *Owner: PM agent*
- **Hard-stops (from `.claude/agents/pm.md` — a review without them is invalid):**
  `[CEREBRO CONTRADICTION]` and `[DATA ASSESSMENT]` in hand before any challenge is
  written. Data NO/CONDITIONAL blocks approval until resolved.
- **Challenges:** mechanism, costs at our capital, PIT/data lags, baseline beatability,
  L1–L7 / KB known-failure-mode violations. Max **2 revision rounds**.
- **Output:** `pm_review.md` with explicit "requirements for approval" checklist.
- **Exit:** verdict CONDITIONAL-or-better. **Kill:** REJECTED → graveyard + `/learn-verdict`.

**S4 — Implementation** · *Owner: Dev (Codex for sweeps/mechanical execution)*
- **Output:** weights-contract entrypoint under `backtests/runners/` + manifest under
  `research/pool/<id>/` + unit tests including the **truncation-invariance look-ahead
  test** (pattern: `test_sector_rotation_strategy.py::test_no_lookahead_truncation_invariance`);
  ≥70% coverage on new modules.
- **Exit (machine-checked):** lint+tests green; manifest validates; manifest `n_trials`
  ≥ ledger count for the hypothesis family.
- **Kill:** spec ambiguous → back to S2 as a **new version** (never silently interpreted).

**S5 — Mechanical validation** · *Owner: review pipeline (built); Data remediates QC failures*
- `python -m alpha_research.review run <manifest>`: QC preflight → vectorized backtest +
  EW baseline → walk-forward segments → PSR/DSR/MinBTL/bootstrap CI → cost 1×/2×/3× →
  params ±20/40% → correlation vs pool → gates → 13-artifact bundle under `run_id`.
- **Automated gates** (= the 11-gate checklist in `RESEARCH_PHILOSOPHY.md` §4, gates 1–8): IS/OOS
  Sharpe floors, max DD, PSR, DSR, IS/OOS ratio, MinBTL, 3× cost survival, |ρ| vs pool.
  **F-1 adds:** the 18-month embargo check (§4.3) and the **spanning-alpha t-stat vs
  pool return streams** (gate 9, automated — stronger than pairwise correlation; kills
  at t < 1.96).
- **Iteration cap: 3 runs per hypothesis version-family** (ledger-enforced). Agents see
  the verdict and *which* gate failed — never a distance-to-passing optimization target.
  3 × REVISE → graveyard + 90-day cooling.
- **Exit:** verdict PASS.

**S6 — Promotion review** · *Owner: **human only** (PM touchpoint 2: results-level)*
- PM first reviews the **executed run bundle** (actual artifacts, never summaries;
  cross-checks metrics against `stats_battery.json`/`sensitivity.json`) and issues a
  recommendation covering its judgment gates: **capacity vs AUM, economic-rationale
  coherence** (+ spanning alpha until automated). Same hard-stops as S3 if new evidence emerged.
- Owner decides on: `verdict.md`, DAC, granularity at current capital, PM recommendation.
  Decision + reason → `python -m alpha_research.pool promote ...`.
- **SLA:** ≤2 candidates/week reach this stage. Your calendar is the factory's clock.

**S7 — Paper / live / monitoring** · *Owner: ops jobs (Phase 3–4); Cerebro Function 3 owns the feedback*
- Paper validates **operations and consistency, not Sharpe**: 20 unattended days,
  clean reconciliation, returns within backtest PSR band, realized vol ±25% of design.
- **Risk limits per live strategy** (capital policy — encoded in `execution/risk.py`,
  not in anyone's memory): ≤20% of portfolio per strategy, gross leverage ≤2.0×,
  per-strategy stop −15%, portfolio stop −10%.
- Monthly health job → pool `health` JSON; **manifest demotion rules fire mechanically**.
  Every demotion emits an S0 hypothesis ("diagnose the decay") — the loop that closes
  the factory.

---

## 3. Hypothesis queue scoring

```
score = 0.30·evidence + 0.30·diversification + 0.20·data_readiness
      + 0.10·capacity_fit + 0.10·implementation_cost(inverse)
```

Weights live in `factory_config.yaml`. Re-scored on every LEARN step; the
diversification weight doubles while C2 binds. `data_readiness`: READY 1.0,
CONDITIONAL 0.6, BLOCKED 0 (parked, visible).

---

## 4. Factory-level rigor

An automated factory is a multiple-testing machine; per-strategy DSR with self-declared
`n_trials` is necessary but not sufficient. Four controls:

**4.1 Global trial ledger** — `experiment_ledger` table (extends `core/models.py`): one
row per review run and per spec version `{hypothesis_id, family, version, manifest_hash,
run_id, verdict, sharpe, timestamp}`. **`n_trials` for DSR is computed from the ledger**
(across versions and researchers); the manifest value is a floor. Quarterly
Benjamini–Hochberg FDR pass (`stats/multiple_testing.py`) across candidate families'
PSR p-values; expected false-discovery share > 25% → **S6 promotions freeze** until resolved.

**4.2 Information barrier** — iteration cap 3 (S5) + revision cap 2 (S3), ledger-enforced;
coarse gate feedback only; **no agent may edit `promotion_rules`** — threshold changes are
owner-only commits with tracker entries.

**4.3 Embargo** — most recent 18 months reserved: S2–S4 design and S5 runs 1–2 use
`data_end − 18m`; only the **final** S5 run includes the embargo window and must show
sign-consistent embargo Sharpe within the full-sample bootstrap CI. Exposes
regime-fitting; cannot validate Sharpe (and doesn't claim to).

**4.4 Graveyard with memory** — `alpha_research/research/graveyard/`: every kill gets
spec, reason, ledger stats. Resurrection needs materially new evidence + 90-day cooling;
S0 checks it before queueing near-duplicates. Every kill also fires
`/learn-verdict {folder}` → KB Curator → domain KBs
(`memory/knowledge/KNOWLEDGE_{FX|EQUITY|MACRO|VOL}.md`): the graveyard is the archive,
the KBs are the working memory agents actually read.

---

## 5. Throughput, WIP limits, cost

Sized to the real bottleneck — owner review time (8–15 h/wk), never compute:

| Queue | WIP limit |
|---|---|
| S0 scored hypotheses | 20 |
| S2–S3 active proposals | 2 |
| S4 implementation | 2 |
| S5 validation | unlimited (mechanical) |
| S6 awaiting owner | 2/week |
| S7 paper onboarding | 1 |

Full downstream queue ⇒ upstream dispatch blocked (Conductor moves to the next
constraint). Per-hypothesis LLM budget cap in the Conductor config; breach ⇒ human
check-in, not silent burn. Cost lever = per-role model assignment
(`RESEARCH_<AGENT>_MODEL=`, see `docs/RESEARCH_TEAM_MODELS.md`): **downgrade a model
before you ever downgrade a stage's rigor.**

---

## 6. Artifact contracts

| Handoff | Artifact | Location |
|---|---|---|
| Cerebro → Researcher | `cerebro_briefing.md` | `research/strategies/<name>/` |
| Cerebro → PM | `[CEREBRO CONTRADICTION]` | same folder (S3/S6 hard-stop) |
| Data → Researcher/PM | `data_review.md` (READY/CONDITIONAL/BLOCKED) | same folder (pre-S2 + S3 hard-stop) |
| Researcher → PM | `proposal.md` + pre-reg hash + `preflight_checklist.md` | same folder + ledger |
| PM → everyone | `pm_review.md` | same folder |
| PM ⇄ Dev | approval checklist; `dev_review.md` | same folder |
| Dev → pipeline | `manifest.yaml` + entrypoint + tests | `research/pool/<id>/`, `backtests/runners/` |
| Pipeline → all | run bundle (13 artifacts) | `data/backtest_runs/<run_id>/` |
| Pipeline → owner | `verdict.md` + DAC + PM recommendation | run bundle + notification |
| Monitor → S0 | decay hypothesis | hypothesis queue |
| Any kill | graveyard entry + `/learn-verdict` | `research/graveyard/`, domain KBs |

Completion protocol: every agent messages the Conductor on completion (files changed +
suggested next step). **The Conductor — not the agent — decides dispatch.**

---

## 7. Team collaboration & feedback loop

The team is an **adversarial, artifact-mediated** loop, not a relay. Per-role behavior is
specified in `.claude/agents/*.md` (**the source of truth for agent protocols**); this
section is the loop those agents run, mapped onto the stages (§2). Chat coordinates;
**artifacts are state** — every challenge, verdict, and revision is a file in the strategy
folder, never a lost message.

```
 CEREBRO/DATA          RESEARCHER            PM (challenger)        DEV / PIPELINE
 (S0–S1)               (S2)                  (S3, S6)               (S4–S5)
     │                     │                      │                      │
  briefing + data_review   │                      │                      │
  (≥1 CONTRADICTION,       │                      │                      │
   READY/COND/BLOCKED) ───►│                      │                      │
     │              proposal.md + pre-reg hash ──►│                      │
     │                     │            ADVERSARIAL REVIEW               │
     │              ◄───── pm_review.md (challenges + approval checklist) │
     │                     │  revise (≤2 rounds)  │                      │
     │              re-submit ──────────────────►│                       │
     │                     │     CONDITIONAL+  ───┼── implement ────────►│
     │                     │                      │           manifest + tests + run
     │                     │                      │       ◄── S5 verdict (which gate,
     │                     │                      │            coarse — no distance)
     │                     │                      │  PASS ─► S6 results review (human)
     │                     │                      │  3×REVISE ─► graveyard + cooling
     │                     │                      ▼
     │                     │            VERDICT → /learn-verdict → domain KBs
     └─────────── feedback: decay hypothesis (S7→S0) ──────────────────────┘
```

**Hard-stops (a review missing these is invalid):**
- `[DATA ASSESSMENT]` — Data's `data_review.md` verdict (READY / CONDITIONAL / BLOCKED) in
  hand **before S2**; a NO/CONDITIONAL blocks PM approval at S3 until resolved.
- `[CEREBRO CONTRADICTION]` — the contradicting-evidence artifact in hand **before any S3 or
  S6 challenge is written**. No briefing and no review without it.

**Feedback discipline (the anti-gaming rules, §4.2):** agents see *which* gate failed, never
a distance-to-passing target. Revision cap **2 rounds** (S3); iteration cap **3 runs** (S5),
both ledger-enforced. A verdict **renames the strategy folder** (`…_REVISE` → `…_PASS` /
`…_REJECTED`) — the filesystem shows the loop's state.

**Closing the loop:** every verdict — pass *or* kill — fires `/learn-verdict {folder}` → KB
Curator → domain KBs (`memory/knowledge/KNOWLEDGE_{FX|EQUITY|MACRO|VOL}.md`), and every kill
also lands in the graveyard (§4.4). Completion protocol (§6) routes all of it through the
Conductor, which decides the next dispatch. **No agent self-dispatches; no agent edits gates
or `promotion_rules`.**

---

## 8. Build roadmap

**F-0 (now — owner is the dispatcher; ~15 min/week SENSE/DIAGNOSE):**
- ✅ S4–S6 machinery (manifest, review pipeline, pool, gates)
- ✅ `factory_config.yaml`, seeded `hypothesis_queue.yaml`, graveyard convention
- ✅ `experiment_ledger` table + write-hook in `run_review` — DSR/MinBTL deflate by the
  ledger-derived effective `n_trials` (manifest = floor); trial identity excludes the
  entrypoint so the multi-impl cross-check is one trial, not N (`alpha_research/review/ledger.py`)
- ☐ **Protocol sync:** update `.claude/agents/*.md` — they predate Phase 1 and still
  treat Codex-executed notebooks as the canonical validation path; the manifest →
  review pipeline supersedes it for execution (notebooks remain for exploration).
  `scripts/sync_agents.sh` propagates automatically via the PostToolUse hook.

**F-1 (with Phase 2 — semi-automated):**
- Conductor session runs SENSE/DIAGNOSE from `factory_config.yaml` + queue + pool and
  *proposes* dispatch; owner approves with one message
- Ledger-enforced iteration caps + machine-checked `n_trials` at S4/S5
- **Embargo support** in the review pipeline (final-run flag)
- **Spanning-alpha gate automated in S5**: regress candidate daily returns on active
  pool streams; kill if alpha t-stat < 1.96 (replaces pairwise |ρ| as the binding
  diversification test; |ρ| stays as a cheap pre-filter)
- Cerebro unfrozen **for S0/S1 only** (D8 revisited: idea supply becomes binding once
  the harness is cheap to feed)

**F-2 (with Phase 3–4 — closed loop):**
- S7 → S0 decay hypotheses automated (Cerebro Function 3); quarterly FDR job;
  factory KPI panel (stage conversions, time-in-stage, ledger totals, FDR estimate,
  pool DAC). **Promotion authority never automates.**

**Factory KPIs:** S2→PASS conversion (healthy 10–30%; ~100% = gates too soft, ~0% =
intake is noise) · median days S2→S6 · trials per surviving strategy · live-vs-backtest
tracking error · blended pool Sharpe vs 0.8–1.2.

---

## 9. Failure modes → guards

| Failure mode | Guard |
|---|---|
| Agents grind against the gates | iteration caps + ledger n_trials + coarse feedback (4.2) |
| Factory-wide selection bias | global ledger + quarterly BH-FDR + promotion freeze (4.1) |
| Regime-fitted backtests | 18-month embargo, final-run-only (4.3) |
| Re-testing dead ideas | graveyard + cooling + S0 duplicate check (4.4) |
| Redundant "diversifiers" | DAC ranking + spanning-alpha gate (S5, F-1) |
| Throughput outrunning the human | WIP limits + backpressure sized to 8–15 h/wk (§5) |
| Knowledge trapped in transcripts | schema'd artifacts (§6) + KB capture on every verdict |
| Silent gate erosion | promotion_rules owner-only; config changes need tracker entries |
| Building factory before product | F-0→F-2 gated on EXECUTION_PLAN phases (§8) |

---

*All tunables (iteration cap, cooling, embargo, FDR threshold, WIP limits, score
weights, gate thresholds, risk limits) live in
`alpha_research/research/factory/factory_config.yaml`. Tune them there, in writing,
with a tracker entry — never ad hoc.*
