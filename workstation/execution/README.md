# Execution

`execution/` contains the order-handling path shared by paper trading and future live trading.

Use this directory for:

- order request and fill types
- broker abstractions
- pre-trade risk checks
- execution runners and audit trail logic

This package is downstream of research. It should not own signal-generation or dataset-ingestion code.
