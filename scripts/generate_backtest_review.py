#!/usr/bin/env python
"""Generate a standardized review bundle for a saved backtest run.

Example:
    conda run -n ibkr-analytics python scripts/generate_backtest_review.py \
        --run-id 1234abcd \
        --strategy-archetype optimizer_heavy \
        --execution-convention close_to_next_open \
        --benchmark SPY \
        --benchmark-file data/benchmarks/spy_returns.parquet
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backtests.reporting import (
    ReviewConfig,
    build_review_bundle_from_run,
    load_series_from_file,
)
from backtests.run_manager import RunManager


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", default="data/backtest_runs")
    parser.add_argument("--rigor-mode", default="highly-rigorous")
    parser.add_argument("--strategy-archetype", default="cross_sectional")
    parser.add_argument("--primary-engine", default="local")
    parser.add_argument("--validation-engine", action="append", default=[])
    parser.add_argument("--report-backend", default="quantstats")
    parser.add_argument("--optimizer-backend", default="local")
    parser.add_argument("--data-source", default="")
    parser.add_argument("--date-coverage", default="")
    parser.add_argument("--execution-convention", default="")
    parser.add_argument("--cost-model", default="")
    parser.add_argument("--benchmark", default="")
    parser.add_argument("--naive-baseline", default="")
    parser.add_argument("--hypothesis", default="")
    parser.add_argument("--engine-confidence", default="local_only")
    parser.add_argument("--verdict", default="REVISE")
    parser.add_argument("--benchmark-file")
    parser.add_argument("--benchmark-column")
    parser.add_argument("--gate-summary-file")
    parser.add_argument("--optimizer-comparison-file")
    parser.add_argument("--key-lens", action="append", default=[])
    parser.add_argument("--residual-risk", action="append", default=[])
    parser.add_argument("--title")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    benchmark_returns = None
    if args.benchmark_file:
        benchmark_returns = load_series_from_file(
            args.benchmark_file,
            column=args.benchmark_column,
        )

    gate_summary = None
    if args.gate_summary_file:
        gate_summary = json.loads(Path(args.gate_summary_file).read_text())

    optimizer_comparison = None
    if args.optimizer_comparison_file:
        optimizer_comparison = json.loads(
            Path(args.optimizer_comparison_file).read_text()
        )

    review_config = ReviewConfig(
        rigor_mode=args.rigor_mode,
        strategy_archetype=args.strategy_archetype,
        primary_engine=args.primary_engine,
        validation_engines=args.validation_engine,
        report_backend=args.report_backend,
        optimizer_backend=args.optimizer_backend,
        data_source=args.data_source,
        date_coverage=args.date_coverage,
        execution_convention=args.execution_convention,
        cost_model=args.cost_model,
        benchmark=args.benchmark,
        naive_baseline=args.naive_baseline,
        hypothesis=args.hypothesis,
        engine_confidence=args.engine_confidence,
        verdict=args.verdict,
    )

    run_manager = RunManager(output_dir=args.output_dir)
    bundle = build_review_bundle_from_run(
        run_manager=run_manager,
        run_id=args.run_id,
        review_config=review_config,
        benchmark_returns=benchmark_returns,
        gate_summary=gate_summary,
        key_review_lenses=args.key_lens,
        optimizer_comparison=optimizer_comparison,
        residual_risks=args.residual_risk,
        title=args.title,
    )

    print(json.dumps(bundle["paths"], indent=2))


if __name__ == "__main__":
    main()
