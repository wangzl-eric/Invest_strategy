<!--
Template for /read-industrial-report digests.
Save as: knowledge/reports/<YYYY>/<MM>/<tag>_<issuer>_<topic>_<YYYY-MM-DD>.md
  where YYYY/MM and the trailing date are the REPORT'S PUBLICATION date (not the read
  date), and <tag> is one of: macro rates economics equities crossasset flows factor event.
  Move the source PDF into the same folder under the same stem (.pdf).
  See "Output location & convention" in SKILL.md for the full rules.
The three numbered sections are MANDATORY and must appear in order; the
"Connection to our platform" and "Commentary — value to our investment learning"
sections that follow them are also mandatory (for the former, one line saying
nothing applies is fine — omitting it is not).
The Commentary carries two INDEPENDENT verdicts — directness (direct|indirect)
and value (useful|limited) — plus why / take / ignore / second read.
"indirect" is not a synonym for "weak". Be willing to write "limited".
Also add a row to knowledge/reports/INDEX.md.
Genuine academic/research-grade papers go to ../papers/ via /read-to-learn instead.
Delete this comment and any unused optional header rows before saving.
Math: $...$ inline / $$...$$ display.
-->

# Report Digest: <Issuer> — <Short Title> (<Year>)

- **Source:** <file path / URL / DOI>
- **Type / issuer:** <sell-side note / consulting report / central-bank note / white paper>
- **Read on:** <YYYY-MM-DD>
- **One-line claim:** <the central finding/forecast/recommendation in one sentence>
- **Decision it changes:** <what a reader does differently if true>
- **Scores (1–5):** Credibility <n> · Relevance <n> · Actionability <n> — <one-line rationale>

## 1. Executive summary
<Flowing prose, 3 to 5 sentences, no bullets, no visible labels — but ordered
deliberately, STAR-wise: Situation+Task sentence(s) (who published it, when, for whom,
and the question/decision it addresses) → Action sentence(s) (the methodology /
analytical approach) → Result sentence(s) (the headline finding/forecast/recommendation
and any stated confidence, hedged to the report's own epistemic status — "GS expects…",
not bare assertion).>

## 2. Methodology & reasoning (PEE blocks + bulleted causal chains — no prose walls)
<One block per independent pillar of the argument (2–4 typical: e.g. a growth pillar, a
policy pillar, a valuation pillar). Never collapse this into a single paragraph.>

- **Point:** <the one-line claim this pillar establishes>
  **Evidence:** <specific number(s)/data/quote — units, period, sample>
  **Chain:** <observation> → <inference> → <inference> → **<conclusion>**
  **Read:** <descriptive or inferential? load-bearing or corroborating? where does it leap?>

- **Point:** <second pillar's claim>
  **Evidence:** <...>
  **Chain:** <...> → <...> → **<...>**
  **Read:** <...>

<Repeat for each remaining pillar.>

**Weakest link:** <one sentence — the single most load-bearing, least-tested assumption
across all pillars>

<Reproduce the load-bearing calculation if the call rests on one, symbols defined:>

$$<equation>$$

<Then: which single input carries the conclusion, and how much the headline moves if
that input is off by a plausible amount.>

## 3. Keywords (5–10)
`<keyword>`, `<keyword>`, `<keyword>`, `<keyword>`, `<keyword>`, `<keyword>`, `<keyword>`

## What to watch (required — 3–5 observables)
<The indicators that would confirm or kill the call, each with its current level and the
threshold/direction that flips the conclusion. Name the FRED series / ticker where one
exists in our data lake, so this is checkable later.>

| Observable | Series | Level now | Confirms if | Breaks if |
|-----------|--------|-----------|-------------|-----------|
| <...> | <FRED id / ticker> | <...> | <...> | <...> |

## Connection to our platform (required)
<One bullet per connection — never a paragraph. Each bullet names the strategy / signal
/ runner / manifest / dataset / note in THIS repo, and states validates / challenges /
could-improve / gap in 1–2 sentences. Flag contradictions explicitly.>

- **<repo anchor, e.g. alpha_research/backtests/runners/... or research/pool/<id>/manifest.yaml>** —
  <validates / challenges / could improve / gap> — <why, 1–2 sentences>
- **<second anchor>** — <...>

<If nothing applies: a single bullet saying so, and score Relevance down accordingly.>
