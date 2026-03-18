"""Backtest run manager for reproducibility and comparison.

Tracks every backtest run with its parameters, git commit, metrics,
and optional equity curve artifacts.  Enables comparing runs across
parameter changes and code versions.

Two workflows are supported:

1. **Two-step** (create then save):
    mgr = RunManager()
    run_cfg = mgr.create_run("momentum_60_21", {"lookback": 60}, "baseline")
    # ... run backtest ...
    mgr.save_results(run_cfg.run_id, metrics_dict, equity_df)

2. **One-step** (save_run):
    run = mgr.save_run(
        strategy_name="momentum_60_21",
        params={"lookback": 60},
        metrics={"sharpe_ratio": 1.2},
    )

Usage:
    from backtests.run_manager import RunManager

    mgr = RunManager()
    runs_df = mgr.list_runs(strategy_name="momentum_60_21")
    comparison = mgr.compare_runs(runs_df["run_id"].tolist()[:3])
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RunConfig:
    """Immutable configuration snapshot created before the backtest runs."""

    run_id: str
    strategy_name: str
    params: Dict[str, Any]
    description: str
    git_commit: str
    random_seed: int
    created_at: str  # ISO-8601
    data_hash: str = ""
    config_path: Optional[str] = None


@dataclass(frozen=True)
class BacktestRun:
    """Immutable record of a completed backtest execution."""

    run_id: str
    timestamp: datetime
    git_commit: str
    strategy_name: str
    params: Dict[str, Any]
    data_hash: str
    random_seed: int
    metrics: Dict[str, float]
    description: str = ""
    config_path: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_git_commit() -> str:
    """Return the current HEAD commit hash, or 'unknown' on failure."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return "unknown"


def _serialize_value(v: Any) -> Any:
    """Make a value JSON-serializable."""
    if isinstance(v, (int, float, str, bool, type(None))):
        return v
    if isinstance(v, datetime):
        return v.isoformat()
    try:
        import numpy as np

        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            return float(v)
        if isinstance(v, np.ndarray):
            return v.tolist()
    except ImportError:
        pass
    return str(v)


