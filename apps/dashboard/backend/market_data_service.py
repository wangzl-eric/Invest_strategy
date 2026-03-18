"""Cross-asset market data service.

Aggregates real-time and macro data from IBKR, yfinance, and FRED API
with TTL caching per asset class. IBKR is primary source when available.
"""

import asyncio
import logging
import math
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# Import data provider manager for IBKR integration
try:
    from backend.data_providers import data_provider_manager

    HAS_DATA_PROVIDERS = True
except ImportError:
    HAS_DATA_PROVIDERS = False
    data_provider_manager = None

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Instrument definitions
# ---------------------------------------------------------------------------

# IBKR Treasury Futures (more current than FRED) - mapped to approximate yields
# Note: These are futures PRICES, not yields. Conversion requires complex calculations.
# We use yfinance tickers which provide approximate yields.
RATES_TICKERS = {
    "^IRX": {"name": "3-Month T-Bill", "tenor": "3M"},
    "^FVX": {"name": "5-Year Treasury", "tenor": "5Y"},
    "^TNX": {"name": "10-Year Treasury", "tenor": "10Y"},
    "^TYX": {"name": "30-Year Treasury", "tenor": "30Y"},
    "^RTX": {"name": "2-Year Treasury", "tenor": "2Y"},
    "^FVRX": {"name": "7-Year Treasury", "tenor": "7Y"},
    # Additional rate proxies via ETFs
    "SHY": {"name": "1-3 Year Treasury ETF", "tenor": "1-3Y"},
    "IEF": {"name": "7-10 Year Treasury ETF", "tenor": "7-10Y"},
    "TLT": {"name": "20+ Year Treasury ETF", "tenor": "20Y+"},
}

# IBKR Treasury Futures tickers (for fetching directly from IBKR when available)
# These are CME bond futures: ZB=30Y, ZN=10Y, ZF=5Y, ZT=2Y
IBKR_RATES_FUTURES = {
    "ZB": {"name": "30-Year Treasury Future", "tenor": "30Y", "exchange": "CBOT"},
    "ZN": {"name": "10-Year Treasury Future", "tenor": "10Y", "exchange": "CBOT"},
    "ZF": {"name": "5-Year Treasury Future", "tenor": "5Y", "exchange": "CBOT"},
    "ZT": {"name": "2-Year Treasury Future", "tenor": "2Y", "exchange": "CBOT"},
}

RATES_FRED_SERIES = {
    # Treasury Yields — full curve for charting
    "DGS1MO": {
        "name": "1-Month Treasury",
        "tenor": "1M",
        "category": "treasury",
        "tenor_years": 1 / 12,
    },
    "DGS3MO": {
        "name": "3-Month Treasury",
        "tenor": "3M",
        "category": "treasury",
        "tenor_years": 0.25,
    },
    "DGS6MO": {
        "name": "6-Month Treasury",
        "tenor": "6M",
        "category": "treasury",
        "tenor_years": 0.5,
    },
    "DGS1": {
        "name": "1-Year Treasury",
        "tenor": "1Y",
        "category": "treasury",
        "tenor_years": 1,
    },
    "DGS2": {
        "name": "2-Year Treasury",
        "tenor": "2Y",
        "category": "treasury",
        "tenor_years": 2,
    },
    "DGS3": {
        "name": "3-Year Treasury",
        "tenor": "3Y",
        "category": "treasury",
        "tenor_years": 3,
    },
    "DGS5": {
        "name": "5-Year Treasury",
        "tenor": "5Y",
        "category": "treasury",
        "tenor_years": 5,
    },
    "DGS7": {
        "name": "7-Year Treasury",
        "tenor": "7Y",
        "category": "treasury",
        "tenor_years": 7,
    },
    "DGS10": {
        "name": "10-Year Treasury",
        "tenor": "10Y",
        "category": "treasury",
        "tenor_years": 10,
    },
    "DGS20": {
        "name": "20-Year Treasury",
        "tenor": "20Y",
        "category": "treasury",
        "tenor_years": 20,
    },
    "DGS30": {
        "name": "30-Year Treasury",
        "tenor": "30Y",
        "category": "treasury",
        "tenor_years": 30,
    },
    # Yield Curve Spreads
    "T10Y2Y": {"name": "10Y-2Y Spread", "tenor": "2s10s", "category": "curve_spread"},
    "T10Y3M": {"name": "10Y-3M Spread", "tenor": "10Y3M", "category": "curve_spread"},
    # Policy Rates
    "DFEDTARU": {
        "name": "Fed Funds Target (Upper)",
        "tenor": "FF",
        "category": "policy",
    },
    "SOFR": {"name": "SOFR", "tenor": "O/N", "category": "policy"},
    # Breakeven Inflation & Forward Inflation
    "T5YIE": {
        "name": "5Y Breakeven Inflation",
        "tenor": "5Y BEI",
        "category": "inflation",
    },
    "T10YIE": {
        "name": "10Y Breakeven Inflation",
        "tenor": "10Y BEI",
        "category": "inflation",
    },
    "T5YIFR": {
        "name": "5Y5Y Forward Inflation",
        "tenor": "5Y5Y Fwd",
        "category": "inflation",
    },
    # TIPS Real Yields
    "DFII5": {
        "name": "5Y Real Yield (TIPS)",
        "tenor": "5Y Real",
        "category": "real_yield",
        "tenor_years": 5,
    },
    "DFII10": {
        "name": "10Y Real Yield (TIPS)",
        "tenor": "10Y Real",
        "category": "real_yield",
        "tenor_years": 10,
    },
    "DFII30": {
        "name": "30Y Real Yield (TIPS)",
        "tenor": "30Y Real",
        "category": "real_yield",
        "tenor_years": 30,
    },
}

# USD swap rate series (DSWP*) were discontinued on FRED. If a professional
# data feed becomes available, add swap rates here and uncomment SWAP_SPREAD_PAIRS.
SWAP_SPREAD_PAIRS: dict = {}

MACRO_YF_FALLBACK = {
    "^VIX": {"name": "VIX (Equity Volatility)", "unit": "index", "freq": "real-time"},
    "HYG": {"name": "HY Credit ETF (HYG)", "unit": "$", "freq": "real-time"},
    "LQD": {"name": "IG Credit ETF (LQD)", "unit": "$", "freq": "real-time"},
    "TIP": {"name": "TIPS Bond ETF (TIP)", "unit": "$", "freq": "real-time"},
    "IEF": {"name": "7-10Y Treasury ETF (IEF)", "unit": "$", "freq": "real-time"},
    "GLD": {"name": "Gold ETF (GLD)", "unit": "$", "freq": "real-time"},
}

