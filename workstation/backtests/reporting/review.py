"""Standardized backtest review artifacts, QuantStats reports, and optimizer comparisons."""

from __future__ import annotations

import importlib
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

from backtests.run_manager import BacktestRun, RunManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReviewConfig:
    """Control block for a backtest review."""

    rigor_mode: str = "highly-rigorous"
    strategy_archetype: str = "cross_sectional"
    primary_engine: str = "local"
    validation_engines: List[str] = field(default_factory=list)
    report_backend: str = "quantstats"
    optimizer_backend: str = "local"
    data_source: str = ""
    date_coverage: str = ""
    execution_convention: str = ""
    cost_model: str = ""
    benchmark: str = ""
    naive_baseline: str = ""
    hypothesis: str = ""
    engine_confidence: str = "local_only"
    verdict: str = "REVISE"


def _normalize_series(
    data: Optional[pd.Series | pd.DataFrame | Sequence[float]],
    *,
    preferred_columns: Sequence[str] = ("returns", "portfolio_value", "close", "value"),
) -> pd.Series:
    if data is None:
        return pd.Series(dtype=float)
    if isinstance(data, pd.Series):
        series = data.copy()
    elif isinstance(data, pd.DataFrame):
        lower_map = {c.lower(): c for c in data.columns}
        selected = None
        for col in preferred_columns:
            if col in lower_map:
                selected = lower_map[col]
                break
        if selected is None:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                return pd.Series(dtype=float)
            selected = numeric_cols[0]
        series = data[selected].copy()
    else:
        series = pd.Series(data)

    series = pd.to_numeric(series, errors="coerce").dropna()
    if not isinstance(series.index, pd.DatetimeIndex):
        try:
            series.index = pd.to_datetime(series.index)
        except Exception:
            pass
    return series.sort_index()


def load_series_from_file(path: str | Path, column: Optional[str] = None) -> pd.Series:
    """Load a returns-like series from CSV or Parquet."""
    path = Path(path)
    if path.suffix.lower() == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)

    date_column = None
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in ("date", "datetime", "timestamp", "time"):
        if candidate in lower_map:
            date_column = lower_map[candidate]
            break

    if date_column is not None:
        datetime_index = pd.to_datetime(df[date_column], errors="coerce")
        if datetime_index.isna().all():
            raise ValueError(
                f"Could not parse datetime values from column '{date_column}' in {path}"
            )
        df = df.copy()
        df.index = datetime_index
        df = df.drop(columns=[date_column])
    elif not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(
            f"{path} must include a date-like column (date/datetime/timestamp/time) or a DatetimeIndex"
        )

    if column and column in df.columns:
        series = df[column]
        return _normalize_series(series)

    return _normalize_series(df)


