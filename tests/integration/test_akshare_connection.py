"""Live connectivity regtest for the akshare global connector.

This is the "check connection" regression test from the data-infra goal: it makes
**real** network calls to akshare and asserts that the reliable global backbone
(US/HK/CN equities, US/CN indices, treasury yields, FX & crypto snapshots)
actually returns well-formed data.

Markers / gating
----------------
- ``requires_network`` + ``integration`` + ``slow`` — excluded from the default
  unit run; opt in with ``pytest -m requires_network``.
- Skips cleanly (not fails) when akshare is missing or there is no internet, so
  an offline CI box is never red for reasons outside the code's control.
- EastMoney-backed datasets (``reliable=False``, e.g. ``forex``) are *best
  effort*: ``push2his.eastmoney.com`` routinely blocks non-CN IPs, so a transient
  failure there is reported as ``xfail`` rather than failing the suite. The
  Sina-backed reliable backbone is asserted hard.
"""
from __future__ import annotations

import socket

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.requires_network,
    pytest.mark.slow,
]

ak = pytest.importorskip("akshare", reason="akshare not installed")

from alpha_research.quant_data.connectors.akshare_global import (  # noqa: E402
    AKSHARE_BARS_DATASETS,
    AkShareConnector,
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

# One representative, liquid symbol per reliable bars dataset.
RELIABLE_BARS = [
    ("us_stock", "AAPL"),
    ("hk_stock", "00700"),
    ("cn_stock", "sh600000"),
    ("us_index", ".INX"),
    ("cn_index", "sh000001"),
]

# EastMoney-backed datasets: validated best-effort.
BEST_EFFORT_BARS = [
    ("forex", "USDCNH"),
]

_START = "2024-01-01"
_END = "2024-02-01"


def _has_internet(host: str = "8.8.8.8", port: int = 53, timeout: float = 3.0) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False


@pytest.fixture(scope="module", autouse=True)
def _require_internet():
    if not _has_internet():
        pytest.skip("no internet connectivity")


@pytest.fixture(scope="module")
def conn():
    return AkShareConnector()


@pytest.mark.parametrize(
    "dataset,symbol", RELIABLE_BARS, ids=[d for d, _ in RELIABLE_BARS]
)
def test_reliable_bars_connect(conn, dataset, symbol):
    """Each reliable dataset returns non-empty, canonical, in-window bars."""
    df = conn.fetch_bars(dataset, symbol, start=_START, end=_END)
    assert not df.empty, f"{dataset}:{symbol} returned no rows"
    assert list(df.columns) == CANON
    assert str(df["timestamp"].dt.tz) == "UTC"
    assert df["timestamp"].is_monotonic_increasing
    # Window respected.
    assert df["timestamp"].min() >= __import__("pandas").Timestamp(_START, tz="UTC")
    # Prices are positive numbers.
    assert (df["close"].dropna() > 0).all()
    assert (df["symbol"] == symbol.upper()).all()


@pytest.mark.parametrize(
    "dataset,symbol", BEST_EFFORT_BARS, ids=[d for d, _ in BEST_EFFORT_BARS]
)
def test_best_effort_bars_connect(conn, dataset, symbol):
    """EastMoney datasets: pass if reachable, xfail if the endpoint blocks us."""
    assert AKSHARE_BARS_DATASETS[dataset].reliable is False
    try:
        df = conn.fetch_bars(dataset, symbol, start=_START, end=_END)
    except Exception as exc:  # noqa: BLE001 - upstream block, not our bug
        pytest.xfail(f"{dataset} endpoint unreachable: {exc}")
    if df.empty:
        pytest.xfail(f"{dataset} endpoint returned no rows")
    assert list(df.columns) == CANON


def test_treasury_yields_connect(conn):
    df = conn.us_treasury_yields(start=_START, end=_END)
    assert not df.empty
    assert list(df.columns) == ["date", "series_id", "value"]
    series = set(df["series_id"])
    # Both China and US tenors should be present.
    assert any("美国国债收益率" in s for s in series)
    assert any("中国国债收益率" in s for s in series)


def test_crypto_spot_connect(conn):
    df = conn.crypto_spot()
    assert not df.empty
    assert {"venue", "symbol", "price"} <= set(df.columns)


def test_fx_spot_connect(conn):
    df = conn.fx_spot()
    assert not df.empty
    assert {"pair", "bid", "ask"} <= set(df.columns)


def test_check_connection_helper(conn):
    assert conn.check_connection() is True


def test_catalog_matches_live_functions(conn):
    """Every cataloged bars function actually exists on the akshare module."""
    for spec in AKSHARE_BARS_DATASETS.values():
        assert hasattr(conn.ak, spec.func), f"akshare missing {spec.func}"