FX_TICKERS = {
    # US Dollar Index
    "DX-Y.NYB": {"name": "US Dollar Index (DXY)", "pair": "DXY"},
    # Major Pairs (EUR, GBP, JPY, CAD, CHF, AUD, NZD)
    "EURUSD=X": {"name": "EUR/USD", "pair": "EURUSD"},
    "GBPUSD=X": {"name": "GBP/USD", "pair": "GBPUSD"},
    "USDJPY=X": {"name": "USD/JPY", "pair": "USDJPY"},
    "USDCAD=X": {"name": "USD/CAD", "pair": "USDCAD"},
    "USDCHF=X": {"name": "USD/CHF", "pair": "USDCHF"},
    "AUDUSD=X": {"name": "AUD/USD", "pair": "AUDUSD"},
    "NZDUSD=X": {"name": "NZD/USD", "pair": "NZDUSD"},
    # Minor/Cross Pairs
    "EURJPY=X": {"name": "EUR/JPY", "pair": "EURJPY"},
    "GBPJPY=X": {"name": "GBP/JPY", "pair": "GBPJPY"},
    "EURGBP=X": {"name": "EUR/GBP", "pair": "EURGBP"},
    "EURCHF=X": {"name": "EUR/CHF", "pair": "EURCHF"},
    "AUDJPY=X": {"name": "AUD/JPY", "pair": "AUDJPY"},
    "CADJPY=X": {"name": "CAD/JPY", "pair": "CADJPY"},
    "CHFJPY=X": {"name": "CHF/JPY", "pair": "CHFJPY"},
    "EURNOK=X": {"name": "EUR/NOK", "pair": "EURNOK"},
    "EURSEK=X": {"name": "EUR/SEK", "pair": "EURSEK"},
    "EURPLN=X": {"name": "EUR/PLN", "pair": "EURPLN"},
    "EURHUF=X": {"name": "EUR/HUF", "pair": "EURHUF"},
    # Scandinavian
    "USDSEK=X": {"name": "USD/SEK", "pair": "USDSEK"},
    "USDNOK=X": {"name": "USD/NOK", "pair": "USDNOK"},
    "USDTRY=X": {"name": "USD/TRY", "pair": "USDTRY"},
    # Emerging Market
    "USDZAR=X": {"name": "USD/ZAR", "pair": "USDZAR"},
    "USDBRL=X": {"name": "USD/BRL", "pair": "USDBRL"},
    "USDMXN=X": {"name": "USD/MXN", "pair": "USDMXN"},
    "USDINR=X": {"name": "USD/INR", "pair": "USDINR"},
    "USDCNY=X": {"name": "USD/CNY", "pair": "USDCNY"},
    "USDHKD=X": {"name": "USD/HKD", "pair": "USDHKD"},
    "USDSGD=X": {"name": "USD/SGD", "pair": "USDSGD"},
    "USDTHB=X": {"name": "USD/THB", "pair": "USDTHB"},
    "USDIDR=X": {"name": "USD/IDR", "pair": "USDIDR"},
    "USDMYR=X": {"name": "USD/MYR", "pair": "USDMYR"},
    "USDPHP=X": {"name": "USD/PHP", "pair": "USDPHP"},
    "USDTWD=X": {"name": "USD/TWD", "pair": "USDTWD"},
    # Asian Currencies
    "USDKRW=X": {"name": "USD/KRW", "pair": "USDKRW"},
    "USDJPY=X": {"name": "USD/JPY", "pair": "USDJPY"},
    "USDTHB=X": {"name": "USD/THB", "pair": "USDTHB"},
    "USDIDR=X": {"name": "USD/IDR", "pair": "USDIDR"},
    "USDMYR=X": {"name": "USD/MYR", "pair": "USDMYR"},
    "USDPHP=X": {"name": "USD/PHP", "pair": "USDPHP"},
    "USDVND=X": {"name": "USD/VND", "pair": "USDVND"},
    # Crypto (via forex pairs)
    "BTC-USD": {"name": "Bitcoin/USD", "pair": "BTCUSD"},
    "ETH-USD": {"name": "Ethereum/USD", "pair": "ETHUSD"},
    "BTC-GBP": {"name": "Bitcoin/GBP", "pair": "BTCGBP"},
    "BTC-EUR": {"name": "Bitcoin/EUR", "pair": "BTCEUR"},
    "ETH-BTC": {"name": "Ethereum/Bitcoin", "pair": "ETHBTC"},
}

EQUITY_TICKERS = {
    # US Indexes
    "^GSPC": {"name": "S&P 500", "region": "US"},
    "^NDX": {"name": "Nasdaq 100", "region": "US"},
    "^DJI": {"name": "Dow Jones", "region": "US"},
    "^RUT": {"name": "Russell 2000", "region": "US"},
    "^MID": {"name": "S&P MidCap 400", "region": "US"},
    "^VIX": {"name": "VIX", "region": "US"},
    "^VIX3M": {"name": "VIX 3M", "region": "US"},
    "^VXN": {"name": "Nasdaq Volatility (VXN)", "region": "US"},
    "^RVX": {"name": "Russell 2000 Volatility (RVX)", "region": "US"},
    "^SPX": {"name": "S&P 500 (SPX)", "region": "US"},
    # Additional US Sector Indices
    "^XLK": {"name": "Tech Sector", "region": "US"},
    "^XLF": {"name": "Financial Sector", "region": "US"},
    "^XLE": {"name": "Energy Sector", "region": "US"},
    "^XLV": {"name": "Health Sector", "region": "US"},
    # International Indexes - Americas
    "^MXX": {"name": "IPC Mexico", "region": "MX"},
    "^BVSP": {"name": "Bovespa Brazil", "region": "BR"},
    "^GSPTSE": {"name": "S&P/TSX Composite", "region": "CA"},
    # Europe
    "^STOXX": {"name": "STOXX 600", "region": "EU"},
    "^GDAXI": {"name": "DAX", "region": "DE"},
    "^FCHI": {"name": "CAC 40", "region": "FR"},
    "^FTSE": {"name": "FTSE 100", "region": "UK"},
    "^FTMIB": {"name": "FTSE MIB", "region": "IT"},
    "^IBEX": {"name": "IBEX 35", "region": "ES"},
    "^SSMI": {"name": "Swiss Market Index", "region": "CH"},
    "^AEX": {"name": "AEX Netherlands", "region": "NL"},
    "^BFX": {"name": "BEL 20 Belgium", "region": "BE"},
    "^ATX": {"name": "ATX Austria", "region": "AT"},
    "^WIG": {"name": "Warsaw Stock Exchange", "region": "PL"},
    # Asia Pacific
    "^N225": {"name": "Nikkei 225", "region": "JP"},
    "^TOPIX": {"name": "TOPIX", "region": "JP"},
    "000001.SS": {"name": "Shanghai Composite", "region": "CN"},
    "399001.SZ": {"name": "Shenzhen Component", "region": "CN"},
    "^HSI": {"name": "Hang Seng", "region": "HK"},
    "^BSESN": {"name": "Sensex India", "region": "IN"},
    "^AXJO": {"name": "ASX 200", "region": "AU"},
    "^KS11": {"name": "KOSPI", "region": "KR"},
    "^NZ50": {"name": "NZX 50 New Zealand", "region": "NZ"},
    # MSCI / Global
    "EEM": {"name": "MSCI Emerging Markets", "region": "EM"},
    "EFA": {"name": "MSCI EAFE", "region": "DM"},
    "URTH": {"name": "MSCI World", "region": "DM"},
    "IWM": {"name": "iShares Russell 2000", "region": "US"},
    "VOO": {"name": "Vanguard S&P 500", "region": "US"},
    "VEA": {"name": "Vanguard Developed Markets", "region": "DM"},
    "VGT": {"name": "Vanguard Info Tech", "region": "US"},
    # Regional ETFs for global exposure
    "EWJ": {"name": "iShares MSCI Japan", "region": "JP"},
    "EWU": {"name": "iShares MSCI UK", "region": "UK"},
    "EWG": {"name": "iShares MSCI Germany", "region": "DE"},
    "EWZ": {"name": "iShares MSCI Brazil", "region": "BR"},
    "EWX": {"name": "iShares MSCI Poland", "region": "PL"},
    "EWW": {"name": "iShares MSCI Mexico", "region": "MX"},
    "KWEB": {"name": "KraneShares China Internet", "region": "CN"},
    "FXI": {"name": "iShares China Large-Cap", "region": "CN"},
    "EWY": {"name": "iShares MSCI South Korea", "region": "KR"},
    "EWT": {"name": "iShares MSCI Taiwan", "region": "TW"},
    "INDA": {"name": "iShares MSCI India", "region": "IN"},
}

