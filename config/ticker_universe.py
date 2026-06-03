# IBKR Ticker Universe Configuration
#
# Curated list of tickers based on verified IBKR subscriptions:
# - US Equities: US Real-Time Non-Consolidated Streaming Quotes (IBKR-PRO)
# - Hong Kong: HKSE L1, HK Derivatives L1
# - Forex: IDEALPRO FX
#
# This file provides quick-lookup universes for different asset classes

# ==============================================================================
# US Equities - Large Cap Core
# ==============================================================================
US_LARGE_CAP = [
    # Mega Cap (Top 10)
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "GOOGL",  # Alphabet Class A
    "AMZN",  # Amazon
    "NVDA",  # NVIDIA
    "META",  # Meta Platforms
    "TSLA",  # Tesla
    "BRK.B",  # Berkshire Hathaway Class B
    "JPM",  # JPMorgan Chase
    "JNJ",  # Johnson & Johnson
    # Top 20
    "V",  # Visa
    "PG",  # Procter & Gamble
    "UNH",  # UnitedHealth
    "HD",  # Home Depot
    "MA",  # Mastercard
    "DIS",  # Walt Disney
    "PYPL",  # PayPal
    "BAC",  # Bank of America
    "ADBE",  # Adobe
    "NFLX",  # Netflix
    # Top 30
    "CRM",  # Salesforce
    "INTC",  # Intel
    "VZ",  # Verizon
    "T",  # AT&T
    "PFE",  # Pfizer
    "MRK",  # Merck
    "KO",  # Coca-Cola
    "PEP",  # PepsiCo
    "ABT",  # Abbott Labs
    "TMO",  # Thermo Fisher
]

# ==============================================================================
# US Equities - ETFs (Popular)
# ==============================================================================
US_ETFS = [
    # SPAC/Index ETFs
    "SPY",  # S&P 500 ETF
    "QQQ",  # Nasdaq 100 ETF
    "IWM",  # Russell 2000 ETF
    "DIA",  # Dow Jones ETF
    # Sector ETFs
    "XLK",  # Technology
    "XLF",  # Financials
    "XLE",  # Energy
    "XLV",  # Healthcare
    "XLC",  # Communications
    "XLY",  # Consumer Discretionary
    "XLP",  # Consumer Staples
    "XLB",  # Materials
    "XLRE",  # Real Estate
    "XLU",  # Utilities
    # Bond ETFs
    "TLT",  # 20+ Year Treasury
    "IEF",  # 7-10 Year Treasury
    "SHY",  # 1-3 Year Treasury
    "LQD",  # Investment Grade Corporate Bonds
    "HYG",  # High Yield Corporate Bonds
    "AGG",  # US Aggregate Bond
    # Commodity ETFs
    "GLD",  # Gold
    "SLV",  # Silver
    "USO",  # Oil
    "UNG",  # Natural Gas
    # Volatility
    "VXX",  # Volatility
    "UVXY",  # Ultra VIX
]

# ==============================================================================
# US Equities - Mid/Small Cap (Selected)
# ==============================================================================
US_MID_SMALL_CAP = [
    # Mid Cap
    "SNAP",  # Snap
    "ROKU",  # Roku
    "ZM",  # Zoom
    "DDOG",  # Datadog
    "CRWD",  # CrowdStrike
    "NET",  # Cloudflare
    "OKTA",  # Okta
    "SNOW",  # Snowflake
    "PLTR",  # Palantir
    "U",  # Unity Software
    # Small Cap / IPO
    "RIVN",  # Rivian
    "LCID",  # Lucid
    "SOFI",  # SoFi
    "ARM",  # Arm Holdings
    "PATH",  # UiPath
]

# ==============================================================================
# Hong Kong Equities - Major Stocks
# ==============================================================================
HK_EQUITIES = [
    # Index Components (HSI)
    "0700.HK",  # Tencent
    "0992.HK",  # Lenovo
    "0005.HK",  # HSBC
    "0941.HK",  # China Mobile
    "0388.HK",  # HKEX
    "0011.HK",  # Hang Seng Bank
    "0001.HK",  # CK Hutchison
    "0012.HK",  # Henderson Land
    "0066.HK",  # MTR
    "0019.A.HK",  # Swire Pacific
    # Tech / Growth
    "1024.HK",  # Xiaomi
    "3690.HK",  # Meituan
    "6618.HK",  # JD Health
    "9961.HK",  # Trip.com
    # Finance
    "3988.HK",  # Bank of China
    "0939.HK",  # CCB
    "2388.HK",  # BOC Hong Kong
    # Properties
    "0016.HK",  # Vanke
    "1109.HK",  # China Resources Land
    # H-Derivatives (for options)
    # Note: HK options require specific subscription
]

