# Cerebro

`cerebro/` is an optional research-ingestion and idea-generation service.

It is separate from the core portfolio analytics path:

- core platform: `backend/`, `frontend/`, `backtests/`, `portfolio/`, `execution/`, `quant_data/`
- optional research service: `cerebro/`

Keep new dependencies on `cerebro/` explicit. Do not assume it is required for routine backtesting or portfolio workflows.
