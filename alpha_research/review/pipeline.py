"""One-call review pipeline: manifest -> rigor battery -> artifacts -> pool.

``run_review`` is the single supported path from a strategy manifest to a
strategy-pool entry. Data loaders are injectable so the full pipeline runs
offline in tests; the defaults use ``quant_data.api.get_data`` (local
Parquet first, API fallback, PIT-shifted macro).

Artifact set per run (under ``data/backtest_runs/<run_id>/``):

    config.yaml             frozen run config (RunManager)
    manifest_snapshot.yaml  manifest as reviewed
    qc_report.json          data QC preflight
    metrics.json            primary backtest metrics (RunManager)
    daily_returns.parquet   net daily returns
    equity_curve.parquet    equity curve
    stats_battery.json      PSR/DSR/MinBTL/CI/segments/regime stats
    sensitivity.json        cost (1x/2x/3x) and parameter (+/-20/40%) grids
    correlations.json       pairwise correlation vs active pool strategies
    gates.json              promotion-gate evaluation
    verdict.md              human-readable verdict summary
    review.json / review.md / quantstats_report.html  (reporting layer)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

from alpha_research.backtests.reporting.review import (
    ReviewConfig,
    build_review_bundle_from_run,
)
from alpha_research.backtests.run_manager import RunManager
from alpha_research.backtests.stats import (
    correlation_with_existing,
    deflated_sharpe_ratio,
    minimum_backtest_length,
    probabilistic_sharpe_ratio,
    regime_conditional_sharpe,
    sharpe_confidence_interval,
)
from alpha_research.backtests.strategies.manifest import StrategyManifest, load_manifest
from alpha_research.pool.registry import PoolRegistry
from alpha_research.quant_data.qc import run_price_qc
from alpha_research.review.engine import (
    BacktestResult,
    equal_weight_baseline,
    run_weights_backtest,
)

logger = logging.getLogger(__name__)

COST_MULTIPLIERS = (1.0, 2.0, 3.0)
PARAM_SCALES = (0.6, 0.8, 1.2, 1.4)
N_WALKFORWARD_SEGMENTS = 4

PriceLoader = Callable[[List[str], str, str], pd.DataFrame]
MacroLoader = Callable[[List[str], str, str, pd.DatetimeIndex], Dict[str, pd.Series]]


# ---------------------------------------------------------------------------
# Default data loaders (quant_data.api; local Parquet first)
# ---------------------------------------------------------------------------


def default_price_loader(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    """Wide close-price frame via the unified data interface."""
    from alpha_research.quant_data.api import get_data

    raw = get_data(tickers, start=start, end=end)
    if raw.empty or "ticker" not in raw.columns:
        return pd.DataFrame()
    wide = raw.pivot_table(index="date", columns="ticker", values="close")
    wide.index = pd.to_datetime(wide.index)
    return wide.sort_index()


def default_macro_loader(
    series_ids: List[str], start: str, end: str, index: pd.DatetimeIndex
) -> Dict[str, pd.Series]:
    """PIT-shifted macro series aligned to the price calendar (as-of ffill)."""
    from alpha_research.quant_data.api import get_data
    from alpha_research.quant_data.pit import as_of_series

    if not series_ids:
        return {}
    raw = get_data(series_ids, start=start, end=end, source="fred", pit=True)
    if raw.empty:
        return {}
    return {sid: as_of_series(raw, sid, index) for sid in series_ids}


# ---------------------------------------------------------------------------
# Battery pieces
# ---------------------------------------------------------------------------


def _stats_battery(
    returns: pd.Series, manifest: StrategyManifest, sharpe: float
) -> Dict[str, Any]:
    arr = returns.to_numpy(dtype=float)
    psr = float(probabilistic_sharpe_ratio(arr, benchmark_sharpe=0.0))
    dsr = float(deflated_sharpe_ratio(arr, n_trials=manifest.n_trials))
    try:
        ci_low, _, ci_high = sharpe_confidence_interval(arr)
    except Exception:
        ci_low, ci_high = float("nan"), float("nan")
    min_len = int(minimum_backtest_length(sharpe, n_trials=manifest.n_trials))

    # Walk-forward segment consistency: contiguous folds, per-fold Sharpe.
    segments = []
    folds = np.array_split(np.arange(len(returns)), N_WALKFORWARD_SEGMENTS)
    for i, idx in enumerate(folds):
        seg = returns.iloc[idx]
        seg_sharpe = (
            float(seg.mean() / seg.std() * np.sqrt(252)) if seg.std() > 0 else 0.0
        )
        segments.append(
            {
                "segment": i + 1,
                "start": str(seg.index.min().date()),
                "end": str(seg.index.max().date()),
                "sharpe": seg_sharpe,
            }
        )
    positive_segments = sum(1 for s in segments if s["sharpe"] > 0)

    # Regime-conditional Sharpe: trailing-63d realized-vol terciles of the
    # strategy's own returns (no external data dependency).
    try:
        trailing_vol = returns.rolling(63).std() * np.sqrt(252)
        labels = pd.qcut(
            trailing_vol,
            3,
            labels=["low_vol", "mid_vol", "high_vol"],
            duplicates="drop",
        )
        labels = labels[labels.notna()].astype(str)
        regime = regime_conditional_sharpe(returns, labels)
    except Exception:  # near-constant vol (synthetic/short samples)
        regime = {}

    return {
        "psr": psr,
        "dsr": dsr,
        "n_trials_declared": manifest.n_trials,
        "sharpe_ci_95": [float(ci_low), float(ci_high)],
        "min_backtest_length_days": min_len,
        "n_days": int(len(returns)),
        "minbtl_satisfied": bool(len(returns) >= min_len),
        "walkforward_segments": segments,
        "walkforward_positive_segments": positive_segments,
        "regime_conditional_sharpe": {str(k): float(v) for k, v in regime.items()},
    }


def _cost_sensitivity(
    weights: pd.DataFrame, prices: pd.DataFrame, manifest: StrategyManifest
) -> List[Dict[str, float]]:
    rows = []
    for mult in COST_MULTIPLIERS:
        res = run_weights_backtest(
            weights,
            prices,
            cost_bps=manifest.cost_model.bps * mult,
            shift_bars=manifest.rebalance.execution_convention.shift_bars,
        )
        rows.append(
            {
                "cost_multiplier": mult,
                "cost_bps": manifest.cost_model.bps * mult,
                "sharpe_ratio": res.metrics["sharpe_ratio"],
                "annualized_return": res.metrics["annualized_return"],
            }
        )
    return rows


def _param_sensitivity(
    weights_fn: Callable,
    prices: pd.DataFrame,
    macro: Optional[Dict[str, pd.Series]],
    manifest: StrategyManifest,
) -> List[Dict[str, Any]]:
    """Re-run the strategy with each numeric param scaled +/-20% and +/-40%."""
    rows: List[Dict[str, Any]] = []
    numeric_params = {
        k: v
        for k, v in manifest.params.items()
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    }
    for pname, pval in numeric_params.items():
        for scale in PARAM_SCALES:
            scaled = type(pval)(pval * scale) if isinstance(pval, int) else pval * scale
            params = dict(manifest.params)
            params[pname] = scaled
            row: Dict[str, Any] = {
                "param": pname,
                "scale": scale,
                "value": scaled,
            }
            try:
                w = weights_fn(prices, macro, params)
                res = run_weights_backtest(
                    w,
                    prices,
                    cost_bps=manifest.cost_model.bps,
                    shift_bars=manifest.rebalance.execution_convention.shift_bars,
                )
                row["sharpe_ratio"] = res.metrics["sharpe_ratio"]
            except Exception as exc:  # record, don't abort the battery
                row["error"] = str(exc)
            rows.append(row)
    return rows


def _pool_correlations(
    returns: pd.Series,
    strategy_id: str,
    run_manager: RunManager,
    pool: PoolRegistry,
) -> Dict[str, Any]:
    """Pairwise correlation of the candidate vs every active pool strategy."""
    existing: Dict[str, pd.Series] = {}
    try:
        entries = pool.list_entries(active_only=True)
    except Exception as exc:
        logger.warning("Pool unavailable for correlation check: %s", exc)
        return {"available": False, "error": str(exc)}

    if not entries.empty:
        for _, row in entries.iterrows():
            if row["strategy_id"] == strategy_id or not row["latest_run_id"]:
                continue
            other = run_manager.load_daily_returns(row["latest_run_id"])
            if other is not None and len(other) >= 60:
                existing[row["strategy_id"]] = other

    if not existing:
        return {"available": True, "n_existing": 0, "max_abs_correlation": None}

    corr = correlation_with_existing(returns, existing)
    new_corr = corr["new_strategy"].drop(labels=["new_strategy"], errors="ignore")
    new_corr = new_corr.dropna()
    return {
        "available": True,
        "n_existing": len(existing),
        "pairwise": {k: float(v) for k, v in new_corr.items()},
        "max_abs_correlation": float(new_corr.abs().max()) if len(new_corr) else None,
    }


def _evaluate_gates(
    manifest: StrategyManifest,
    battery: Dict[str, Any],
    cost_rows: List[Dict[str, float]],
    correlations: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate candidate->paper gates against pre-committed promotion rules."""
    rules = manifest.promotion_rules
    gates: Dict[str, Any] = {}

    gates["psr"] = {
        "value": battery["psr"],
        "threshold": rules.min_psr,
        "passed": battery["psr"] >= rules.min_psr,
    }
    gates["dsr"] = {
        "value": battery["dsr"],
        "threshold": rules.min_dsr,
        "passed": battery["dsr"] >= rules.min_dsr,
    }
    gates["minbtl"] = {
        "value": battery["n_days"],
        "threshold": battery["min_backtest_length_days"],
        "passed": battery["minbtl_satisfied"],
    }

    # Cost survival: Sharpe must stay positive at the survival multiplier.
    survival_rows = [
        r for r in cost_rows if r["cost_multiplier"] >= rules.cost_multiplier_survival
    ]
    survival_row = min(
        survival_rows, key=lambda r: r["cost_multiplier"], default=cost_rows[-1]
    )
    gates["cost_survival"] = {
        "value": survival_row["sharpe_ratio"],
        "at_multiplier": survival_row["cost_multiplier"],
        "threshold": 0.0,
        "passed": survival_row["sharpe_ratio"] > 0.0,
    }

    max_corr = correlations.get("max_abs_correlation")
    gates["correlation"] = {
        "value": max_corr,
        "threshold": rules.max_abs_correlation,
        "passed": True if max_corr is None else max_corr <= rules.max_abs_correlation,
        "note": "no active pool strategies to compare" if max_corr is None else "",
    }

    all_passed = all(g["passed"] for g in gates.values())
    return {
        "gates": gates,
        "all_passed": all_passed,
        "verdict": "PASS" if all_passed else "REVISE",
    }


