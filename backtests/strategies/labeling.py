"""Triple-Barrier Labeling — López de Prado (2018), Ch. 3.

Replaces fixed-time horizon labeling with path-aware labels that respect
risk management (stop-loss, profit-take) and adapt barriers to volatility.

Three possible outcomes for each trade entry:
    +1  profit-take barrier hit first (successful trade)
    -1  stop-loss barrier hit first (losing trade)
     0  vertical (time) barrier hit first (inconclusive)

The ``label_end_times`` output (t1 per t0) feeds directly into
``purged_kfold_split`` to prevent label-overlap contamination.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


class TripleBarrierLabeler:
    """Labels observations by which barrier is touched first.

    Barriers are set dynamically using rolling volatility so they
    automatically widen in turbulent regimes and narrow in calm ones.

    Args:
        profit_take_mult: Vol multiplier for the upper (profit-take) barrier.
        stop_loss_mult: Vol multiplier for the lower (stop-loss) barrier.
            Set to None to disable the stop-loss barrier (long-only labeling).
        vertical_barrier_days: Max holding period in trading days.
        vol_lookback: Rolling window for daily vol estimation (log-returns).
        min_ret: Drop observations with |return| below this threshold.
            Useful for removing near-zero noise trades. Default 0 (keep all).
    """

    def __init__(
        self,
        profit_take_mult: float = 2.0,
        stop_loss_mult: float = 2.0,
        vertical_barrier_days: int = 10,
        vol_lookback: int = 20,
        min_ret: float = 0.0,
    ) -> None:
        if profit_take_mult <= 0:
            raise ValueError("profit_take_mult must be positive")
        if stop_loss_mult is not None and stop_loss_mult <= 0:
            raise ValueError("stop_loss_mult must be positive or None")
        if vertical_barrier_days < 1:
            raise ValueError("vertical_barrier_days must be >= 1")

        self.profit_take_mult = profit_take_mult
        self.stop_loss_mult = stop_loss_mult
        self.vertical_barrier_days = vertical_barrier_days
        self.vol_lookback = vol_lookback
        self.min_ret = min_ret

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_daily_vol(self, close: pd.Series) -> pd.Series:
        """Rolling daily volatility of log-returns.

        Args:
            close: Close price series with DatetimeIndex.

        Returns:
            pd.Series of daily vol estimates, NaN for the first vol_lookback obs.
        """
        log_ret = np.log(close).diff()
        return log_ret.rolling(
            window=self.vol_lookback, min_periods=self.vol_lookback
        ).std()

    def label(
        self,
        close: pd.Series,
        events: Optional[pd.DatetimeIndex] = None,
    ) -> pd.DataFrame:
        """Apply triple-barrier labeling to a price series.

        Args:
            close: Close price series with a sorted DatetimeIndex.
            events: Entry dates to label. Defaults to all dates where vol
                is available (i.e., after the vol_lookback warmup period).

        Returns:
            DataFrame indexed by entry date (t0) with columns:
                - t1      : exit date (when a barrier was first touched)
                - ret     : simple return from entry to exit
                - label   : +1, -1, or 0
                - pt      : profit-take price at entry
                - sl      : stop-loss price at entry (NaN if disabled)

        The ``t1`` column is the ``label_end_times`` input for
        ``purged_kfold_split``.
        """
        close = close.sort_index().copy()
        vol = self.get_daily_vol(close)

        if events is None:
            events = vol.dropna().index

        records = []
        close_arr = close.values
        dates_arr = close.index

        for t0 in events:
            if t0 not in close.index:
                continue
            sigma = vol.get(t0, np.nan)
            if pd.isna(sigma) or sigma == 0:
                continue

            loc = dates_arr.get_loc(t0)
            price0 = close_arr[loc]

            pt_price = price0 * (1 + self.profit_take_mult * sigma)
            sl_price = (
                price0 * (1 - self.stop_loss_mult * sigma)
                if self.stop_loss_mult is not None
                else -np.inf
            )

            # Scan forward within the vertical barrier window
            end_loc = min(loc + self.vertical_barrier_days + 1, len(close_arr))
            future_prices = close_arr[loc + 1 : end_loc]
            future_dates = dates_arr[loc + 1 : end_loc]

            label = 0
            t1 = future_dates[-1] if len(future_dates) > 0 else t0
            exit_price = close_arr[end_loc - 1] if end_loc > loc + 1 else price0

            for j, price in enumerate(future_prices):
                if price >= pt_price:
                    label = 1
                    t1 = future_dates[j]
                    exit_price = price
                    break
                if price <= sl_price:
                    label = -1
                    t1 = future_dates[j]
                    exit_price = price
                    break

            ret = (exit_price / price0) - 1

            if self.min_ret > 0 and abs(ret) < self.min_ret:
                continue

            records.append(
                {
                    "t0": t0,
                    "t1": t1,
                    "ret": ret,
                    "label": label,
                    "pt": pt_price,
                    "sl": sl_price if self.stop_loss_mult is not None else np.nan,
                }
            )

        if not records:
            return pd.DataFrame(columns=["t1", "ret", "label", "pt", "sl"])

        result = pd.DataFrame(records).set_index("t0")
        result.index.name = "t0"
        result["t1"] = pd.to_datetime(result["t1"])
        return result

    def label_end_times(self, labeled: pd.DataFrame) -> pd.Series:
        """Extract t1 Series suitable for ``purged_kfold_split``.

        Args:
            labeled: Output of ``self.label()``.

        Returns:
            pd.Series indexed by t0 (entry date), values = t1 (exit date).
        """
        return labeled["t1"]


__all__ = ["TripleBarrierLabeler"]
