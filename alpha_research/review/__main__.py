"""One-call review CLI.

Usage (from repo root, PYTHONPATH=.):

    python -m alpha_research.review run alpha_research/research/pool/<id>/manifest.yaml
    python -m alpha_research.review run <manifest> --force --no-tearsheet
    python -m alpha_research.review report <run_id> --out <strategy_folder>
"""

from __future__ import annotations

import argparse
import json
import sys

from alpha_research.backtests.reporting.report import render_backtest_report
from alpha_research.review.pipeline import run_review


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="alpha_research.review")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run the full review battery for a manifest")
    p_run.add_argument("manifest", help="Path to manifest.yaml")
    p_run.add_argument(
        "--force", action="store_true", help="Proceed past a failing data QC report"
    )
    p_run.add_argument(
        "--no-tearsheet", action="store_true", help="Skip the QuantStats HTML report"
    )
    p_run.add_argument(
        "--no-register", action="store_true", help="Do not touch the strategy pool"
    )
    p_run.add_argument(
        "--output-dir", default="data/backtest_runs", help="Run artifact root"
    )

    p_rep = sub.add_parser(
        "report",
        help="Render the chart-embedded backtest report (artifact 02) from a run bundle",
    )
    p_rep.add_argument("run_id", help="Run bundle id under the run root")
    p_rep.add_argument(
        "--out",
        default=None,
        help="Destination dir (e.g. the strategy folder); default: the run bundle dir",
    )
    p_rep.add_argument(
        "--filename",
        default="02_BACKTEST_REPORT.md",
        help="Report filename written into --out",
    )
    p_rep.add_argument(
        "--run-root", default="data/backtest_runs", help="Run artifact root"
    )

    args = parser.parse_args(argv)

    if args.command == "run":
        result = run_review(
            args.manifest,
            output_dir=args.output_dir,
            force=args.force,
            tearsheet=not args.no_tearsheet,
            register=not args.no_register,
        )
        print(
            json.dumps(
                {
                    "run_id": result["run_id"],
                    "verdict": result["verdict"],
                    "qc_status": result["qc_status"],
                    "sharpe_ratio": result["metrics"]["sharpe_ratio"],
                    "artifacts": result["artifacts"],
                },
                indent=2,
            )
        )
        return 0

    if args.command == "report":
        info = render_backtest_report(
            args.run_id,
            run_root=args.run_root,
            out_dir=args.out,
            filename=args.filename if args.out else "report.md",
        )
        print(json.dumps(info, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
