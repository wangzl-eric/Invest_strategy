#!/usr/bin/env python3
"""Paper trading runner (SIM broker by default).

This is a safe starting point:
- Use SIM broker (no IBKR orders)
- Enforce conservative risk limits
- Record orders/fills/risk events into ibkr_analytics.db

Example:
  PYTHONPATH="$(pwd)" python scripts/run_paper_trader.py --orders "AAPL:BUY:10,MSFT:SELL:5" --prices "AAPL=190,MSFT=410"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.runner import ExecutionRunner, RunnerConfig
from execution.sim_broker import SimBrokerImpl, SimMarket
from execution.types import OrderRequest


def parse_orders(s: str) -> list[OrderRequest]:
    # "AAPL:BUY:10,MSFT:SELL:5"
    orders: list[OrderRequest] = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        sym, side, qty = part.split(":")
        orders.append(OrderRequest(symbol=sym.strip().upper(), side=side.strip().upper(), quantity=float(qty)))
    return orders


def parse_prices(s: str) -> dict[str, float]:
    # "AAPL=190,MSFT=410"
    out: dict[str, float] = {}
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        k, v = part.split("=")
        out[k.strip().upper()] = float(v)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--orders", required=True, help="Comma-separated orders: SYM:BUY|SELL:QTY")
    p.add_argument("--prices", required=True, help="Comma-separated prices: SYM=PX")
    args = p.parse_args()

    prices = parse_prices(args.prices)
    market = SimMarket(last_prices=prices)
    broker = SimBrokerImpl(market)

    runner = ExecutionRunner(broker=broker, price_getter=lambda sym: market.get_price(sym) or 0.0, cfg=RunnerConfig(mode="sim"))
    runner.submit_orders(parse_orders(args.orders))
    runner.poll_and_record_fills()
    print("Submitted orders and recorded fills to DB.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

