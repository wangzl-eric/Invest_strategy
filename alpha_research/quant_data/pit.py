"""Point-in-time (PIT) discipline for macro/FRED series.

FRED timestamps observations by **reference period**, not by publication
date: the CPI row dated 2024-01-01 describes January but was not public
until mid-February. Any backtest that joins raw FRED data on its reference
date is look-ahead biased.

This module shifts each observation's date to a conservative estimate of
its **availability date** (reference date + publication lag), so that a
standard as-of/ffill join only ever sees published values.

The shifted frame keeps the original reference date in a
``reference_date`` column for transparency.

Usage::

    from alpha_research.quant_data.pit import apply_publication_lag
    pit_df = apply_publication_lag(raw_fred_df)  # (date, series_id, value)

``quant_data.api.get_data`` applies this automatically to macro results
(``pit=True`` is the default; opting out logs a warning).
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Publication lags (calendar days, conservative)
# ---------------------------------------------------------------------------
# Monthly macro releases: CPI is published ~2 weeks after month *end*, i.e.
# ~45 days after the reference date FRED uses (month *start*). Employment
# data lands the first Friday after month end (~7 days after month end,
# ~38 days after month start) — we key lags off the FRED reference date.
PUBLICATION_LAG_DAYS: Dict[str, int] = {
    # Monthly, released mid-following-month (reference date = month start)
    "CPIAUCSL": 45,
    "CPILFESL": 45,
    "PCEPI": 60,
    "PCEPILFE": 60,
    "INDPRO": 45,
    "RSAFS": 45,
    "HOUST": 48,
    "PAYEMS": 38,
    "UNRATE": 38,
    # Quarterly, advance estimate ~30 days after quarter end
    # (reference date = quarter start -> ~120 days)
    "GDP": 120,
    "GDPC1": 120,
    # Weekly balance-sheet style (published within days of reference)
    "WALCL": 2,
    "WTREGEN": 2,
    "RRPONTSYD": 1,
    "ICSA": 5,
    # Daily market-derived series (published next business day)
    "DGS2": 1,
    "DGS5": 1,
    "DGS10": 1,
    "DGS30": 1,
    "T10Y2Y": 1,
    "T10YIE": 1,
    "DFF": 1,
    "IORB": 1,
    "BAMLH0A0HYM2": 1,
    "BAMLC0A0CM": 1,
    "VIXCLS": 1,
    "DTWEXBGS": 1,
    "DEXUSEU": 1,
    "DEXJPUS": 1,
}

# Fallback lags by inferred reference-period spacing (calendar days).
_FALLBACK_BY_SPACING = [
    (3, 1),  # ~daily -> 1 day
    (10, 7),  # ~weekly -> 7 days
    (45, 45),  # ~monthly -> 45 days (conservative)
    (120, 120),  # ~quarterly -> 120 days
]
_DEFAULT_LAG = 45


def get_publication_lag(
    series_id: str,
    dates: Optional[pd.Series] = None,
) -> int:
    """Return the publication lag (calendar days) for a series.

    Known series use :data:`PUBLICATION_LAG_DAYS`. Unknown series fall back
    to a conservative lag inferred from the spacing of ``dates`` (daily ->
    1d, weekly -> 7d, monthly -> 45d, quarterly -> 120d) and log a warning
    so the table can be extended deliberately.
    """
    if series_id in PUBLICATION_LAG_DAYS:
        return PUBLICATION_LAG_DAYS[series_id]

    lag = _DEFAULT_LAG
    if dates is not None and len(dates) >= 3:
        spacing = (
            pd.to_datetime(pd.Series(dates).sort_values())
            .diff()
            .dt.days.dropna()
            .median()
        )
        for max_spacing, fallback in _FALLBACK_BY_SPACING:
            if spacing <= max_spacing:
                lag = fallback
                break
        else:
            lag = 120
    logger.warning(
        "PIT: no publication lag registered for '%s'; using conservative "
        "fallback of %d days. Add it to PUBLICATION_LAG_DAYS.",
        series_id,
        lag,
    )
    return lag


def apply_publication_lag(
    df: pd.DataFrame,
    lag_days: Optional[int] = None,
) -> pd.DataFrame:
    """Shift macro observations from reference date to availability date.

    Args:
        df: Long-format macro frame with columns ``(date, series_id, value)``
            (the ``get_data`` macro schema).
        lag_days: Override lag for *all* rows. When None (default), each
            series uses its registered/inferred lag.

    Returns:
        A copy with ``date`` moved forward to the availability date and the
        original reference date preserved in ``reference_date``. Rows are
        re-sorted by (series_id, date).
    """
    if df is None or df.empty:
        return df
    required = {"date", "series_id", "value"}
    if not required.issubset(df.columns):
        raise ValueError(
            f"apply_publication_lag expects columns {sorted(required)}, "
            f"got {list(df.columns)}"
        )

    out = df.copy()
    out["date"] = pd.to_datetime(out["date"])
    out["reference_date"] = out["date"]

    if lag_days is not None:
        out["date"] = out["date"] + pd.to_timedelta(int(lag_days), unit="D")
    else:
        shifted = []
        for sid, grp in out.groupby("series_id"):
            lag = get_publication_lag(str(sid), grp["reference_date"])
            grp = grp.copy()
            grp["date"] = grp["reference_date"] + pd.to_timedelta(lag, unit="D")
            shifted.append(grp)
        out = pd.concat(shifted, ignore_index=True)

    return out.sort_values(["series_id", "date"]).reset_index(drop=True)


def as_of_series(
    df: pd.DataFrame,
    series_id: str,
    index: pd.DatetimeIndex,
) -> pd.Series:
    """Return a PIT-safe daily series aligned to ``index`` via as-of ffill.

    ``df`` must already be availability-dated (output of
    :func:`apply_publication_lag`). At each index date *t* the value is the
    most recent observation published on or before *t*.
    """
    sub = df[df["series_id"].str.upper() == series_id.upper()]
    if sub.empty:
        return pd.Series(index=index, dtype=float, name=series_id)
    s = sub.set_index(pd.to_datetime(sub["date"]))["value"].sort_index().astype(float)
    # Collapse duplicate availability dates (revisions): keep the latest.
    s = s[~s.index.duplicated(keep="last")]
    return s.reindex(index.union(s.index)).ffill().reindex(index).rename(series_id)


__all__ = [
    "PUBLICATION_LAG_DAYS",
    "get_publication_lag",
    "apply_publication_lag",
    "as_of_series",
]
