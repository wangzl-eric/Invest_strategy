"""Offline unit tests for the akshare global connector.

These run with **no network**: akshare is replaced by a fake module exposing
the handful of functions the connector calls. They lock in the normalization,
retry, dispatch, and discovery behavior so the contract can't silently drift.

Live connectivity is checked separately in
``tests/integration/test_akshare_connection.py`` (marked ``requires_network``).
"""
from __future__ import annotations

import sys

import pandas as pd
import pytest

from alpha_research.quant_data.connectors.akshare_global import (
    AKSHARE_BARS_DATASETS,
    AkShareConnector,
    AkShareUnavailable,
    _is_transient,
    _with_retry,
    normalize_bars,
)

CANON = [
    "timestamp",
    "symbol",
    "venue",
    "currency",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "vwap",
]


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


def _en_ohlcv():
    """Sina-style English OHLCV frame (us_stock/hk_stock/index/cn_stock)."""
    return pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-03", "2024-01-04"],
            "open": [1.0, 2.0, 3.0],
            "high": [1.5, 2.5, 3.5],
            "low": [0.5, 1.5, 2.5],
            "close": [1.2, 2.2, 3.2],
            "volume": [100, 200, 300],
            "amount": [120, 440, 960],  # extra col must be dropped
        }
    )


def _cn_yield_wide():
    return pd.DataFrame(
        {
            "日期": ["2024-01-02", "2024-01-03"],
            "中国国债收益率10年": [2.56, 2.55],
            "美国国债收益率10年": [3.95, 3.91],
            "美国GDP年增率": [None, None],  # all-NaN col -> melted rows dropped
        }
    )


def _crypto_snapshot():
    return pd.DataFrame(
        {
            "市场": ["Bitfinex"],
            "交易品种": ["BTCUSD"],
            "最近报价": [42000.0],
            "涨跌额": [100.0],
            "涨跌幅": [0.2],
            "24小时最高": [42500.0],
            "24小时最低": [41000.0],
            "24小时成交量": [123.4],
            "更新时间": ["2024-01-02 10:00:00"],
        }
    )


def _fx_snapshot():
    return pd.DataFrame({"货币对": ["EUR/USD"], "买报价": [1.10], "卖报价": [1.11]})


class _FakeAk:
    """Stand-in akshare module; records calls and returns canned frames."""

    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    def stock_us_daily(self, **kw):
        self.calls.append(("stock_us_daily", kw))
        return _en_ohlcv()

    def stock_hk_daily(self, **kw):
        self.calls.append(("stock_hk_daily", kw))
        return _en_ohlcv()

    def stock_zh_a_daily(self, **kw):
        self.calls.append(("stock_zh_a_daily", kw))
        return _en_ohlcv()

    def index_us_stock_sina(self, **kw):
        self.calls.append(("index_us_stock_sina", kw))
        return _en_ohlcv()

    def stock_zh_index_daily(self, **kw):
        self.calls.append(("stock_zh_index_daily", kw))
        return _en_ohlcv()

    def forex_hist_em(self, **kw):
        self.calls.append(("forex_hist_em", kw))
        return _en_ohlcv()

    def bond_zh_us_rate(self, **kw):
        self.calls.append(("bond_zh_us_rate", kw))
        return _cn_yield_wide()

    def crypto_js_spot(self, **kw):
        self.calls.append(("crypto_js_spot", kw))
        return _crypto_snapshot()

    def fx_spot_quote(self, **kw):
        self.calls.append(("fx_spot_quote", kw))
        return _fx_snapshot()

    def macro_china_cpi(self, **kw):
        self.calls.append(("macro_china_cpi", kw))
        return pd.DataFrame({"月份": ["2024年01月份"], "全国-同比增长": [1.2]})


@pytest.fixture
def fake_conn(monkeypatch):
    fake = _FakeAk()
    c = AkShareConnector(base_delay=0)
    monkeypatch.setattr(c, "_ak", fake)  # inject fake, bypass lazy import
    return c, fake


# ---------------------------------------------------------------------------
# Retry classification
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRetry:
    def test_transient_markers_detected(self):
        assert _is_transient(ConnectionError("Connection aborted."))
        assert _is_transient(RuntimeError("Remote end closed connection"))
        assert _is_transient(TimeoutError("Read timed out"))

    def test_non_transient_not_retried(self):
        assert not _is_transient(KeyError("no such symbol"))
        assert not _is_transient(ValueError("bad arg"))

    def test_retries_then_succeeds(self):
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise ConnectionError("Connection aborted.")
            return pd.DataFrame({"ok": [1]})

        out = _with_retry(flaky, attempts=3, base_delay=0, sleep=lambda _: None)
        assert calls["n"] == 3
        assert not out.empty

    def test_gives_up_after_attempts(self):
        def always_fail():
            raise ConnectionError("Connection aborted.")

        with pytest.raises(ConnectionError):
            _with_retry(always_fail, attempts=2, base_delay=0, sleep=lambda _: None)

    def test_non_transient_raises_immediately(self):
        calls = {"n": 0}

        def boom():
            calls["n"] += 1
            raise KeyError("nope")

        with pytest.raises(KeyError):
            _with_retry(boom, attempts=3, base_delay=0, sleep=lambda _: None)
        assert calls["n"] == 1  # not retried


