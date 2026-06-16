# 2026-06-16: Professional, presentation-grade backtest report rendered from an
# existing run bundle (data/backtest_runs/<run_id>/). This is an ADDITIVE deliverable
# (artifact 03) that sits alongside — and never replaces — the auto-generated
# 02_BACKTEST_REPORT.md (reporting/report.py). It changes neither the backtest engine
# nor the existing report: it only consumes the artifacts already on disk (metrics.json,
# performance.json, stats_battery.json, sensitivity.json, gates.json, daily_returns/
# equity_curve parquet, manifest_snapshot.yaml) plus OPTIONAL richer artifacts when a
# caller chooses to drop them in the bundle (weights.parquet, prices.parquet,
# benchmarks.parquet). Everything degrades gracefully when an input is absent, so the
# report is always a valid markdown file.
"""Render an elegant, presentation-grade backtest report (artifact 03).

``render_professional_report(run_id, ...)`` turns a saved run bundle into a clean,
professionally formatted markdown report with a rich visualization deck:

  * cumulative return vs. buy-and-hold, with buy/sell markers
  * underwater (drawdown) curve
  * parameter-stability (parameter "volatility") fan
  * signal seasonality decomposition (month-of-year / weekday / trend-seasonal-resid)
  * return distribution annotated with skewness & excess kurtosis
  * beta exposure to multiple market indices (S&P 500, Nasdaq, ...)
  * rolling Sharpe and a volatility-adjusted (vol-targeted) rolling Sharpe

plus the mathematical/statistical rationale of the signal definition and a generated
portfolio-manager review of the performance. The existing report archetype is left
completely intact; this module is a strictly additive layer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:  # charts are optional — degrade to tables-only if matplotlib is unavailable
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import gridspec  # noqa: F401  (used for layout)

    _MPL = True
except Exception:  # pragma: no cover - exercised only when matplotlib is missing
    _MPL = False

TRADING_DAYS = 252

# Elegant, restrained palette (colour-blind friendly-ish, print-safe).
_C = {
    "strategy": "#1b4965",
    "buyhold": "#9aa0a6",
    "buy": "#1b9e77",
    "sell": "#d62728",
    "fill": "#cfe3ee",
    "drawdown": "#c1121f",
    "accent": "#5e60ce",
    "grid": "#dddddd",
    "bar_pos": "#2a9d8f",
    "bar_neg": "#e76f51",
}


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        import yaml

        return yaml.safe_load(path.read_text()) or {}
    except Exception:  # pragma: no cover - missing pyyaml or malformed file
        return {}


def _series_from_parquet(
    path: Path, value_col: Optional[str] = None
) -> Optional[pd.Series]:
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    if df.empty:
        return None
    if "date" in df.columns:
        idx = pd.to_datetime(df["date"])
        cols = [c for c in df.columns if c != "date"]
    else:
        idx = pd.to_datetime(df.index)
        cols = list(df.columns)
    col = (
        value_col if (value_col and value_col in cols) else (cols[0] if cols else None)
    )
    if col is None:
        return None
    return pd.Series(pd.to_numeric(df[col], errors="coerce").values, index=idx).dropna()


def _frame_from_parquet(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    if df.empty:
        return None
    if "date" in df.columns:
        df = df.set_index(pd.to_datetime(df["date"])).drop(columns=["date"])
    else:
        df.index = pd.to_datetime(df.index)
    return df.sort_index()


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
# Quant helpers (numpy/pandas only — no hard scipy/statsmodels dependency)
# ---------------------------------------------------------------------------


def _equity_from_returns(returns: pd.Series, start: float = 1.0) -> pd.Series:
    return (1.0 + returns.fillna(0.0)).cumprod() * start


def _beta(strategy: pd.Series, market: pd.Series) -> Optional[float]:
    joined = pd.concat([strategy.rename("r"), market.rename("b")], axis=1).dropna()
    if len(joined) < 20 or joined["b"].std() == 0:
        return None
    cov = float(np.cov(joined["r"], joined["b"])[0, 1])
    var_b = float(np.var(joined["b"]))
    return cov / var_b if var_b > 0 else None


def _rolling_sharpe(returns: pd.Series, window: int) -> pd.Series:
    mu = returns.rolling(window).mean()
    sd = returns.rolling(window).std()
    return (mu / sd) * np.sqrt(TRADING_DAYS)


def _vol_targeted_returns(
    returns: pd.Series, target_vol: float = 0.10, window: int = 21
) -> pd.Series:
    """Scale daily returns to a constant annualized target vol using *trailing*
    realized vol (shifted one day to avoid look-ahead)."""
    daily_target = target_vol / np.sqrt(TRADING_DAYS)
    trailing = returns.rolling(window).std().shift(1)
    scale = (daily_target / trailing).clip(upper=5.0)  # cap leverage at 5x
    return (returns * scale).dropna()


def _seasonal_decompose(returns: pd.Series) -> Dict[str, pd.Series]:
    """Classical additive month-of-year decomposition of the monthly return series.

    trend     = 12-month centred rolling mean
    seasonal  = mean deviation per calendar month (de-meaned to sum ~0)
    residual  = observed - trend - seasonal
    Dependency-light; statsmodels is not required.
    """
    monthly = (1.0 + returns).groupby(returns.index.to_period("M")).prod() - 1.0
    monthly.index = monthly.index.to_timestamp()
    if len(monthly) < 6:
        return {
            "observed": monthly,
            "trend": monthly * np.nan,
            "seasonal": monthly * 0.0,
            "residual": monthly * np.nan,
        }
    trend = monthly.rolling(12, center=True, min_periods=4).mean()
    detr = monthly - trend
    by_month = detr.groupby(detr.index.month).mean()
    by_month = by_month - by_month.mean()  # centre so seasonal sums to ~0
    seasonal = pd.Series(
        [by_month.get(ts.month, 0.0) for ts in monthly.index], index=monthly.index
    )
    residual = monthly - trend - seasonal
    return {
        "observed": monthly,
        "trend": trend,
        "seasonal": seasonal,
        "residual": residual,
    }


def _buy_sell_markers(
    weights: pd.DataFrame, max_markers: int = 40
) -> Tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    """Classify rebalance days into buys (risk added) and sells (risk cut) from a
    post-shift weights frame; thin to the largest moves so the chart stays readable.

    Uses the change in *net* exposure for directional (e.g. long-only) books. For a
    dollar-neutral long-short book net exposure is ~0 every day, so it falls back to
    the change in *gross* exposure (scaling risk in = buy, scaling out = sell) — that
    way rebalance activity is still surfaced on a market-neutral strategy.
    """
    net = weights.sum(axis=1)
    signal = net
    # Net-flat (dollar-neutral) → switch to gross exposure as the activity signal.
    if float(net.abs().max()) < 1e-6:
        signal = weights.abs().sum(axis=1)
    delta = signal.diff()
    delta.iloc[0] = signal.iloc[0]
    moves = delta[delta.abs() > 1e-9]
    if moves.empty:
        return pd.DatetimeIndex([]), pd.DatetimeIndex([])
    if len(moves) > max_markers:
        moves = moves.reindex(
            moves.abs().sort_values(ascending=False).index[:max_markers]
        )
    buys = moves[moves > 0].index.sort_values()
    sells = moves[moves < 0].index.sort_values()
    return pd.DatetimeIndex(buys), pd.DatetimeIndex(sells)


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------


def _style(ax) -> None:
    ax.grid(alpha=0.35, color=_C["grid"], lw=0.7)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def _chart_return_vs_buyhold(
    strat_equity: pd.Series,
    buyhold_equity: Optional[pd.Series],
    buys: pd.DatetimeIndex,
    sells: pd.DatetimeIndex,
    path: Path,
) -> bool:
    if strat_equity is None or len(strat_equity) < 5:
        return False
    base = strat_equity / strat_equity.iloc[0]
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(
        base.index,
        base.values,
        color=_C["strategy"],
        lw=1.6,
        label="Strategy",
        zorder=3,
    )
    if buyhold_equity is not None and len(buyhold_equity) > 5:
        bh = buyhold_equity.reindex(base.index).ffill()
        bh = bh / bh.dropna().iloc[0]
        ax.plot(
            bh.index,
            bh.values,
            color=_C["buyhold"],
            lw=1.4,
            ls="--",
            label="Buy & hold",
            zorder=2,
        )
    for dts, marker, color, label in (
        (buys, "^", _C["buy"], "Buy"),
        (sells, "v", _C["sell"], "Sell"),
    ):
        pts = base.reindex(pd.DatetimeIndex(dts)).dropna()
        if len(pts):
            ax.scatter(
                pts.index,
                pts.values,
                marker=marker,
                s=55,
                color=color,
                edgecolor="white",
                linewidth=0.6,
                zorder=4,
                label=label,
            )
    ax.set_title(
        "Cumulative return — strategy vs. buy & hold", fontsize=12, fontweight="bold"
    )
    ax.set_ylabel("Growth of $1")
    ax.legend(frameon=False, fontsize=9, ncol=4, loc="upper left")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return True


def _chart_drawdown(strat_equity: pd.Series, path: Path) -> bool:
    if strat_equity is None or len(strat_equity) < 5:
        return False
    peak = strat_equity.cummax()
    dd = (strat_equity - peak) / peak * 100.0
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.fill_between(dd.index, dd.values, 0, color=_C["drawdown"], alpha=0.35)
    ax.plot(dd.index, dd.values, color=_C["drawdown"], lw=1.0)
    ax.set_title("Underwater curve (drawdown)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Drawdown %")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return True


def _chart_parameter_volatility(
    param_rows: List[Dict[str, Any]], base_sharpe: Optional[float], path: Path
) -> bool:
    rows = [
        r
        for r in (param_rows or [])
        if "sharpe_ratio" in r and "scale" in r and "param" in r
    ]
    if not rows:
        return False
    df = pd.DataFrame(rows)
    params = list(dict.fromkeys(df["param"]))
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    cmap = plt.get_cmap("viridis")
    for i, p in enumerate(params):
        sub = df[df["param"] == p].sort_values("scale")
        ax.plot(
            sub["scale"] * 100,
            sub["sharpe_ratio"],
            marker="o",
            lw=1.4,
            color=cmap(i / max(1, len(params) - 1)),
            label=p,
        )
    if base_sharpe is not None and base_sharpe == base_sharpe:
        ax.axhline(base_sharpe, color="k", lw=0.8, ls=":", label="base (100%)")
    ax.axhline(0, color="#999999", lw=0.6)
    ax.set_title(
        "Parameter stability — Sharpe vs. parameter perturbation",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Parameter value (% of base)")
    ax.set_ylabel("Net Sharpe")
    ax.legend(frameon=False, fontsize=8)
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return True


def _chart_seasonality(returns: pd.Series, path: Path) -> bool:
    if returns is None or len(returns) < 40:
        return False
    decomp = _seasonal_decompose(returns)
    # Numeric x positions with explicit tick labels — single-letter month names repeat
    # (M/J/A appear twice), and matplotlib would merge same-named categorical bars.
    month_pos = list(range(1, 13))
    month_names = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    moy = returns.groupby(returns.index.month).mean() * 100
    dow = returns.groupby(returns.index.dayofweek).mean() * 100
    dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    fig, axes = plt.subplots(2, 2, figsize=(11, 6.2))
    ax = axes[0, 0]
    vals = [moy.get(m, np.nan) for m in range(1, 13)]
    ax.bar(
        month_pos,
        vals,
        color=[_C["bar_pos"] if (v or 0) >= 0 else _C["bar_neg"] for v in vals],
    )
    ax.set_xticks(month_pos)
    ax.set_xticklabels(month_names)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_title("Avg return by month-of-year (%)", fontsize=10, fontweight="bold")
    _style(ax)

    ax = axes[0, 1]
    dow_pos = list(range(len(dow_names)))
    dvals = [dow.get(d, np.nan) for d in dow_pos]
    ax.bar(
        dow_pos,
        dvals,
        color=[_C["bar_pos"] if (v or 0) >= 0 else _C["bar_neg"] for v in dvals],
    )
    ax.set_xticks(dow_pos)
    ax.set_xticklabels(dow_names)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_title("Avg return by weekday (%)", fontsize=10, fontweight="bold")
    _style(ax)

    ax = axes[1, 0]
    ax.plot(
        decomp["observed"].index,
        decomp["observed"].values * 100,
        color=_C["buyhold"],
        lw=0.9,
        label="monthly",
    )
    ax.plot(
        decomp["trend"].index,
        decomp["trend"].values * 100,
        color=_C["strategy"],
        lw=1.8,
        label="trend",
    )
    ax.set_title("Trend component (monthly %)", fontsize=10, fontweight="bold")
    ax.legend(frameon=False, fontsize=8)
    _style(ax)

    ax = axes[1, 1]
    seas_by_month = (
        decomp["seasonal"].groupby(decomp["seasonal"].index.month).mean() * 100
    )
    svals = [seas_by_month.get(m, 0.0) for m in range(1, 13)]
    ax.bar(month_pos, svals, color=_C["accent"], alpha=0.85)
    ax.set_xticks(month_pos)
    ax.set_xticklabels(month_names)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_title("Seasonal component (monthly %)", fontsize=10, fontweight="bold")
    _style(ax)

    fig.suptitle("Signal seasonality decomposition", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return True


def _chart_distribution(
    returns: pd.Series, skew: Optional[float], kurt: Optional[float], path: Path
) -> bool:
    if returns is None or len(returns) < 20:
        return False
    x = returns.values * 100
    mu, sd = float(np.mean(x)), float(np.std(x))
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    ax.hist(
        x, bins=60, density=True, color=_C["fill"], edgecolor=_C["strategy"], lw=0.4
    )
    if sd > 0:
        grid = np.linspace(x.min(), x.max(), 200)
        pdf = np.exp(-0.5 * ((grid - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi))
        ax.plot(grid, pdf, color=_C["sell"], lw=1.6, label="Normal fit")
    ax.axvline(mu, color="k", lw=0.8, ls=":", label=f"mean {mu:.2f}%")
    txt = []
    if skew is not None and skew == skew:
        txt.append(f"skew = {skew:.2f}")
    if kurt is not None and kurt == kurt:
        txt.append(f"excess kurt = {kurt:.2f}")
    if txt:
        ax.text(
            0.97,
            0.95,
            "\n".join(txt),
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=9,
            bbox=dict(boxstyle="round", fc="white", ec=_C["grid"]),
        )
    ax.set_title("Daily return distribution", fontsize=12, fontweight="bold")
    ax.set_xlabel("Daily return %")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return True


def _chart_beta_exposures(betas: Dict[str, float], path: Path) -> bool:
    items = [(k, v) for k, v in (betas or {}).items() if v is not None and v == v]
    if not items:
        return False
    names = [k for k, _ in items]
    vals = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(7.0, max(2.4, 0.6 * len(items) + 1.2)))
    colors = [_C["bar_pos"] if v >= 0 else _C["bar_neg"] for v in vals]
    ax.barh(names, vals, color=colors)
    ax.axvline(0, color="k", lw=0.6)
    for i, v in enumerate(vals):
        ax.text(
            v, i, f" {v:.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=9
        )
    ax.set_title("Market beta exposure by index", fontsize=12, fontweight="bold")
    ax.set_xlabel("Beta")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return True


def _chart_rolling_sharpe(returns: pd.Series, path: Path, window: int = 126) -> bool:
    if returns is None or len(returns) < window + 5:
        return False
    raw = _rolling_sharpe(returns, window)
    adj_returns = _vol_targeted_returns(returns)
    adj = (
        _rolling_sharpe(adj_returns, window) if len(adj_returns) > window + 5 else None
    )
    fig, ax = plt.subplots(figsize=(11, 3.4))
    ax.plot(
        raw.index,
        raw.values,
        color=_C["strategy"],
        lw=1.3,
        label=f"Rolling {window}d Sharpe",
    )
    if adj is not None:
        ax.plot(
            adj.index,
            adj.values,
            color=_C["accent"],
            lw=1.3,
            ls="--",
            label="Vol-adjusted (10% target)",
        )
    ax.axhline(0, color="k", lw=0.6)
    ax.axhline(1.0, color="#bbbbbb", lw=0.6, ls=":")
    ax.set_title(
        "Rolling & volatility-adjusted Sharpe ratio", fontsize=12, fontweight="bold"
    )
    ax.set_ylabel("Sharpe")
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper left")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return True


# ---------------------------------------------------------------------------
# Narrative sections
# ---------------------------------------------------------------------------


def _signal_definition_section(manifest: Dict[str, Any]) -> List[str]:
    name = manifest.get("name") or manifest.get("strategy_id") or "the strategy"
    desc = manifest.get("description") or "_No description recorded in the manifest._"
    entrypoint = manifest.get("entrypoint", "n/a")
    params = manifest.get("params", {}) or {}
    universe = manifest.get("universe", []) or []
    bench = manifest.get("benchmark") or "—"

    L = [
        "## Signal Definition & Mathematical Rationale",
        "",
        f"**Strategy:** {name}  ",
        f"**Entrypoint:** `{entrypoint}`  ",
        f"**Universe:** {', '.join(map(str, universe)) if universe else '—'}  ·  "
        f"**Benchmark:** {bench}",
        "",
        desc,
        "",
        "### Weights contract",
        "",
        "The strategy is expressed as an *unshifted* target-weight map; the engine applies "
        "the execution-convention shift so weights at date $t$ use only information available "
        "up to $t$:",
        "",
        "$$ \\mathbf{w}_t = f(\\,\\mathcal{P}_{\\le t},\\ \\mathcal{M}_{\\le t};\\ \\theta\\,), "
        "\\qquad \\mathbf{w}^{\\text{eff}}_t = \\mathbf{w}_{t-k}, \\quad k = \\text{shift bars}. $$",
        "",
        "Net portfolio return, after proportional costs on turnover $\\tau_t = "
        "\\sum_i |w^{\\text{eff}}_{i,t} - w^{\\text{eff}}_{i,t-1}|$:",
        "",
        "$$ r^{\\text{net}}_t = \\sum_i w^{\\text{eff}}_{i,t}\\, r_{i,t} "
        "\\;-\\; c\\cdot \\tau_t, \\qquad c = \\tfrac{\\text{cost bps}}{10^4}. $$",
        "",
    ]
    if params:
        L += ["### Parameters $\\theta$", "", "| parameter | value |", "|---|---|"]
        for k, v in params.items():
            L.append(f"| `{k}` | {v} |")
        L.append("")
    return L


def _statistics_formula_section(perf: Dict[str, Any]) -> List[str]:
    risk = perf.get("risk", {})
    ra = perf.get("risk_adjusted", {})
    ret = perf.get("returns", {})
    return [
        "## Statistical Moments & Risk Definitions",
        "",
        "| moment / ratio | formula | value |",
        "|---|---|---|",
        f"| Annualized Sharpe | $\\sqrt{{252}}\\,\\bar r / \\sigma_r$ | {_num(ra.get('sharpe'))} |",
        f"| Sortino | $\\sqrt{{252}}\\,\\bar r / \\sigma_{{\\text{{down}}}}$ | {_num(ra.get('sortino'))} |",
        f"| Calmar | $\\text{{CAGR}} / |\\text{{MaxDD}}|$ | {_num(ra.get('calmar'))} |",
        f"| Skewness | $\\mathbb{{E}}[(r-\\bar r)^3]/\\sigma_r^3$ | {_num(risk.get('skew'), 2)} |",
        f"| Excess kurtosis | $\\mathbb{{E}}[(r-\\bar r)^4]/\\sigma_r^4 - 3$ | {_num(risk.get('kurtosis'), 2)} |",
        f"| 95% VaR (daily) | $-Q_{{0.05}}(r)$ | {_pct(risk.get('var_95_daily'))} |",
        f"| 95% CVaR (daily) | $\\mathbb{{E}}[r \\mid r \\le Q_{{0.05}}]$ | {_pct(risk.get('cvar_95_daily'))} |",
        f"| Tail ratio | $|Q_{{0.95}}| / |Q_{{0.05}}|$ | {_num(risk.get('tail_ratio'), 2)} |",
        f"| Max drawdown | $\\min_t (E_t/\\max_{{s\\le t}}E_s - 1)$ | {_pct(risk.get('max_drawdown'))} |",
        f"| CAGR | $(E_T/E_0)^{{252/n}}-1$ | {_pct(ret.get('cagr'))} |",
        "",
        "_Beta vs. index $j$: $\\beta_j = \\operatorname{Cov}(r, r^{(j)}) / "
        "\\operatorname{Var}(r^{(j)})$. Volatility-adjusted Sharpe rescales daily returns to "
        "a constant 10% annualized target vol using trailing 21-day realized vol (lagged one "
        "day) before computing the rolling ratio._",
        "",
    ]


def _methodology_section(
    perf: Dict[str, Any],
    battery: Dict[str, Any],
    recon: Dict[str, Any],
    control: Dict[str, Any],
    manifest: Dict[str, Any],
) -> List[str]:
    """Horizon, win-probability, data source, engine, and the qualitative rigor
    narrative — sourced from review.json's control block when present, else from the
    manifest and the platform's documented defaults."""
    win = perf.get("window", {})
    ret = perf.get("returns", {})
    periodic = perf.get("periodic", {})

    data_source = control.get("data_source") or (
        "quant_data.api — local Parquet lake first, API fallback "
        "(yfinance / FRED / Stooq); macro series are point-in-time shifted"
    )
    date_coverage = control.get("date_coverage") or (
        f"{win.get('start', '?')} → {win.get('end', '?')}"
    )
    primary_engine = control.get("primary_engine") or "weights_contract_vectorized"
    val_engines = control.get("validation_engines") or []
    if isinstance(val_engines, (list, tuple)):
        val_engines = (
            ", ".join(map(str, val_engines)) or "event-driven (Backtrader adapter)"
        )
    exec_conv = (
        control.get("execution_convention") or "close-to-next-open (1-bar shift)"
    )
    cost_model = control.get("cost_model") or (
        f"proportional {manifest.get('cost_bps', 5)}bps on turnover"
    )
    benchmark = control.get("benchmark") or manifest.get("benchmark") or "—"
    baseline = (
        control.get("naive_baseline")
        or manifest.get("naive_baseline")
        or "equal_weight"
    )

    # Win-probability metrics.
    win_rate = ret.get("win_rate")
    pos_months = periodic.get("positive_months_pct")
    profit_factor = ret.get("profit_factor")
    payoff = ret.get("win_loss_ratio")

    recon_line = "_engine reconciliation not recorded for this run._"
    if recon.get("available"):
        ok = "reconciled ✅" if recon.get("reconciled") else "DIVERGENCE ❌"
        recon_line = (
            f"Independent event-driven replay of the vectorized engine: **{ok}** "
            f"(max daily-return divergence {recon.get('max_daily_return_divergence')})."
        )

    return [
        "## Methodology & Backtest Rigor",
        "",
        "### Backtest horizon",
        "",
        f"- **Window:** {win.get('start', '?')} → {win.get('end', '?')}",
        f"- **Length:** {win.get('n_days', '?')} trading days "
        f"(~{_num(win.get('years'), 1)} years)",
        f"- **Walk-forward folds:** {len(battery.get('walkforward_segments', []))} contiguous "
        f"out-of-sample segments, {battery.get('walkforward_positive_segments', '?')} positive — "
        "consistency is judged across folds, not on the full-sample number alone.",
        "",
        "### Win probability",
        "",
        "| measure | value | definition |",
        "|---|---:|---|",
        f"| Daily win rate | {_pct(win_rate, 1)} | $\\Pr(r_t > 0)$ |",
        f"| Positive months | {_pct(pos_months, 1)} | share of calendar months with $r>0$ |",
        f"| Profit factor | {_num(profit_factor, 2)} | $\\sum r^{{+}} / |\\sum r^{{-}}|$ |",
        f"| Payoff ratio | {_num(payoff, 2)} | avg win / avg loss |",
        "",
        "_A win rate near 50% with a payoff ratio > 1 (or vice-versa) is normal; the two must "
        "be read together — neither alone establishes an edge._",
        "",
        "### Data source",
        "",
        f"- **Provider:** {data_source}",
        f"- **Coverage:** {date_coverage}",
        f"- **Universe / benchmark:** {', '.join(map(str, manifest.get('universe', []))) or '—'} "
        f"· benchmark {benchmark}",
        "- **Look-ahead control:** macro/FRED series are point-in-time shifted to their "
        "publication-availability date before they enter any signal.",
        "",
        "### Backtest engine",
        "",
        f"- **Primary engine:** `{primary_engine}` — a vectorized weights-contract backtester "
        "(`alpha_research.review.engine.run_weights_backtest`). Target weights at date $t$ use "
        "only data $\\le t$; the engine applies the execution shift, so strategies never "
        "pre-shift their own output.",
        f"- **Execution convention:** {exec_conv}.",
        f"- **Cost model:** {cost_model}, charged on one-way turnover each rebalance.",
        f"- **Validation engine(s):** {val_engines} — used only to cross-check the primary "
        "engine, never to produce headline numbers.",
        f"- **Reconciliation:** {recon_line}",
        "",
        "### How the backtest is carried out rigorously",
        "",
        "1. **Data QC preflight** — missing-bar, stale-price, and extreme-return checks run "
        "before any signal is computed; a failing report blocks the run.",
        "2. **No look-ahead by construction** — the weights contract forbids pre-shifting and "
        "PIT-shifts macro data; weights are lagged by the execution convention before earning "
        "returns.",
        "3. **Costs and turnover** — net returns subtract proportional costs on realized "
        "turnover, and survival is re-tested at 1× / 2× / 3× the modelled cost.",
        f"4. **Naive-baseline comparison** — every result is benchmarked against a `{baseline}` "
        "alternative; edge is the Sharpe *above* that baseline, not the raw Sharpe.",
        "5. **Multiple-testing control** — PSR, the Deflated Sharpe Ratio, and the Minimum "
        "Backtest Length deflate significance by the *effective* number of trials "
        f"(n_trials = {battery.get('n_trials_effective', '?')}), so repeated searching cannot "
        "manufacture a pass.",
        "6. **Robustness sweeps** — parameters are perturbed ±20/40% and Sharpe dispersion is "
        "reported; a result that only works at one setting is treated as fragile.",
        "7. **Out-of-sample consistency** — walk-forward folds and regime-conditional Sharpe "
        "check that the edge is not concentrated in a single period or volatility regime.",
        "8. **Independent reconciliation** — an event-driven replay must reproduce the "
        "vectorized engine's daily returns before the run is trusted.",
        "",
    ]


