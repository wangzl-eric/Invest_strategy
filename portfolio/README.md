# Portfolio

`portfolio/` contains allocation logic that sits between alpha generation and order execution.

Use this directory for:

- signal blending
- optimization and risk models
- rebalancing logic
- portfolio-level analytics

It is a shared library, not an app. Keep transport concerns in `backend/` and raw signal research in `backtests/`.