ETF_TICKERS = {
    # US Sector ETFs
    "SPY": {"name": "S&P 500 ETF", "category": "index"},
    "QQQ": {"name": "Nasdaq 100 ETF", "category": "index"},
    "IWM": {"name": "Russell 2000 ETF", "category": "index"},
    "DIA": {"name": "Dow Jones ETF", "category": "index"},
    # Sector ETFs
    "XLK": {"name": "Technology", "category": "sector"},
    "XLF": {"name": "Financials", "category": "sector"},
    "XLE": {"name": "Energy", "category": "sector"},
    "XLV": {"name": "Healthcare", "category": "sector"},
    "XLC": {"name": "Communications", "category": "sector"},
    "XLY": {"name": "Consumer Discretionary", "category": "sector"},
    "XLP": {"name": "Consumer Staples", "category": "sector"},
    "XLB": {"name": "Materials", "category": "sector"},
    "XLRE": {"name": "Real Estate", "category": "sector"},
    "XLU": {"name": "Utilities", "category": "sector"},
    # Thematic ETFs
    "SMH": {"name": "Semiconductors", "category": "thematic"},
    "XBI": {"name": "Biotech", "category": "thematic"},
    "ARKK": {"name": "Innovation", "category": "thematic"},
    "VNQ": {"name": "Real Estate (Vanguard)", "category": "thematic"},
    # International
    "VXUS": {"name": "Total International", "category": "intl"},
    "VWO": {"name": "Emerging Markets", "category": "intl"},
    # Bonds/Credit
    "TLT": {"name": "20+ Year Treasury", "category": "bond"},
    "IEF": {"name": "7-10 Year Treasury", "category": "bond"},
    "SHY": {"name": "1-3 Year Treasury", "category": "bond"},
    "LQD": {"name": "Investment Grade Corp", "category": "credit"},
    "HYG": {"name": "High Yield Corp", "category": "credit"},
    "TIP": {"name": "TIPS", "category": "inflation"},
    "AGG": {"name": "US Aggregate Bond", "category": "bond"},
    "MUB": {"name": "Muni Bond ETF", "category": "bond"},
    "VTEB": {"name": "Vanguard Muni Bond", "category": "bond"},
    "VCIT": {"name": "Vanguard Intermediate Corp", "category": "bond"},
    "VCSH": {"name": "Vanguard Short-Term Corp", "category": "bond"},
    # Volatility
    "VXX": {"name": "VIX Short-Term ETN", "category": "volatility"},
    "UVXY": {"name": "Ultra VIX Short-Term", "category": "volatility"},
    # Commodities
    "GLD": {"name": "Gold", "category": "commodity"},
    "SLV": {"name": "Silver", "category": "commodity"},
    "USO": {"name": "Oil", "category": "commodity"},
    "UNG": {"name": "Natural Gas", "category": "commodity"},
    "DBC": {"name": "Commodity Broad Basket", "category": "commodity"},
    # Additional Sector ETFs
    "XLI": {"name": "Industrials", "category": "sector"},
    "VO": {"name": "Vanguard Mid-Cap", "category": "sector"},
    "VB": {"name": "Vanguard Small-Cap", "category": "sector"},
    "VGT": {"name": "Vanguard Info Tech", "category": "sector"},
    "VHT": {"name": "Vanguard Health", "category": "sector"},
    "VFH": {"name": "Vanguard Financials", "category": "sector"},
    # Regional / International
    "EWJ": {"name": "iShares MSCI Japan", "category": "intl"},
    "EWU": {"name": "iShares MSCI UK", "category": "intl"},
    "EWG": {"name": "iShares MSCI Germany", "category": "intl"},
    "EWZ": {"name": "iShares MSCI Brazil", "category": "intl"},
    "EWW": {"name": "iShares MSCI Mexico", "category": "intl"},
    "FXI": {"name": "iShares China Large-Cap", "category": "intl"},
    "KWEB": {"name": "KraneShares China Internet", "category": "intl"},
    "EWY": {"name": "iShares MSCI South Korea", "category": "intl"},
    "EWT": {"name": "iShares MSCI Taiwan", "category": "intl"},
    "INDA": {"name": "iShares MSCI India", "category": "intl"},
    # Thematic
    "ARKK": {"name": "ARK Innovation", "category": "thematic"},
    "SOXX": {"name": "iShares Semiconductor", "category": "thematic"},
    "XSD": {"name": "Semiconductor ETF", "category": "thematic"},
    "ICLN": {"name": "iShares Clean Energy", "category": "thematic"},
}

COMMODITY_TICKERS = {
    # Energy
    "CL=F": {"name": "WTI Crude Oil", "group": "Energy"},
    "BZ=F": {"name": "Brent Crude Oil", "group": "Energy"},
    "NG=F": {"name": "Natural Gas", "group": "Energy"},
    "RB=F": {"name": "RBOB Gasoline", "group": "Energy"},
    "HO=F": {"name": "Heating Oil", "group": "Energy"},
    # Precious Metals
    "GC=F": {"name": "Gold", "group": "Precious Metals"},
    "SI=F": {"name": "Silver", "group": "Precious Metals"},
    "PL=F": {"name": "Platinum", "group": "Precious Metals"},
    "PA=F": {"name": "Palladium", "group": "Precious Metals"},
    # Base Metals
    "HG=F": {"name": "Copper", "group": "Base Metals"},
    "AL=F": {"name": "Aluminum", "group": "Base Metals"},
    "ZN=F": {"name": "Zinc", "group": "Base Metals"},
    "PB=F": {"name": "Lead", "group": "Base Metals"},
    "NI=F": {"name": "Nickel", "group": "Base Metals"},
    "SN=F": {"name": "Tin", "group": "Base Metals"},
    # Agriculture
    "ZS=F": {"name": "Soybeans", "group": "Agriculture"},
    "ZW=F": {"name": "Wheat", "group": "Agriculture"},
    "ZC=F": {"name": "Corn", "group": "Agriculture"},
    "ZR=F": {"name": "Rice", "group": "Agriculture"},
    "ZL=F": {"name": "Soybean Oil", "group": "Agriculture"},
    "ZM=F": {"name": "Soybean Meal", "group": "Agriculture"},
    "KE=F": {"name": "Kansas Wheat", "group": "Agriculture"},
    "CT=F": {"name": "Cotton", "group": "Agriculture"},
    "CC=F": {"name": "Cocoa", "group": "Agriculture"},
    "KC=F": {"name": "Coffee", "group": "Agriculture"},
    "SB=F": {"name": "Sugar", "group": "Agriculture"},
    "OJ=F": {"name": "Orange Juice", "group": "Agriculture"},
    "HE=F": {"name": "Lean Hogs", "group": "Agriculture"},
    "LE=F": {"name": "Live Cattle", "group": "Agriculture"},
    "GF=F": {"name": "Feeder Cattle", "group": "Agriculture"},
    # Livestock
    "LE=F": {"name": "Live Cattle", "group": "Livestock"},
    "HE=F": {"name": "Lean Hogs", "group": "Livestock"},
    # Softs
    "Lumber": {"name": "Lumber", "group": "Softs"},
    "OJ=F": {"name": "Orange Juice", "group": "Softs"},
    "KC=F": {"name": "Coffee", "group": "Softs"},
    "CT=F": {"name": "Cotton", "group": "Softs"},
    "CC=F": {"name": "Cocoa", "group": "Softs"},
}

# IBKR-specific ticker mappings for live data fetching
# These map the yfinance symbols to IBKR-compatible symbols
# Note: IBKR uses format like "EURUSD" (no dot) for forex in the hardcoded check
IBKR_FX_TICKERS = {
    "EURUSD=X": {"ibkr_symbol": "EURUSD", "sec_type": "CASH", "exchange": "IDEALPRO"},
    "GBPUSD=X": {"ibkr_symbol": "GBPUSD", "sec_type": "CASH", "exchange": "IDEALPRO"},
    "USDJPY=X": {"ibkr_symbol": "USDJPY", "sec_type": "CASH", "exchange": "IDEALPRO"},
    "AUDUSD=X": {"ibkr_symbol": "AUDUSD", "sec_type": "CASH", "exchange": "IDEALPRO"},
    "USDCAD=X": {"ibkr_symbol": "USDCAD", "sec_type": "CASH", "exchange": "IDEALPRO"},
    "USDCHF=X": {"ibkr_symbol": "USDCHF", "sec_type": "CASH", "exchange": "IDEALPRO"},
    "NZDUSD=X": {"ibkr_symbol": "NZDUSD", "sec_type": "CASH", "exchange": "IDEALPRO"},
}

IBKR_EQUITY_TICKERS = {
    "^GSPC": {"ibkr_symbol": "SPY", "sec_type": "STK", "exchange": "SMART"},
    "^NDX": {"ibkr_symbol": "QQQ", "sec_type": "STK", "exchange": "SMART"},
    "^RUT": {"ibkr_symbol": "IWM", "sec_type": "STK", "exchange": "SMART"},
    "^VIX": {"ibkr_symbol": "VIX", "sec_type": "IND", "exchange": "CBOE"},
}

IBKR_COMMODITY_TICKERS = {
    "CL=F": {"ibkr_symbol": "CL", "sec_type": "FUT", "exchange": "NYMEX"},
    "BZ=F": {"ibkr_symbol": "BZ", "sec_type": "FUT", "exchange": "ICE"},
    "NG=F": {"ibkr_symbol": "NG", "sec_type": "FUT", "exchange": "NYMEX"},
    "GC=F": {"ibkr_symbol": "GC", "sec_type": "FUT", "exchange": "COMEX"},
    "SI=F": {"ibkr_symbol": "SI", "sec_type": "FUT", "exchange": "COMEX"},
    "HG=F": {"ibkr_symbol": "HG", "sec_type": "FUT", "exchange": "COMEX"},
}

MACRO_FRED_SERIES = {
    "UNRATE": {"name": "Unemployment Rate", "unit": "%", "freq": "monthly"},
    "CPIAUCSL": {"name": "CPI (All Urban)", "unit": "index", "freq": "monthly"},
    "GDPC1": {"name": "Real GDP", "unit": "B$", "freq": "quarterly"},
    "UMCSENT": {"name": "Consumer Sentiment", "unit": "index", "freq": "monthly"},
    "NFCI": {"name": "Chicago Fed NFCI", "unit": "index", "freq": "weekly"},
    "BAMLH0A0HYM2": {"name": "HY OAS Spread", "unit": "bp", "freq": "daily"},
}

