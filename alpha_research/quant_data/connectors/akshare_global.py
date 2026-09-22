"""AkShare global multi-asset connector (research only).

`akshare <https://akshare.akfamily.xyz>`_ is a free, keyless aggregator exposing
1000+ endpoints across Chinese **and** global markets. This connector wraps the
subset that gives broad *global* coverage and normalizes everything to the
canonical schemas in :mod:`alpha_research.quant_data.spec`.

Design
------
- A small, declarative **dataset catalog** (:data:`AKSHARE_BARS_DATASETS`) maps a
  stable logical key (e.g. ``"us_stock"``) to the akshare function, the argument
  convention, a vendor→canonical column rename map, and venue/currency metadata.
  Adding coverage is a one-line catalog entry, not new code.
- akshare returns a mix of English- and Chinese-titled columns depending on the
  upstream source (Sina/EastMoney/...). The rename maps cover both.
- EastMoney/Sina endpoints occasionally drop a connection mid-stream; every call
  goes through :func:`_with_retry` (bounded exponential backoff).

This is a **research / idea-generation** data source, not an execution feed.
Nothing here is imported by ``core`` (layering rule); akshare is imported lazily
so the rest of the platform works without it installed.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

import pandas as pd

from alpha_research.quant_data.spec import (
    DatasetFrequency,
    DatasetId,
    MarketDataKind,
    validate_columns,
)

log = logging.getLogger(__name__)

CANONICAL_BARS = (
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
)


class AkShareUnavailable(RuntimeError):
    """Raised when the akshare package is not importable."""


def _import_akshare():
    try:
        import akshare as ak  # noqa: WPS433 (lazy import is intentional)
    except Exception as exc:  # pragma: no cover - exercised only when missing
        raise AkShareUnavailable(
            "akshare is not installed. `pip install akshare` (see requirements.txt)."
        ) from exc
    return ak


# ---------------------------------------------------------------------------
# Retry: EastMoney/Sina endpoints are flaky under burst load
# ---------------------------------------------------------------------------

# Transient network failures worth retrying. Matched on the exception's str so we
# don't depend on importing urllib3/requests exception classes here.
_TRANSIENT_MARKERS = (
    "RemoteDisconnected",
    "Connection aborted",
    "Connection reset",
    "timed out",
    "Read timed out",
    "Max retries exceeded",
    "Temporary failure",
    "Remote end closed",
)


def _is_transient(exc: Exception) -> bool:
    msg = f"{type(exc).__name__}: {exc}"
    return any(marker in msg for marker in _TRANSIENT_MARKERS)


def _with_retry(
    fn: Callable[[], pd.DataFrame],
    *,
    attempts: int = 3,
    base_delay: float = 0.8,
    label: str = "akshare call",
    sleep: Callable[[float], None] = time.sleep,
) -> pd.DataFrame:
    """Call *fn* with bounded exponential backoff on transient network errors."""
    last: Optional[Exception] = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - classify, then re-raise
            last = exc
            if not _is_transient(exc) or i == attempts - 1:
                raise
            delay = base_delay * (2**i)
            log.warning(
                "%s failed (%s); retry %d/%d in %.1fs",
                label,
                exc,
                i + 1,
                attempts - 1,
                delay,
            )
            sleep(delay)
    assert last is not None  # for type-checkers; unreachable
    raise last


# ---------------------------------------------------------------------------
# Bars dataset catalog
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AkBarsSpec:
    """Declarative description of one akshare *bars* (OHLCV) dataset."""

    key: str
    func: str  # akshare function name
    universe: str
    venue: str
    currency: str
    rename: dict[str, str]
    # How the symbol + date window are passed to the akshare function.
    symbol_arg: str = "symbol"
    # date_style: "ymd" -> 20240101 kwargs, "iso" -> client-side filter only,
    # "none" -> function takes no date args (full history; filtered locally).
    date_style: str = "none"
    start_arg: str = "start_date"
    end_arg: str = "end_date"
    extra_kwargs: dict[str, str] = field(default_factory=dict)
    description: str = ""
    upstream: str = "sina"  # upstream source: sina | eastmoney | other
    # Reliable from any region? EastMoney (push2his.eastmoney.com) frequently
    # blocks/rate-limits non-CN IPs; such datasets are best-effort and the live
    # regtest treats their failure as a skip rather than a hard error.
    reliable: bool = True

    def dataset_id(self) -> DatasetId:
        return DatasetId(
            provider="akshare",
            kind=MarketDataKind.BARS,
            universe=self.universe,
            frequency=DatasetFrequency.DAY,
        )


# Vendor column maps. akshare mixes English (Sina US/HK) and Chinese (EastMoney).
_EN_OHLCV = {
    "date": "timestamp",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
}
_CN_OHLCV = {
    "日期": "timestamp",
    "开盘": "open",
    "最高": "high",
    "最低": "low",
    "收盘": "close",
    "成交量": "volume",
}


AKSHARE_BARS_DATASETS: dict[str, AkBarsSpec] = {
    "us_stock": AkBarsSpec(
        key="us_stock",
        func="stock_us_daily",
        universe="us_equities",
        venue="US",
        currency="USD",
        rename=dict(_EN_OHLCV),
        date_style="iso",
        description="US equities daily OHLCV (Sina). Symbol e.g. 'AAPL', 'MSFT'.",
    ),
    "hk_stock": AkBarsSpec(
        key="hk_stock",
        func="stock_hk_daily",
        universe="hk_equities",
        venue="HKEX",
        currency="HKD",
        rename=dict(_EN_OHLCV),
        date_style="iso",
        description="Hong Kong equities daily OHLCV (Sina). Symbol e.g. '00700'.",
    ),
    "cn_stock": AkBarsSpec(
        key="cn_stock",
        func="stock_zh_a_daily",
        universe="cn_equities",
        venue="SSE/SZSE",
        currency="CNY",
        rename=dict(_EN_OHLCV),
        date_style="ymd",
        extra_kwargs={"adjust": "qfq"},
        upstream="sina",
        description="China A-share daily OHLCV, fwd-adjusted (Sina). Symbol e.g. 'sh600000', 'sz000001'.",
    ),
    "us_index": AkBarsSpec(
        key="us_index",
        func="index_us_stock_sina",
        universe="us_indices",
        venue="US",
        currency="USD",
        rename=dict(_EN_OHLCV),
        date_style="iso",
        description="US index daily OHLCV (Sina). Symbol e.g. '.INX' (S&P 500), '.DJI', '.IXIC'.",
    ),
    "cn_index": AkBarsSpec(
        key="cn_index",
        func="stock_zh_index_daily",
        universe="cn_indices",
        venue="SSE/SZSE",
        currency="CNY",
        rename=dict(_EN_OHLCV),
        date_style="iso",
        description="China index daily OHLCV (Sina). Symbol e.g. 'sh000001', 'sz399001'.",
    ),
    "forex": AkBarsSpec(
        key="forex",
        func="forex_hist_em",
        universe="fx_pairs",
        venue="FX",
        currency="",
        rename=dict(_EN_OHLCV)
        | {
            "日期": "timestamp",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
        },
        date_style="iso",
        upstream="eastmoney",
        reliable=False,
        description="FX pair daily OHLC (EastMoney). Symbol e.g. 'USDCNH', 'EURUSD'.",
    ),
}


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def normalize_bars(df: pd.DataFrame, spec: AkBarsSpec, symbol: str) -> pd.DataFrame:
    """Map a raw akshare OHLCV frame onto the canonical bars schema."""
    if df is None or df.empty:
        return pd.DataFrame(columns=CANONICAL_BARS)

    out = df.rename(columns=spec.rename)
    # Keep only canonical OHLCV columns that survived the rename.
    keep = [
        c
        for c in ("timestamp", "open", "high", "low", "close", "volume")
        if c in out.columns
    ]
    out = out[keep].copy()

    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce", utc=True)
    out = out.dropna(subset=["timestamp"])
    for col in ("open", "high", "low", "close", "volume"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
        else:
            out[col] = pd.NA

    out["symbol"] = str(symbol).upper()
    out["venue"] = spec.venue
    out["currency"] = spec.currency
    out["vwap"] = pd.NA

    out = out[list(CANONICAL_BARS)].sort_values("timestamp").reset_index(drop=True)
    validate_columns(
        dataset=f"akshare {spec.key}",
        columns=out.columns,
        required=("timestamp", "symbol", "open", "high", "low", "close", "volume"),
    )
    return out


def _filter_window(
    df: pd.DataFrame, start: Optional[str], end: Optional[str]
) -> pd.DataFrame:
    if df.empty:
        return df
    if start:
        df = df[df["timestamp"] >= pd.Timestamp(start, tz="UTC")]
    if end:
        end_ts = (
            pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        )
        df = df[df["timestamp"] <= end_ts]
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


class AkShareConnector:
    """Unified, normalized access to akshare's global datasets.

    Examples
    --------
    >>> c = AkShareConnector()
    >>> c.fetch_bars("us_stock", "AAPL", start="2024-01-01", end="2024-02-01")
    >>> c.fetch_bars("hk_stock", "00700")
    >>> c.us_treasury_yields(start="2024-01-01")
    >>> c.crypto_spot()
    """

    provider = "akshare"

    def __init__(self, *, attempts: int = 3, base_delay: float = 0.8):
        self._ak = None  # lazy
        self._attempts = attempts
        self._base_delay = base_delay

    @property
    def ak(self):
        if self._ak is None:
            self._ak = _import_akshare()
        return self._ak

    # -- discovery ---------------------------------------------------------

    @staticmethod
    def list_datasets() -> list[dict]:
        """Return the catalog of supported bars datasets (for discovery/UI)."""
        return [
            {
                "key": s.key,
                "func": s.func,
                "universe": s.universe,
                "venue": s.venue,
                "currency": s.currency,
                "upstream": s.upstream,
                "reliable": s.reliable,
                "description": s.description,
            }
            for s in AKSHARE_BARS_DATASETS.values()
        ]

    # -- bars --------------------------------------------------------------

    def fetch_bars(
        self,
        dataset: str,
        symbol: str,
        *,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> pd.DataFrame:
        """Fetch canonical daily bars for *symbol* from a catalog *dataset*."""
        if dataset not in AKSHARE_BARS_DATASETS:
            raise KeyError(
                f"unknown akshare dataset '{dataset}'. "
                f"Known: {sorted(AKSHARE_BARS_DATASETS)}"
            )
        spec = AKSHARE_BARS_DATASETS[dataset]
        func = getattr(self.ak, spec.func)

        kwargs: dict[str, object] = {spec.symbol_arg: symbol}
        kwargs.update(spec.extra_kwargs)
        if spec.date_style == "ymd":
            if start:
                kwargs[spec.start_arg] = pd.Timestamp(start).strftime("%Y%m%d")
            if end:
                kwargs[spec.end_arg] = pd.Timestamp(end).strftime("%Y%m%d")

        raw = _with_retry(
            lambda: func(**kwargs),
            attempts=self._attempts,
            base_delay=self._base_delay,
            label=f"{spec.func}({symbol})",
        )
        out = normalize_bars(raw, spec, symbol)
        # ymd functions already filtered server-side; iso/none need local filter.
        if spec.date_style != "ymd":
            out = _filter_window(out, start, end)
        return out

    # -- bonds -------------------------------------------------------------

    def us_treasury_yields(
        self, *, start: Optional[str] = None, end: Optional[str] = None
    ) -> pd.DataFrame:
        """US + China treasury yield curve, long format (date, series_id, value).

        Wraps ``bond_zh_us_rate`` (China & US tenors in one wide frame).
        """
        kwargs = {}
        if start:
            kwargs["start_date"] = pd.Timestamp(start).strftime("%Y%m%d")
        raw = _with_retry(
            lambda: self.ak.bond_zh_us_rate(**kwargs),
            attempts=self._attempts,
            base_delay=self._base_delay,
            label="bond_zh_us_rate",
        )
        if raw is None or raw.empty:
            return pd.DataFrame(columns=["date", "series_id", "value"])
        df = raw.rename(columns={"日期": "date"})
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        long = df.melt(id_vars="date", var_name="series_id", value_name="value")
        long = long.dropna(subset=["value"]).reset_index(drop=True)
        if start:
            long = long[long["date"] >= pd.Timestamp(start)]
        if end:
            long = long[long["date"] <= pd.Timestamp(end)]
        return long.sort_values(["series_id", "date"]).reset_index(drop=True)

    # -- crypto ------------------------------------------------------------

    def crypto_spot(self) -> pd.DataFrame:
        """Global crypto spot snapshot across venues (normalized column names)."""
        raw = _with_retry(
            lambda: self.ak.crypto_js_spot(),
            attempts=self._attempts,
            base_delay=self._base_delay,
            label="crypto_js_spot",
        )
        if raw is None or raw.empty:
            return pd.DataFrame()
        return raw.rename(
            columns={
                "市场": "venue",
                "交易品种": "symbol",
                "最近报价": "price",
                "涨跌额": "change",
                "涨跌幅": "change_pct",
                "24小时最高": "high_24h",
                "24小时最低": "low_24h",
                "24小时成交量": "volume_24h",
                "更新时间": "updated_at",
            }
        )

    def fx_spot(self) -> pd.DataFrame:
        """Global FX spot quote snapshot (bid/ask per currency pair, Sina)."""
        raw = _with_retry(
            lambda: self.ak.fx_spot_quote(),
            attempts=self._attempts,
            base_delay=self._base_delay,
            label="fx_spot_quote",
        )
        if raw is None or raw.empty:
            return pd.DataFrame()
        return raw.rename(columns={"货币对": "pair", "买报价": "bid", "卖报价": "ask"})

    # -- macro -------------------------------------------------------------

    def macro(self, func: str, **kwargs) -> pd.DataFrame:
        """Escape hatch to any akshare ``macro_*`` function, with retry.

        akshare exposes 100+ macro series (``macro_china_cpi``,
        ``macro_usa_gdp_monthly``, ``macro_china_pmi``, ...). Column names stay
        as akshare returns them — too heterogeneous to normalize generically.
        """
        if not func.startswith("macro_"):
            raise ValueError("macro() only dispatches akshare macro_* functions")
        fn = getattr(self.ak, func)
        return _with_retry(
            lambda: fn(**kwargs),
            attempts=self._attempts,
            base_delay=self._base_delay,
            label=func,
        )

    # -- connection health -------------------------------------------------

    def check_connection(self, dataset: str = "us_stock", symbol: str = "AAPL") -> bool:
        """Lightweight live ping: fetch one symbol and assert non-empty bars.

        Returns True on success; raises on hard (non-transient) failure so the
        regtest surfaces the real error.
        """
        df = self.fetch_bars(dataset, symbol)
        return not df.empty
