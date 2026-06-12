# Alpha Factory — Goal-Oriented Agentic Research Pipeline

> Created 2026-06-12. Build spec for the automated quant research workflow: **data in,
> validated low-correlation strategies out**. Grounded in `EXECUTION_PLAN.md` (D1–D8),
> `alpha_research/research/RESEARCH_PHILOSOPHY.md`, the v2 challenge loop
> (`alpha_research/research/README.md`), agent protocols (`.claude/agents/*.md`), and
> the collaboration architecture (`docs/guides/RESEARCH_COLLABORATION_MODEL.md`) — the
> factory *inherits* that model's working protocols (§2.1) rather than replacing them.
> This document is the contract between the agents; change it deliberately and log the
> change in `STRATEGY_TRACKER.md`.

---

## 0. Objective function (what the factory optimizes)

The factory does **not** maximize strategy count or backtest Sharpe. It maximizes:

```
marginal blended-portfolio Sharpe per unit of owner review time,
subject to: factory-wide false discovery control.
```

**Goal state** (from the brief): 3–4 active streams, pairwise |ρ| < 0.4, blended net
Sharpe 0.8–1.2 at ~10% vol, ≥1 promoted to live capital via the paper gate.

**Terminal metric per candidate** — Diversification-Adjusted Contribution (DAC):

```
DAC = SR_net × √(1 − ρ̄²)        ρ̄ = mean |corr| vs active pool streams
```

A 0.5-Sharpe stream at ρ̄=0.1 (DAC 0.50) beats a 0.9-Sharpe stream at ρ̄=0.7 (DAC 0.64 →
but fails the |ρ|<0.4 hard gate anyway). DAC ranks the queue; the correlation gate stays
binary.

---

## 1. The control loop (what makes it dynamic)

The Conductor runs a **SENSE → DIAGNOSE → DISPATCH → GATE → LEARN** cycle. Work is never
dispatched on a calendar; it is dispatched against the **binding constraint** of the goal
state.

```
SENSE      pool state: active streams, pairwise ρ matrix, realized vol vs budget,
           decay stats, stage queue depths, trial-ledger totals
DIAGNOSE   binding constraint, in priority order:
             C1 pool risk broken (vol off-budget, drawdown breach, decay trigger)
             C2 diversification gap (a correlation cluster > 0.4, or < 3 streams)
             C3 pipeline starvation (a stage queue empty while downstream has capacity)
             C4 validation backlog (candidates waiting on review/implementation)
DISPATCH   route work to the stage that relaxes the constraint (see §2);
           respect WIP limits (§5) — never push past them
GATE       every stage exit is machine-checked (§2 exit criteria); promotion
           gates are evaluated by the review pipeline, decided by the owner
LEARN      write outcomes to the trial ledger + lessons file; re-score the
           hypothesis queue (§3); retire/cool-off losers
```

**Dispatch rule for C2 (the common case):** compute the pool's correlation clusters;
boost hypothesis-queue scores for families with low *predicted* correlation to the
dominant cluster (e.g., pool is long-equity-beta heavy → boost CTA trend, defensive,
carry families). The factory hunts the *missing* return stream, not the best absolute one.

---

## 2. Stage map (S0–S7)

Each stage: **owner → input artifact → output artifact → exit gate → kill rule**.
All artifacts are files or DB rows — no knowledge lives only in a chat transcript.

| # | Stage | Owner | Output artifact |
|---|-------|-------|-----------------|
| S0 | Intake & scan | Cerebro (+ Data: `data_readiness` assessment) | `hypothesis.yaml` in queue |
| S1 | Briefing | Cerebro | `briefing.md` (evidence FOR + AGAINST) |
| S2 | Proposal | Researcher (Elena/Marco) | `proposal.md` + frozen pre-registration |
| S3 | Adversarial review | PM agent | challenge verdict in proposal |
| S4 | Implementation | Dev (Codex for sweeps/execution) | weights entrypoint + `manifest.yaml` + unit tests |
| S5 | Mechanical validation | review pipeline (built); Data agent remediates QC failures | `run_id` bundle + PASS/REVISE |
| S6 | Promotion review | **Owner (human)** | pool state transition + reason |
| S7 | Paper / live / monitor | ops jobs (Phase 3–4) | health JSON + monthly report |

