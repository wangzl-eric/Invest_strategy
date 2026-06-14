<!-- TEMPLATE — copy into research/strategies/<id>_<date>_<verdict>/00_BRIEFING.md and fill.
Keep this to one screen of front matter + four short sections. The trade expression MUST map
1:1 to the manifest params. Pre-committed gates are the pre-registration — changing them later
bumps n_trials (anti-gaming). Delete these comments when filling. -->

# <Strategy name> — Briefing

| | |
|---|---|
| **strategy_id** | `<id>` |
| **track** | `etf_rotation` \| `cta_futures` \| `factor_etf` |
| **stage / verdict** | `S0` · `PENDING` |
| **runner** | `alpha_research/backtests/runners/<id>.py` |
| **manifest** | `alpha_research/research/pool/<id>/manifest.yaml` |
| **report** | `02_BACKTEST_REPORT.md` (run_id `<…>`) |
| **headline** | net Sharpe `—` · max DD `—` · vs EW `—` · \|ρ\| vs pool `—` _(filled from 02)_ |
| **owner / researcher** | Zelin / <Elena\|Marco> · created `<YYYY-MM-DD>` |

## 1. Description
<One paragraph: what the strategy does, in plain terms. Asset class, horizon, long-only vs
long/short, what it is betting on.>

## 2. Trade expression
<The exact systematic rule. Signal construction step-by-step; universe; rebalance frequency +
execution convention; sizing/neutralization/caps. Then the parameter table — every value here
must equal the manifest `params`.>

| param | value | rationale |
|---|---|---|
| … | … | … |

## 3. Rationale — why the edge exists, and who is on the other side
<Economic mechanism (risk premium / behavioral / structural-flows). Who loses money to us and
why they must transact. Then the evidence, BOTH sides:>
- **Supporting:** <≥2 papers — author (year, venue): claim.>
- **Contradicting / failure modes:** <≥1 — the strongest reason this fails; how the design answers it.>
- **Decay / crowding:** <post-publication haircut; who already harvests this; capacity at our AUM.>

## 4. Pre-committed kill thresholds (pre-registration — do not relax after seeing results)
<Map each to the 11-gate checklist. Committed BEFORE the backtest.>

| # | kill predicate | maps to |
|---|---|---|
| K1 | … | Gate … |
| … | … | … |
