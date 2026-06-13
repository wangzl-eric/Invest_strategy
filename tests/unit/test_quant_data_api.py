"""Tests for alpha_research.quant_data.api — the unified data interface.

Everything here runs offline: the prices/fred dirs are redirected to tmp_path
and all network calls (yfinance/FRED/requests) are monkeypatched.
"""
from datetime import date, timedelta

import pandas as pd
import pytest

import alpha_research.quant_data.api as api
from alpha_research.quant_data.ticker_map import TickerInfo


@pytest.fixture
def cache_dirs(monkeypatch, tmp_path):
    """Redirect the prices dir (and a sibling fred/ dir) into tmp_path."""
    prices = tmp_path / "prices"
    prices.mkdir()
    (tmp_path / "fred").mkdir()
    monkeypatch.setattr(api, "_PRICES_DIR", prices)
    return tmp_path


def _price_info(canonical_id="SPY"):
    return TickerInfo(
        canonical_id=canonical_id,
        asset_class="etf",
        source="yfinance",
        dataset="equities",
        name=canonical_id,
    )


def _fred_info(canonical_id="DGS10"):
    return TickerInfo(
        canonical_id=canonical_id,
        asset_class="macro",
        source="fred",
        dataset="fred",
        name=canonical_id,
    )


def _write_price_parquet(prices_dir, ticker, dates, fname="bundle.parquet"):
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(dates),
            "ticker": ticker,
            "open": 1.0,
            "high": 1.0,
            "low": 1.0,
            "close": 100.0,
            "volume": 1000,
        }
    )
    df.to_parquet(prices_dir / fname, index=False)
    return df


def _write_fred_parquet(fred_dir, series_id, dates, value, fname):
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(dates),
            "series_id": series_id,
            "value": value,
        }
    )
    df.to_parquet(fred_dir / fname, index=False)
    return df


# ---------------------------------------------------------------------------
# Local parquet reads
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestReadParquetPrices:
    def test_reads_matching_ticker(self, cache_dirs):
        prices = cache_dirs / "prices"
        _write_price_parquet(prices, "SPY", pd.bdate_range("2020-01-01", periods=20))
        out = api._read_parquet_prices("SPY", "2020-01-01", "2020-02-01")
        assert out is not None
        assert (out["ticker"].str.upper() == "SPY").all()

    def test_missing_ticker_returns_none(self, cache_dirs):
        prices = cache_dirs / "prices"
        _write_price_parquet(prices, "SPY", pd.bdate_range("2020-01-01", periods=10))
        assert api._read_parquet_prices("TLT", "2020-01-01", "2020-02-01") is None

    def test_no_files_returns_none(self, cache_dirs):
        assert api._read_parquet_prices("SPY", "2020-01-01", "2020-02-01") is None


@pytest.mark.unit
class TestReadParquetMacro:
    def test_prefers_freshest_matching_file(self, cache_dirs):
        fred = cache_dirs / "fred"
        # Stale bundle ends earlier; fresh per-series cache ends later.
        _write_fred_parquet(
            fred,
            "DGS10",
            pd.bdate_range("2020-01-01", periods=10),
            1.0,
            "stale.parquet",
        )
        _write_fred_parquet(
            fred,
            "DGS10",
            pd.bdate_range("2020-01-01", periods=40),
            2.0,
            "fresh.parquet",
        )
        out = api._read_parquet_macro("DGS10", "2020-01-01", "2020-04-01")
        assert out is not None
        # Fresh file extends further than the stale one
        assert out["date"].max() > pd.Timestamp("2020-01-20")

    def test_searches_fred_dir(self, cache_dirs):
        fred = cache_dirs / "fred"
        _write_fred_parquet(
            fred,
            "VIXCLS",
            pd.bdate_range("2021-01-01", periods=30),
            18.0,
            "vix.parquet",
        )
        out = api._read_parquet_macro("VIXCLS", "2021-01-01", "2021-03-01")
        assert out is not None
        assert (out["series_id"] == "VIXCLS").all()

    def test_no_match_returns_none(self, cache_dirs):
        fred = cache_dirs / "fred"
        _write_fred_parquet(
            fred, "DGS10", pd.bdate_range("2021-01-01", periods=5), 1.0, "x.parquet"
        )
        assert api._read_parquet_macro("UNRATE", "2021-01-01", "2021-03-01") is None