Stage owners map to agent-deck sessions; **role definitions and binding protocols live in
`.claude/agents/*.md`** (source of truth), with model defaults/overrides in
`docs/RESEARCH_TEAM_MODELS.md` (opus for cognitive roles, sonnet for Data, Codex for
mechanical execution) — that mapping is the factory's per-stage cost lever.

### 2.1 Inherited from the Research Collaboration Model

These working protocols (`docs/guides/RESEARCH_COLLABORATION_MODEL.md`) carry over
unchanged — the factory adds the dispatch loop and ledger *around* them:

- **Strategy folder convention:** every hypothesis that reaches S2 gets
  `research/strategies/{idea}_{YYYY-MM-DD}_{verdict}/` containing `proposal.md`,
  `data_review.md`, `cerebro_briefing.md`, `pm_review.md`, `dev_review.md` (+ exploratory
  notebooks). The folder is **renamed when the verdict changes** — the filesystem is the
  pipeline state display.
- **Phase-0 data check semantics:** Data's `data_review.md` carries a verdict —
  **READY / CONDITIONAL / BLOCKED**. BLOCKED parks the hypothesis (queued, unscored on
  data_readiness) until the pipeline gap is built; *no research proceeds on a wish*.
  This check runs **before** the Cerebro briefing — coverage before literature.
- **Two required questions before any code** (S2 entry): *"Who loses money?"* and
  *"What is the economic mechanism?"* — with ≥2 papers + ≥1 book reference cited.
- **The 11-gate PM checklist** is the results-level review rubric (S6 touchpoint).
  Division of labor with the review pipeline: gates 1–8 (IS/OOS Sharpe, max DD, PSR,
  DSR, IS/OOS ratio, MinBTL, 3× cost survival) are **automated in S5**; PM owns
  gates 9–11 — **spanning-alpha t-stat vs the existing pool (< 1.96 kills; stronger
  than the plain correlation gate), capacity vs AUM target, and economic rationale** —
  plus narrative coherence between cells/artifacts.
- **Knowledge capture:** after **every** verdict (incl. graveyard kills), run
  `/learn-verdict {folder}` → KB Curator proposes entries to the domain knowledge bases
  (`memory/knowledge/KNOWLEDGE_{FX|EQUITY|MACRO|VOL}.md`); owner confirms writes. S0
  intake and PM reviews read these KBs (known-failure-modes check is a mandatory
  challenge question).
- **Playground → factory migration:** `book_notes/playground/` remains the no-rigor
  exploration space; promising studies enter S0 via `/capture-finding` + the migration
  path. The factory's gates start at S2 — never police the playground.

### S0 — Intake & scan
- **Sources:** literature (arXiv/SSRN/blogs), playground studies via `/capture-finding`
  (§2.1), the idea graveyard (§4.4) after cooling, decay diagnostics from S7
  ("X stopped working — why?" is a hypothesis), domain-KB open questions, owner ideas.
- **Output `hypothesis.yaml`:** `{id, family (trend/carry/value/momentum/defensive/...),
  asset_track (D3 tracks only), one-line economic mechanism, predicted_correlation_family,
  data_readiness (have|cheap|blocked), evidence_score 1–5}`.
- **Exit gate:** queue score (§3) ≥ threshold AND data_readiness ≠ blocked.
- **Kill:** mechanism cannot be stated in one falsifiable sentence → reject at intake.

### S1 — Briefing
- **Mandatory contents:** ≥2 supporting papers, **≥1 contradicting study or known failure
  mode**, post-publication decay estimate, crowding assessment, prior art in our own
  graveyard. No briefing without contradicting evidence — return to Cerebro.
- **Exit gate:** Researcher accepts (proceeds) or rejects (logged, queue re-scored).

### S2 — Proposal + pre-registration (the rigor anchor)
- `proposal.md` must contain, **before any backtest**: signal construction, universe,
  rebalance frequency, *all* parameter values with rationale, expected net Sharpe
  (haircut per PM priors: long-only tilts 1–2% alpha, L/S factors 2–4%), kill thresholds.
- **Pre-registration:** hash `(proposal.md + manifest params)` → write to the trial
  ledger. The declared spec is version 1. Every subsequent material change = new version,
  and **trial counts accumulate across versions** (§4.1).
- **Exit gate:** pre-registration hash recorded.