# ---------------------------------------------------------------------------
# normalize_bars
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNormalize:
    def test_canonical_schema_and_metadata(self):
        spec = AKSHARE_BARS_DATASETS["us_stock"]
        out = normalize_bars(_en_ohlcv(), spec, "aapl")
        assert list(out.columns) == CANON
        assert (out["symbol"] == "AAPL").all()  # upper-cased
        assert (out["venue"] == "US").all()
        assert (out["currency"] == "USD").all()
        assert str(out["timestamp"].dt.tz) == "UTC"
        assert "amount" not in out.columns  # extra vendor col dropped

    def test_numeric_coercion(self):
        spec = AKSHARE_BARS_DATASETS["us_stock"]
        df = _en_ohlcv()
        df["close"] = df["close"].astype(str)  # vendor sometimes returns strings
        out = normalize_bars(df, spec, "AAPL")
        assert pd.api.types.is_numeric_dtype(out["close"])

    def test_empty_returns_canonical_columns(self):
        spec = AKSHARE_BARS_DATASETS["hk_stock"]
        out = normalize_bars(pd.DataFrame(), spec, "00700")
        assert list(out.columns) == CANON
        assert out.empty

    def test_sorted_by_timestamp(self):
        spec = AKSHARE_BARS_DATASETS["us_stock"]
        df = _en_ohlcv().iloc[::-1]  # reversed
        out = normalize_bars(df, spec, "AAPL")
        assert out["timestamp"].is_monotonic_increasing


# ---------------------------------------------------------------------------
# fetch_bars dispatch + date handling
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFetchBars:
    @pytest.mark.parametrize(
        "dataset,func",
        [
            ("us_stock", "stock_us_daily"),
            ("hk_stock", "stock_hk_daily"),
            ("cn_stock", "stock_zh_a_daily"),
            ("us_index", "index_us_stock_sina"),
            ("cn_index", "stock_zh_index_daily"),
            ("forex", "forex_hist_em"),
        ],
    )
    def test_each_dataset_dispatches_to_its_function(self, fake_conn, dataset, func):
        c, fake = fake_conn
        out = c.fetch_bars(dataset, "X")
        assert not out.empty
        assert list(out.columns) == CANON
        assert fake.calls[-1][0] == func

    def test_unknown_dataset_raises(self, fake_conn):
        c, _ = fake_conn
        with pytest.raises(KeyError, match="unknown akshare dataset"):
            c.fetch_bars("not_a_dataset", "X")

    def test_ymd_dataset_passes_formatted_dates(self, fake_conn):
        c, fake = fake_conn
        c.fetch_bars("cn_stock", "sh600000", start="2024-01-01", end="2024-01-31")
        _, kw = fake.calls[-1]
        assert kw["start_date"] == "20240101"
        assert kw["end_date"] == "20240131"
        assert kw["adjust"] == "qfq"  # extra_kwargs forwarded

    def test_iso_dataset_filters_client_side(self, fake_conn):
        c, fake = fake_conn
        # Fake returns 2024-01-02..04; window should clip to the 3rd only.
        out = c.fetch_bars("us_stock", "AAPL", start="2024-01-03", end="2024-01-03")
        _, kw = fake.calls[-1]
        assert "start_date" not in kw  # iso style doesn't pass server-side dates
        assert len(out) == 1
        assert out["timestamp"].iloc[0] == pd.Timestamp("2024-01-03", tz="UTC")


# ---------------------------------------------------------------------------
# Non-bars helpers
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNonBars:
    def test_treasury_yields_long_format(self, fake_conn):
        c, _ = fake_conn
        out = c.us_treasury_yields(start="2024-01-01")
        assert list(out.columns) == ["date", "series_id", "value"]
        # all-NaN US GDP column melted then dropped
        assert "美国GDP年增率" not in out["series_id"].unique()
        assert {"中国国债收益率10年", "美国国债收益率10年"} <= set(out["series_id"])

    def test_crypto_spot_normalized_columns(self, fake_conn):
        c, _ = fake_conn
        out = c.crypto_spot()
        assert {"venue", "symbol", "price"} <= set(out.columns)

    def test_fx_spot_normalized_columns(self, fake_conn):
        c, _ = fake_conn
        out = c.fx_spot()
        assert list(out.columns) == ["pair", "bid", "ask"]

    def test_macro_dispatch(self, fake_conn):
        c, fake = fake_conn
        out = c.macro("macro_china_cpi")
        assert not out.empty
        assert fake.calls[-1][0] == "macro_china_cpi"

    def test_macro_rejects_non_macro_func(self, fake_conn):
        c, _ = fake_conn
        with pytest.raises(ValueError, match="macro_"):
            c.macro("stock_us_daily")


# ---------------------------------------------------------------------------
# Discovery + connection
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDiscoveryAndConnection:
    def test_list_datasets_exposes_catalog(self):
        ds = AkShareConnector.list_datasets()
        keys = {d["key"] for d in ds}
        assert {"us_stock", "hk_stock", "cn_stock", "us_index", "cn_index"} <= keys
        for d in ds:
            assert {"func", "universe", "venue", "currency", "reliable"} <= set(d)

    def test_reliability_flags(self):
        assert AKSHARE_BARS_DATASETS["us_stock"].reliable is True
        assert AKSHARE_BARS_DATASETS["forex"].reliable is False  # EastMoney

    def test_check_connection_true_on_data(self, fake_conn):
        c, _ = fake_conn
        assert c.check_connection() is True

    def test_dataset_id_is_canonical(self):
        did = AKSHARE_BARS_DATASETS["us_stock"].dataset_id()
        assert did.provider == "akshare"
        assert did.slug() == "akshare/bars/us_equities/1d"


# ---------------------------------------------------------------------------
# Lazy import failure
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLazyImport:
    def test_missing_akshare_raises_clear_error(self, monkeypatch):
        # Make `import akshare` fail, then access the lazy property.
        monkeypatch.setitem(sys.modules, "akshare", None)
        c = AkShareConnector()
        with pytest.raises(AkShareUnavailable, match="not installed"):
            _ = c.ak
