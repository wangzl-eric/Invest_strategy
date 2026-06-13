"""Data quality-control preflight for the review pipeline.

Runs deterministic checks on a wide close-price DataFrame before any
backtest is allowed to run (EXECUTION_PLAN.md WP-1.3). A ``fail`` finding
blocks the one-call review unless explicitly forced.

Checks per ticker:

- **coverage**: data spans the requested window (within tolerance).
- **missing_bars**: gaps vs the exchange trading calendar.
- **stale_prices**: runs of N identical consecutive closes.
- **extreme_returns**: |daily return| above a threshold (bad splits/ticks).
- **non_positive**: zero or negative prices.

Usage::

    from alpha_research.quant_data.qc import run_price_qc
    report = run_price_qc(prices, start="2015-01-01", end="2024-12-31")
    if report.failed:
        raise RuntimeError(report.summary())
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

PASS = "pass"
WARN = "warn"
FAIL = "fail"


@dataclass(frozen=True)
class QCFinding:
    """One check result for one ticker."""

    ticker: str
    check: str
    severity: str  # pass | warn | fail
    message: str
    value: Optional[float] = None


@dataclass
class QCReport:
    """Aggregate QC result, serializable as a run artifact."""

    findings: List[QCFinding] = field(default_factory=list)
    start: str = ""
    end: str = ""
    n_tickers: int = 0

    @property
    def failed(self) -> bool:
        return any(f.severity == FAIL for f in self.findings)

    @property
    def warnings(self) -> List[QCFinding]:
        return [f for f in self.findings if f.severity == WARN]

    @property
    def failures(self) -> List[QCFinding]:
        return [f for f in self.findings if f.severity == FAIL]

    @property
    def status(self) -> str:
        if self.failed:
            return FAIL
        if self.warnings:
            return WARN
        return PASS

    def summary(self) -> str:
        lines = [
            f"QC status: {self.status} "
            f"({len(self.failures)} fail / {len(self.warnings)} warn, "
            f"{self.n_tickers} tickers, {self.start} → {self.end})"
        ]
        for f in self.failures + self.warnings:
            lines.append(f"  [{f.severity}] {f.ticker} {f.check}: {f.message}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "start": self.start,
            "end": self.end,
            "n_tickers": self.n_tickers,
            "findings": [asdict(f) for f in self.findings],
        }

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))
        return path


def _trading_days(start: str, end: str, exchange: str) -> pd.DatetimeIndex:
    """Trading sessions in [start, end]; falls back to business days."""
    try:
        import exchange_calendars as xcals

        cal = xcals.get_calendar(exchange)
        return cal.sessions_in_range(
            pd.Timestamp(start), pd.Timestamp(end)
        ).tz_localize(None)
    except Exception:
        logger.debug("exchange_calendars unavailable; using business days")
        return pd.bdate_range(start, end)


def run_price_qc(
    prices: pd.DataFrame,
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
    exchange: str = "XNYS",
    max_missing_frac: float = 0.02,
    coverage_tolerance_days: int = 10,
    stale_run_threshold: int = 5,
    extreme_return_threshold: float = 0.25,
    max_extreme_returns: int = 3,
) -> QCReport:
    """Run all QC checks on a wide close-price DataFrame.

    Args:
        prices: DatetimeIndex x ticker columns of close prices.
        start/end: Requested window (defaults to the data's own span).
        exchange: exchange_calendars code for the trading calendar.
        max_missing_frac: Missing-bar fraction above which a ticker fails
            (below it but >0 is a warning).
        coverage_tolerance_days: Calendar-day slack allowed at each end of
            the requested window before coverage fails.
        stale_run_threshold: Identical consecutive closes counted as stale.
        extreme_return_threshold: |daily return| flagged as extreme.
        max_extreme_returns: More extreme returns than this fails the
            ticker (at or below is a warning).
    """
    has_dt_index = prices is not None and isinstance(prices.index, pd.DatetimeIndex)
    report = QCReport(
        start=str(
            start or (prices.index.min().date() if has_dt_index and len(prices) else "")
        ),
        end=str(
            end or (prices.index.max().date() if has_dt_index and len(prices) else "")
        ),
        n_tickers=prices.shape[1] if prices is not None else 0,
    )

    if prices is None or prices.empty:
        report.findings.append(
            QCFinding("*", "non_empty", FAIL, "price frame is empty")
        )
        return report

    if not has_dt_index:
        report.findings.append(
            QCFinding("*", "index_type", FAIL, "index is not a DatetimeIndex")
        )
        return report

    sessions = _trading_days(report.start, report.end, exchange)
    expected_n = len(sessions)

    for ticker in prices.columns:
        s = prices[ticker].dropna()

        if s.empty:
            report.findings.append(
                QCFinding(ticker, "coverage", FAIL, "no data in window")
            )
            continue

        # --- coverage ---------------------------------------------------
        # End-side gaps fail: fresh data should exist, so a gap means a
        # stale cache or dead feed. Start-side gaps only warn: they are
        # usually genuine instrument inception (e.g. XLC listed 2018).
        gap_start = (s.index.min() - pd.Timestamp(report.start)).days
        gap_end = (pd.Timestamp(report.end) - s.index.max()).days
        if gap_end > coverage_tolerance_days:
            report.findings.append(
                QCFinding(
                    ticker,
                    "coverage_end",
                    FAIL,
                    f"data ends {s.index.max().date()} but {report.end} requested "
                    "(stale cache or dead feed)",
                    value=float(gap_end),
                )
            )
        if gap_start > coverage_tolerance_days:
            report.findings.append(
                QCFinding(
                    ticker,
                    "coverage_start",
                    WARN,
                    f"data starts {s.index.min().date()} vs requested "
                    f"{report.start} (late inception?)",
                    value=float(gap_start),
                )
            )

        # --- missing bars -------------------------------------------------
        if expected_n > 0:
            in_window = sessions[
                (sessions >= s.index.min()) & (sessions <= s.index.max())
            ]
            missing = in_window.difference(s.index.normalize())
            frac = len(missing) / max(len(in_window), 1)
            if frac > max_missing_frac:
                report.findings.append(
                    QCFinding(
                        ticker,
                        "missing_bars",
                        FAIL,
                        f"{len(missing)} of {len(in_window)} sessions missing "
                        f"({frac:.1%})",
                        value=frac,
                    )
                )
            elif len(missing) > 0:
                report.findings.append(
                    QCFinding(
                        ticker,
                        "missing_bars",
                        WARN,
                        f"{len(missing)} sessions missing ({frac:.2%})",
                        value=frac,
                    )
                )

        # --- non-positive prices -------------------------------------------
        n_nonpos = int((s <= 0).sum())
        if n_nonpos > 0:
            report.findings.append(
                QCFinding(
                    ticker,
                    "non_positive",
                    FAIL,
                    f"{n_nonpos} zero/negative prices",
                    value=float(n_nonpos),
                )
            )

        # --- stale runs ----------------------------------------------------
        run_lengths = s.groupby((s != s.shift()).cumsum()).transform("size")
        max_run = int(run_lengths.max()) if len(run_lengths) else 0
        if max_run >= stale_run_threshold:
            report.findings.append(
                QCFinding(
                    ticker,
                    "stale_prices",
                    WARN,
                    f"longest run of identical closes: {max_run} bars",
                    value=float(max_run),
                )
            )

        # --- extreme returns -------------------------------------------------
        rets = s.pct_change().dropna()
        n_extreme = int((rets.abs() > extreme_return_threshold).sum())
        if n_extreme > max_extreme_returns:
            report.findings.append(
                QCFinding(
                    ticker,
                    "extreme_returns",
                    FAIL,
                    f"{n_extreme} daily returns beyond ±{extreme_return_threshold:.0%} "
                    "(possible bad split/dividend adjustment)",
                    value=float(n_extreme),
                )
            )
        elif n_extreme > 0:
            report.findings.append(
                QCFinding(
                    ticker,
                    "extreme_returns",
                    WARN,
                    f"{n_extreme} daily returns beyond ±{extreme_return_threshold:.0%}",
                    value=float(n_extreme),
                )
            )

    return report


__all__ = ["QCFinding", "QCReport", "run_price_qc", "PASS", "WARN", "FAIL"]