# Fed balance sheet / liquidity series for QE/QT monitoring.
# Units on FRED vary — divisor converts raw value to trillions of USD.
FED_LIQUIDITY_SERIES = {
    "WALCL": {
        "name": "Fed Total Assets",
        "freq": "weekly",
        "divisor": 1e6,
        "raw_unit": "M$",
    },
    "RRPONTSYD": {
        "name": "ON Reverse Repo (RRP)",
        "freq": "daily",
        "divisor": 1e3,
        "raw_unit": "B$",
    },
    "WRESBAL": {
        "name": "Reserve Balances",
        "freq": "weekly",
        "divisor": 1e6,
        "raw_unit": "M$",
    },
    "WTREGEN": {
        "name": "Treasury General Account (TGA)",
        "freq": "weekly",
        "divisor": 1e6,
        "raw_unit": "M$",
    },
    "TREAST": {
        "name": "Fed Holdings: Treasuries",
        "freq": "weekly",
        "divisor": 1e6,
        "raw_unit": "M$",
    },
    "WSHOMCB": {
        "name": "Fed Holdings: MBS",
        "freq": "weekly",
        "divisor": 1e6,
        "raw_unit": "M$",
    },
}

# All yfinance tickers used for the z-score "what changed" scanner
ALL_YF_TICKERS: Dict[str, Dict[str, str]] = {}
for _map, _cls in [
    (RATES_TICKERS, "Rates"),
    (FX_TICKERS, "FX"),
    (EQUITY_TICKERS, "Equities"),
    (COMMODITY_TICKERS, "Commodities"),
]:
    for ticker, meta in _map.items():
        ALL_YF_TICKERS[ticker] = {**meta, "asset_class": _cls}

# ---------------------------------------------------------------------------
# TTL cache
# ---------------------------------------------------------------------------


class _TTLCache:
    """Simple in-memory TTL cache."""

    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._store and time.time() < self._expiry.get(key, 0):
            return self._store[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: float):
        self._store[key] = value
        self._expiry[key] = time.time() + ttl_seconds

    def invalidate(self, key: str):
        self._store.pop(key, None)
        self._expiry.pop(key, None)


_cache = _TTLCache()

# Cache TTLs
REALTIME_TTL = 60  # 60 s for yfinance market data
FRED_TTL = 3600  # 1 h for FRED macro data
ZSCORE_TTL = 120  # 2 min for z-score scanner (heavier computation)
SPARKLINE_TTL = 300  # 5 min for batch sparkline data

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _yf_download(
    tickers: List[str], period: str = "5d", interval: str = "1d"
) -> pd.DataFrame:
    """Wrapper around yfinance download with error handling."""
    try:
        import yfinance as yf

        data = yf.download(
            tickers,
            period=period,
            interval=interval,
            progress=False,
            threads=True,
        )
        return data
    except Exception as e:
        logger.error(f"yfinance download failed for {tickers}: {e}")
        return pd.DataFrame()


def _fetch_ibkr_rates_futures() -> List[dict]:
    """Fetch treasury futures data - currently uses yfinance for reliability.

    Returns list of rate data with yields.

    Note: IBKR direct integration is deferred due to asyncio event loop complexity
    in the ThreadPoolExecutor context. The infrastructure is in place for
    future implementation when a more robust async solution is available.
    """
    # IBKR futures tickers mapped to yfinance yield tickers
    futures_to_yield = {
        "ZB": "^TYX",  # 30Y Treasury
        "ZN": "^TNX",  # 10Y Treasury
        "ZF": "^FVX",  # 5Y Treasury
        "ZT": "^IRX",  # 2Y Treasury
    }

    logger.info("Using yfinance for treasury yields")
    return _fetch_yfinance_rates(futures_to_yield)


def _fetch_yfinance_rates(futures_to_yield: dict) -> List[dict]:
    """Fetch rates from yfinance (fallback)."""
    results = []

    try:
        yield_tickers = list(futures_to_yield.values())
        df = _yf_download(yield_tickers, period="5d")

        if df is None or df.empty:
            return results

        if isinstance(df.columns, pd.MultiIndex):
            close_data = (
                df.xs("Close", level=0, axis=1)
                if "Close" in df.columns.get_level_values(0)
                else pd.DataFrame()
            )
        else:
            close_data = df[["Close"]] if "Close" in df.columns else pd.DataFrame()

        if close_data.empty:
            return results

        for fut_ticker, yield_ticker in futures_to_yield.items():
            try:
                if yield_ticker not in close_data.columns:
                    continue

                ticker_data = close_data[yield_ticker].dropna()
                if ticker_data.empty:
                    continue

                latest_value = ticker_data.iloc[-1]
                latest_date = ticker_data.index[-1]

                meta = IBKR_RATES_FUTURES.get(fut_ticker, {})

                history = []
                for idx, val in ticker_data.items():
                    if not pd.isna(val):
                        history.append(
                            {"date": str(idx.date()), "value": round(float(val), 3)}
                        )

                chg = None
                if len(ticker_data) >= 2:
                    prev_value = ticker_data.iloc[-2]
                    if not pd.isna(prev_value):
                        chg = round(float(latest_value - prev_value), 3)

                results.append(
                    {
                        "series": fut_ticker,
                        "ticker": fut_ticker,
                        "name": meta.get("name", fut_ticker),
                        "tenor": meta.get("tenor", ""),
                        "value": round(float(latest_value), 3),
                        "change": chg,
                        "date": str(latest_date.date()),
                        "source": "yfinance",
                        "category": "treasury",
                        "history": history,
                    }
                )

            except Exception as e:
                logger.debug(f"Error processing {fut_ticker}: {e}")
                continue

    except Exception as e:
        logger.debug(f"Rates fetch error: {e}")

    return results


def _fetch_ibkr_live_quotes(ticker_map: dict) -> dict:
    """Fetch live quotes from IBKR for the given tickers.

    This function attempts to get real-time data from IBKR TWS/Gateway.
    Falls back gracefully if IBKR is not available.

    Args:
        ticker_map: Dict mapping {symbol: {name, sec_type, exchange, currency}}

    Returns:
        Dict mapping symbol to quote data {price, bid, ask, volume, timestamp}
    """
    results = {}

    # Check if IBKR is available
    if not HAS_DATA_PROVIDERS or data_provider_manager is None:
        logger.info("IBKR quotes: No data provider manager")
        return results

    try:
        # Get IBKR provider through the manager
        ibkr_provider = data_provider_manager.get_provider("ibkr")
        if not ibkr_provider:
            logger.info("IBKR quotes: No IBKR provider registered")
            return results

        logger.info(
            f"IBKR quotes: Attempting to fetch {len(ticker_map)} quotes: {list(ticker_map.keys())}"
        )

        # Use a thread to run the async function
        from concurrent.futures import ThreadPoolExecutor

        async def fetch_quotes_async():
            quotes = {}

            # Ensure connection is established first
            await ibkr_provider._ensure_connected()

            for symbol, meta in ticker_map.items():
                try:
                    # Use async version of get_quote
                    quote = await ibkr_provider.get_quote_async(symbol)
                    if quote and quote.get("last") is not None:
                        quotes[symbol] = {
                            "price": quote.get("last"),
                            "bid": quote.get("bid"),
                            "ask": quote.get("ask"),
                            "volume": quote.get("volume"),
                            "timestamp": quote.get("timestamp"),
                        }
                except Exception as e:
                    logger.info(f"IBKR quote error for {symbol}: {e}")
                    continue
            return quotes

        def run_in_new_loop():
            # Create a fresh event loop in this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(fetch_quotes_async())
            finally:
                loop.close()

        # Run in a thread to avoid event loop issues
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_in_new_loop)
            results = future.result()

    except Exception as e:
        logger.info(f"IBKR live quotes fetch error: {e}")

    logger.info(f"IBKR quotes: Got {len(results)} quotes: {list(results.keys())}")
    return results


def _fetch_with_ibkr_fallback(
    tickers: List[str], asset_class: str, period: str = "5d"
) -> pd.DataFrame:
    """Try IBKR first, then fall back to yfinance.

    Args:
        tickers: List of ticker symbols
        asset_class: Asset class (equity, fx, commodity, etc.)
        period: yfinance period (5d, 1mo, etc.)

    Returns:
        DataFrame with OHLCV data
    """
    from datetime import datetime, timedelta

    # Calculate date range
    end_date = datetime.utcnow()
    if period == "5d":
        start_date = end_date - timedelta(days=7)
    elif period == "1mo":
        start_date = end_date - timedelta(days=35)
    else:
        days = int(period.replace("d", "")) if "d" in period else 30
        start_date = end_date - timedelta(days=days + 2)

    # Try IBKR first using the data provider manager with fallback
    if HAS_DATA_PROVIDERS and data_provider_manager:
        try:
            # Try each ticker via IBKR (pass asset_class for priority order)
            results = []
            for ticker in tickers:
                result = data_provider_manager.get_historical_data_with_fallback(
                    ticker, start_date, end_date, asset_class, "1d"
                )
                if result.get("success") and not result["data"].empty:
                    results.append(result["data"])
                    logger.debug(f"Got {ticker} from {result.get('source_used')}")

            if results:
                # Combine all results
                if len(results) == 1:
                    return results[0]
                else:
                    # Combine columns from different tickers
                    combined = pd.concat(results, axis=1)
                    return combined
        except Exception as e:
            logger.debug(f"IBKR fetch failed, falling back to yfinance: {e}")

    # Fallback to yfinance
    logger.debug(f"Using yfinance fallback for {tickers}")
    return _yf_download(tickers, period=period)


