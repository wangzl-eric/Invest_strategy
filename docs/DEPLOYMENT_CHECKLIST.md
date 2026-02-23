# Strategy Deployment Checklist (Paper → Live)

This checklist is intentionally conservative.

## 1) Data + research validation

- Confirm dataset lineage exists in the metadata DB (see `scripts/init_quant_data_meta_db.py`)
- Re-run the reference backtest(s) from a clean environment (`environment.yml`)
- Walk-forward / out-of-sample evaluation (no lookahead, no survivorship bias)
- Slippage + transaction cost sensitivity

## 2) Risk controls (must-have before live)

- Kill switch available (`KILL_SWITCH=1`)
- Max daily loss limit and behavior on breach (block new orders)
- Max gross notional limit
- Per-symbol max position notional
- Order rate limits and trading-hours rules

## 3) Paper trading phase

- Run in `sim` mode first (`scripts/run_paper_trader.py`)
- Then run against IBKR **paper** account only (once IBKR broker is implemented/validated)
- Verify audit trail in DB:
  - `execution_orders`
  - `execution_fills`
  - `risk_events`

## 4) Live trading enablement (gated)

- Shadow mode: generate live signals, but do not place orders (log only)
- Manual approval step for order placement
- Reduce size to minimum viable risk
- Monitoring/alerts configured and tested (disconnects, rejected orders, daily loss breach)