# ---------------------------------------------------------------------------
# _fetch_single: staleness + fallback logic
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFetchSingle:
    def test_fresh_cache_served_without_api(self, cache_dirs, monkeypatch):
        prices = cache_dirs / "prices"
        end = date.today()
        dates = pd.bdate_range(end - timedelta(days=20), end)
        _write_price_parquet(prices, "SPY", dates)

        def _boom(*a, **k):
            raise AssertionError("API should not be called for a fresh cache")

        monkeypatch.setattr(api, "_fetch_yfinance", _boom)
        out = api._fetch_single(_price_info("SPY"), "2020-01-01", end.isoformat(), None)
        assert not out.empty

    def test_stale_cache_triggers_refresh(self, cache_dirs, monkeypatch):
        prices = cache_dirs / "prices"
        # Cache ends well before the requested end -> stale.
        _write_price_parquet(prices, "SPY", pd.bdate_range("2020-01-01", periods=10))

        fresh = pd.DataFrame(
            {
                "date": pd.bdate_range("2024-01-01", periods=5),
                "ticker": "SPY",
                "open": 1.0,
                "high": 1.0,
                "low": 1.0,
                "close": 200.0,
                "volume": 1,
            }
        )
        monkeypatch.setattr(api, "_fetch_yfinance", lambda *a, **k: fresh)
        out = api._fetch_single(_price_info("SPY"), "2020-01-01", "2024-01-10", None)
        assert (out["close"] == 200.0).all()
        # Refreshed result written back to cache dir
        assert (prices / "SPY.parquet").exists()

    def test_cache_miss_fetches_and_writes(self, cache_dirs, monkeypatch):
        prices = cache_dirs / "prices"
        fetched = pd.DataFrame(
            {
                "date": pd.bdate_range("2023-01-01", periods=5),
                "ticker": "QQQ",
                "open": 1.0,
                "high": 1.0,
                "low": 1.0,
                "close": 300.0,
                "volume": 1,
            }
        )
        monkeypatch.setattr(api, "_fetch_yfinance", lambda *a, **k: fetched)
        out = api._fetch_single(_price_info("QQQ"), "2023-01-01", "2023-01-10", None)
        assert not out.empty
        assert (prices / "QQQ.parquet").exists()

    def test_api_failure_falls_back_to_stale_cache(self, cache_dirs, monkeypatch):
        prices = cache_dirs / "prices"
        _write_price_parquet(prices, "SPY", pd.bdate_range("2020-01-01", periods=10))

        def _fail(*a, **k):
            raise RuntimeError("network down")

        monkeypatch.setattr(api, "_fetch_yfinance", _fail)
        out = api._fetch_single(_price_info("SPY"), "2020-01-01", "2024-01-10", None)
        # Stale cache returned instead of raising
        assert not out.empty
        assert (out["close"] == 100.0).all()

    def test_api_failure_no_cache_reraises(self, cache_dirs, monkeypatch):
        def _fail(*a, **k):
            raise RuntimeError("network down")

        monkeypatch.setattr(api, "_fetch_yfinance", _fail)
        with pytest.raises(RuntimeError, match="network down"):
            api._fetch_single(_price_info("NEW"), "2023-01-01", "2023-02-01", None)

    def test_empty_api_falls_back_to_stale_cache(self, cache_dirs, monkeypatch):
        prices = cache_dirs / "prices"
        _write_price_parquet(prices, "SPY", pd.bdate_range("2020-01-01", periods=10))
        empty = pd.DataFrame(
            columns=["date", "ticker", "open", "high", "low", "close", "volume"]
        )
        monkeypatch.setattr(api, "_fetch_yfinance", lambda *a, **k: empty)
        out = api._fetch_single(_price_info("SPY"), "2020-01-01", "2024-01-10", None)
        assert not out.empty

    def test_empty_api_no_cache_returns_empty(self, cache_dirs, monkeypatch):
        empty = pd.DataFrame(
            columns=["date", "ticker", "open", "high", "low", "close", "volume"]
        )
        monkeypatch.setattr(api, "_fetch_yfinance", lambda *a, **k: empty)
        out = api._fetch_single(_price_info("GHOST"), "2023-01-01", "2023-02-01", None)
        assert out.empty

    def test_fred_source_uses_macro_reader(self, cache_dirs, monkeypatch):
        fred = cache_dirs / "fred"
        end = date.today()
        dates = pd.bdate_range(end - timedelta(days=40), end)
        _write_fred_parquet(fred, "DGS10", dates, 1.5, "dgs10.parquet")

        def _boom(*a, **k):
            raise AssertionError("FRED API should not be called for a fresh cache")

        monkeypatch.setattr(api, "_fetch_fred", _boom)
        out = api._fetch_single(
            _fred_info("DGS10"), "2020-01-01", end.isoformat(), None
        )
        assert (out["series_id"] == "DGS10").all()

    def test_binance_source_dispatch(self, cache_dirs, monkeypatch):
        fetched = pd.DataFrame(
            {
                "date": pd.bdate_range("2023-01-01", periods=5),
                "ticker": "BTCUSDT",
                "open": 1.0,
                "high": 1.0,
                "low": 1.0,
                "close": 40000.0,
                "volume": 1,
            }
        )
        monkeypatch.setattr(api, "_fetch_binance", lambda *a, **k: fetched)
        info = TickerInfo(
            canonical_id="BTCUSDT",
            asset_class="crypto",
            source="binance",
            dataset="crypto",
            name="BTCUSDT",
        )
        out = api._fetch_single(info, "2023-01-01", "2023-01-10", "binance")
        assert (out["close"] == 40000.0).all()