def _pm_review_section(
    metrics: Dict[str, Any],
    perf: Dict[str, Any],
    battery: Dict[str, Any],
    gates: Dict[str, Any],
    sens: Dict[str, Any],
    betas: Dict[str, float],
    param_vol: Dict[str, float],
) -> List[str]:
    risk = perf.get("risk", {})
    ra = perf.get("risk_adjusted", {})
    obs: List[str] = []

    sharpe = metrics.get("sharpe_ratio")
    edge = metrics.get("sharpe_vs_baseline")
    if isinstance(sharpe, (int, float)):
        verdict_word = (
            "strong"
            if sharpe >= 1.0
            else "moderate"
            if sharpe >= 0.5
            else "weak"
            if sharpe >= 0
            else "negative"
        )
        obs.append(
            f"**Risk-adjusted return.** Net Sharpe of **{_num(sharpe)}** is a {verdict_word} "
            f"result; Sortino {_num(ra.get('sortino'))} and Calmar {_num(ra.get('calmar'))} "
            "corroborate the downside-aware picture."
        )
    if isinstance(edge, (int, float)):
        verdict = (
            "adds genuine edge over"
            if edge > 0.1
            else "barely clears"
            if edge > 0
            else "fails to beat"
        )
        obs.append(
            f"**Edge vs. naive baseline.** The strategy {verdict} the equal-weight baseline "
            f"(ΔSharpe = {_num(edge)}). A small or negative gap means most of the return is "
            "beta the baseline already captures."
        )

    skew = risk.get("skew")
    kurt = risk.get("kurtosis")
    tail_bits = []
    if isinstance(skew, (int, float)) and skew == skew:
        tail_bits.append(
            "left-skewed (crash-prone)"
            if skew < -0.2
            else "right-skewed (favourable)"
            if skew > 0.2
            else "roughly symmetric"
        )
    if isinstance(kurt, (int, float)) and kurt == kurt:
        tail_bits.append("fat-tailed" if kurt > 1 else "near-Gaussian tails")
    if tail_bits:
        obs.append(
            f"**Tail profile.** Returns are {', '.join(tail_bits)} "
            f"(skew {_num(skew, 2)}, excess kurtosis {_num(kurt, 2)}); 95% CVaR "
            f"{_pct(risk.get('cvar_95_daily'))} sizes the expected bad-day loss."
        )

    dd = risk.get("max_drawdown")
    if isinstance(dd, (int, float)) and dd == dd:
        obs.append(
            f"**Drawdown.** Worst peak-to-trough was {_pct(dd)} over "
            f"{risk.get('max_drawdown_days', 'n/a')} days, with "
            f"{_pct(risk.get('time_in_drawdown_pct'), 0)} of the sample spent underwater — "
            "the capital-at-risk a PM must be willing to sit through."
        )

    cost_rows = sens.get("cost", []) if sens else []
    if cost_rows:
        worst = cost_rows[-1]
        survives = worst.get("sharpe_ratio", 0) > 0
        obs.append(
            f"**Cost robustness.** At {worst.get('cost_multiplier')}× modelled costs the net "
            f"Sharpe is {_num(worst.get('sharpe_ratio'))} — "
            f"{'survives' if survives else 'breaks down'} under realistic frictions."
        )

    psr, dsr = battery.get("psr"), battery.get("dsr")
    if psr is not None or dsr is not None:
        wf = (
            f"{battery.get('walkforward_positive_segments', '?')}/"
            f"{len(battery.get('walkforward_segments', []))}"
        )
        obs.append(
            f"**Statistical significance.** PSR {_pct(psr, 1)}, DSR {_num(dsr)} "
            f"(n_trials={battery.get('n_trials_effective', '?')}), MinBTL "
            f"{'satisfied' if battery.get('minbtl_satisfied') else 'NOT satisfied'}; "
            f"walk-forward positive in {wf} segments — consistency across the sample, "
            "not a single lucky regime."
        )

    if param_vol:
        worst_p = max(param_vol, key=param_vol.get)
        obs.append(
            f"**Parameter stability.** Sharpe dispersion across perturbations is largest for "
            f"`{worst_p}` (σ = {_num(param_vol[worst_p])}). Low dispersion is evidence the edge "
            "is not an artefact of a single fragile setting."
        )

    live_betas = {k: v for k, v in (betas or {}).items() if v is not None and v == v}
    if live_betas:
        hi = max(live_betas, key=lambda k: abs(live_betas[k]))
        obs.append(
            f"**Market exposure.** Largest index beta is to {hi} ({_num(live_betas[hi], 2)}); "
            "net directional exposure should be reconciled against the strategy's intended "
            "market-neutrality (or lack thereof)."
        )

    verdict = (gates or {}).get("verdict", "?")
    gate_pass = sum(
        1 for g in (gates or {}).get("gates", {}).values() if g.get("passed")
    )
    gate_total = len((gates or {}).get("gates", {}))
    obs.append(
        f"**Gate verdict.** Pre-committed promotion gates: **{verdict}** "
        f"({gate_pass}/{gate_total} passed). Promotion to paper remains a human decision."
    )

    L = [
        "## Portfolio Manager Review",
        "",
        "_Generated from the run artifacts — a structured reading of the numbers, not a "
        "substitute for the reviewing PM's judgement._",
        "",
    ]
    L += [f"- {o}" for o in obs]
    L.append("")
    return L


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def render_professional_report(
    run_id: str,
    *,
    run_root: str | Path = "data/backtest_runs",
    out_dir: Optional[str | Path] = None,
    filename: str = "03_PROFESSIONAL_REPORT.md",
    charts_subdir: str = "charts_pro",
    strategy_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Render the professional report (artifact 03) from a saved run bundle.

    Consumes the standard bundle artifacts and, when present, the optional richer
    artifacts ``weights.parquet`` (date × ticker effective weights), ``prices.parquet``
    (date × ticker close), and ``benchmarks.parquet`` (date × index price levels) to
    unlock the buy/sell-marker, buy-and-hold overlay, and multi-index beta visuals.
    Every input is optional; the report always renders a valid markdown file.

    Returns a dict with the report path, charts dir, charts rendered, and matplotlib flag.
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
    control = _load_json(run_dir / "review.json").get("control", {})
    manifest = _load_yaml(run_dir / "manifest_snapshot.yaml")

    returns = _series_from_parquet(run_dir / "daily_returns.parquet", "returns")
    equity = _series_from_parquet(run_dir / "equity_curve.parquet", "portfolio_value")
    if equity is None and returns is not None:
        equity = _equity_from_returns(returns, start=100_000.0)

    # Optional richer artifacts (degrade gracefully when absent).
    weights = _frame_from_parquet(run_dir / "weights.parquet")
    prices = _frame_from_parquet(run_dir / "prices.parquet")
    benchmarks = _frame_from_parquet(run_dir / "benchmarks.parquet")

    # Buy-and-hold reference: first benchmark index, else equal-weight of the universe.
    buyhold_equity = None
    if benchmarks is not None and benchmarks.shape[1] >= 1:
        bh_px = benchmarks.iloc[:, 0]
        buyhold_equity = bh_px / bh_px.dropna().iloc[0]
    elif prices is not None and prices.shape[1] >= 1:
        ew = prices.div(prices.iloc[0]).mean(axis=1)
        buyhold_equity = ew

    buys, sells = (pd.DatetimeIndex([]), pd.DatetimeIndex([]))
    if weights is not None and not weights.empty:
        buys, sells = _buy_sell_markers(weights)

    # Multi-index beta exposures.
    betas: Dict[str, float] = {}
    if returns is not None and benchmarks is not None:
        for col in benchmarks.columns:
            bench_ret = benchmarks[col].pct_change().dropna()
            b = _beta(returns, bench_ret)
            if b is not None:
                betas[str(col)] = b
    # Fall back to the single benchmark recorded in performance.json.
    if not betas:
        vb = perf.get("vs_benchmark", {})
        if vb.get("available") and vb.get("beta") is not None:
            betas[manifest.get("benchmark") or "benchmark"] = vb["beta"]

    # Parameter "volatility": Sharpe dispersion per perturbed parameter.
    param_vol: Dict[str, float] = {}
    for r in sens.get("params", []) if sens else []:
        if "param" in r and isinstance(r.get("sharpe_ratio"), (int, float)):
            param_vol.setdefault(r["param"], [])
            param_vol[r["param"]].append(r["sharpe_ratio"])
    param_vol = {k: float(np.std(v)) for k, v in param_vol.items() if len(v) > 1}

    charts: Dict[str, str] = {}
    if _MPL:
        charts_dir.mkdir(parents=True, exist_ok=True)
        rel = charts_subdir

        def _do(key: str, ok: bool) -> None:
            if ok:
                charts[key] = f"{rel}/{key}.png"

        _do(
            "return_vs_buyhold",
            _chart_return_vs_buyhold(
                equity,
                buyhold_equity,
                buys,
                sells,
                charts_dir / "return_vs_buyhold.png",
            ),
        )
        _do("drawdown", _chart_drawdown(equity, charts_dir / "drawdown.png"))
        _do(
            "parameter_volatility",
            _chart_parameter_volatility(
                sens.get("params", []) if sens else [],
                metrics.get("sharpe_ratio"),
                charts_dir / "parameter_volatility.png",
            ),
        )
        _do("seasonality", _chart_seasonality(returns, charts_dir / "seasonality.png"))
        risk = perf.get("risk", {})
        _do(
            "distribution",
            _chart_distribution(
                returns,
                risk.get("skew"),
                risk.get("kurtosis"),
                charts_dir / "distribution.png",
            ),
        )
        _do(
            "beta_exposures",
            _chart_beta_exposures(betas, charts_dir / "beta_exposures.png"),
        )
        _do(
            "rolling_sharpe",
            _chart_rolling_sharpe(returns, charts_dir / "rolling_sharpe.png"),
        )

    # ----------------------------------------------------------------- markdown
    ret_g = perf.get("returns", {})
    risk_g = perf.get("risk", {})
    ra_g = perf.get("risk_adjusted", {})
    win = perf.get("window", {})
    name = (
        strategy_name or manifest.get("name") or metrics.get("strategy_name") or run_id
    )

    L: List[str] = [
        f"# Professional Backtest Report — {name}",
        "",
        f"> **run_id** `{run_id}`  ·  **window** {win.get('start', '?')} → {win.get('end', '?')} "
        f"({win.get('n_days', '?')} days, {_num(win.get('years'), 1)}y)  ·  "
        f"**verdict** `{gates.get('verdict', '?')}`",
        ">",
        "> _Presentation-grade companion to `02_BACKTEST_REPORT.md` — additive deliverable 03. "
        "Auto-generated; re-render with the report API. Math rendered with `$…$` / `$$…$$`._",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        "| metric | value | | metric | value |",
        "|---|---:|---|---|---:|",
        f"| Net Sharpe | **{_num(metrics.get('sharpe_ratio'))}** | | Max drawdown | {_pct(risk_g.get('max_drawdown'))} |",
        f"| CAGR | {_pct(ret_g.get('cagr'))} | | Max DD duration | {risk_g.get('max_drawdown_days', 'n/a')}d |",
        f"| Annualized return | {_pct(ret_g.get('annualized_return'))} | | Sortino | {_num(ra_g.get('sortino'))} |",
        f"| Annualized vol | {_pct(risk_g.get('annual_volatility'))} | | Calmar | {_num(ra_g.get('calmar'))} |",
        f"| Skewness | {_num(risk_g.get('skew'), 2)} | | Excess kurtosis | {_num(risk_g.get('kurtosis'), 2)} |",
        f"| Win rate | {_pct(ret_g.get('win_rate'), 1)} | | Edge vs baseline | {_num(metrics.get('sharpe_vs_baseline'))} |",
        "",
    ]

    # Signal definition + math
    L += _signal_definition_section(manifest)

    # Methodology & backtest rigor (horizon, win-prob, data source, engine, process)
    L += _methodology_section(perf, battery, recon, control, manifest)

    # Visualization deck
    if charts:
        L += ["## Visualization Deck", ""]
        for key, title, caption in [
            (
                "return_vs_buyhold",
                "Cumulative Return vs. Buy & Hold",
                "Strategy growth of $1 against a passive buy-and-hold benchmark; "
                "▲ buys and ▼ sells mark the largest net-exposure changes.",
            ),
            (
                "drawdown",
                "Drawdown",
                "Underwater curve — depth and duration of peak-to-trough losses.",
            ),
            (
                "rolling_sharpe",
                "Rolling & Volatility-Adjusted Sharpe",
                "126-day rolling Sharpe and a 10%-vol-targeted variant; stability of the edge over time.",
            ),
            (
                "distribution",
                "Return Distribution (Skew & Kurtosis)",
                "Daily-return histogram vs. a fitted normal, annotated with the realized "
                "skewness and excess kurtosis.",
            ),
            (
                "seasonality",
                "Signal Seasonality Decomposition",
                "Month-of-year and weekday seasonality plus an additive trend/seasonal split "
                "of the monthly return series.",
            ),
            (
                "parameter_volatility",
                "Parameter Stability",
                "Sharpe response to ±20/40% parameter perturbations — fragility diagnostic.",
            ),
            (
                "beta_exposures",
                "Beta Exposure by Index",
                "OLS beta of strategy returns to each market index (S&P 500, Nasdaq, …).",
            ),
        ]:
            if key in charts:
                L += [
                    f"### {title}",
                    "",
                    f"![{title}]({charts[key]})",
                    "",
                    f"_{caption}_",
                    "",
                ]
    elif not _MPL:
        L += [
            "## Visualization Deck",
            "",
            "_matplotlib unavailable — charts skipped; tables below carry the numbers._",
            "",
        ]

    # Statistical moments & formulas
    L += _statistics_formula_section(perf)

    # Beta exposure table
    if betas:
        L += ["## Beta Exposure (multi-index)", "", "| index | beta |", "|---|---:|"]
        for k, v in betas.items():
            L.append(f"| {k} | {_num(v, 3)} |")
        L.append("")

    # Parameter stability table
    if param_vol:
        L += [
            "## Parameter Stability",
            "",
            "_Parameter “volatility” = standard deviation of net Sharpe across the "
            "±20/40% perturbation grid (lower is more robust)._",
            "",
            "| parameter | Sharpe σ |",
            "|---|---:|",
        ]
        for k, v in sorted(param_vol.items(), key=lambda kv: -kv[1]):
            L.append(f"| `{k}` | {_num(v)} |")
        L.append("")

    # Seasonality table (month-of-year averages)
    if returns is not None and len(returns) >= 40:
        moy = returns.groupby(returns.index.month).mean()
        months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        L += [
            "## Seasonality — average daily return by month",
            "",
            "| " + " | ".join(months) + " |",
            "|" + "---|" * 12,
        ]
        L.append(
            "| "
            + " | ".join(_pct(moy.get(m, float("nan")), 3) for m in range(1, 13))
            + " |"
        )
        L.append("")

    # PM review
    L += _pm_review_section(metrics, perf, battery, gates, sens, betas, param_vol)

    L += [
        "---",
        "",
        "_Definitions: Sharpe/Sortino annualized with 252 trading days; VaR/CVaR at the 5% "
        "daily quantile; beta via OLS covariance; volatility-adjusted Sharpe targets 10% "
        "annualized vol using trailing 21-day realized vol (lagged). This report reads the "
        "existing run bundle and does not alter the backtest engine or `02_BACKTEST_REPORT.md`._",
        "",
    ]

    report_path = dest / filename
    report_path.write_text("\n".join(L) + "\n")
    return {
        "report_path": str(report_path),
        "charts_dir": str(charts_dir) if charts else None,
        "charts_rendered": list(charts),
        "matplotlib": _MPL,
        "betas": betas,
        "param_volatility": param_vol,
    }


__all__ = ["render_professional_report"]