# ==============================================================================
# Forex - Major & Minor Pairs
# ==============================================================================
FOREX_MAJOR = [
    "EURUSD",  # Euro / US Dollar
    "GBPUSD",  # British Pound / US Dollar
    "USDJPY",  # US Dollar / Japanese Yen
    "USDCAD",  # US Dollar / Canadian Dollar
    "USDCHF",  # US Dollar / Swiss Franc
    "AUDUSD",  # Australian Dollar / US Dollar
    "NZDUSD",  # New Zealand Dollar / US Dollar
]

FOREX_MINOR = [
    "EURGBP",  # Euro / British Pound
    "EURJPY",  # Euro / Japanese Yen
    "GBPJPY",  # British Pound / Japanese Yen
    "EURCHF",  # Euro / Swiss Franc
    "AUDJPY",  # Australian Dollar / Japanese Yen
    "CADJPY",  # Canadian Dollar / Japanese Yen
    "CHFJPY",  # Swiss Franc / Japanese Yen
    "EURNOK",  # Euro / Norwegian Krone
    "EURSEK",  # Euro / Swedish Krona
    "EURPLN",  # Euro / Polish Zloty
    "EURHUF",  # Euro / Hungarian Forint
]

FOREX_EM = [
    "USDTRY",  # US Dollar / Turkish Lira
    "USDZAR",  # US Dollar / South African Rand
    "USDBRL",  # US Dollar / Brazilian Real
    "USDMXN",  # US Dollar / Mexican Peso
    "USDINR",  # US Dollar / Indian Rupee
    "USDCNY",  # US Dollar / Chinese Yuan
    "USDHKD",  # US Dollar / Hong Kong Dollar
    "USDSGD",  # US Dollar / Singapore Dollar
]

# ==============================================================================
# US Futures - NOT ACTIVATED (requires CME subscription)
# ==============================================================================
# Uncomment if you add CME futures subscription:
#
# US_FUTURES_INDEX = [
#     "ES",    # E-mini S&P 500
#     "NQ",    # E-mini Nasdaq 100
#     "YM",    # E-mini Dow
#     "RTY",   # E-mini Russell 2000
# ]
#
# US_FUTURES_ENERGY = [
#     "CL",    # Crude Oil
#     "BZ",    # Brent Crude
#     "NG",    # Natural Gas
#     "RB",    # RBOB Gasoline
# ]
#
# US_FUTURES_METALS = [
#     "GC",    # Gold
#     "SI",    # Silver
#     "HG",    # Copper
#     "PL",    # Platinum
#     "PA",    # Palladium
# ]
#
# US_FUTURES_BONDS = [
#     "ZB",    # 30-Year Treasury
#     "ZN",    # 10-Year Treasury
#     "ZF",    # 5-Year Treasury
#     "ZT",    # 2-Year Treasury
# ]

# ==============================================================================
# Quick Lookup Collections
# ==============================================================================

# All US equities (large + mid/small + ETFs)
ALL_US_EQUITIES = US_LARGE_CAP + US_MID_SMALL_CAP + US_ETFS

# All forex pairs
ALL_FOREX = FOREX_MAJOR + FOREX_MINOR + FOREX_EM

# All available with current subscriptions
ACTIVE_UNIVERSE = {
    "us_equities": US_LARGE_CAP,
    "us_etfs": US_ETFS,
    "hk_equities": HK_EQUITIES,
    "forex_major": FOREX_MAJOR,
    "forex_minor": FOREX_MINOR,
}

# ==============================================================================
# Metadata
# ==============================================================================
LAST_UPDATED = "2026-02-28"
SUBSCRIPTIONS_VERIFIED = {
    "us_equities": "US Real-Time Non-Consolidated Streaming Quotes (IBKR-PRO)",
    "hk_equities": "Hong Kong Securities Exchange L1",
    "forex": "IDEALPRO FX",
}