# ---------------------------------------------------------------------------
# get_data: pit branches + dispatch
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetData:
    def test_pit_true_applies_publication_lag(self, cache_dirs, monkeypatch):
        macro = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-31", "2023-02-28"]),
                "series_id": "UNRATE",
                "value": [3.5, 3.6],
            }
        )
        monkeypatch.setattr(api, "_fetch_single", lambda *a, **k: macro.copy())
        monkeypatch.setattr(api, "resolve_strict", lambda q: _fred_info("UNRATE"))

        out = api.get_data("UNRATE", start="2023-01-01", end="2023-04-01", pit=True)
        # PIT mode keeps the original reference date in a separate column
        assert "reference_date" in out.columns
        assert (out["date"] <= pd.Timestamp("2023-04-01")).all()

    def test_pit_false_logs_warning_and_keeps_reference_dates(
        self, cache_dirs, monkeypatch, caplog
    ):
        macro = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-31"]),
                "series_id": "UNRATE",
                "value": [3.5],
            }
        )
        monkeypatch.setattr(api, "_fetch_single", lambda *a, **k: macro.copy())
        monkeypatch.setattr(api, "resolve_strict", lambda q: _fred_info("UNRATE"))

        with caplog.at_level("WARNING"):
            out = api.get_data(
                "UNRATE", start="2023-01-01", end="2023-04-01", pit=False
            )
        assert "reference_date" not in out.columns
        assert any("look-ahead" in r.message for r in caplog.records)

    def test_empty_frame_skipped(self, cache_dirs, monkeypatch):
        empty = pd.DataFrame()
        monkeypatch.setattr(api, "_fetch_single", lambda *a, **k: empty)
        monkeypatch.setattr(api, "resolve_strict", lambda q: _price_info("SPY"))
        out = api.get_data("SPY", start="2020-01-01", end="2020-02-01")
        assert out.empty

    def test_string_ticker_coerced_to_list(self, cache_dirs, monkeypatch):
        px = pd.DataFrame(
            {
                "date": pd.bdate_range("2020-01-01", periods=5),
                "ticker": "SPY",
                "close": 100.0,
            }
        )
        monkeypatch.setattr(api, "_fetch_single", lambda *a, **k: px.copy())
        monkeypatch.setattr(api, "resolve_strict", lambda q: _price_info("SPY"))
        out = api.get_data("SPY", start="2020-01-01", end="2020-02-01")
        assert (out["ticker"] == "SPY").all()

    def test_weekly_resample(self, cache_dirs, monkeypatch):
        px = pd.DataFrame(
            {
                "date": pd.bdate_range("2020-01-01", periods=20),
                "ticker": "SPY",
                "open": 1.0,
                "high": 2.0,
                "low": 0.5,
                "close": 100.0,
                "volume": 10,
            }
        )
        monkeypatch.setattr(api, "_fetch_single", lambda *a, **k: px.copy())
        monkeypatch.setattr(api, "resolve_strict", lambda q: _price_info("SPY"))
        out = api.get_data("SPY", start="2020-01-01", end="2020-02-01", frequency="1w")
        assert len(out) < 20  # resampled to weekly


