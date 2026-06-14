# 2026-06-14: Auto-generated backtest report from a run bundle. Turns
# data/backtest_runs/<run_id>/ into a well-formatted markdown report with embedded
# matplotlib charts (equity+drawdown, rolling Sharpe, monthly heatmap, cost sensitivity,
# return distribution) plus metric/gate/stats/sensitivity tables. This is artifact 02 of
# the canonical strategy deliverable set (docs/guides/backtest_output_reference.md):
# the report is GENERATED, never hand-written, so formatting is consistent every run.
"""Render a comprehensive, chart-embedded backtest report from a saved run bundle."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

try:  # charts are optional — degrade to tables-only if matplotlib is unavailable
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    _MPL = True
except Exception:  # pragma: no cover - exercised only when matplotlib is missing
    _MPL = False


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _pct(x: Any, dp: int = 2) -> str:
    try:
        v = float(x)
        return f"{v * 100:.{dp}f}%" if v == v else "n/a"
    except (TypeError, ValueError):
        return "n/a"


def _num(x: Any, dp: int = 3) -> str:
    try:
        v = float(x)
        return f"{v:.{dp}f}" if v == v else "n/a"
    except (TypeError, ValueError):
        return "n/a"


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------


def _chart_equity_drawdown(equity: pd.Series, path: Path) -> bool:
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 6), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
    )
    ax1.plot(equity.index, equity.values, color="#1f77b4", lw=1.2)
    ax1.set_title("Equity curve")
    ax1.set_ylabel("Portfolio value")
    ax1.grid(alpha=0.3)
    peak = equity.cummax()
    dd = (equity - peak) / peak
    ax2.fill_between(dd.index, dd.values * 100, 0, color="#d62728", alpha=0.5)
    ax2.set_ylabel("Drawdown %")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return True


def _chart_rolling_sharpe(returns: pd.Series, path: Path, window: int = 126) -> bool:
    if len(returns) < window + 5:
        return False
    rs = returns.rolling(window).mean() / returns.rolling(window).std() * (252**0.5)
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(rs.index, rs.values, color="#2ca02c", lw=1.0)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_title(f"Rolling {window}-day Sharpe")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return True


def _chart_monthly_heatmap(monthly: Dict[str, float], path: Path) -> bool:
    if not monthly:
        return False
    rows: Dict[int, Dict[int, float]] = {}
    for k, v in monthly.items():
        try:
            y, m = int(k[:4]), int(k[5:7])
        except (ValueError, IndexError):
            continue
        rows.setdefault(y, {})[m] = float(v) * 100
    if not rows:
        return False
    years = sorted(rows)
    mat = [[rows[y].get(m, float("nan")) for m in range(1, 13)] for y in years]
    fig, ax = plt.subplots(figsize=(10, max(2.2, 0.4 * len(years) + 1)))
    import numpy as np

    arr = np.array(mat, dtype=float)
    vmax = np.nanmax(np.abs(arr)) if np.isfinite(arr).any() else 1.0
    im = ax.imshow(arr, cmap="RdYlGn", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(12))
    ax.set_xticklabels(["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    ax.set_yticks(range(len(years)))
    ax.set_yticklabels(years)
    for i in range(len(years)):
        for j in range(12):
            if np.isfinite(arr[i, j]):
                ax.text(j, i, f"{arr[i, j]:.0f}", ha="center", va="center", fontsize=7)
    ax.set_title("Monthly returns (%)")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return True


def _chart_cost_sensitivity(cost_rows: List[Dict[str, Any]], path: Path) -> bool:
    if not cost_rows:
        return False
    mults = [r["cost_multiplier"] for r in cost_rows]
    sharpes = [r["sharpe_ratio"] for r in cost_rows]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    colors = ["#2ca02c" if s > 0 else "#d62728" for s in sharpes]
    ax.bar([f"{m:g}x" for m in mults], sharpes, color=colors)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_title("Net Sharpe vs cost multiplier")
    ax.set_ylabel("Sharpe")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return True


def _chart_return_hist(returns: pd.Series, var95: Optional[float], path: Path) -> bool:
    if len(returns) < 20:
        return False
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.hist(returns.values * 100, bins=60, color="#1f77b4", alpha=0.8)
    if var95 is not None and var95 == var95:
        ax.axvline(
            var95 * 100, color="#d62728", lw=1.2, label=f"95% VaR {var95*100:.2f}%"
        )
        ax.legend(fontsize=8)
    ax.set_title("Daily return distribution")
    ax.set_xlabel("Daily return %")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return True


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------


def _gates_table(gates: Dict[str, Any]) -> List[str]:
    g = gates.get("gates", {})
    if not g:
        return ["_no gates recorded_"]
    lines = ["| gate | value | threshold | passed |", "|---|---|---|---|"]
    for name, gg in g.items():
        val = gg.get("value")
        val_s = _num(val) if isinstance(val, (int, float)) else str(val)
        lines.append(
            f"| {name} | {val_s} | {gg.get('threshold')} | {'✅' if gg.get('passed') else '❌'} |"
        )
    return lines


def render_backtest_report(
    run_id: str,
    *,
    run_root: str | Path = "data/backtest_runs",
    out_dir: Optional[str | Path] = None,
    filename: str = "report.md",
    charts_subdir: str = "charts",
    strategy_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Render ``02_BACKTEST_REPORT.md`` (+ charts) from a saved run bundle.

    Args:
        run_id: the run bundle id under ``run_root``.
        out_dir: where to write the report + charts (default: the run bundle dir).
        filename: report markdown filename (CLI uses ``02_BACKTEST_REPORT.md``).
    Returns dict with the report path, charts dir, and which charts rendered.
    """
    run_dir = Path(run_root) / run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"run bundle not found: {run_dir}")
    dest = Path(out_dir) if out_dir else run_dir
    charts_dir = dest / charts_subdir
    dest.mkdir(parents=True, exist_ok=True)

    metrics = _load_json(run_dir / "metrics.json")
    perf = _load_json(run_dir / "performance.json")
    battery = _load_json(run_dir / "stats_battery.json")
    sens = _load_json(run_dir / "sensitivity.json")
    gates = _load_json(run_dir / "gates.json")
    recon = _load_json(run_dir / "engine_reconciliation.json")

    equity = None
    eq_path = run_dir / "equity_curve.parquet"
    if eq_path.exists():
        eq = pd.read_parquet(eq_path)
        if "date" in eq.columns and "portfolio_value" in eq.columns:
            equity = pd.Series(
                eq["portfolio_value"].values, index=pd.to_datetime(eq["date"])
            )
    returns = None
    ret_path = run_dir / "daily_returns.parquet"
    if ret_path.exists():
        rr = pd.read_parquet(ret_path)
        col = "returns" if "returns" in rr.columns else rr.columns[0]
        returns = pd.Series(rr[col].values, index=pd.to_datetime(rr.index))

    charts: Dict[str, str] = {}
    if _MPL:
        charts_dir.mkdir(parents=True, exist_ok=True)
        rel = charts_subdir
        if (
            equity is not None
            and len(equity) > 5
            and _chart_equity_drawdown(equity, charts_dir / "equity_drawdown.png")
        ):
            charts["equity_drawdown"] = f"{rel}/equity_drawdown.png"
        if returns is not None and _chart_rolling_sharpe(
            returns, charts_dir / "rolling_sharpe.png"
        ):
            charts["rolling_sharpe"] = f"{rel}/rolling_sharpe.png"
        monthly = (perf.get("periodic") or {}).get("monthly_returns", {})
        if _chart_monthly_heatmap(monthly, charts_dir / "monthly_heatmap.png"):
            charts["monthly_heatmap"] = f"{rel}/monthly_heatmap.png"
        if _chart_cost_sensitivity(
            sens.get("cost", []), charts_dir / "cost_sensitivity.png"
        ):
            charts["cost_sensitivity"] = f"{rel}/cost_sensitivity.png"
        var95 = (perf.get("risk") or {}).get("var_95_daily")
        if returns is not None and _chart_return_hist(
            returns, var95, charts_dir / "return_hist.png"
        ):
            charts["return_hist"] = f"{rel}/return_hist.png"

    ret_g = perf.get("returns", {})
    risk_g = perf.get("risk", {})
    ra_g = perf.get("risk_adjusted", {})
    vb = perf.get("vs_benchmark", {})
    name = strategy_name or metrics.get("strategy_name") or run_id
    win = perf.get("window", {})

    L: List[str] = [
        f"# Backtest Report — {name}",
        "",
        f"> **run_id:** `{run_id}` · **window:** {win.get('start','?')} → {win.get('end','?')} "
        f"({win.get('n_days','?')} days, {_num(win.get('years'),1)}y) · "
        f"**verdict:** `{gates.get('verdict','?')}`",
        "> _Auto-generated from the run bundle — do not hand-edit; re-render with "
        "`python -m alpha_research.review report <run_id>`._",
        "",
        "## Headline",
        "",
        "| metric | value | | metric | value |",
        "|---|---|---|---|---|",
        f"| Net Sharpe | **{_num(metrics.get('sharpe_ratio'))}** | | Max drawdown | {_pct(risk_g.get('max_drawdown'))} |",
        f"| CAGR | {_pct(ret_g.get('cagr'))} | | Max DD duration | {risk_g.get('max_drawdown_days','n/a')}d |",
        f"| Ann. return | {_pct(ret_g.get('annualized_return'))} | | Sortino | {_num(ra_g.get('sortino'))} |",
        f"| Ann. vol | {_pct(risk_g.get('annual_volatility'))} | | Calmar | {_num(ra_g.get('calmar'))} |",
        f"| Annual turnover | {_pct(metrics.get('annual_turnover'),0)} | | Win rate | {_pct(ret_g.get('win_rate'),1)} |",
        f"| vs EW baseline | {_num(metrics.get('sharpe_vs_baseline'))} | | Profit factor | {_num(ret_g.get('profit_factor'),2)} |",
        "",
    ]

    if charts:
        L.append("## Charts")
        L.append("")
        for key, title in [
            ("equity_drawdown", "Equity & drawdown"),
            ("rolling_sharpe", "Rolling Sharpe"),
            ("monthly_heatmap", "Monthly returns"),
            ("cost_sensitivity", "Cost sensitivity"),
            ("return_hist", "Return distribution"),
        ]:
            if key in charts:
                L += [f"**{title}**", "", f"![{title}]({charts[key]})", ""]
    elif not _MPL:
        L += [
            "## Charts",
            "",
            "_matplotlib unavailable — charts skipped (tables below)._",
            "",
        ]

    # Gates
    L += ["## Promotion gates", ""] + _gates_table(gates) + [""]

    # Significance / battery
    L += [
        "## Statistical significance",
        "",
        "| stat | value |",
        "|---|---|",
        f"| PSR | {_pct(battery.get('psr'),1)} |",
        f"| DSR (n_trials={battery.get('n_trials_effective','?')}) | {_num(battery.get('dsr'))} |",
        f"| MinBTL (days) | {battery.get('min_backtest_length_days','n/a')} (have {battery.get('n_days','?')}, "
        f"{'OK' if battery.get('minbtl_satisfied') else 'FAIL'}) |",
        f"| Sharpe 95% CI | {battery.get('sharpe_ci_95','n/a')} |",
        f"| Walk-forward +segments | {battery.get('walkforward_positive_segments','?')}/"
        f"{len(battery.get('walkforward_segments',[]))} |",
        "",
    ]

    # Risk detail
    L += [
        "## Risk detail",
        "",
        "| metric | value | metric | value |",
        "|---|---|---|---|",
        f"| Downside dev | {_pct(risk_g.get('downside_deviation'))} | Skew | {_num(risk_g.get('skew'),2)} |",
        f"| 95% VaR (daily) | {_pct(risk_g.get('var_95_daily'))} | Kurtosis | {_num(risk_g.get('kurtosis'),1)} |",
        f"| 95% CVaR (daily) | {_pct(risk_g.get('cvar_95_daily'))} | Tail ratio | {_num(risk_g.get('tail_ratio'),2)} |",
        f"| Time in drawdown | {_pct(risk_g.get('time_in_drawdown_pct'),0)} | Ulcer index | {_num(risk_g.get('ulcer_index'),2)} |",
        "",
    ]

    # Cost sensitivity table
    if sens.get("cost"):
        L += [
            "## Cost sensitivity",
            "",
            "| multiplier | bps | Sharpe | ann. return |",
            "|---|---|---|---|",
        ]
        for r in sens["cost"]:
            L.append(
                f"| {r['cost_multiplier']:g}x | {r['cost_bps']:g} | {_num(r['sharpe_ratio'])} | {_pct(r.get('annualized_return'))} |"
            )
        L.append("")

    # Benchmark
    if vb.get("available"):
        L += [
            "## Vs benchmark",
            "",
            "| metric | value | metric | value |",
            "|---|---|---|---|",
            f"| Beta | {_num(vb.get('beta'),2)} | Correlation | {_num(vb.get('correlation'),2)} |",
            f"| Alpha (ann.) | {_pct(vb.get('alpha_annualized'))} | R² | {_num(vb.get('r_squared'),2)} |",
            f"| Information ratio | {_num(vb.get('information_ratio'),2)} | Tracking error | {_pct(vb.get('tracking_error'))} |",
            f"| Up capture | {_num(vb.get('up_capture'),2)} | Down capture | {_num(vb.get('down_capture'),2)} |",
            "",
        ]

    # Engine reconciliation
    if recon.get("available"):
        ok = "✅ reconciled" if recon.get("reconciled") else "❌ DIVERGENCE"
        L += [
            "## Engine reconciliation",
            "",
            f"- Vectorized vs independent event-driven replay: **{ok}** "
            f"(max daily divergence {recon.get('max_daily_return_divergence')}).",
            f"- Vectorized Sharpe {_num((recon.get('vectorized') or {}).get('sharpe'))} · "
            f"event-driven Sharpe {_num((recon.get('event_driven') or {}).get('sharpe'))}.",
            "",
        ]

    report_path = dest / filename
    report_path.write_text("\n".join(L) + "\n")
    return {
        "report_path": str(report_path),
        "charts_dir": str(charts_dir) if charts else None,
        "charts_rendered": list(charts),
        "matplotlib": _MPL,
    }


__all__ = ["render_backtest_report"]
