# Field Reference (retired taxonomy)

> **RETIRED 2026-08-18.** The `fields/` taxonomy was never populated — nine field READMEs and two
> empty study indexes, no content in four months. Topic organisation now lives where the content is:
> concept `domain:` frontmatter in [`brain/concepts/`](brain/concepts/) and the six mechanism families
> in [`reports/IDEAS.md`](reports/IDEAS.md#how-the-pool-interconnects). A taxonomy imposed ahead of
> content is a guess about what you will learn; a taxonomy derived from atoms is a description of what
> you did learn. Kept for reference; do not file new work here.


**Purpose:** Organize personal research and exploration by field/topic to maintain clear boundaries and context.

## What remains

```
knowledge/fields/
├── fields_manifest.json      # machine-readable field list (retired, unused by code)
├── volatility/README.md      # ← only READMEs remain: key questions + data sources
├── momentum/README.md
├── carry/README.md
├── macro/README.md
├── correlation/README.md
├── options/README.md
├── fx/README.md
├── crypto/README.md
└── portfolio/README.md
```

The per-field `notebooks/`, `studies/`, `data/`, and `agents/` folders were removed on
2026-09-04 — they held nothing in the five months after they were created.

## Available Fields

### 1. Volatility (`fields/volatility/`)
- VIX analysis and regime detection
- Realized vs implied volatility
- Volatility risk premium studies
- Vol surface analysis
- GARCH modeling

### 2. Momentum (`fields/momentum/`)
- Price momentum signals
- Cross-sectional momentum
- Time-series momentum
- Momentum crashes
- Factor timing

### 3. Carry (`fields/carry/`)
- FX carry strategies
- Commodity carry
- Yield curve positioning
- Roll yield analysis

### 4. Macro (`fields/macro/`)
- Economic regime identification
- Macro indicators (PMI, CPI, etc.)
- Central bank policy analysis
- Business cycle positioning
- Recession indicators

### 5. Correlation (`fields/correlation/`)
- Cross-asset correlation
- Correlation breakdowns
- Diversification analysis
- Regime-dependent correlations

### 6. Options (`fields/options/`)
- Options pricing
- Greeks analysis
- Volatility trading
- Skew and term structure

### 7. FX (`fields/fx/`)
- Currency pairs analysis
- FX carry and momentum
- Central bank divergence
- Real exchange rates

### 8. Crypto (`fields/crypto/`)
- Cryptocurrency analysis
- Crypto-equity correlation
- On-chain metrics
- Crypto momentum

### 9. Portfolio (`fields/portfolio/`)
- Asset allocation
- Risk parity
- Mean-variance optimization
- Rebalancing strategies
- Portfolio construction experiments


## Where the work goes instead

| What you are doing | Where it goes |
|---|---|
| Your own investigation | `knowledge/studies/<YYYY-MM-DD>_<topic>/` (template: `studies/TEMPLATE.md`) |
| A claim that survived it | `knowledge/brain/` — concepts carry `domain:` frontmatter |
| An idea queued for rigor | `knowledge/reports/IDEAS.md` — grouped by mechanism family |
| A promotable strategy | `alpha_research/` — manifest → review → pool |

Reference layout for a study: `knowledge/studies/2026-06-24_volatility_workstation/`.

## Why this was retired

A taxonomy imposed ahead of content is a guess about what you will learn; a taxonomy
derived from atoms is a description of what you did learn. Nine fields were declared up
front and none filled, while the one real study spanned four of them at once
(volatility, macro liquidity, gold, FX) and would not have fitted in any single bucket.
Topic structure now emerges from `domain:` frontmatter on concepts and from the
mechanism families in `IDEAS.md`.