# ---------------------------------------------------------------------------
# _resample directly (macro 'value' branch)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestResample:
    def test_macro_value_weekly(self):
        df = pd.DataFrame(
            {
                "date": pd.bdate_range("2020-01-01", periods=40),
                "series_id": "DGS10",
                "value": range(40),
            }
        )
        out = api._resample(df, "1w")
        assert "value" in out.columns
        assert len(out) < 40


# ---------------------------------------------------------------------------
# _fetch_fred_csv: fredgraph fallback parsing
# ---------------------------------------------------------------------------


class _StubResponse:
    def __init__(self, text, status=200):
        self.text = text
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


@pytest.mark.unit
class TestFetchFredCsv:
    def test_parses_fredgraph_csv_and_drops_missing(self, monkeypatch):
        csv = (
            "observation_date,DGS10\n"
            "2023-01-02,3.79\n"
            "2023-01-03,.\n"  # missing value -> dropped
            "2023-01-04,3.69\n"
        )

        def _get(url, timeout=30):
            assert "DGS10" in url
            return _StubResponse(csv)

        import requests

        monkeypatch.setattr(requests, "get", _get)
        out = api._fetch_fred_csv("DGS10", "2023-01-01", "2023-02-01")
        assert list(out.columns) == ["date", "series_id", "value"]
        assert len(out) == 2  # the '.' row dropped
        assert (out["series_id"] == "DGS10").all()
        assert out["value"].tolist() == [3.79, 3.69]

    def test_legacy_date_column(self, monkeypatch):
        csv = "DATE,UNRATE\n2023-01-01,3.5\n2023-02-01,3.6\n"

        def _get(url, timeout=30):
            return _StubResponse(csv)

        import requests

        monkeypatch.setattr(requests, "get", _get)
        out = api._fetch_fred_csv("UNRATE", "2023-01-01", "2023-03-01")
        assert len(out) == 2
        assert pd.api.types.is_datetime64_any_dtype(out["date"])