def _verdict_markdown(
    manifest: StrategyManifest,
    run_id: str,
    metrics: Dict[str, float],
    baseline_metrics: Dict[str, float],
    gate_result: Dict[str, Any],
) -> str:
    lines = [
        f"# Verdict: {manifest.strategy_id} — {gate_result['verdict']}",
        "",
        f"- run_id: `{run_id}`",
        f"- track: `{manifest.track.value}`",
        f"- sharpe (net, 1x costs): `{metrics['sharpe_ratio']:.3f}`",
        f"- equal-weight baseline sharpe: `{baseline_metrics['sharpe_ratio']:.3f}`",
        f"- max drawdown: `{metrics['max_drawdown']:.1%}`",
        f"- annual turnover: `{metrics['annual_turnover']:.1f}x`",
        "",
        "## Gates (candidate → paper, pre-committed in manifest)",
        "",
        "| gate | value | threshold | passed |",
        "|------|-------|-----------|--------|",
    ]
    for name, g in gate_result["gates"].items():
        value = g["value"]
        value_s = f"{value:.3f}" if isinstance(value, float) else str(value)
        lines.append(
            f"| {name} | {value_s} | {g['threshold']} | "
            f"{'✅' if g['passed'] else '❌'} |"
        )
    lines += [
        "",
        "_PASS means the rigor gates are satisfied; promotion to paper remains "
        "a human decision (`python -m alpha_research.pool promote ...`)._",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def run_review(
    manifest_or_path: StrategyManifest | str | Path,
    *,
    output_dir: str = "data/backtest_runs",
    price_loader: Optional[PriceLoader] = None,
    macro_loader: Optional[MacroLoader] = None,
    pool: Optional[PoolRegistry] = None,
    force: bool = False,
    tearsheet: bool = True,
    register: bool = True,
) -> Dict[str, Any]:
    """Run the full rigor battery for one manifest and register the result.

    Args:
        manifest_or_path: A loaded ``StrategyManifest`` or a path to its YAML.
        output_dir: RunManager root for run artifacts.
        price_loader / macro_loader: Injectable data loaders (tests pass
            synthetic frames; defaults hit the local lake / APIs).
        pool: Injectable ``PoolRegistry`` (tests pass one bound to an
            in-memory session).
        force: Proceed past a failing data QC report.
        tearsheet: Generate the QuantStats HTML report.
        register: Register/refresh the pool entry and attach the run.

    Returns:
        Dict with ``run_id``, ``verdict``, ``metrics``, ``gate_result``,
        ``artifacts`` (paths), and ``qc_status``.
    """
    if isinstance(manifest_or_path, (str, Path)):
        manifest = load_manifest(manifest_or_path)
        manifest_path = str(manifest_or_path)
    else:
        manifest = manifest_or_path
        manifest_path = manifest.proposal_path or f"<in-memory:{manifest.strategy_id}>"

    price_loader = price_loader or default_price_loader
    macro_loader = macro_loader or default_macro_loader
    pool = pool or PoolRegistry()
    run_manager = RunManager(output_dir=output_dir)

    start = manifest.backtest_start or "2010-01-01"
    end = manifest.backtest_end or str(pd.Timestamp.today().date())

    # ------------------------------------------------------------------
    # 1. Data
    # ------------------------------------------------------------------
    price_tickers = list(manifest.universe)
    if manifest.benchmark and manifest.benchmark not in price_tickers:
        price_tickers.append(manifest.benchmark)
    prices = price_loader(price_tickers, start, end)
    if prices is None or prices.empty:
        raise RuntimeError(f"price loader returned no data for {price_tickers}")

    macro_ids = [r.id for r in manifest.data_requirements if r.kind == "macro"]
    macro = macro_loader(macro_ids, start, end, prices.index) if macro_ids else None

    # ------------------------------------------------------------------
    # 2. QC preflight
    # ------------------------------------------------------------------
    qc_report = run_price_qc(
        prices, start=str(prices.index.min().date()), end=str(prices.index.max().date())
    )
    if qc_report.failed and not force:
        raise RuntimeError(
            "Data QC failed — fix the data or pass force=True.\n" + qc_report.summary()
        )

    # ------------------------------------------------------------------
    # 3. Strategy weights (the contract) + primary backtest
    # ------------------------------------------------------------------
    weights_fn = manifest.resolve_entrypoint()
    universe_prices = prices[[t for t in manifest.universe if t in prices.columns]]
    weights = weights_fn(universe_prices, macro, dict(manifest.params))
    _validate_weights(weights, manifest)

    shift = manifest.rebalance.execution_convention.shift_bars
    primary: BacktestResult = run_weights_backtest(
        weights, universe_prices, cost_bps=manifest.cost_model.bps, shift_bars=shift
    )
    baseline = equal_weight_baseline(
        universe_prices,
        rebalance=manifest.rebalance.frequency,
        cost_bps=manifest.cost_model.bps,
        shift_bars=shift,
    )

    # ------------------------------------------------------------------
    # 4. Battery
    # ------------------------------------------------------------------
    battery = _stats_battery(
        primary.daily_returns, manifest, primary.metrics["sharpe_ratio"]
    )
    cost_rows = _cost_sensitivity(weights, universe_prices, manifest)
    param_rows = _param_sensitivity(weights_fn, universe_prices, macro, manifest)
    correlations = _pool_correlations(
        primary.daily_returns, manifest.strategy_id, run_manager, pool
    )
    gate_result = _evaluate_gates(manifest, battery, cost_rows, correlations)

    # ------------------------------------------------------------------
    # 5. Artifacts under a run_id
    # ------------------------------------------------------------------
    run_cfg = run_manager.create_run(
        strategy_name=manifest.strategy_id,
        params=dict(manifest.params),
        description=manifest.description or manifest.name,
        config_path=manifest_path,
    )
    run_id = run_cfg.run_id

    metrics = dict(primary.metrics)
    metrics["baseline_sharpe_ratio"] = baseline.metrics["sharpe_ratio"]
    metrics["sharpe_vs_baseline"] = (
        metrics["sharpe_ratio"] - baseline.metrics["sharpe_ratio"]
    )
    run_manager.save_results(run_id, metrics, primary.equity_curve)
    run_dir = run_manager.get_run_dir(run_id)
    primary.daily_returns.to_frame("returns").to_parquet(
        run_dir / "daily_returns.parquet", engine="pyarrow"
    )

    run_manager.save_text_artifact(run_id, "manifest_snapshot.yaml", manifest.to_yaml())
    run_manager.save_json_artifact(run_id, "qc_report.json", qc_report.to_dict())
    run_manager.save_json_artifact(run_id, "stats_battery.json", battery)
    run_manager.save_json_artifact(
        run_id, "sensitivity.json", {"cost": cost_rows, "params": param_rows}
    )
    run_manager.save_json_artifact(run_id, "correlations.json", correlations)
    run_manager.save_json_artifact(run_id, "gates.json", gate_result)
    verdict_md = _verdict_markdown(
        manifest, run_id, metrics, baseline.metrics, gate_result
    )
    run_manager.save_text_artifact(run_id, "verdict.md", verdict_md)

    review_config = ReviewConfig(
        strategy_archetype=manifest.track.value,
        primary_engine="weights_contract_vectorized",
        report_backend="quantstats" if tearsheet else "none",
        data_source="quant_data.api (local-first)",
        date_coverage=f"{prices.index.min().date()} → {prices.index.max().date()}",
        execution_convention=manifest.rebalance.execution_convention.value,
        cost_model=f"{manifest.cost_model.id} {manifest.cost_model.bps}bps",
        benchmark=manifest.benchmark or "",
        naive_baseline=manifest.naive_baseline or "equal_weight",
        hypothesis=manifest.description,
        verdict=gate_result["verdict"],
    )
    benchmark_returns = None
    if manifest.benchmark and manifest.benchmark in prices.columns:
        benchmark_returns = prices[manifest.benchmark].pct_change().dropna()
    bundle = build_review_bundle_from_run(
        run_manager=run_manager,
        run_id=run_id,
        review_config=review_config,
        benchmark_returns=benchmark_returns,
        gate_summary={k: g["passed"] for k, g in gate_result["gates"].items()},
        residual_risks=[w.message for w in qc_report.warnings],
        title=manifest.name,
    )

    # ------------------------------------------------------------------
    # 6. Pool registration
    # ------------------------------------------------------------------
    if register:
        pool.register(manifest, manifest_path=manifest_path)
        pool.attach_run(
            manifest.strategy_id, run_id=run_id, verdict=gate_result["verdict"]
        )

    logger.info(
        "Review complete: %s run_id=%s verdict=%s",
        manifest.strategy_id,
        run_id,
        gate_result["verdict"],
    )
    return {
        "run_id": run_id,
        "verdict": gate_result["verdict"],
        "metrics": metrics,
        "battery": battery,
        "gate_result": gate_result,
        "qc_status": qc_report.status,
        "artifacts": {
            "run_dir": str(run_dir),
            **bundle["paths"],
        },
    }


def _validate_weights(weights: pd.DataFrame, manifest: StrategyManifest) -> None:
    """Enforce the weights contract before anything is backtested."""
    if not isinstance(weights, pd.DataFrame):
        raise TypeError(
            f"entrypoint must return a DataFrame, got {type(weights).__name__}"
        )
    if not isinstance(weights.index, pd.DatetimeIndex):
        raise ValueError("weights must be indexed by DatetimeIndex")
    unknown = [c for c in weights.columns if c not in manifest.universe]
    if unknown:
        raise ValueError(f"weights contain tickers outside the universe: {unknown}")
    gross = weights.abs().sum(axis=1).max()
    if gross > 3.0 + 1e-9:
        raise ValueError(
            f"max gross exposure {gross:.2f} exceeds sanity bound of 3.0 — "
            "leverage at this level needs an explicit design decision"
        )


__all__ = ["run_review", "default_price_loader", "default_macro_loader"]
