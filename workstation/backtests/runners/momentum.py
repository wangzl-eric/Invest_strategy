#!/usr/bin/env python3
"""Example parameterized research experiment: simple momentum signal.

This is intentionally small but end-to-end:
Parquet lake -> DuckDB scan -> feature -> backtest -> MLflow log.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# Add repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import mlflow  # noqa: E402

from workstation.backtests.event_driven.backtest_engine import (  # noqa: E402
    BacktestEngine,
    IBKRDataFeed,
)


@dataclass(frozen=True)
class MomentumParams:
    lookback: int
    holding: int


def compute_momentum_signal(close: pd.Series, lookback: int) -> pd.Series:
    # simple % return over lookback
    return close.pct_change(lookback)


def run_momentum_experiment(
    ticker: str,
    params: MomentumParams,
    start_date: str,
    end_date: str,
) -> dict:
    """Run a single experiment with given parameters."""

    # 1. Load data (stub: replace with DuckDB query)
    # prices = ...
    # For now, generate synthetic data for testing
    dates = pd.date_range(start=start_date, end=end_date, freq="B")
    np.random.seed(42)
    prices = pd.Series(
        100 * np.cumprod(1 + np.random.randn(len(dates)) * 0.02),
        index=dates,
    )

    # 2. Compute signal
    _ = compute_momentum_signal(prices, params.lookback)

    # 3. Backtest using BacktestEngine
    # Prepare data for Backtrader
    bt_data = pd.DataFrame(
        {
            "open": prices,
            "high": prices * 1.01,
            "low": prices * 0.99,
            "close": prices,
            "volume": 1000000,
        },
        index=prices.index,
    )
    bt_data = bt_data.reset_index()
    bt_data.columns = ["date", "open", "high", "low", "close", "volume"]

    # Simple momentum strategy
    class MomentumStrategy:
        name = "momentum"

        def __init__(self, lookback):
            self.lookback = lookback
            self.sma = None

        def generate_positions(self, bars):
            close = bars["close"]
            sma = close.rolling(self.lookback).mean()
            signal = (close > sma).astype(float)
            return signal

    engine = BacktestEngine(cash=100000, commission=0.001)
    engine.add_data(IBKRDataFeed(dataname=bt_data), name=ticker)
    engine.add_strategy(MomentumStrategy, lookback=params.lookback)
    result = engine.run_backtest()

    return {
        "total_return": result["total_return"],
        "sharpe_ratio": result["sharpe_ratio"],
        "max_drawdown": result["max_drawdown"],
        "final_value": result["final_value"],
    }


def run_batch_experiment(
    ticker: str,
    param_grid: list[MomentumParams],
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Run batch of experiments, log to MLflow."""

    # Track experiment in MLflow
    mlflow.set_experiment(f"momentum_{ticker}")

    results = []
    for params in param_grid:
        with mlflow.start_run(
            run_name=f"lookback={params.lookback}_holding={params.holding}"
        ):
            # Log params
            mlflow.log_params(
                {
                    "lookback": params.lookback,
                    "holding": params.holding,
                    "ticker": ticker,
                }
            )

            # Run backtest
            metrics = run_momentum_experiment(ticker, params, start_date, end_date)

            # Log metrics
            mlflow.log_metrics(metrics)

            results.append(
                {"lookback": params.lookback, "holding": params.holding, **metrics}
            )

    return pd.DataFrame(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", default="SPY")
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2023-12-31")
    args = parser.parse_args()

    # Simple grid
    param_grid = [
        MomentumParams(lookback=lookback, holding=holding)
        for lookback in [20, 60, 120]
        for holding in [1, 5, 10]
    ]

    results = run_batch_experiment(args.ticker, param_grid, args.start, args.end)
    print(results.sort_values("sharpe_ratio", ascending=False).to_string(index=False))