# ---------------------------------------------------------------------------
# _fetch_fred: pandas_datareader-missing fallback path
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFetchYfinance:
    def test_normalizes_columns_and_adds_ticker(self, monkeypatch):
        import sys
        import types

        idx = pd.bdate_range("2023-01-01", periods=3)
        raw = pd.DataFrame(
            {
                ("Open", "SPY"): [1.0, 1.1, 1.2],
                ("High", "SPY"): [1.0, 1.1, 1.2],
                ("Low", "SPY"): [1.0, 1.1, 1.2],
                ("Close", "SPY"): [100.0, 101.0, 102.0],
                ("Volume", "SPY"): [10, 11, 12],
            },
            index=idx,
        )
        raw.index.name = "Date"

        fake_yf = types.SimpleNamespace(download=lambda *a, **k: raw)
        monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
        out = api._fetch_yfinance("SPY", "2023-01-01", "2023-01-10")
        assert list(out.columns) == [
            "date",
            "ticker",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        assert (out["ticker"] == "SPY").all()

    def test_empty_download_returns_empty_schema(self, monkeypatch):
        import sys
        import types

        fake_yf = types.SimpleNamespace(download=lambda *a, **k: pd.DataFrame())
        monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
        out = api._fetch_yfinance("SPY", "2023-01-01", "2023-01-10")
        assert out.empty
        assert "close" in out.columns


@pytest.mark.unit
class TestFetchBinance:
    def test_http_fallback_parses_klines(self, monkeypatch):
        # Force the connector import to fail so the raw HTTP path runs.
        import builtins

        real_import = builtins.__import__

        def _fake_import(name, *args, **kwargs):
            if "binance_public" in name:
                raise ImportError("no connector")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fake_import)

        kline = [
            1672531200000,  # open_time (2023-01-01)
            "16500.0",
            "16600.0",
            "16400.0",
            "16550.0",
            "1234.5",
            1672617599999,
            "0",
            10,
            "0",
            "0",
            "0",
        ]
        calls = {"n": 0}

        def _get(url, params=None, timeout=10):
            calls["n"] += 1
            return _StubResponse_json([kline] if calls["n"] == 1 else [])

        import requests

        monkeypatch.setattr(requests, "get", _get)
        out = api._fetch_binance("BTCUSDT", "2023-01-01", "2023-01-03")
        assert list(out.columns) == [
            "date",
            "ticker",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        assert (out["ticker"] == "BTCUSDT").all()
        assert out["close"].iloc[0] == 16550.0

    def test_http_fallback_empty(self, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def _fake_import(name, *args, **kwargs):
            if "binance_public" in name:
                raise ImportError("no connector")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fake_import)

        import requests

        monkeypatch.setattr(requests, "get", lambda *a, **k: _StubResponse_json([]))
        out = api._fetch_binance("BTCUSDT", "2023-01-01", "2023-01-03")
        assert out.empty


class _StubResponse_json:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


@pytest.mark.unit
class TestFetchFred:
    def test_falls_back_to_csv_when_datareader_missing(self, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def _fake_import(name, *args, **kwargs):
            if name.startswith("pandas_datareader"):
                raise ImportError("no datareader")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fake_import)

        sentinel = pd.DataFrame(
            {
                "date": pd.to_datetime(["2023-01-01"]),
                "series_id": "DGS10",
                "value": [1.0],
            }
        )
        monkeypatch.setattr(api, "_fetch_fred_csv", lambda *a, **k: sentinel)
        out = api._fetch_fred("DGS10", "2023-01-01", "2023-02-01")
        assert out.equals(sentinel)

    def test_uses_datareader_when_available(self, monkeypatch):
        import sys
        import types

        idx = pd.DatetimeIndex(
            pd.to_datetime(["2023-01-01", "2023-02-01"]), name="DATE"
        )
        reader_df = pd.DataFrame({"DGS10": [3.5, 3.6]}, index=idx)

        fake_web = types.SimpleNamespace(
            DataReader=lambda series_id, source, start, end, **kw: reader_df.copy()
        )
        fake_pdr = types.ModuleType("pandas_datareader")
        fake_pdr_data = types.ModuleType("pandas_datareader.data")
        fake_pdr_data.web = fake_web
        # `import pandas_datareader.data as web` -> module object exposing DataReader
        fake_pdr_data.DataReader = fake_web.DataReader
        monkeypatch.setitem(sys.modules, "pandas_datareader", fake_pdr)
        monkeypatch.setitem(sys.modules, "pandas_datareader.data", fake_pdr_data)
        monkeypatch.delenv("FRED_API_KEY", raising=False)

        out = api._fetch_fred("DGS10", "2023-01-01", "2023-03-01")
        assert list(out.columns) == ["date", "series_id", "value"]
        assert (out["series_id"] == "DGS10").all()
        assert out["value"].tolist() == [3.5, 3.6]