### S3 — Adversarial review (PM touchpoint 1: spec-level)
- PM agent challenges the *pre-registered spec*: economic mechanism ("who loses money?"),
  costs at our capital, data lags (PIT), baseline beatability, lessons L1–L7 and
  KB known-failure-mode violations. Max **2 revision rounds** here.
- **Mandatory hard-stops (from `.claude/agents/pm.md` — a review without them is
  invalid):** PM must hold `[CEREBRO CONTRADICTION]` (devil's-advocate evidence) and
  `[DATA ASSESSMENT]` (Data agent's coverage/quality verdict) before writing challenges.
  Data returning NO/CONDITIONAL blocks approval until the gap is resolved.
- **Exit gate:** PM verdict CONDITIONAL-or-better with explicit "requirements for
  approval" checklist (the sector-rotation proposal is the template), plus the
  researcher's completed `preflight_checklist.md` in the strategy folder.
- **Kill:** REJECTED → graveyard with reason; lessons file updated if novel.

### S4 — Implementation
- Dev implements the weights contract entrypoint exactly as pre-registered; unit tests
  must include the **truncation-invariance look-ahead test** (pattern:
  `tests/unit/test_sector_rotation_strategy.py::test_no_lookahead_truncation_invariance`)
  and long-only/exposure contract checks. Coverage ≥70% on the new module.
- **Exit gate:** `make lint` green, tests green, manifest validates, `n_trials` in the
  manifest equals the ledger count for this hypothesis family (machine-checked).
- **Kill:** implementation reveals the spec is ambiguous → back to S2 as a new version
  (not silently "interpreted").

### S5 — Mechanical validation (already built)
- `python -m alpha_research.review run <manifest>`: QC → backtest + EW baseline →
  walk-forward segments → PSR/DSR/MinBTL/CI → cost 1×/2×/3× → params ±20/40% →
  correlation vs pool → gates. Plus the **embargo check** (§4.3) once implemented.
- **Iteration cap: 3 review runs per hypothesis version-family.** Every run increments
  the ledger. After 3 REVISE verdicts → automatic graveyard + 90-day cooling period.
  This is the information barrier: agents cannot grind against the gates (§4.2).
- **Exit gate:** verdict PASS.

### S6 — Promotion review (human-only; PM touchpoint 2: results-level)
- Before the owner decides, the PM agent reviews the **executed run bundle** (v2
  protocol: actual results, never summaries — cross-check Sharpe/PSR/DSR/segments
  against the artifacts, verify cost realism and look-ahead) and issues a promotion
  recommendation. Same hard-stops apply as S3 if new evidence has emerged.
- Owner reviews: `verdict.md`, `sensitivity.json`, the DAC score, capacity/granularity at
  current capital, and the PM agent's recommendation. Decision + reason → pool CLI.
- **SLA:** ≤2 candidates per week reach this stage (WIP limit, §5). The factory's
  throughput is sized to *your* 8–15 h/wk, not to compute.

### S7 — Paper / live / monitoring (Phase 3–4 infrastructure)
- Paper validates **operations and consistency, not Sharpe** (philosophy §7): 20 unattended
  days, reconciliation clean, returns within backtest PSR band, realized vol ±25% of design.
- **Risk limits per live strategy** (capital policy, collaboration model): max 20% of
  portfolio per strategy, aggregate gross leverage ≤ 2.0×, per-strategy drawdown stop
  −15%, portfolio drawdown stop −10%. Encoded in `execution/risk.py` limits, not in
  anyone's memory.
- Monthly health job writes decay stats to the pool `health` JSON; **mechanical demotion
  rules** from the manifest fire without discussion. Demotions emit an S0 hypothesis
  ("diagnose the decay") — the feedback loop that closes the factory. Owner of that
  loop: **Cerebro Function 3 (Active Monitoring)**, already defined in
  `.claude/agents/cerebro.md`.

---

## 3. Hypothesis queue scoring (the dispatcher's ranking)

```
score = 0.30·evidence            (S1 briefing strength, 1–5 normalized)
      + 0.30·diversification     (1 − predicted |ρ| vs current dominant pool cluster)
      + 0.20·data_readiness      (1.0 have · 0.6 cheap · 0 blocked)
      + 0.10·capacity_fit        (tradeable at $25–100k with integer sizing?)
      + 0.10·implementation_cost (inverse; reuses existing signals/data = high)
```

Re-scored on every LEARN step. Diversification weight doubles while constraint C2 binds.
Blocked-data hypotheses (e.g., futures pre-Phase-2) stay queued, visible, and unscored —
they justify data spend decisions; they don't silently rot.

---

## 4. Factory-level rigor (the part single-strategy rigor misses)

An automated factory is a multiple-testing machine. Per-strategy DSR with self-declared
`n_trials` is necessary but **not sufficient** once agents generate trials at machine
speed. Four controls:

### 4.1 Global trial ledger
- New table (extend `core/models.py`): `experiment_ledger` — one row per review run
  *and* per material spec version: `{hypothesis_id, family, version, manifest_hash,
  run_id, verdict, sharpe, timestamp}`.
- `n_trials` for DSR is **computed from the ledger** (count of runs in the hypothesis
  family, across versions and researchers), not hand-declared. The manifest value is a
  floor, the ledger a hard override. S4's exit gate machine-checks this.
- Quarterly: factory-wide FDR pass — Benjamini–Hochberg (`stats/multiple_testing.py`,
  already implemented) across all candidate families' PSR p-values. If the pool's
  expected false-discovery share exceeds **25%**, freeze S6 promotions until resolved.

### 4.2 Information barrier & iteration caps
- Agents see verdicts and *which gate failed*, never fine-grained "distance to passing"
  optimization targets. Max 3 S5 runs per version-family (hard, enforced by the ledger),
  max 2 S3 revision rounds. Exhausted → graveyard + 90-day cooling.
- **No agent may edit `promotion_rules` in a manifest.** Gate-threshold changes are
  owner-only, in a separate commit, with a tracker entry.

### 4.3 Embargo (true out-of-sample reserve)
- The most recent **18 months** of data are embargoed: S2–S4 design and S5 iterations 1–2
  run on `data_end − 18m`. The **final** S5 run (the one that can yield PASS) includes
  the embargo window and must show: embargo-segment Sharpe sign-consistent and within the
  full-sample bootstrap CI. A strategy that dies exactly in the unseen window was fitted,
  not found.
- 18 months is a discipline check, not a significance test — it cannot validate Sharpe,
  only expose snooping. (Owner-tunable; shorten only with a written reason.)

### 4.4 Idea graveyard with memory
- `research/graveyard/` — every killed hypothesis: spec, reason, ledger stats, lesson (if
  novel → L-numbered in the tracker). S0 must check the graveyard before queueing
  near-duplicates; resurrection requires materially new evidence + cooled-off 90 days.
  Rejections are training data for the factory, not embarrassments to delete.
- Each kill also fires `/learn-verdict {folder}` (§2.1) so the lesson lands in the
  domain KB the PM and researchers actually read — the graveyard is the archive, the
  KBs are the working memory.

---

## 5. Throughput, WIP limits, and backpressure

Sized to the real bottleneck — owner review time (8–15 h/wk) — not to compute:

| Queue | WIP limit | Rationale |
|---|---|---|
| S0 hypothesis queue | 20 scored (cap) | beyond this, scanning is procrastination |
| S2–S3 active proposals | 2 | PM challenge quality degrades in parallel |
| S4 implementation | 2 | Dev focus; merge conflicts |
| S5 validation | unlimited (mechanical) | cheap, deterministic |
| S6 awaiting owner | 2/week | your calendar is the SLA |
| S7 paper onboarding | 1 at a time | ops attention is serial |

**Backpressure rule:** a full downstream queue blocks upstream dispatch (Conductor skips
to the next constraint). **Token/compute budget:** per-hypothesis LLM budget cap set in
the Conductor config; exceeding it forces a human check-in rather than silent burn.
Cost control per stage = model assignment (`docs/RESEARCH_TEAM_MODELS.md`): downgrade a
role's model via `RESEARCH_<AGENT>_MODEL=` before downgrading the stage's rigor.

---

## 6. Artifact & message contracts

Every inter-agent handoff is a file/row with a schema. Chat is coordination, never storage.

| Handoff | Artifact | Location |
|---|---|---|
| Cerebro → Researcher | `cerebro_briefing.md` (FOR/AGAINST/decay/crowding) | `research/strategies/<name>/` |
| Cerebro → PM | `[CEREBRO CONTRADICTION]` evidence | same folder (S3/S6 hard-stop) |
| Data → Researcher/PM | `data_review.md` — READY/CONDITIONAL/BLOCKED | same folder (pre-S2 + S3 hard-stop) |
| Researcher → PM | `proposal.md` + pre-registration hash + `preflight_checklist.md` | same folder + ledger |
| PM → everyone | `pm_review.md` (challenges + verdict) | same folder |
| PM → Dev | approval checklist in `proposal.md`; Dev replies `dev_review.md` | same folder |
| Dev → pipeline | `manifest.yaml` + entrypoint + tests | `research/pool/<id>/`, `backtests/runners/` |
| Pipeline → everyone | run bundle (13 artifacts) | `data/backtest_runs/<run_id>/` |
| Pipeline → owner | `verdict.md` + DAC + PM recommendation | run bundle + notification |
| Monitor → S0 | decay hypothesis | hypothesis queue |
| Any kill → factory | graveyard entry + lesson | `research/graveyard/`, tracker |

Completion protocol (existing rule): every agent messages the Conductor on task completion
with files changed + suggested next step. The Conductor — not the agent — decides dispatch.

---

## 7. Build roadmap (incremental; do not build the factory before the product)

The factory automates a loop that must first work manually. Phases gate on
`EXECUTION_PLAN.md`:

**F-0 (now, manual conductor — you are the dispatcher):**
- Already built: S4–S6 machinery (manifest, review pipeline, pool, gates).
- Build: `experiment_ledger` table + ledger write in `run_review` (small: one model +
  one hook) ·  `research/graveyard/` convention · hypothesis queue as
  `research/hypothesis_queue.yaml` with the §3 score fields. Run SENSE/DIAGNOSE yourself
  weekly (15 min): pool ρ matrix + queue review.
- **Protocol sync:** update `.claude/agents/*.md` — they predate Phase 1 and still
  describe Codex-executed notebooks as the canonical validation path. The manifest →
  one-call review pipeline supersedes that for execution (notebooks remain for
  exploration); PM's metric cross-checks point at the run bundle artifacts. Propagate
  with `scripts/sync_agents.sh`.

**F-1 (with Phase 2 — semi-automated):**
- Conductor session (agent-deck) runs SENSE/DIAGNOSE and *proposes* dispatch; owner
  approves with one message. Enforce iteration caps + n_trials machine-check in S4/S5.
- Embargo support in the review pipeline (`backtest_end` handling + final-run flag).
- Unfreeze Cerebro **for S0/S1 only** (D8 revisited): idea supply becomes binding once
  three tracks are live and the harness is cheap to feed.

**F-2 (with Phase 3–4 — closed loop):**
- S7 monitoring emits decay hypotheses into S0 automatically; quarterly FDR job;
  factory KPI panel on the dashboard (stage conversion, time-in-stage, ledger totals,
  FDR estimate, DAC of pool).
- Owner remains the only promotion authority. This never automates.

**KPIs to judge the factory itself:** S2→PASS conversion (healthy: 10–30%; 100% means
gates are too soft, ~0% means intake is noise), median days S2→S6, trials per surviving
strategy (ledger), realized-vs-backtest tracking error of promoted strategies, and
blended pool Sharpe vs the 0.8–1.2 goal.

---

## 8. Failure modes this design guards against

| Failure mode | Guard |
|---|---|
| Agents grind hyperparameters against the gates | iteration cap 3 + ledger-driven n_trials + coarse gate feedback (4.2) |
| Factory-wide selection bias despite per-strategy DSR | global ledger + quarterly BH-FDR + promotion freeze (4.1) |
| Pretty backtests fitted to the recent regime | 18-month embargo, final-run-only (4.3) |
| Idea churn / re-testing the same dead idea | graveyard + cooling + S0 duplicate check (4.4) |
| Throughput outrunning the human decision-maker | WIP limits + backpressure sized to 8–15 h/wk (§5) |
| Knowledge trapped in chat transcripts | every handoff is a schema'd artifact (§6) |
| Strategy-count maximization ("collecting") | DAC objective + correlation hard gate (§0) |
| Silent gate erosion | promotion_rules owner-only; threshold changes need tracker entries (4.2) |
| Building the factory instead of the product | F-0→F-2 roadmap gated on EXECUTION_PLAN phases (§7) |

---

*Owner-tunable defaults in this doc: iteration cap (3), cooling period (90d), embargo
(18m), FDR freeze threshold (25%), WIP limits (§5), queue score weights (§3). Tune them
in writing, here, with a tracker entry — never ad hoc.*