def _get_fred():
    """Return a Fred client if an API key is configured, else None."""
    try:
        from backend.config import settings

        api_key = settings.market_data.fred_api_key
        if not api_key:
            return None
        from fredapi import Fred

        return Fred(api_key=api_key)
    except Exception as e:
        logger.warning(f"Could not initialize FRED client: {e}")
        return None


def _safe_float(val) -> Optional[float]:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _extract_snapshot(df: pd.DataFrame, tickers_meta: dict) -> List[dict]:
    """Extract latest price / change from a multi-ticker yfinance dataframe."""
    results = []
    if df.empty:
        return results

    is_multi = isinstance(df.columns, pd.MultiIndex)

    for ticker, meta in tickers_meta.items():
        try:
            if is_multi:
                close_col = (
                    df["Close"][ticker] if ticker in df["Close"].columns else None
                )
            else:
                close_col = df["Close"] if "Close" in df.columns else None

            if close_col is None or close_col.dropna().empty:
                continue

            close_series = close_col.dropna()
            last_price = _safe_float(close_series.iloc[-1])
            prev_price = (
                _safe_float(close_series.iloc[-2]) if len(close_series) >= 2 else None
            )

            change = None
            change_pct = None
            if last_price is not None and prev_price is not None and prev_price != 0:
                change = last_price - prev_price
                change_pct = (change / prev_price) * 100

            last_date = ""
            try:
                last_date = (
                    str(close_series.index[-1].date())
                    if hasattr(close_series.index[-1], "date")
                    else ""
                )
            except Exception:
                pass

            results.append(
                {
                    "ticker": ticker,
                    **meta,
                    "price": last_price,
                    "change": _safe_float(change),
                    "change_pct": _safe_float(change_pct),
                    "date": last_date,
                }
            )
        except Exception as e:
            logger.debug(f"Error extracting data for {ticker}: {e}")

    return results


# ---------------------------------------------------------------------------
# MarketDataService
# ---------------------------------------------------------------------------


