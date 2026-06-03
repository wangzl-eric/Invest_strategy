# Backend

`backend/` is the FastAPI application and broker-facing service layer.

Use this directory for:

- API routes and request/response schemas
- database models and persistence
- IBKR clients, schedulers, alerts, and reporting
- service-layer orchestration used by the dashboard or automation scripts

Do not put reusable research logic here if it can live in `backtests/`, `portfolio/`, `execution/`, or `quant_data/`.
