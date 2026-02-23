#!/usr/bin/env python3
"""Example: blend signals -> optimize portfolio weights with constraints."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from portfolio.blend import Signal, blend_signals
from portfolio.optimizer import OptimizationConfig, weights_from_alpha


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--returns_csv", required=True, help="CSV with columns: timestamp,<asset1>,<asset2>,...")
    p.add_argument("--max_weight", type=float, default=0.20)
    p.add_argument("--risk_aversion", type=float, default=5.0)
    args = p.parse_args()

    df = pd.read_csv(args.returns_csv)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.set_index("timestamp").sort_index()

    # Example alpha: last 20d return z-scored per asset
    alpha = df.tail(20).sum()
    alpha.name = "mom20"

    cfg = OptimizationConfig(
        max_weight=args.max_weight,
        min_weight=-args.max_weight,
        risk_aversion=args.risk_aversion,
        turnover_aversion=0.1,
        target_gross=1.5,
    )
    w = weights_from_alpha(alpha=alpha, returns=df, cfg=cfg)
    print(w.sort_values(ascending=False).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

