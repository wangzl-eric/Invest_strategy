# Vol-Conditioned Sector Reversal — Strategy Folder (PENDING)

> **Status:** PENDING (spec only — no code, no manifest, no trial-ledger row written)
> **Opened:** 2026-06-13 · **Track:** ETF rotation (equity) · **Stage reached:** S0→S3 (spec vetting)
> **Owner of decision:** Zelin (approve before any implementation / Fire 2)

## The idea
5-day short-term cross-sectional reversal among liquid SPDR sector ETFs, traded **only when
VIX is above its 60-day median** (high-volatility regime). Mechanism: elevated volatility
raises the compensation liquidity providers demand for absorbing uninformed flow, so the
short-horizon reversal premium is larger in high-vol regimes (Nagel 2012, "Evaporating
Liquidity").

## Artifacts (filesystem is the pipeline state)
| File | Stage | Produced by |
|---|---|---|
| `hypothesis.md` | S0 framing | framing agent |
| `cerebro_briefing.md` | S1 briefing (≥2 supporting + ≥1 contradicting — HARD) | briefing fan-out |
| `proposal_draft_*.md` | S2 independent drafts | drafters |
| `proposal.md` | S2 synthesis (the spec) | synthesizer |
| `pm_review.md` | S3 adversarial review (≤2 revision rounds) | PM challenger |
| `implementation_plan.md` | hand-off to Fire 2 | dev planner |

## Guardrails for this fire
- This is **spec vetting only**. No runner, no `manifest.yaml`, no `experiment_ledger` row.
- Rigor source of truth: `alpha_research/research/RESEARCH_PHILOSOPHY.md` (constitution) +
  `docs/guides/alpha_factory_workflow.md` (S0–S3).
- Near-neighbor prior art: `vix_regime_2026-03-15_rejected` (different mechanism; 90-day
  cooling boundary) and `vol_scaled_momentum_2026-03-13_rejected` (high-VIX fair-weather
  lessons). Same universe as `sector_rotation` → |ρ|≤0.4 gate is central.