def _serialize_structure(value: Any) -> Any:
    """Recursively make nested structures JSON-serializable."""
    if isinstance(value, dict):
        return {str(k): _serialize_structure(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize_structure(v) for v in value]
    return _serialize_value(value)


# ---------------------------------------------------------------------------
# Run Manager
# ---------------------------------------------------------------------------


class RunManager:
    """Track and compare backtest runs for reproducibility.

    Each run is stored in its own directory under ``output_dir/<run_id>/``
    containing:

    - ``config.yaml`` -- parameters, metadata, git commit, description
    - ``metrics.json`` -- performance metrics
    - ``equity_curve.parquet`` -- optional equity curve data

    Args:
        output_dir: Root directory for run artifacts.
    """

    def __init__(self, output_dir: str = "data/backtest_runs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_run_dir(self, run_id: str) -> Path:
        """Return the directory for a run, raising if it does not exist."""
        run_dir = self.output_dir / run_id
        if not run_dir.exists():
            raise FileNotFoundError(f"Run directory not found: {run_dir}")
        return run_dir

    # ------------------------------------------------------------------
    # Two-step workflow: create_run → save_results
    # ------------------------------------------------------------------

    def create_run(
        self,
        strategy_name: str,
        params: Dict[str, Any],
        description: str = "",
        random_seed: int = 42,
        data_hash: str = "",
        config_path: Optional[str] = None,
    ) -> RunConfig:
        """Register a new run and persist its frozen config.

        Returns an immutable RunConfig with the assigned run_id.
        """
        run_id = str(uuid.uuid4())[:8]
        timestamp_str = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        git_commit = _get_git_commit()

        config = RunConfig(
            run_id=run_id,
            strategy_name=strategy_name,
            params=_serialize_structure(params),
            description=description,
            git_commit=git_commit,
            random_seed=random_seed,
            created_at=timestamp_str,
            data_hash=data_hash,
            config_path=config_path,
        )

        run_dir = self.output_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        config_file = run_dir / "config.yaml"
        config_file.write_text(yaml.dump(asdict(config), default_flow_style=False))

        logger.info("Created run %s for strategy '%s'", run_id, strategy_name)
        return config

    def save_results(
        self,
        run_id: str,
        results: Dict[str, Any],
        equity_curve: Optional[pd.DataFrame] = None,
    ) -> Path:
        """Persist backtest results and optional equity curve for a run.

        Args:
            run_id: Run identifier from :meth:`create_run`.
            results: Dict of metric name -> value.
            equity_curve: DataFrame with at least a date and value column.

        Returns:
            Path to the run directory.
        """
        run_dir = self.get_run_dir(run_id)

        metrics_file = run_dir / "metrics.json"
        clean = _serialize_structure(results)
        metrics_file.write_text(json.dumps(clean, indent=2))

        if equity_curve is not None and not equity_curve.empty:
            eq_path = run_dir / "equity_curve.parquet"
            try:
                equity_curve.to_parquet(eq_path, engine="pyarrow")
            except Exception as exc:
                logger.warning("Failed to save equity curve for %s: %s", run_id, exc)

        logger.info("Saved results for run %s", run_id)
        return run_dir

    def save_json_artifact(
        self,
        run_id: str,
        filename: str,
        payload: Dict[str, Any],
    ) -> Path:
        """Persist a JSON artifact inside a run directory."""
        run_dir = self.get_run_dir(run_id)
        path = run_dir / filename
        clean = _serialize_structure(payload)
        path.write_text(json.dumps(clean, indent=2))
        return path

    def save_text_artifact(
        self,
        run_id: str,
        filename: str,
        content: str,
    ) -> Path:
        """Persist a text artifact inside a run directory."""
        run_dir = self.get_run_dir(run_id)
        path = run_dir / filename
        path.write_text(content)
        return path

    # ------------------------------------------------------------------
    # One-step workflow (backward compatible)
    # ------------------------------------------------------------------

    def save_run(
        self,
        strategy_name: str,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        equity_curve: Optional[pd.DataFrame] = None,
        daily_returns: Optional[pd.Series] = None,
        data_hash: str = "",
        seed: int = 42,
        description: str = "",
        config_path: Optional[str] = None,
    ) -> BacktestRun:
        """Save a backtest run and its artifacts in one call.

        Returns:
            Immutable BacktestRun record.
        """
        run_cfg = self.create_run(
            strategy_name=strategy_name,
            params=params,
            description=description,
            random_seed=seed,
            data_hash=data_hash,
            config_path=config_path,
        )

        self.save_results(run_cfg.run_id, metrics, equity_curve)

        # Save daily returns separately if provided
        if daily_returns is not None and len(daily_returns) > 0:
            ret_path = self.output_dir / run_cfg.run_id / "daily_returns.parquet"
            try:
                daily_returns.to_frame("returns").to_parquet(ret_path, engine="pyarrow")
            except Exception as exc:
                logger.warning(
                    "Failed to save daily returns for %s: %s",
                    run_cfg.run_id,
                    exc,
                )

        return BacktestRun(
            run_id=run_cfg.run_id,
            timestamp=datetime.fromisoformat(run_cfg.created_at.rstrip("Z")),
            git_commit=run_cfg.git_commit,
            strategy_name=strategy_name,
            params=run_cfg.params,
            data_hash=data_hash,
            random_seed=seed,
            metrics=metrics,
            description=description,
            config_path=config_path,
        )

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load_run(self, run_id: str) -> BacktestRun:
        """Load a previously saved run by its ID.

        Raises:
            FileNotFoundError: If run directory does not exist.
        """
        run_dir = self.output_dir / run_id

        config_file = run_dir / "config.yaml"
        if not config_file.exists():
            raise FileNotFoundError(f"Run {run_id} not found at {run_dir}")

        config_data = yaml.safe_load(config_file.read_text())

        metrics_file = run_dir / "metrics.json"
        metrics = {}
        if metrics_file.exists():
            metrics = json.loads(metrics_file.read_text())

        ts_raw = config_data.get("timestamp") or config_data.get("created_at", "")
        if isinstance(ts_raw, str):
            ts_raw = ts_raw.rstrip("Z")
            timestamp = datetime.fromisoformat(ts_raw) if ts_raw else datetime.min
        elif isinstance(ts_raw, datetime):
            timestamp = ts_raw
        else:
            timestamp = datetime.min

        return BacktestRun(
            run_id=config_data.get("run_id", run_id),
            timestamp=timestamp,
            git_commit=config_data.get("git_commit", "unknown"),
            strategy_name=config_data.get("strategy_name", ""),
            params=config_data.get("params", {}),
            data_hash=config_data.get("data_hash", ""),
            random_seed=config_data.get("random_seed", 42),
            metrics=metrics,
            description=config_data.get("description", ""),
            config_path=config_data.get("config_path"),
        )

    def load_equity_curve(self, run_id: str) -> Optional[pd.DataFrame]:
        """Load the equity curve for a run, if saved."""
        path = self.output_dir / run_id / "equity_curve.parquet"
        if not path.exists():
            return None
        try:
            return pd.read_parquet(path)
        except Exception as exc:
            logger.warning("Failed to load equity curve for %s: %s", run_id, exc)
            return None

    def load_daily_returns(self, run_id: str) -> Optional[pd.Series]:
        """Load daily returns for a run, if saved."""
        path = self.output_dir / run_id / "daily_returns.parquet"
        if not path.exists():
            return None
        try:
            df = pd.read_parquet(path)
            return df["returns"]
        except Exception as exc:
            logger.warning("Failed to load daily returns for %s: %s", run_id, exc)
            return None

    # ------------------------------------------------------------------
    # List / search
    # ------------------------------------------------------------------

    def list_runs(
        self,
        strategy_name: Optional[str] = None,
        since: Optional[str] = None,
        limit: int = 50,
    ) -> pd.DataFrame:
        """List recent backtest runs as a DataFrame, newest first.

        Args:
            strategy_name: Filter by strategy name. None = all.
            since: ISO-8601 cutoff -- only runs created at or after this.
            limit: Maximum number of runs to return.

        Returns:
            DataFrame with columns: run_id, strategy_name, description,
            git_commit, random_seed, created_at, plus any scalar metrics.
        """
        rows: List[Dict[str, Any]] = []

        if not self.output_dir.exists():
            return pd.DataFrame(
                columns=[
                    "run_id",
                    "strategy_name",
                    "description",
                    "git_commit",
                    "created_at",
                    "has_results",
                ]
            )

        for run_dir in self.output_dir.iterdir():
            if not run_dir.is_dir():
                continue
            config_file = run_dir / "config.yaml"
            if not config_file.exists():
                continue

            try:
                run = self.load_run(run_dir.name)
            except Exception as exc:
                logger.debug("Skipping corrupt run %s: %s", run_dir.name, exc)
                continue

            if strategy_name is not None and run.strategy_name != strategy_name:
                continue

            created_at = run.timestamp.isoformat()
            if since is not None and created_at < since:
                continue

            has_results = (run_dir / "metrics.json").exists()
            row: Dict[str, Any] = {
                "run_id": run.run_id,
                "strategy_name": run.strategy_name,
                "description": run.description,
                "git_commit": run.git_commit,
                "random_seed": run.random_seed,
                "created_at": created_at,
                "has_results": has_results,
            }
            # Include scalar metrics
            for k, v in run.metrics.items():
                if isinstance(v, (int, float)):
                    row[k] = v
            rows.append(row)

        df = pd.DataFrame(rows)
        if not df.empty and "created_at" in df.columns:
            df = df.sort_values("created_at", ascending=False).reset_index(drop=True)
            df = df.head(limit)
        return df

    # ------------------------------------------------------------------
    # Compare
    # ------------------------------------------------------------------

    def compare_runs(self, run_ids: List[str]) -> pd.DataFrame:
        """Build a comparison table across multiple runs.

        Args:
            run_ids: List of run IDs to compare.

        Returns:
            DataFrame indexed by run_id with columns for strategy,
            params, and all metric keys.
        """
        rows: List[Dict[str, Any]] = []

        for rid in run_ids:
            try:
                run = self.load_run(rid)
            except FileNotFoundError:
                logger.warning("Run %s not found, skipping", rid)
                continue

            row: Dict[str, Any] = {
                "run_id": run.run_id,
                "strategy": run.strategy_name,
                "description": run.description,
                "timestamp": run.timestamp,
                "git_commit": run.git_commit,
                "seed": run.random_seed,
            }

            # Flatten params with prefix
            for k, v in run.params.items():
                row[f"param_{k}"] = v

            # Add metrics
            row.update(run.metrics)
            rows.append(row)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        if "run_id" in df.columns:
            df = df.set_index("run_id")

        return df

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_run(self, run_id: str) -> bool:
        """Delete a run and its artifacts.

        Returns True if the run was found and deleted.
        """
        run_dir = self.output_dir / run_id
        if not run_dir.exists():
            return False

        shutil.rmtree(run_dir)
        logger.info("Deleted run %s", run_id)
        return True


__all__ = ["BacktestRun", "RunConfig", "RunManager"]
