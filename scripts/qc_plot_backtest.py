#!/usr/bin/env python3
"""Plot key charts from a QuantConnect Lean backtest JSON output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _extract_series(results: dict, chart_name: str, series_name: str) -> pd.DataFrame:
    charts = results.get("charts") or {}
    chart = charts.get(chart_name) or {}
    series = (chart.get("series") or {}).get(series_name) or {}
    values = series.get("values") or []
    if not values:
        return pd.DataFrame()

    # Each value row is typically:
    # - [unix_time, y]
    # - [unix_time, open, high, low, close] (OHLC-style series)
    rows = []
    for v in values:
        ts = pd.to_datetime(int(v[0]), unit="s", utc=True)
        if len(v) >= 5:
            # Use close for OHLC-like series
            y = float(v[4])
        else:
            y = float(v[1])
        rows.append({"timestamp": ts, "value": y})
    df = pd.DataFrame(rows).set_index("timestamp").sort_index()
    return df


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to *-summary.json or full backtest JSON")
    p.add_argument("--outdir", required=True, help="Output directory for images")
    args = p.parse_args()

    inp = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    results = json.loads(inp.read_text(encoding="utf-8"))

    equity = _extract_series(results, "Strategy Equity", "Equity")
    if equity.empty:
        raise SystemExit("Could not find Strategy Equity/Equity series in JSON.")

    # Basic equity curve plot
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(equity.index, equity["value"], linewidth=1.5)
    ax.set_title("Strategy Equity (QuantConnect Lean)")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Equity ($)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    equity_png = outdir / "equity_curve.png"
    fig.savefig(equity_png, dpi=160)
    plt.close(fig)

    # Drawdown plot
    dd = equity["value"] / equity["value"].cummax() - 1.0
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.fill_between(dd.index, dd.values, 0, alpha=0.3)
    ax.set_title("Drawdown")
    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    dd_png = outdir / "drawdown.png"
    fig.savefig(dd_png, dpi=160)
    plt.close(fig)

    print(f"✓ Wrote {equity_png}")
    print(f"✓ Wrote {dd_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