def generate_quantstats_tearsheet(
    returns: pd.Series,
    *,
    benchmark_returns: Optional[pd.Series] = None,
    output_html: str | Path,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a QuantStats HTML tear sheet if QuantStats is available."""
    returns = _normalize_series(returns)
    benchmark_returns = _normalize_series(benchmark_returns)
    output_html = Path(output_html)

    if returns.empty:
        return {
            "enabled": True,
            "generated": False,
            "path": str(output_html),
            "error": "daily returns are empty",
        }

    try:
        qs = importlib.import_module("quantstats")
    except Exception as exc:
        return {
            "enabled": True,
            "generated": False,
            "path": str(output_html),
            "error": f"quantstats unavailable: {exc}",
        }

    try:
        output_html.parent.mkdir(parents=True, exist_ok=True)
        qs.reports.html(
            returns,
            benchmark=benchmark_returns if not benchmark_returns.empty else None,
            output=str(output_html),
            title=title or "Backtest Report",
        )
        return {
            "enabled": True,
            "generated": True,
            "path": str(output_html),
            "error": None,
        }
    except Exception as exc:
        logger.warning("QuantStats report generation failed: %s", exc)
        return {
            "enabled": True,
            "generated": False,
            "path": str(output_html),
            "error": str(exc),
        }


def compare_with_pypfopt(
    *,
    expected_return: pd.Series,
    cov: pd.DataFrame,
    local_weights: Optional[pd.Series] = None,
    weight_bounds: tuple[float, float] = (0.0, 1.0),
    objective: str = "max_sharpe",
    risk_free_rate: float = 0.0,
) -> Dict[str, Any]:
    """Compare local optimizer output with PyPortfolioOpt when available."""
    expected_return = _normalize_series(expected_return)
    if expected_return.empty:
        return {
            "enabled": True,
            "available": False,
            "error": "expected returns are empty",
        }

    try:
        mod = importlib.import_module("pypfopt")
        EfficientFrontier = getattr(mod, "EfficientFrontier")
    except Exception as exc:
        return {
            "enabled": True,
            "available": False,
            "error": f"PyPortfolioOpt unavailable: {exc}",
        }

    cov = cov.reindex(
        index=expected_return.index, columns=expected_return.index
    ).astype(float)

    try:
        ef = EfficientFrontier(expected_return, cov, weight_bounds=weight_bounds)
        if objective == "min_volatility":
            weights_dict = ef.min_volatility()
            perf = ef.portfolio_performance(verbose=False)
        else:
            weights_dict = ef.max_sharpe(risk_free_rate=risk_free_rate)
            perf = ef.portfolio_performance(
                verbose=False, risk_free_rate=risk_free_rate
            )

        clean = (
            pd.Series(ef.clean_weights(), dtype=float)
            .reindex(expected_return.index)
            .fillna(0.0)
        )
        local_aligned = (
            local_weights.reindex(expected_return.index).fillna(0.0)
            if local_weights is not None
            else None
        )

        comparison = {
            "enabled": True,
            "available": True,
            "objective": objective,
            "weights": clean.to_dict(),
            "expected_return": float(perf[0]) if perf[0] is not None else None,
            "volatility": float(perf[1]) if perf[1] is not None else None,
            "sharpe_ratio": float(perf[2]) if perf[2] is not None else None,
        }

        if local_aligned is not None:
            diff = clean - local_aligned
            comparison["l1_distance_vs_local"] = float(diff.abs().sum())
            comparison["max_abs_diff_vs_local"] = float(diff.abs().max())

        return comparison
    except Exception as exc:
        logger.warning("PyPortfolioOpt comparison failed: %s", exc)
        return {
            "enabled": True,
            "available": False,
            "error": str(exc),
        }


def build_review_payload(
    *,
    run: BacktestRun,
    review_config: ReviewConfig,
    metrics: Dict[str, Any],
    daily_returns: Optional[pd.Series],
    equity_curve: Optional[pd.DataFrame],
    gate_summary: Optional[Dict[str, Any]] = None,
    key_review_lenses: Optional[List[str]] = None,
    optimizer_comparison: Optional[Dict[str, Any]] = None,
    quantstats_report: Optional[Dict[str, Any]] = None,
    residual_risks: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build a standardized review payload for markdown and JSON artifacts."""
    daily_returns = _normalize_series(daily_returns)
    artifact_status = {
        "metrics": bool(metrics),
        "daily_returns": not daily_returns.empty,
        "equity_curve": equity_curve is not None and not equity_curve.empty,
        "quantstats_report": bool(
            quantstats_report and quantstats_report.get("generated")
        ),
    }

    payload = {
        "control": asdict(review_config),
        "run": {
            "run_id": run.run_id,
            "strategy_name": run.strategy_name,
            "git_commit": run.git_commit,
            "created_at": run.timestamp.isoformat(),
            "params": run.params,
            "description": run.description,
        },
        "metrics": metrics,
        "gate_summary": gate_summary or {},
        "key_review_lenses": key_review_lenses or [],
        "optimizer_comparison": optimizer_comparison or {"status": "not_required"},
        "quantstats_report": quantstats_report or {"enabled": False},
        "artifact_status": artifact_status,
        "residual_risks": residual_risks or [],
        "verdict": review_config.verdict,
    }
    return payload


def render_review_markdown(payload: Dict[str, Any]) -> str:
    """Render a concise markdown review from a standardized payload."""
    control = payload["control"]
    run = payload["run"]
    metrics = payload.get("metrics", {})
    artifact_status = payload.get("artifact_status", {})
    gate_summary = payload.get("gate_summary", {})
    lenses = payload.get("key_review_lenses", [])
    optimizer = payload.get("optimizer_comparison", {})
    quantstats_report = payload.get("quantstats_report", {})
    residual_risks = payload.get("residual_risks", [])

    lines = [
        f"# Backtest Review: {run['strategy_name']}",
        "",
        "## Control Block",
        f"- rigor_mode: `{control['rigor_mode']}`",
        f"- strategy_archetype: `{control['strategy_archetype']}`",
        f"- primary_engine: `{control['primary_engine']}`",
        f"- validation_engines: `{', '.join(control['validation_engines']) if control['validation_engines'] else 'none'}`",
        f"- report_backend: `{control['report_backend']}`",
        f"- optimizer_backend: `{control['optimizer_backend']}`",
        "",
        "## Hypothesis",
        f"- {control.get('hypothesis') or run.get('description') or 'not provided'}",
        "",
        "## Engine Path",
        f"- run_id: `{run['run_id']}`",
        f"- git_commit: `{run['git_commit']}`",
        f"- engine_confidence: `{control['engine_confidence']}`",
        "",
        "## Data and Timing",
        f"- data_source: `{control['data_source'] or 'unspecified'}`",
        f"- date_coverage: `{control['date_coverage'] or 'unspecified'}`",
        "",
        "## Execution Convention",
        f"- execution_convention: `{control['execution_convention'] or 'unspecified'}`",
        f"- cost_model: `{control['cost_model'] or 'unspecified'}`",
        "",
        "## Baseline and Benchmark",
        f"- naive_baseline: `{control['naive_baseline'] or 'unspecified'}`",
        f"- benchmark: `{control['benchmark'] or 'unspecified'}`",
        "",
        "## Metrics",
    ]

    if metrics:
        for key in sorted(metrics):
            lines.append(f"- {key}: `{metrics[key]}`")
    else:
        lines.append("- no metrics saved")

    lines.extend(["", "## Key Review Lenses"])
    if lenses:
        lines.extend([f"- {lens}" for lens in lenses])
    else:
        lines.append("- none provided")

    lines.extend(["", "## Gate Summary"])
    if gate_summary:
        for key in sorted(gate_summary):
            lines.append(f"- {key}: `{gate_summary[key]}`")
    else:
        lines.append("- not provided")

    lines.extend(["", "## Optimizer Comparison"])
    if optimizer.get("status") == "not_required":
        lines.append("- not required")
    elif optimizer.get("available") is False:
        lines.append(f"- unavailable: {optimizer.get('error', 'unknown error')}")
    else:
        if "l1_distance_vs_local" in optimizer:
            lines.append(
                f"- l1_distance_vs_local: `{optimizer['l1_distance_vs_local']:.6f}`"
            )
        if "max_abs_diff_vs_local" in optimizer:
            lines.append(
                f"- max_abs_diff_vs_local: `{optimizer['max_abs_diff_vs_local']:.6f}`"
            )
        if "sharpe_ratio" in optimizer:
            lines.append(f"- pypfopt_sharpe_ratio: `{optimizer['sharpe_ratio']}`")

    lines.extend(["", "## Artifact Status"])
    for key in sorted(artifact_status):
        lines.append(f"- {key}: `{artifact_status[key]}`")

    lines.extend(["", "## QuantStats"])
    if quantstats_report.get("enabled"):
        lines.append(f"- generated: `{quantstats_report.get('generated', False)}`")
        if quantstats_report.get("path"):
            lines.append(f"- path: `{quantstats_report['path']}`")
        if quantstats_report.get("error"):
            lines.append(f"- error: `{quantstats_report['error']}`")
    else:
        lines.append("- disabled")

    lines.extend(["", "## Residual Risks"])
    if residual_risks:
        lines.extend([f"- {risk}" for risk in residual_risks])
    else:
        lines.append("- none recorded")

    lines.extend(["", "## Verdict", f"- `{payload.get('verdict', 'REVISE')}`", ""])
    return "\n".join(lines)


def build_review_bundle_from_run(
    *,
    run_manager: RunManager,
    run_id: str,
    review_config: ReviewConfig,
    benchmark_returns: Optional[pd.Series] = None,
    gate_summary: Optional[Dict[str, Any]] = None,
    key_review_lenses: Optional[List[str]] = None,
    optimizer_comparison: Optional[Dict[str, Any]] = None,
    residual_risks: Optional[List[str]] = None,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """Build and persist a standardized review bundle from a saved run."""
    run = run_manager.load_run(run_id)
    run_dir = run_manager.get_run_dir(run_id)
    daily_returns = run_manager.load_daily_returns(run_id)
    equity_curve = run_manager.load_equity_curve(run_id)

    quantstats_report = {"enabled": False}
    if review_config.report_backend == "quantstats" and daily_returns is not None:
        quantstats_report = generate_quantstats_tearsheet(
            daily_returns,
            benchmark_returns=benchmark_returns,
            output_html=run_dir / "quantstats_report.html",
            title=title or run.strategy_name,
        )

    payload = build_review_payload(
        run=run,
        review_config=review_config,
        metrics=run.metrics,
        daily_returns=daily_returns,
        equity_curve=equity_curve,
        gate_summary=gate_summary,
        key_review_lenses=key_review_lenses,
        optimizer_comparison=optimizer_comparison,
        quantstats_report=quantstats_report,
        residual_risks=residual_risks,
    )
    markdown = render_review_markdown(payload)

    json_path = run_manager.save_json_artifact(
        run_id,
        "review.json",
        payload,
    )
    markdown_path = run_manager.save_text_artifact(
        run_id,
        "review.md",
        markdown,
    )

    return {
        "payload": payload,
        "markdown": markdown,
        "paths": {
            "review_json": str(json_path),
            "review_markdown": str(markdown_path),
            "quantstats_html": quantstats_report.get("path"),
        },
    }
