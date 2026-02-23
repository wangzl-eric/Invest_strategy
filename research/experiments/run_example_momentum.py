#!/usr/bin/env python3
"""Example parameterized research experiment: simple momentum signal.

This is intentionally small but end-to-end:
Parquet lake -> DuckDB scan -> feature -> backtest -> MLflow log.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# Add repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import mlflow

from backtests.core import CostModel, SlippageModel
from backtests.vectorized import VectorizedBacktestConfig, run_vectorized_backtest
from quant_data.duckdb_store import connect, register_parquet_view


@dataclass(frozen=True)
class MomentumParams:
    lookback: int
    holding: int


def compute_momentum_signal(close: pd.Series, lookback: int) -> pd.Series:
    # simple % return over lookback
    return close.pct_change(lookback)


def vectorized_backtest(prices: pd.Series, signal: pd.Series, holding: int) -> pd.Series:
    # Long-only: when signal>0 hold long for `holding` days (simple, illustrative).
    pos = (signal > 0).astype(float)
    pos = pos.shift(1).fillna(0.0)  # trade on next bar
    # crude holding: EMA-style decay is better; keep simple: forward-fill for holding horizon
    pos_h = pos.rolling(holding, min_periods=1).max()
    rets = prices.pct_change().fillna(0.0)
    strat = pos_h * rets
    return strat


def sharpe(daily_returns: pd.Series) -> float:
    if daily_returns.std() == 0 or len(daily_returns) < 2:
        return 0.0
    return float(np.sqrt(252) * daily_returns.mean() / daily_returns.std())


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--parquet_glob", required=True, help="Parquet glob to bars (e.g. data_lake/clean/stooq/bars/us_equities/1d/date=*/symbol=AAPL/part-*.parquet)")
    p.add_argument("--symbol", required=True)
    p.add_argument("--lookback", type=int, default=60)
    p.add_argument("--holding", type=int, default=5)
    p.add_argument("--experiment", default="example_momentum")
    args = p.parse_args()

    mlflow.set_experiment(args.experiment)
    with mlflow.start_run():
        mlflow.log_params({"symbol": args.symbol, "lookback": args.lookback, "holding": args.holding})

        con = connect()
        register_parquet_view(con, view_name="bars", parquet_glob=args.parquet_glob, replace=True)

        df = con.execute(
            "SELECT timestamp, symbol, close FROM bars WHERE symbol = ? ORDER BY timestamp",
            [args.symbol],
        ).df()
        if df.empty:
            raise SystemExit(f"No data found for symbol={args.symbol}")

        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.set_index("timestamp")
        close = df["close"].astype(float)

        # Use shared backtesting stack (so research results match standardized reports)
        df_bt = pd.DataFrame({"timestamp": close.index, "close": close.values})
        df_bt["timestamp"] = pd.to_datetime(df_bt["timestamp"], utc=True)

        class _Strat:
            name = "example_momentum"

            def generate_positions(self, bars: pd.DataFrame) -> pd.Series:
                # holding is applied by the backtester via turnover/cost conventions,
                # so here we generate the raw signal position (0/1).
                px = bars["close"].astype(float)
                sig = compute_momentum_signal(px, args.lookback)
                return (sig > 0).astype(float)

        bt_cfg = VectorizedBacktestConfig(
            shift_positions_by=1,
            cost_model=CostModel(cost_tps=0.0),
            slippage_model=SlippageModel(slippage_bps=0.0),
        )
        bt = run_vectorized_backtest(bars=df_bt, strategy=_Strat(), cfg=bt_cfg, price_col="close")

        total_return = float(bt.stats["total_return"])
        s = float(bt.stats["sharpe"])

        mlflow.log_metrics({"total_return": total_return, "sharpe": s})

        # Persist a small artifact (CSV) for traceability
        out = pd.DataFrame(
            {
                "close": close.reindex(bt.returns.index),
                "position": bt.positions,
                "strategy_ret": bt.returns,
                "equity": bt.equity,
            }
        )
        out_path = Path("artifacts") / f"momentum_{args.symbol}.csv"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out.tail(500).to_csv(out_path)
        mlflow.log_artifact(str(out_path))

        print(f"symbol={args.symbol} total_return={total_return:.2%} sharpe={s:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

