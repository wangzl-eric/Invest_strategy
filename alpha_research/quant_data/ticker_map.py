"""Ticker registry and natural-language resolver.

Seeds from config/ticker_universe.py plus hand-coded FRED shortcuts and
NL aliases so agents can resolve queries like '10-year yield' → DGS10.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class TickerInfo:
    """Canonical descriptor for a single instrument or data series."""

    canonical_id: str  # e.g. "DGS10", "SPY", "EURUSD=X"
    asset_class: str  # "equity"|"etf"|"macro"|"fx"|"crypto"
    source: str  # "yfinance"|"fred"|"stooq"|"ecb"|"binance"
    dataset: str  # DatasetSpec key used by the old pipeline
    name: str  # Human-readable label
    aliases: tuple[str, ...] = field(default_factory=tuple)  # NL aliases


# ---------------------------------------------------------------------------
# Registry seed data
# ---------------------------------------------------------------------------

_FRED_ENTRIES: list[dict] = [
    {
        "id": "VIXCLS",
        "name": "CBOE Volatility Index (VIX)",
        "aliases": ("vix", "fear index", "volatility index"),
    },
    {"id": "VVIX", "name": "VIX of VIX", "aliases": ("vvix",)},
    {
        "id": "DGS10",
        "name": "10-Year Treasury Yield",
        "aliases": (
            "10-year yield",
            "10y yield",
            "treasury yield",
            "dgs10",
            "10yr yield",
            "10 year treasury",
        ),
    },
    {
        "id": "DGS2",
        "name": "2-Year Treasury Yield",
        "aliases": ("2-year yield", "2y yield", "dgs2", "2yr yield"),
    },
    {
        "id": "DGS5",
        "name": "5-Year Treasury Yield",
        "aliases": ("5-year yield", "5y yield", "dgs5"),
    },
    {
        "id": "DGS30",
        "name": "30-Year Treasury Yield",
        "aliases": ("30-year yield", "30y yield", "dgs30", "long bond yield"),
    },
    {
        "id": "T10Y2Y",
        "name": "10Y-2Y Yield Spread",
        "aliases": ("yield curve", "inversion", "t10y2y", "2s10s", "yield spread"),
    },
    {
        "id": "DFF",
        "name": "Federal Funds Effective Rate",
        "aliases": ("fed funds", "policy rate", "dff", "fed rate", "ffr"),
    },
    {
        "id": "BAMLH0A0HYM2",
        "name": "US High Yield OAS",
        "aliases": ("high yield spread", "hy spread", "hy oas", "junk bond spread"),
    },
    {
        "id": "BAMLC0A0CM",
        "name": "US Investment Grade OAS",
        "aliases": ("investment grade spread", "ig spread", "ig oas", "credit spread"),
    },
    {
        "id": "UNRATE",
        "name": "Unemployment Rate",
        "aliases": ("unemployment", "unrate"),
    },
    {
        "id": "CPIAUCSL",
        "name": "CPI All Urban Consumers",
        "aliases": ("cpi", "inflation", "consumer prices"),
    },
    {
        "id": "GDP",
        "name": "Gross Domestic Product",
        "aliases": ("gdp", "economic growth"),
    },
    {
        "id": "WALCL",
        "name": "Fed Balance Sheet (Total Assets)",
        "aliases": ("fed balance sheet", "fed assets", "walcl", "qe"),
    },
    {
        "id": "T10YIE",
        "name": "10-Year Breakeven Inflation Rate",
        "aliases": ("breakeven inflation", "tips spread", "inflation expectations"),
    },
    {
        "id": "IORB",
        "name": "Interest on Reserve Balances",
        "aliases": ("iorb", "interest on reserves"),
    },
]

_ETF_ENTRIES: list[dict] = [
    {
        "id": "SPY",
        "name": "SPDR S&P 500 ETF",
        "aliases": ("s&p 500", "spx", "spy", "s&p500", "s&p"),
    },
    {
        "id": "QQQ",
        "name": "Invesco Nasdaq 100 ETF",
        "aliases": ("nasdaq 100", "qqq", "nasdaq"),
    },
    {
        "id": "IWM",
        "name": "iShares Russell 2000 ETF",
        "aliases": ("russell 2000", "small cap", "iwm"),
    },
    {
        "id": "DIA",
        "name": "SPDR Dow Jones ETF",
        "aliases": ("dow jones", "djia", "dia"),
    },
    {
        "id": "TLT",
        "name": "iShares 20+ Year Treasury",
        "aliases": ("long bond", "tlt", "20-year treasury", "long duration"),
    },
    {"id": "GLD", "name": "SPDR Gold Shares", "aliases": ("gold", "gld")},
    {"id": "SLV", "name": "iShares Silver Trust", "aliases": ("silver", "slv")},
    {
        "id": "USO",
        "name": "United States Oil Fund",
        "aliases": ("oil", "uso", "crude oil etf"),
    },
    {"id": "QUAL", "name": "iShares MSCI USA Quality", "aliases": ("quality", "qual")},
    {
        "id": "USMV",
        "name": "iShares MSCI USA Min Vol",
        "aliases": ("minimum volatility", "low vol", "usmv"),
    },
    {
        "id": "HYG",
        "name": "iShares iBoxx HY Corp Bond",
        "aliases": ("high yield bonds", "hyg"),
    },
    {
        "id": "LQD",
        "name": "iShares IG Corp Bond",
        "aliases": ("investment grade bonds", "lqd"),
    },
    {
        "id": "XLK",
        "name": "Technology Select Sector",
        "aliases": ("tech sector", "xlk"),
    },
    {
        "id": "XLF",
        "name": "Financial Select Sector",
        "aliases": ("financials sector", "xlf"),
    },
    {"id": "XLE", "name": "Energy Select Sector", "aliases": ("energy sector", "xle")},
    {
        "id": "XLV",
        "name": "Health Care Select Sector",
        "aliases": ("healthcare sector", "xlv"),
    },
]

_FX_ENTRIES: list[dict] = [
    {"id": "EURUSD=X", "name": "EUR/USD", "aliases": ("euro", "eur/usd", "eurusd")},
    {
        "id": "GBPUSD=X",
        "name": "GBP/USD",
        "aliases": ("sterling", "cable", "gbp/usd", "gbpusd"),
    },
    {"id": "USDJPY=X", "name": "USD/JPY", "aliases": ("yen", "usd/jpy", "usdjpy")},
    {"id": "USDCAD=X", "name": "USD/CAD", "aliases": ("loonie", "usd/cad", "usdcad")},
    {
        "id": "USDCHF=X",
        "name": "USD/CHF",
        "aliases": ("swiss franc", "usd/chf", "usdchf"),
    },
    {"id": "AUDUSD=X", "name": "AUD/USD", "aliases": ("aussie", "aud/usd", "audusd")},
    {"id": "NZDUSD=X", "name": "NZD/USD", "aliases": ("kiwi", "nzd/usd", "nzdusd")},
]

_CRYPTO_ENTRIES: list[dict] = [
    {"id": "BTCUSDT", "name": "Bitcoin/USDT", "aliases": ("bitcoin", "btc", "btcusdt")},
    {
        "id": "ETHUSDT",
        "name": "Ethereum/USDT",
        "aliases": ("ethereum", "eth", "ethusdt"),
    },
    {"id": "SOLUSDT", "name": "Solana/USDT", "aliases": ("solana", "sol", "solusdt")},
    {"id": "BNBUSDT", "name": "BNB/USDT", "aliases": ("bnb", "bnbusdt")},
]

# ---------------------------------------------------------------------------
# Build the registry
# ---------------------------------------------------------------------------


def _build_registry() -> dict[str, TickerInfo]:
    reg: dict[str, TickerInfo] = {}

    # FRED macro series
    for e in _FRED_ENTRIES:
        info = TickerInfo(
            canonical_id=e["id"],
            asset_class="macro",
            source="fred",
            dataset="macro_indicators",
            name=e["name"],
            aliases=e["aliases"],
        )
        reg[e["id"].lower()] = info
        for alias in e["aliases"]:
            reg[alias.lower()] = info

    # ETFs
    for e in _ETF_ENTRIES:
        info = TickerInfo(
            canonical_id=e["id"],
            asset_class="etf",
            source="yfinance",
            dataset="equities",
            name=e["name"],
            aliases=e["aliases"],
        )
        reg[e["id"].lower()] = info
        for alias in e["aliases"]:
            reg[alias.lower()] = info

    # FX pairs
    for e in _FX_ENTRIES:
        info = TickerInfo(
            canonical_id=e["id"],
            asset_class="fx",
            source="yfinance",
            dataset="fx",
            name=e["name"],
            aliases=e["aliases"],
        )
        reg[e["id"].lower()] = info
        for alias in e["aliases"]:
            reg[alias.lower()] = info

    # Crypto
    for e in _CRYPTO_ENTRIES:
        info = TickerInfo(
            canonical_id=e["id"],
            asset_class="crypto",
            source="binance",
            dataset="binance",
            name=e["name"],
            aliases=e["aliases"],
        )
        reg[e["id"].lower()] = info
        for alias in e["aliases"]:
            reg[alias.lower()] = info

    # US equities from ticker_universe (large cap + mid/small)
    try:
        import sys
        from pathlib import Path

        _root = Path(__file__).resolve().parents[2]
        if str(_root) not in sys.path:
            sys.path.insert(0, str(_root))
        from config.ticker_universe import HK_EQUITIES, US_LARGE_CAP, US_MID_SMALL_CAP

        for ticker in US_LARGE_CAP + US_MID_SMALL_CAP:
            if ticker.lower() not in reg:
                info = TickerInfo(
                    canonical_id=ticker,
                    asset_class="equity",
                    source="yfinance",
                    dataset="equities",
                    name=ticker,
                    aliases=(ticker.lower(),),
                )
                reg[ticker.lower()] = info
        for ticker in HK_EQUITIES:
            if ticker.lower() not in reg:
                info = TickerInfo(
                    canonical_id=ticker,
                    asset_class="equity",
                    source="yfinance",
                    dataset="equities",
                    name=ticker,
                    aliases=(ticker.lower(),),
                )
                reg[ticker.lower()] = info
    except ImportError:
        pass

    return reg


_REGISTRY: dict[str, TickerInfo] = _build_registry()

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resolve(query: str) -> Optional[TickerInfo]:
    """Resolve a ticker symbol or natural-language alias to a TickerInfo.

    Tries exact case-insensitive match first, then alias match.
    Returns None if not found.
    """
    return _REGISTRY.get(query.strip().lower())


def resolve_strict(query: str) -> TickerInfo:
    """Like resolve() but raises ValueError with suggestions on miss."""
    info = resolve(query)
    if info is not None:
        return info
    # Suggest closest keys
    q = query.lower()
    suggestions = [k for k in _REGISTRY if q in k or k in q][:5]
    hint = f" Suggestions: {suggestions}" if suggestions else ""
    raise ValueError(f"Unknown ticker or alias: {query!r}.{hint}")


def resolve_many(queries: list[str]) -> list[TickerInfo]:
    """Resolve a list of queries, raising ValueError on the first miss."""
    return [resolve_strict(q) for q in queries]


def list_universe(asset_class: Optional[str] = None) -> list[TickerInfo]:
    """Return deduplicated TickerInfo entries, optionally filtered by asset_class."""
    seen: set[str] = set()
    result: list[TickerInfo] = []
    for info in _REGISTRY.values():
        if info.canonical_id in seen:
            continue
        if asset_class is None or info.asset_class == asset_class:
            seen.add(info.canonical_id)
            result.append(info)
    return result


def auto_detect_source(ticker: str) -> str:
    """Best-effort source detection for a canonical ticker ID.

    Used by api.get_data() when source is not explicitly provided.
    """
    t = ticker.upper()
    # FRED series patterns
    fred_prefixes = (
        "DGS",
        "T10Y",
        "BAML",
        "WALCL",
        "VIXCLS",
        "VVIX",
        "UNRATE",
        "CPIAUCSL",
        "GDP",
        "DFF",
        "IORB",
        "T10YIE",
    )
    if any(t.startswith(p) for p in fred_prefixes):
        return "fred"
    # Crypto: ends in USDT, BTC, ETH
    if t.endswith(("USDT", "BTC", "ETH")) and len(t) > 4:
        return "binance"
    # HK equities
    if t.endswith(".HK"):
        return "yfinance"
    # ECB FX: 6-char uppercase with no special chars, EUR-base crosses
    ecb_eur_pairs = {
        "EURUSD",
        "EURGBP",
        "EURJPY",
        "EURCHF",
        "EURAUD",
        "EURCAD",
        "EURNZD",
        "EURSGD",
        "EURHKD",
        "EURCNY",
    }
    if t in ecb_eur_pairs:
        return "ecb"
    # Default
    return "yfinance"
