"""Tests for the point-in-time FRED layer (WP-1.2)."""
import pandas as pd
import pytest

from alpha_research.quant_data.pit import (
    PUBLICATION_LAG_DAYS,
    apply_publication_lag,
    as_of_series,
    get_publication_lag,
)


def _macro_frame(series_id: str, dates, values=None):
    dates = pd.to_datetime(dates)
    values = values if values is not None else range(1, len(dates) + 1)
    return pd.DataFrame(
        {"date": dates, "series_id": series_id, "value": [float(v) for v in values]}
    )


@pytest.mark.unit
class TestPublicationLag:
    def test_cpi_shifted_45_days(self):
        """January CPI (reference 01-01) must be unavailable until ~mid-Feb."""
        raw = _macro_frame("CPIAUCSL", ["2024-01-01"])
        shifted = apply_publication_lag(raw)
        assert shifted.loc[0, "date"] == pd.Timestamp("2024-01-01") + pd.Timedelta(
            days=45
        )
        assert shifted.loc[0, "reference_date"] == pd.Timestamp("2024-01-01")

    def test_market_series_shifted_one_day(self):
        raw = _macro_frame("T10Y2Y", ["2024-03-04"])
        shifted = apply_publication_lag(raw)
        assert shifted.loc[0, "date"] == pd.Timestamp("2024-03-05")

    def test_explicit_lag_override(self):
        raw = _macro_frame("T10Y2Y", ["2024-03-04"])
        shifted = apply_publication_lag(raw, lag_days=10)
        assert shifted.loc[0, "date"] == pd.Timestamp("2024-03-14")

    def test_values_unchanged(self):
        raw = _macro_frame("CPIAUCSL", ["2024-01-01", "2024-02-01"], [310.3, 311.0])
        shifted = apply_publication_lag(raw)
        assert list(shifted["value"]) == [310.3, 311.0]

    def test_unknown_daily_series_falls_back_to_one_day(self):
        dates = pd.bdate_range("2024-01-01", periods=30)
        lag = get_publication_lag("MYSTERY_DAILY", dates.to_series())
        assert lag == 1

    def test_unknown_monthly_series_falls_back_conservatively(self):
        dates = pd.date_range("2022-01-01", periods=24, freq="MS")
        lag = get_publication_lag("MYSTERY_MONTHLY", dates.to_series())
        assert lag == 45

    def test_unknown_series_without_dates_uses_default(self):
        assert get_publication_lag("MYSTERY") == 45

    def test_known_series_table_used(self):
        assert get_publication_lag("CPIAUCSL") == PUBLICATION_LAG_DAYS["CPIAUCSL"]

    def test_bad_columns_raise(self):
        with pytest.raises(ValueError, match="columns"):
            apply_publication_lag(pd.DataFrame({"foo": [1]}))

    def test_empty_frame_passthrough(self):
        df = pd.DataFrame(columns=["date", "series_id", "value"])
        assert apply_publication_lag(df).empty


@pytest.mark.unit
class TestAsOfSeries:
    def test_value_not_visible_before_publication(self):
        """The look-ahead test: pre-publication dates must see the prior value."""
        raw = _macro_frame("CPIAUCSL", ["2024-01-01", "2024-02-01"], [100.0, 200.0])
        shifted = apply_publication_lag(raw)  # available 02-15 and 03-17

        index = pd.date_range("2024-02-10", "2024-03-20", freq="D")
        s = as_of_series(shifted, "CPIAUCSL", index)

        # Before the Jan print publishes (02-15): nothing known
        assert pd.isna(s.loc["2024-02-14"])
        # After Jan publishes, before Feb publishes: see Jan value only
        assert s.loc["2024-02-16"] == 100.0
        assert s.loc["2024-03-16"] == 100.0
        # After Feb publishes (03-17): see Feb value
        assert s.loc["2024-03-18"] == 200.0

    def test_missing_series_returns_empty(self):
        raw = apply_publication_lag(_macro_frame("T10Y2Y", ["2024-01-02"]))
        index = pd.date_range("2024-01-01", periods=5)
        s = as_of_series(raw, "NOPE", index)
        assert s.isna().all()


@pytest.mark.unit
def test_get_data_applies_pit_by_default(monkeypatch):
    """get_data(pit=True default) must availability-shift macro frames."""
    from alpha_research.quant_data import api

    raw = _macro_frame("CPIAUCSL", ["2024-01-01"], [310.0])

    monkeypatch.setattr(api, "_fetch_single", lambda info, s, e, src: raw.copy())

    out = api.get_data("CPIAUCSL", start="2024-01-01", end="2024-12-31")
    assert "reference_date" in out.columns
    assert out.loc[0, "date"] == pd.Timestamp("2024-02-15")

    out_raw = api.get_data("CPIAUCSL", start="2024-01-01", end="2024-12-31", pit=False)
    assert out_raw.loc[0, "date"] == pd.Timestamp("2024-01-01")
