"""Parallel backtesting via ProcessPoolExecutor.

Run parameter sweeps and strategy comparisons across multiple CPU cores
without shared mutable state.

Usage:
    from backtests.parallel import ParallelBacktester

    pb = ParallelBacktester(n_workers=4)
    results = pb.run_parameter_sweep(
        param_grid={"lookback": [20, 40, 60], "threshold": [0.0, 0.01]},
        data=price_df,
        strategy_factory=my_strategy_fn,
    )
"""

from __future__ import annotations

import logging
import os
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level worker functions (must be picklable — no lambdas/closures)
# ---------------------------------------------------------------------------


def _run_single_backtest(args: Tuple) -> Dict[str, Any]:
    """Execute one backtest in a worker process.

    Args:
        args: Tuple of (params_dict, data_bytes, strategy_factory, metric).
              data_bytes is a Parquet-serialized DataFrame to avoid large
              pickle overhead.

    Returns:
        Dict with 'params', 'metrics', and 'error' keys.
    """
    import io

    params, data_bytes, strategy_factory, metric = args

    try:
        data = pd.read_parquet(io.BytesIO(data_bytes))
        result = strategy_factory(params, data)

        if not isinstance(result, dict):
            return {
                "params": params,
                "metrics": {},
                "error": "strategy_factory must return a dict of metrics",
            }

        return {"params": params, "metrics": result, "error": None}

    except Exception as exc:
        return {
            "params": params,
            "metrics": {},
            "error": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
        }


def _run_named_strategy(args: Tuple) -> Dict[str, Any]:
    """Execute a named strategy in a worker process.

    Args:
        args: Tuple of (strategy_name, data_bytes, strategy_factory).

    Returns:
        Dict with 'strategy', 'metrics', and 'error' keys.
    """
    import io

    strategy_name, data_bytes, strategy_factory = args

    try:
        data = pd.read_parquet(io.BytesIO(data_bytes))
        result = strategy_factory(data)

        if not isinstance(result, dict):
            return {
                "strategy": strategy_name,
                "metrics": {},
                "error": "strategy callable must return a dict of metrics",
            }

        return {"strategy": strategy_name, "metrics": result, "error": None}

    except Exception as exc:
        return {
            "strategy": strategy_name,
            "metrics": {},
            "error": f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _serialize_dataframe(data: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to Parquet bytes for inter-process transfer."""
    import io

    buf = io.BytesIO()
    data.to_parquet(buf, engine="pyarrow")
    return buf.getvalue()


def _build_param_combos(param_grid: Dict[str, List]) -> List[Dict[str, Any]]:
    """Expand a parameter grid into a list of individual param dicts."""
    keys = list(param_grid.keys())
    values = list(param_grid.values())
    return [dict(zip(keys, combo)) for combo in product(*values)]


class ParallelBacktester:
    """Run multiple backtests in parallel using ProcessPoolExecutor.

    Workers receive serialized copies of data (no shared state).

    Args:
        n_workers: Max number of parallel worker processes.
                   Clamped to os.cpu_count().
    """

    def __init__(self, n_workers: int = 4):
        cpu_count = os.cpu_count() or 4
        self.n_workers = max(1, min(n_workers, cpu_count))

    def run_parameter_sweep(
        self,
        param_grid: Dict[str, List],
        data: pd.DataFrame,
        strategy_factory: Callable[[Dict[str, Any], pd.DataFrame], Dict[str, float]],
        metric: str = "sharpe_ratio",
    ) -> pd.DataFrame:
        """Run backtests across a parameter grid in parallel.

        Args:
            param_grid: Dict of parameter name -> list of values.
            data: Price DataFrame shared across all runs.
            strategy_factory: Module-level function ``(params, data) -> metrics_dict``.
                Must be picklable (no lambdas or closures).
            metric: Metric name used for sorting the results.

        Returns:
            DataFrame with one row per param combo.  Columns include every
            param key, every metric key, and an ``error`` column.
        """
        combos = _build_param_combos(param_grid)
        if not combos:
            return pd.DataFrame()

        data_bytes = _serialize_dataframe(data)
        tasks = [(combo, data_bytes, strategy_factory, metric) for combo in combos]

        logger.info(
            "Starting parameter sweep: %d combos across %d workers",
            len(tasks),
            self.n_workers,
        )

        raw_results = self._execute_tasks(_run_single_backtest, tasks)

        # Flatten into rows
        rows: List[Dict[str, Any]] = []
        for res in raw_results:
            row = {**res["params"], **res["metrics"]}
            row["error"] = res["error"]
            rows.append(row)

        df = pd.DataFrame(rows)

        # Sort by metric descending (errors sink to bottom)
        if metric in df.columns:
            df = df.sort_values(metric, ascending=False, na_position="last")
            df = df.reset_index(drop=True)

        return df

    def run_strategy_comparison(
        self,
        strategies: Dict[str, Callable[[pd.DataFrame], Dict[str, float]]],
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        """Run multiple strategies on the same data in parallel.

        Args:
            strategies: Dict of strategy_name -> callable(data) -> metrics_dict.
                Each callable must be picklable.
            data: Shared price DataFrame.

        Returns:
            DataFrame with strategy names as index and metric columns.
        """
        if not strategies:
            return pd.DataFrame()

        data_bytes = _serialize_dataframe(data)
        tasks = [(name, data_bytes, factory) for name, factory in strategies.items()]

        logger.info(
            "Comparing %d strategies across %d workers",
            len(tasks),
            self.n_workers,
        )

        raw_results = self._execute_tasks(_run_named_strategy, tasks)

        rows: List[Dict[str, Any]] = []
        for res in raw_results:
            row = {"strategy": res["strategy"], **res["metrics"]}
            row["error"] = res["error"]
            rows.append(row)

        df = pd.DataFrame(rows)
        if "strategy" in df.columns and not df.empty:
            df = df.set_index("strategy")

        return df

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _execute_tasks(
        self,
        worker_fn: Callable,
        tasks: List[Tuple],
    ) -> List[Dict[str, Any]]:
        """Submit tasks to the process pool and collect results."""
        results: List[Dict[str, Any]] = []

        with ProcessPoolExecutor(max_workers=self.n_workers) as pool:
            future_to_idx = {
                pool.submit(worker_fn, task): i for i, task in enumerate(tasks)
            }

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    # Pool-level failure (e.g. worker crash)
                    logger.error("Worker %d crashed: %s", idx, exc)
                    results.append(
                        {
                            "params": {},
                            "strategy": f"worker_{idx}",
                            "metrics": {},
                            "error": f"WorkerCrash: {exc}",
                        }
                    )

        return results


__all__ = [
    "ParallelBacktester",
    "_run_single_backtest",
    "_run_named_strategy",
]
