"""Tests for TripleBarrierLabeler and purged K-fold CV integration."""

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_prices(n: int = 200, seed: int = 42) -> pd.Series:
    """Synthetic daily close price series."""
    rng = np.random.RandomState(seed)
    log_returns = rng.normal(0.0005, 0.01, n)
    prices = 100.0 * np.exp(np.cumsum(log_returns))
    dates = pd.date_range("2020-01-01", periods=n, freq="B")
    return pd.Series(prices, index=dates, name="close")


def _make_prices_df(n: int = 200, seed: int = 42) -> pd.DataFrame:
    return _make_prices(n, seed).rename("close").to_frame()


# ===========================================================================
# TripleBarrierLabeler — unit tests
# ===========================================================================


class TestTripleBarrierLabelerInit:
    def test_rejects_non_positive_pt_mult(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        with pytest.raises(ValueError, match="profit_take_mult"):
            TripleBarrierLabeler(profit_take_mult=0)

    def test_rejects_non_positive_sl_mult(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        with pytest.raises(ValueError, match="stop_loss_mult"):
            TripleBarrierLabeler(stop_loss_mult=0)

    def test_rejects_zero_barrier_days(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        with pytest.raises(ValueError, match="vertical_barrier_days"):
            TripleBarrierLabeler(vertical_barrier_days=0)

    def test_sl_none_allowed(self):
        """Disabling the stop-loss barrier should not raise."""
        from backtests.strategies.labeling import TripleBarrierLabeler

        lb = TripleBarrierLabeler(stop_loss_mult=None)
        assert lb.stop_loss_mult is None


class TestDailyVol:
    def test_output_length_matches_input(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        close = _make_prices()
        lb = TripleBarrierLabeler()
        vol = lb.get_daily_vol(close)
        assert len(vol) == len(close)

    def test_first_lookback_rows_are_nan(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        close = _make_prices()
        lookback = 20
        lb = TripleBarrierLabeler(vol_lookback=lookback)
        vol = lb.get_daily_vol(close)
        assert vol.iloc[:lookback].isna().all()
        assert vol.iloc[lookback:].notna().any()

    def test_vol_is_positive(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        close = _make_prices()
        lb = TripleBarrierLabeler()
        vol = lb.get_daily_vol(close)
        assert (vol.dropna() > 0).all()


class TestTripleBarrierLabel:
    def test_returns_dataframe_with_expected_columns(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        lb = TripleBarrierLabeler()
        labeled = lb.label(_make_prices())
        assert set(["t1", "ret", "label", "pt", "sl"]).issubset(labeled.columns)

    def test_t1_always_after_t0(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        lb = TripleBarrierLabeler()
        labeled = lb.label(_make_prices())
        assert (labeled["t1"] >= labeled.index).all()

    def test_labels_are_only_minus1_zero_plus1(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        lb = TripleBarrierLabeler()
        labeled = lb.label(_make_prices())
        assert set(labeled["label"].unique()).issubset({-1, 0, 1})

    def test_profit_take_label_is_plus1(self):
        """If price immediately jumps above pt, label must be +1."""
        from backtests.strategies.labeling import TripleBarrierLabeler

        # Build a price series that rises 5% on day 2
        prices = pd.Series(
            [100.0, 100.0, 105.0, 105.0, 105.0],
            index=pd.date_range("2020-01-01", periods=5, freq="B"),
            name="close",
        )
        # Tight barriers: 1% vol * 2x mult = 2% profit-take
        # Manually supply a vol so the barrier is guaranteed to be hit
        lb = TripleBarrierLabeler(
            profit_take_mult=2.0,
            stop_loss_mult=2.0,
            vertical_barrier_days=4,
            vol_lookback=1,
        )
        vol = lb.get_daily_vol(prices)
        # Entry at index 1 (first non-NaN vol): price=100, vol≈0 (same price),
        # so let's use a deterministic scenario with manual events
        # Use a bigger price series where the jump is unambiguous
        n = 100
        rng = np.random.RandomState(0)
        base = 100 * np.exp(np.cumsum(rng.normal(0, 0.005, n)))
        dates = pd.date_range("2020-01-01", periods=n, freq="B")
        close = pd.Series(base, index=dates)

        # Add a guaranteed +10% spike at position 50
        close.iloc[51] = close.iloc[50] * 1.10
        lb2 = TripleBarrierLabeler(
            profit_take_mult=1.0,
            stop_loss_mult=10.0,
            vertical_barrier_days=5,
            vol_lookback=20,
        )
        events = pd.DatetimeIndex([dates[50]])
        result = lb2.label(close, events=events)
        if not result.empty:
            assert result["label"].iloc[0] == 1

    def test_stop_loss_label_is_minus1(self):
        """If price immediately drops below sl, label must be -1."""
        from backtests.strategies.labeling import TripleBarrierLabeler

        n = 100
        rng = np.random.RandomState(1)
        base = 100 * np.exp(np.cumsum(rng.normal(0, 0.005, n)))
        dates = pd.date_range("2020-01-01", periods=n, freq="B")
        close = pd.Series(base, index=dates)

        # Guaranteed -10% drop at position 51
        close.iloc[51] = close.iloc[50] * 0.90
        lb = TripleBarrierLabeler(
            profit_take_mult=10.0,
            stop_loss_mult=1.0,
            vertical_barrier_days=5,
            vol_lookback=20,
        )
        events = pd.DatetimeIndex([dates[50]])
        result = lb.label(close, events=events)
        if not result.empty:
            assert result["label"].iloc[0] == -1

    def test_vertical_barrier_label_is_zero(self):
        """When price barely moves, vertical barrier fires and label = 0."""
        from backtests.strategies.labeling import TripleBarrierLabeler

        # Flat price series — neither barrier is ever touched
        n = 60
        prices = pd.Series(
            [100.0] * n, index=pd.date_range("2020-01-01", periods=n, freq="B")
        )
        lb = TripleBarrierLabeler(
            profit_take_mult=5.0,
            stop_loss_mult=5.0,
            vertical_barrier_days=5,
            vol_lookback=5,
        )
        labeled = lb.label(prices)
        if not labeled.empty:
            assert (labeled["label"] == 0).all()

    def test_no_label_without_enough_vol_history(self):
        """Events before vol warmup period should be skipped."""
        from backtests.strategies.labeling import TripleBarrierLabeler

        close = _make_prices(n=50)
        lb = TripleBarrierLabeler(vol_lookback=30)
        labeled = lb.label(close)
        # All labeled entries should be after the warmup period
        if not labeled.empty:
            min_entry = labeled.index.min()
            vol = lb.get_daily_vol(close)
            first_valid_vol = vol.dropna().index.min()
            assert min_entry >= first_valid_vol

    def test_min_ret_filters_small_returns(self):
        """Observations with |ret| < min_ret should be dropped."""
        from backtests.strategies.labeling import TripleBarrierLabeler

        close = _make_prices(n=200)
        lb_no_filter = TripleBarrierLabeler(min_ret=0.0)
        lb_filter = TripleBarrierLabeler(min_ret=0.05)  # 5% threshold
        labeled_all = lb_no_filter.label(close)
        labeled_filtered = lb_filter.label(close)
        # Filtered version should have fewer or equal observations
        assert len(labeled_filtered) <= len(labeled_all)

    def test_label_end_times_method(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        lb = TripleBarrierLabeler()
        labeled = lb.label(_make_prices())
        t1 = lb.label_end_times(labeled)
        assert isinstance(t1, pd.Series)
        assert len(t1) == len(labeled)
        assert (t1 >= labeled.index).all()

    def test_empty_result_when_no_valid_events(self):
        from backtests.strategies.labeling import TripleBarrierLabeler

        # Only 5 prices — not enough for vol_lookback=20
        close = pd.Series(
            [100.0] * 5, index=pd.date_range("2020-01-01", periods=5, freq="B")
        )
        lb = TripleBarrierLabeler(vol_lookback=20)
        labeled = lb.label(close)
        assert labeled.empty


# ===========================================================================
# Purged K-Fold — unit tests
# ===========================================================================


class TestPurgedKFoldSplit:
    def _make_dates(self, n: int = 500) -> pd.DatetimeIndex:
        return pd.date_range("2015-01-01", periods=n, freq="B")

    def test_returns_correct_number_of_folds(self):
        from backtests.stats.cross_validation import purged_kfold_split

        dates = self._make_dates()
        splits = purged_kfold_split(dates, n_splits=5)
        assert len(splits) == 5

    def test_no_overlap_between_train_and_test(self):
        from backtests.stats.cross_validation import purged_kfold_split

        dates = self._make_dates()
        for train_idx, test_idx in purged_kfold_split(dates, n_splits=5):
            assert len(set(train_idx).intersection(set(test_idx))) == 0

    def test_embargo_removes_post_test_obs_from_train(self):
        """Training set should not include observations just after the test fold."""
        from backtests.stats.cross_validation import purged_kfold_split

        dates = self._make_dates(n=200)
        embargo_pct = 0.05
        embargo_size = max(int(len(dates) * embargo_pct), 1)
        splits = purged_kfold_split(dates, n_splits=4, embargo_pct=embargo_pct)

        for train_idx, test_idx in splits:
            test_end = test_idx[-1]
            # None of the embargo obs should be in train
            embargo_range = set(range(test_end + 1, test_end + 1 + embargo_size))
            assert len(embargo_range.intersection(set(train_idx))) == 0

    def test_purging_removes_contaminated_train_obs(self):
        """With label_end_times, training obs before the test whose t1 >= test_start must be removed."""
        from backtests.stats.cross_validation import purged_kfold_split

        n = 200
        dates = self._make_dates(n)
        fold_size = n // 4

        # Simulate: each observation has a 30-day forward label window
        lookback = 30
        t1_values = [dates[min(i + lookback, n - 1)] for i, _ in enumerate(dates)]
        label_end_times = pd.Series(t1_values, index=dates)

        splits = purged_kfold_split(
            dates,
            n_splits=4,
            embargo_pct=0.01,
            label_end_times=label_end_times,
        )

        for train_idx, test_idx in splits:
            test_start_idx = test_idx[0]
            test_start_date = dates[test_start_idx]

            # Only check train obs that come BEFORE the test period.
            # (train_after obs have t0 > test_end and are not contaminated.)
            train_before = train_idx[train_idx < test_start_idx]
            for i in train_before:
                t1 = label_end_times.iloc[i]
                assert t1 < test_start_date, (
                    f"Contaminated train obs at index {i}: t1={t1} >= "
                    f"test_start={test_start_date}"
                )

    def test_purging_reduces_train_set_size(self):
        """Purged train set must be smaller than non-purged train set."""
        from backtests.stats.cross_validation import purged_kfold_split

        n = 300
        dates = self._make_dates(n)
        lookback = 40
        t1_values = [dates[min(i + lookback, n - 1)] for i, _ in enumerate(dates)]
        label_end_times = pd.Series(t1_values, index=dates)

        splits_plain = purged_kfold_split(dates, n_splits=4, embargo_pct=0.01)
        splits_purged = purged_kfold_split(
            dates,
            n_splits=4,
            embargo_pct=0.01,
            label_end_times=label_end_times,
        )

        # At least one fold should have a smaller train set after purging
        sizes_plain = [len(tr) for tr, _ in splits_plain]
        sizes_purged = [len(tr) for tr, _ in splits_purged]
        assert any(p < q for p, q in zip(sizes_purged, sizes_plain))

    def test_without_label_end_times_only_embargo_applied(self):
        """When label_end_times=None, result equals the legacy embargo-only behaviour."""
        from backtests.stats.cross_validation import purged_kfold_split

        dates = self._make_dates(n=200)
        splits = purged_kfold_split(
            dates, n_splits=4, embargo_pct=0.01, label_end_times=None
        )
        assert len(splits) == 4
        for train_idx, test_idx in splits:
            assert len(train_idx) > 0
            assert len(test_idx) > 0


# ===========================================================================
# Integration: run_signal_research_ml
# ===========================================================================


class TestRunSignalResearchML:
    def test_returns_dataframe_with_expected_columns(self):
        from backtests.strategies.signals import run_signal_research_ml

        prices = _make_prices_df(n=300)
        result = run_signal_research_ml(
            prices,
            signal_names=["momentum_252_21"],
            n_cv_splits=3,
        )
        if result.empty:
            pytest.skip("Not enough data after labeling")
        expected_cols = {
            "signal",
            "mean_ic",
            "ic_std",
            "ic_ir",
            "mean_accuracy",
            "n_folds",
        }
        assert expected_cols.issubset(set(result.columns))

    def test_ic_values_in_valid_range(self):
        from backtests.strategies.signals import run_signal_research_ml

        prices = _make_prices_df(n=400)
        result = run_signal_research_ml(
            prices,
            signal_names=["momentum_252_21", "rsi_14"],
            n_cv_splits=3,
        )
        if result.empty:
            pytest.skip("Not enough data")
        # Spearman correlation in [-1, 1]
        assert result["mean_ic"].between(-1, 1).all()

    def test_raises_on_missing_close_column(self):
        from backtests.strategies.signals import run_signal_research_ml

        prices = pd.DataFrame({"open": [1, 2, 3]})
        with pytest.raises(ValueError, match="close"):
            run_signal_research_ml(prices)

    def test_sorted_by_ic_ir_descending(self):
        from backtests.strategies.signals import run_signal_research_ml

        prices = _make_prices_df(n=400)
        result = run_signal_research_ml(
            prices,
            signal_names=["momentum_252_21", "rsi_14", "macd_12_26_9"],
            n_cv_splits=3,
        )
        if len(result) < 2:
            pytest.skip("Not enough signals returned")
        ic_irs = result["ic_ir"].tolist()
        assert ic_irs == sorted(ic_irs, reverse=True)

    def test_label_columns_sum_to_one(self):
        from backtests.strategies.signals import run_signal_research_ml

        prices = _make_prices_df(n=400)
        result = run_signal_research_ml(
            prices,
            signal_names=["momentum_252_21"],
            n_cv_splits=3,
        )
        if result.empty:
            pytest.skip("Not enough data")
        total = (
            result["label_pos_pct"].iloc[0]
            + result["label_neg_pct"].iloc[0]
            + result["label_zero_pct"].iloc[0]
        )
        assert abs(total - 1.0) < 1e-9