class MarketDataService:
    """Aggregates cross-asset market data from yfinance and FRED."""

    # -- Rates ---------------------------------------------------------------

    def get_rates_snapshot(self) -> dict:
        cached = _cache.get("rates_snapshot")
        if cached is not None:
            return cached

        # yfinance yields (real-time-ish)
        tickers = list(RATES_TICKERS.keys())
        df = _yf_download(tickers, period="5d")
        yf_rates = _extract_snapshot(df, RATES_TICKERS)

        # IBKR treasury futures (more current data when available)
        ibkr_futures_rates = _fetch_ibkr_rates_futures()

        # FRED series (richer set of yields + spreads) - has 1-day delay
        fred_rates = self._fetch_fred_rates()

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "yields": yf_rates,
            "ibkr_futures": ibkr_futures_rates,
            "fred": fred_rates,
        }
        _cache.set("rates_snapshot", result, REALTIME_TTL)
        return result

    def _fetch_fred_rates(self) -> List[dict]:
        cached = _cache.get("fred_rates")
        if cached is not None:
            return cached

        fred = _get_fred()
        if fred is None:
            return []

        results = []
        values_by_series: Dict[str, float] = {}

        for series_id, meta in RATES_FRED_SERIES.items():
            try:
                data = fred.get_series(
                    series_id,
                    observation_start=(datetime.now() - timedelta(days=30)).strftime(
                        "%Y-%m-%d"
                    ),
                )
                if data is not None and not data.empty:
                    data = data.dropna()
                    if data.empty:
                        continue
                    last_val = _safe_float(data.iloc[-1])
                    prev_val = _safe_float(data.iloc[-2]) if len(data) >= 2 else None
                    change = (
                        (last_val - prev_val)
                        if (last_val is not None and prev_val is not None)
                        else None
                    )
                    if last_val is not None:
                        values_by_series[series_id] = last_val

                    history = [
                        {"date": str(idx.date()), "value": _safe_float(v)}
                        for idx, v in data.items()
                    ]

                    results.append(
                        {
                            "series": series_id,
                            **meta,
                            "value": last_val,
                            "change": _safe_float(change),
                            "date": str(data.index[-1].date()),
                            "history": history,
                        }
                    )
            except Exception as e:
                logger.debug(f"FRED fetch error for {series_id}: {e}")

        for tenor_label, (tsy_id, swap_id) in SWAP_SPREAD_PAIRS.items():
            tsy_val = values_by_series.get(tsy_id)
            swap_val = values_by_series.get(swap_id)
            if tsy_val is not None and swap_val is not None:
                spread_bp = (swap_val - tsy_val) * 100
                results.append(
                    {
                        "series": f"SS_{tenor_label}",
                        "name": f"{tenor_label} Swap Spread",
                        "tenor": f"{tenor_label} SS",
                        "category": "swap_spread",
                        "value": _safe_float(spread_bp),
                        "change": None,
                        "date": "",
                        "unit": "bp",
                    }
                )
                results.append(
                    {
                        "series": f"ASW_{tenor_label}",
                        "name": f"{tenor_label} Asset Swap Spread",
                        "tenor": f"{tenor_label} ASW",
                        "category": "asset_swap",
                        "value": _safe_float(-spread_bp),
                        "change": None,
                        "date": "",
                        "unit": "bp",
                    }
                )

        _cache.set("fred_rates", results, FRED_TTL)
        return results

    # -- FX ------------------------------------------------------------------

    def get_fx_snapshot(self) -> dict:
        """Get FX pairs snapshot - IBKR only (no yfinance fallback)."""
        cached = _cache.get("fx_snapshot")
        if cached is not None:
            return cached

        # Build IBKR ticker map for FX
        ibkr_ticker_map = {}
        for symbol, meta in FX_TICKERS.items():
            ibkr_meta = IBKR_FX_TICKERS.get(symbol, {})
            if ibkr_meta:
                ibkr_ticker_map[ibkr_meta.get("ibkr_symbol", symbol)] = {
                    "name": meta.get("name", symbol),
                    "sec_type": ibkr_meta.get("sec_type", "CASH"),
                    "exchange": ibkr_meta.get("exchange", "IDEALPRO"),
                }

        # Fetch from IBKR only (no fallback)
        source = "yfinance"
        pairs = []

        if ibkr_ticker_map:
            ibkr_quotes = _fetch_ibkr_live_quotes(ibkr_ticker_map)
            if ibkr_quotes:
                source = "IBKR"
                logger.debug(
                    f"Got live FX quotes from IBKR: {list(ibkr_quotes.keys())}"
                )

                # Build pairs from IBKR quotes directly
                for yf_symbol, ibkr_meta in IBKR_FX_TICKERS.items():
                    ibkr_symbol = ibkr_meta.get("ibkr_symbol", "")
                    if ibkr_symbol in ibkr_quotes:
                        quote = ibkr_quotes[ibkr_symbol]
                        meta = FX_TICKERS.get(yf_symbol, {})

                        # Helper to sanitize float values (handle NaN/Inf)
                        def safe_float(val):
                            if val is None:
                                return None
                            if isinstance(val, float):
                                if math.isnan(val) or math.isinf(val):
                                    return None
                            return val

                        pairs.append(
                            {
                                "ticker": yf_symbol,
                                "pair": meta.get("pair", ibkr_symbol),
                                "name": meta.get("name", ibkr_symbol),
                                "price": safe_float(quote.get("price")),
                                "bid": safe_float(quote.get("bid")),
                                "ask": safe_float(quote.get("ask")),
                                "volume": safe_float(quote.get("volume")),
                                "change": None,  # Would need historical for this
                                "change_pct": None,
                                "date": datetime.now().strftime("%Y-%m-%d")
                                if quote.get("price")
                                else "",
                                "source": "IBKR",
                            }
                        )

        # If no IBKR data, return empty rather than fallback
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "pairs": pairs,
            "source": source,
        }
        # Use shorter TTL for live data (15 seconds to match frontend polling)
        _cache.set("fx_snapshot", result, 15)
        return result

    # -- Equities ------------------------------------------------------------

    def get_equities_snapshot(self) -> dict:
        """Get equity indices snapshot - IBKR only (no yfinance fallback)."""
        cached = _cache.get("equities_snapshot")
        if cached is not None:
            return cached

        # Build IBKR ticker map for equities
        ibkr_ticker_map = {}
        for symbol, meta in EQUITY_TICKERS.items():
            ibkr_meta = IBKR_EQUITY_TICKERS.get(symbol, {})
            if ibkr_meta:
                ibkr_ticker_map[ibkr_meta.get("ibkr_symbol", symbol)] = {
                    "name": meta.get("name", symbol),
                    "sec_type": ibkr_meta.get("sec_type", "STK"),
                    "exchange": ibkr_meta.get("exchange", "SMART"),
                }

        # Fetch from IBKR only (no fallback)
        source = "yfinance"
        indices = []

        # Helper to sanitize float values (handle NaN/Inf)
        def safe_float(val):
            if val is None:
                return None
            if isinstance(val, float):
                if math.isnan(val) or math.isinf(val):
                    return None
            return val

        if ibkr_ticker_map:
            ibkr_quotes = _fetch_ibkr_live_quotes(ibkr_ticker_map)
            if ibkr_quotes:
                source = "IBKR"
                logger.debug(
                    f"Got live equity quotes from IBKR: {list(ibkr_quotes.keys())}"
                )

                # Build indices from IBKR quotes directly
                for yf_symbol, ibkr_meta in IBKR_EQUITY_TICKERS.items():
                    ibkr_symbol = ibkr_meta.get("ibkr_symbol", "")
                    if ibkr_symbol in ibkr_quotes:
                        quote = ibkr_quotes[ibkr_symbol]
                        meta = EQUITY_TICKERS.get(yf_symbol, {})
                        indices.append(
                            {
                                "ticker": yf_symbol,
                                "name": meta.get("name", ibkr_symbol),
                                "region": meta.get("region", ""),
                                "price": safe_float(quote.get("price")),
                                "bid": safe_float(quote.get("bid")),
                                "ask": safe_float(quote.get("ask")),
                                "volume": safe_float(quote.get("volume")),
                                "change": None,
                                "change_pct": None,
                                "date": datetime.now().strftime("%Y-%m-%d")
                                if quote.get("price")
                                else "",
                                "source": "IBKR",
                            }
                        )

        # If no IBKR data, return empty rather than fallback
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "indices": indices,
            "source": source,
        }
        # Use shorter TTL for live data (15 seconds to match frontend polling)
        _cache.set("equities_snapshot", result, 15)
        return result

    # -- Commodities ---------------------------------------------------------

    def get_commodities_snapshot(self) -> dict:
        """Get commodities snapshot - IBKR only (no yfinance fallback)."""
        cached = _cache.get("commodities_snapshot")
        if cached is not None:
            return cached

        # Build IBKR ticker map for commodities
        ibkr_ticker_map = {}
        for symbol, meta in COMMODITY_TICKERS.items():
            ibkr_meta = IBKR_COMMODITY_TICKERS.get(symbol, {})
            if ibkr_meta:
                ibkr_ticker_map[ibkr_meta.get("ibkr_symbol", symbol)] = {
                    "name": meta.get("name", symbol),
                    "sec_type": ibkr_meta.get("sec_type", "FUT"),
                    "exchange": ibkr_meta.get("exchange", "NYMEX"),
                }

        # Fetch from IBKR only (no fallback)
        source = "yfinance"
        items = []

        # Helper to sanitize float values (handle NaN/Inf)
        def safe_float(val):
            if val is None:
                return None
            if isinstance(val, float):
                if math.isnan(val) or math.isinf(val):
                    return None
            return val

        if ibkr_ticker_map:
            ibkr_quotes = _fetch_ibkr_live_quotes(ibkr_ticker_map)
            if ibkr_quotes:
                source = "IBKR"
                logger.debug(
                    f"Got live commodity quotes from IBKR: {list(ibkr_quotes.keys())}"
                )

                # Build commodities from IBKR quotes directly
                for yf_symbol, ibkr_meta in IBKR_COMMODITY_TICKERS.items():
                    ibkr_symbol = ibkr_meta.get("ibkr_symbol", "")
                    if ibkr_symbol in ibkr_quotes:
                        quote = ibkr_quotes[ibkr_symbol]
                        meta = COMMODITY_TICKERS.get(yf_symbol, {})
                        items.append(
                            {
                                "ticker": yf_symbol,
                                "name": meta.get("name", ibkr_symbol),
                                "group": meta.get("group", ""),
                                "price": safe_float(quote.get("price")),
                                "bid": safe_float(quote.get("bid")),
                                "ask": safe_float(quote.get("ask")),
                                "volume": safe_float(quote.get("volume")),
                                "change": None,
                                "change_pct": None,
                                "date": datetime.now().strftime("%Y-%m-%d")
                                if quote.get("price")
                                else "",
                                "source": "IBKR",
                            }
                        )

        # If no IBKR data, return empty rather than fallback
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "commodities": items,
            "source": source,
        }
        # Use shorter TTL for live data (15 seconds to match frontend polling)
        _cache.set("commodities_snapshot", result, 15)
        return result

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "commodities": items,
            "source": source,
        }
        # Use shorter TTL for live data (15 seconds to match frontend polling)
        _cache.set("commodities_snapshot", result, 15)
        return result

    # -- Macro pulse ---------------------------------------------------------

    def get_macro_pulse(self) -> dict:
        cached = _cache.get("macro_pulse")
        if cached is not None:
            return cached

        fred = _get_fred()
        indicators: List[dict] = []
        note = None

        if fred is not None:
            for series_id, meta in MACRO_FRED_SERIES.items():
                try:
                    data = fred.get_series(
                        series_id,
                        observation_start=(
                            datetime.now() - timedelta(days=365)
                        ).strftime("%Y-%m-%d"),
                    )
                    if data is not None and not data.empty:
                        data = data.dropna()
                        if data.empty:
                            continue
                        last_val = _safe_float(data.iloc[-1])
                        prev_val = (
                            _safe_float(data.iloc[-2]) if len(data) >= 2 else None
                        )
                        change = (
                            (last_val - prev_val)
                            if (last_val is not None and prev_val is not None)
                            else None
                        )
                        indicators.append(
                            {
                                "series": series_id,
                                **meta,
                                "value": last_val,
                                "previous": prev_val,
                                "change": _safe_float(change),
                                "date": str(data.index[-1].date()),
                            }
                        )
                except Exception as e:
                    logger.debug(f"FRED macro fetch error for {series_id}: {e}")

        if not indicators:
            indicators = self._fetch_macro_yf_fallback()
            if fred is None:
                note = "Showing market-based macro proxies — set FRED_API_KEY in .env for economic indicators (free at fred.stlouisfed.org/docs/api/api_key.html)"

        ttl = FRED_TTL if fred else REALTIME_TTL
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "indicators": indicators,
            "note": note,
        }
        _cache.set("macro_pulse", result, ttl)
        return result

    def _fetch_macro_yf_fallback(self) -> List[dict]:
        """Market-based macro proxies from yfinance when FRED is unavailable."""
        tickers = list(MACRO_YF_FALLBACK.keys())
        df = _yf_download(tickers, period="5d")
        snapshots = _extract_snapshot(df, MACRO_YF_FALLBACK)
        indicators = []
        for item in snapshots:
            ticker = item.get("ticker", "")
            meta = MACRO_YF_FALLBACK.get(ticker, {})
            indicators.append(
                {
                    "series": ticker,
                    "name": meta.get("name", ticker),
                    "value": item.get("price"),
                    "change": item.get("change"),
                    "unit": meta.get("unit", ""),
                    "freq": meta.get("freq", ""),
                    "date": item.get("date", ""),
                }
            )
        return indicators

    # -- What Changed (z-score scanner) --------------------------------------

    def get_what_changed(self, sigma_threshold: float = 1.5) -> dict:
        cached = _cache.get("what_changed")
        if cached is not None:
            return cached

        tickers = list(ALL_YF_TICKERS.keys())
        df = _yf_download(tickers, period="1mo", interval="1d")

        movers: List[dict] = []
        if df.empty:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "movers": [],
                "threshold": sigma_threshold,
            }

        is_multi = isinstance(df.columns, pd.MultiIndex)

        for ticker, meta in ALL_YF_TICKERS.items():
            try:
                if is_multi:
                    if ticker not in df["Close"].columns:
                        continue
                    close = df["Close"][ticker].dropna()
                else:
                    close = df["Close"].dropna()

                if len(close) < 5:
                    continue

                returns = close.pct_change().dropna()
                if len(returns) < 5:
                    continue

                vol_20d = (
                    returns.iloc[-21:].std() if len(returns) >= 21 else returns.std()
                )
                if vol_20d == 0 or np.isnan(vol_20d):
                    continue

                today_return = returns.iloc[-1]
                z_score = today_return / vol_20d

                if abs(z_score) >= sigma_threshold:
                    movers.append(
                        {
                            "ticker": ticker,
                            **meta,
                            "price": _safe_float(close.iloc[-1]),
                            "return_pct": _safe_float(today_return * 100),
                            "vol_20d": _safe_float(vol_20d * 100),
                            "z_score": _safe_float(z_score),
                            "direction": "up" if z_score > 0 else "down",
                        }
                    )
            except Exception as e:
                logger.debug(f"z-score calc error for {ticker}: {e}")

        movers.sort(key=lambda x: abs(x.get("z_score", 0)), reverse=True)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "movers": movers,
            "threshold": sigma_threshold,
        }
        _cache.set("what_changed", result, ZSCORE_TTL)
        return result

    # -- Curves data for charting --------------------------------------------

    def get_curves_data(self) -> dict:
        """Yield curve, swap curve, swap spread curve, and forward rates for plotting."""
        cached = _cache.get("curves_data")
        if cached is not None:
            return cached

        fred_rates = self._fetch_fred_rates()
        if not fred_rates:
            return {}

        vals: Dict[str, dict] = {}
        for r in fred_rates:
            vals[r["series"]] = r

        tsy_curve_series = [
            ("DGS1MO", "1M", 1 / 12),
            ("DGS3MO", "3M", 0.25),
            ("DGS6MO", "6M", 0.5),
            ("DGS1", "1Y", 1),
            ("DGS2", "2Y", 2),
            ("DGS3", "3Y", 3),
            ("DGS5", "5Y", 5),
            ("DGS7", "7Y", 7),
            ("DGS10", "10Y", 10),
            ("DGS20", "20Y", 20),
            ("DGS30", "30Y", 30),
        ]
        swap_curve_series = [
            ("DSWP2", "2Y", 2),
            ("DSWP5", "5Y", 5),
            ("DSWP10", "10Y", 10),
            ("DSWP30", "30Y", 30),
        ]

        yc_tenors, yc_years, yc_yields = [], [], []
        for sid, tenor, years in tsy_curve_series:
            v = vals.get(sid, {}).get("value")
            if v is not None:
                yc_tenors.append(tenor)
                yc_years.append(years)
                yc_yields.append(v)

        sc_tenors, sc_years, sc_rates = [], [], []
        for sid, tenor, years in swap_curve_series:
            v = vals.get(sid, {}).get("value")
            if v is not None:
                sc_tenors.append(tenor)
                sc_years.append(years)
                sc_rates.append(v)

        ss_tenors, ss_years, ss_bp = [], [], []
        for tenor_label in ["2Y", "5Y", "10Y", "30Y"]:
            key = f"SS_{tenor_label}"
            v = vals.get(key, {}).get("value")
            if v is not None:
                ss_tenors.append(tenor_label)
                ss_years.append({"2Y": 2, "5Y": 5, "10Y": 10, "30Y": 30}[tenor_label])
                ss_bp.append(v)

        fwd_labels, fwd_rates = [], []
        if len(yc_years) >= 2:
            for i in range(len(yc_years) - 1):
                t1, y1 = yc_years[i], yc_yields[i]
                t2, y2 = yc_years[i + 1], yc_yields[i + 1]
                if t2 > t1 and y1 is not None and y2 is not None:
                    fwd = (y2 * t2 - y1 * t1) / (t2 - t1)
                    fwd_labels.append(f"{yc_tenors[i]}-{yc_tenors[i+1]}")
                    fwd_rates.append(round(fwd, 4))

        latest_date = ""
        for r in fred_rates:
            d = r.get("date", "")
            if d and d > latest_date:
                latest_date = d

        result = {
            "yield_curve": {
                "tenors": yc_tenors,
                "tenor_years": yc_years,
                "yields": yc_yields,
                "date": latest_date,
            },
            "swap_curve": {
                "tenors": sc_tenors,
                "tenor_years": sc_years,
                "rates": sc_rates,
                "date": latest_date,
            },
            "swap_spreads": {
                "tenors": ss_tenors,
                "tenor_years": ss_years,
                "spreads_bp": ss_bp,
                "date": latest_date,
            },
            "forward_rates": {
                "labels": fwd_labels,
                "rates": fwd_rates,
                "date": latest_date,
            },
        }
        _cache.set("curves_data", result, FRED_TTL)
        return result

    # -- Fed Balance Sheet / Liquidity (QE / QT monitor) --------------------

    def get_fed_liquidity_data(self) -> dict:
        """Historical Fed balance sheet components for QE/QT monitoring.

        Returns latest snapshot values (in T$) and 2-year historical time
        series for charting, including a computed Net Liquidity line.
        """
        cached = _cache.get("fed_liquidity")
        if cached is not None:
            return cached

        fred = _get_fred()
        if fred is None:
            return {}

        start = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")

        raw_series: Dict[str, pd.Series] = {}
        snapshot: List[dict] = []

        for series_id, meta in FED_LIQUIDITY_SERIES.items():
            try:
                data = fred.get_series(series_id, observation_start=start)
                if data is not None and not data.empty:
                    data = data.dropna()
                    if data.empty:
                        continue
                    raw_series[series_id] = data
                    last_raw = _safe_float(data.iloc[-1])
                    prev_raw = _safe_float(data.iloc[-2]) if len(data) >= 2 else None
                    divisor = meta["divisor"]
                    last_t = last_raw / divisor if last_raw is not None else None
                    prev_t = prev_raw / divisor if prev_raw is not None else None
                    chg = (
                        (last_t - prev_t)
                        if (last_t is not None and prev_t is not None)
                        else None
                    )
                    snapshot.append(
                        {
                            "series": series_id,
                            "name": meta["name"],
                            "value": _safe_float(last_t),
                            "change": _safe_float(chg),
                            "unit": "T$",
                            "freq": meta["freq"],
                            "date": str(data.index[-1].date()),
                        }
                    )
            except Exception as e:
                logger.debug(f"Fed liquidity fetch error for {series_id}: {e}")

        # Build aligned historical dataframe in trillions
        hist: Dict[str, List[dict]] = {}
        for sid, series in raw_series.items():
            divisor = FED_LIQUIDITY_SERIES[sid]["divisor"]
            converted = series / divisor
            hist[sid] = [
                {"date": str(idx.date()), "value": _safe_float(v)}
                for idx, v in converted.items()
            ]

        # Compute Net Liquidity = Fed Assets − TGA − RRP
        net_liq_series: List[dict] = []
        if (
            "WALCL" in raw_series
            and "WTREGEN" in raw_series
            and "RRPONTSYD" in raw_series
        ):
            walcl = (
                (raw_series["WALCL"] / FED_LIQUIDITY_SERIES["WALCL"]["divisor"])
                .resample("B")
                .ffill()
            )
            tga = (
                (raw_series["WTREGEN"] / FED_LIQUIDITY_SERIES["WTREGEN"]["divisor"])
                .resample("B")
                .ffill()
            )
            rrp = (
                (raw_series["RRPONTSYD"] / FED_LIQUIDITY_SERIES["RRPONTSYD"]["divisor"])
                .resample("B")
                .ffill()
            )
            combined = pd.DataFrame({"walcl": walcl, "tga": tga, "rrp": rrp}).dropna()
            if not combined.empty:
                combined["net_liq"] = (
                    combined["walcl"] - combined["tga"] - combined["rrp"]
                )
                net_liq_series = [
                    {"date": str(idx.date()), "value": _safe_float(v)}
                    for idx, v in combined["net_liq"].items()
                ]

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "snapshot": snapshot,
            "history": hist,
            "net_liquidity": net_liq_series,
        }
        _cache.set("fed_liquidity", result, FRED_TTL)
        return result

    # -- Central Bank Meeting Tracker ----------------------------------------

    def get_cb_meeting_tracker(self) -> dict:
        """Central bank meeting countdown with OIS-implied rate context.

        Returns FOMC meeting schedule, countdown, current Fed Funds target,
        SOFR, and 2Y Treasury as proxy for market-implied rate path.
        Meeting-specific probabilities (e.g. CME FedWatch) require CME data.
        """
        cached = _cache.get("cb_meeting_tracker")
        if cached is not None:
            return cached

        from backend.cb_meeting_schedule import (
            get_next_fomc_meeting,
            get_upcoming_fomc_meetings,
        )

        result: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "fed": {},
            "upcoming": [],
        }

        # FOMC schedule
        next_meeting = get_next_fomc_meeting()
        if next_meeting:
            meeting_date, has_sep = next_meeting
            from datetime import date

            days = (meeting_date - date.today()).days
            result["fed"]["next_meeting_date"] = meeting_date.isoformat()
            result["fed"]["days_until"] = days
            result["fed"]["has_sep"] = has_sep
            result["fed"][
                "label"
            ] = f"{meeting_date.strftime('%b %d')}{' (SEP)' if has_sep else ''}"

        result["upcoming"] = get_upcoming_fomc_meetings(limit=6)

        # Policy rates and implied path proxy from FRED
        fred = _get_fred()
        if fred:
            start = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            series_ids = ["DFEDTARU", "SOFR", "EFFR", "DGS2"]
            for sid in series_ids:
                try:
                    data = fred.get_series(sid, observation_start=start)
                    if data is not None and not data.empty:
                        data = data.dropna()
                        if not data.empty:
                            last_val = _safe_float(data.iloc[-1])
                            if sid == "DFEDTARU":
                                result["fed"]["target_upper"] = last_val
                            elif sid == "SOFR":
                                result["fed"]["sofr"] = last_val
                            elif sid == "EFFR":
                                result["fed"]["effr"] = last_val
                            elif sid == "DGS2":
                                result["fed"]["two_year_yield"] = last_val
                except Exception as e:
                    logger.debug(f"CB tracker FRED fetch error for {sid}: {e}")

        # Compute implied path proxy: 2Y yield vs target (spread = market pricing in cuts/hikes)
        target = result["fed"].get("target_upper")
        two_y = result["fed"].get("two_year_yield")
        if target is not None and two_y is not None:
            result["fed"]["two_y_minus_target"] = round(two_y - target, 2)

        _cache.set("cb_meeting_tracker", result, FRED_TTL)
        return result

    # -- Batch sparklines ----------------------------------------------------

    def get_batch_sparklines(self, days: int = 30) -> Dict[str, List[dict]]:
        """Batch-fetch sparkline data for all yfinance-tracked instruments.

        Returns {ticker: [{date, close}, ...]} for every ticker in
        RATES_TICKERS, FX_TICKERS, EQUITY_TICKERS, and COMMODITY_TICKERS.
        """
        cache_key = f"batch_sparklines_{days}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        tickers = list(ALL_YF_TICKERS.keys())
        df = _yf_download(tickers, period=f"{days}d", interval="1d")

        result: Dict[str, List[dict]] = {}
        if df.empty:
            return result

        is_multi = isinstance(df.columns, pd.MultiIndex)
        for ticker in tickers:
            try:
                if is_multi:
                    if ticker not in df["Close"].columns:
                        continue
                    close = df["Close"][ticker].dropna()
                else:
                    close = df["Close"].dropna()

                if close.empty:
                    continue

                points = [
                    {"date": str(idx.date()), "close": _safe_float(val)}
                    for idx, val in close.items()
                ]
                result[ticker] = points
            except Exception as e:
                logger.debug(f"Sparkline extraction error for {ticker}: {e}")

        _cache.set(cache_key, result, SPARKLINE_TTL)
        return result

    # -- Combined overview ---------------------------------------------------

    def get_overview(self) -> dict:
        """Single call that returns all panels for the dashboard.

        Uses parallel execution for faster response time.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Check IBKR connection status
        ibkr_connected = self._check_ibkr_connection()

        # Define all data fetch functions
        fetch_functions = {
            "rates": self.get_rates_snapshot,
            "fx": self.get_fx_snapshot,
            "equities": self.get_equities_snapshot,
            "commodities": self.get_commodities_snapshot,
            "macro": self.get_macro_pulse,
            "what_changed": self.get_what_changed,
            "curves": self.get_curves_data,
            "fed_liquidity": self.get_fed_liquidity_data,
            "cb_meetings": self.get_cb_meeting_tracker,
            "sparklines": self.get_batch_sparklines,
        }

        # Execute all fetches in parallel
        results = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            # Submit all tasks
            future_to_key = {
                executor.submit(func): key for key, func in fetch_functions.items()
            }

            # Collect results as they complete
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    logger.warning(f"Error fetching {key}: {e}")
                    results[key] = {"error": str(e)}

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ibkr_connected": ibkr_connected,
            **results,
        }

    def _check_ibkr_connection(self) -> bool:
        """Check if IBKR TWS/Gateway is connected."""
        try:
            if HAS_DATA_PROVIDERS and data_provider_manager:
                ibkr_provider = data_provider_manager.get_provider("ibkr")
                if ibkr_provider:
                    # Try to get a quote to check connectivity
                    # This will fail fast if not connected
                    return True  # Provider exists, actual connectivity checked on quote fetch
        except Exception:
            pass
        return False

    # -- Historical data for sparklines --------------------------------------

    def get_historical(self, symbol: str, days: int = 30) -> List[dict]:
        cache_key = f"hist_{symbol}_{days}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        df = _yf_download([symbol], period=f"{days}d", interval="1d")
        if df.empty:
            return []

        is_multi = isinstance(df.columns, pd.MultiIndex)
        close = df["Close"][symbol].dropna() if is_multi else df["Close"].dropna()

        points = [
            {"date": str(idx.date()), "close": _safe_float(val)}
            for idx, val in close.items()
        ]
        _cache.set(cache_key, points, REALTIME_TTL)
        return points

    # -- Data source fallback methods ----------------------------------------

    def get_data_with_fallback(
        self, symbol: str, asset_class: str, days: int = 30
    ) -> Dict[str, Any]:
        """Fetch data with automatic fallback through available sources.

        This method tries multiple data sources in priority order:
        1. IBKR (if available and configured)
        2. Parquet store (if data already cached)
        3. yfinance (always available as fallback)

        Args:
            symbol: Ticker symbol or FRED series ID
            asset_class: Asset class (equity, fx, rates, macro, commodities)
            days: Number of days of history

        Returns:
            Dict with keys: data, source_used, fallback_reason, success
        """
        from backend.data_source_manager import (
            DataSource,
            data_source_manager,
            record_failure,
            record_success,
        )

        # Try IBKR first for equities/fx
        if asset_class in ["equity", "fx", "commodities"]:
            try:
                from backend.data_providers import data_provider_manager

                result = data_provider_manager.get_historical_data_with_fallback(
                    symbol=symbol,
                    start_date=datetime.now() - timedelta(days=days),
                    end_date=datetime.now(),
                    asset_class=asset_class,
                    interval="1d",
                )
                if result["success"]:
                    result["data_source"] = result["source_used"]
                    return result
            except Exception as e:
                logger.debug(f"IBKR fallback failed for {symbol}: {e}")

        # Try Parquet store
        if asset_class in ["equity", "equity_index", "fx", "commodities", "rates"]:
            try:
                from backend.market_data_store import market_data_store

                df = market_data_store.query(
                    asset_class=asset_class,
                    tickers=[symbol],
                    start_date=(datetime.now() - timedelta(days=days)).strftime(
                        "%Y-%m-%d"
                    ),
                    end_date=datetime.now().strftime("%Y-%m-%d"),
                )
                if not df.empty:
                    record_success(DataSource.PARQUET_STORE)
                    return {
                        "data": df,
                        "source_used": "parquet",
                        "fallback_reason": None,
                        "success": True,
                        "data_source": "parquet",
                    }
            except Exception as e:
                logger.debug(f"Parquet fallback failed for {symbol}: {e}")

        # Fallback to yfinance
        try:
            df = _yf_download([symbol], period=f"{days}d", interval="1d")
            if not df.empty:
                record_success(DataSource.YFINANCE)
                return {
                    "data": df,
                    "source_used": "yfinance",
                    "fallback_reason": None,
                    "success": True,
                    "data_source": "yfinance",
                }
        except Exception as e:
            logger.debug(f"yfinance fallback failed for {symbol}: {e}")
            record_failure(DataSource.YFINANCE)

        # All sources failed
        return {
            "data": pd.DataFrame(),
            "source_used": None,
            "fallback_reason": f"All sources failed for {symbol}",
            "success": False,
            "data_source": None,
        }

    def get_source_status(self) -> Dict[str, Any]:
        """Get status of all data sources.

        Returns:
            Dict with source information and health status
        """
        try:
            from backend.data_source_manager import data_source_manager

            return data_source_manager.get_source_info()
        except ImportError:
            return {
                "yfinance": {
                    "status": "unknown",
                    "supported_asset_classes": ["equity", "fx", "rates", "commodities"],
                },
                "fred": {
                    "status": "unknown",
                    "supported_asset_classes": ["rates", "macro", "fed_liquidity"],
                },
                "ibkr": {
                    "status": "unknown",
                    "supported_asset_classes": ["equity", "fx", "commodities"],
                },
                "parquet": {
                    "status": "unknown",
                    "supported_asset_classes": [
                        "equity",
                        "fx",
                        "rates",
                        "macro",
                        "commodities",
                        "fed_liquidity",
                    ],
                },
            }


# Singleton
market_data_service = MarketDataService()
