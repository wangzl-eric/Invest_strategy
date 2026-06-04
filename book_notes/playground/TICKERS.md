# Supported Tickers Reference

Popular and supported tickers organized by asset class and market.
All tickers in the **Active** sections are verified against current IBKR subscriptions
and available via `get_prices()` or `get_macro_series()` in `data_helpers.py`.

> **Source of truth:** `config/ticker_universe.py`
> **Last verified:** 2026-02-28
> **Subscriptions active:** US Equities (IBKR-PRO), Hong Kong L1, IDEALPRO FX

---

## Quick Import

```python
from config.ticker_universe import (
    US_LARGE_CAP, US_MID_SMALL_CAP, US_ETFS,
    HK_EQUITIES,
    FOREX_MAJOR, FOREX_MINOR, FOREX_EM,
    ALL_US_EQUITIES, ALL_FOREX, ACTIVE_UNIVERSE,
)
```

---

## US Equities

### Large Cap — `US_LARGE_CAP`

#### Mega Cap (Top 10)

| Ticker | Name |
|--------|------|
| AAPL | Apple |
| MSFT | Microsoft |
| GOOGL | Alphabet Class A |
| AMZN | Amazon |
| NVDA | NVIDIA |
| META | Meta Platforms |
| TSLA | Tesla |
| BRK.B | Berkshire Hathaway Class B |
| JPM | JPMorgan Chase |
| JNJ | Johnson & Johnson |

#### Top 20

| Ticker | Name |
|--------|------|
| V | Visa |
| PG | Procter & Gamble |
| UNH | UnitedHealth |
| HD | Home Depot |
| MA | Mastercard |
| DIS | Walt Disney |
| PYPL | PayPal |
| BAC | Bank of America |
| ADBE | Adobe |
| NFLX | Netflix |

#### Top 30

| Ticker | Name |
|--------|------|
| CRM | Salesforce |
| INTC | Intel |
| VZ | Verizon |
| T | AT&T |
| PFE | Pfizer |
| MRK | Merck |
| KO | Coca-Cola |
| PEP | PepsiCo |
| ABT | Abbott Labs |
| TMO | Thermo Fisher |

---

### Mid / Small Cap — `US_MID_SMALL_CAP`

| Ticker | Name | Category |
|--------|------|----------|
| SNAP | Snap | Mid Cap |
| ROKU | Roku | Mid Cap |
| ZM | Zoom | Mid Cap |
| DDOG | Datadog | Mid Cap |
| CRWD | CrowdStrike | Mid Cap |
| NET | Cloudflare | Mid Cap |
| OKTA | Okta | Mid Cap |
| SNOW | Snowflake | Mid Cap |
| PLTR | Palantir | Mid Cap |
| U | Unity Software | Mid Cap |
| RIVN | Rivian | Small Cap / IPO |
| LCID | Lucid | Small Cap / IPO |
| SOFI | SoFi | Small Cap / IPO |
| ARM | Arm Holdings | Small Cap / IPO |
| PATH | UiPath | Small Cap / IPO |

---

## US ETFs — `US_ETFS`

### Broad Index

| Ticker | Name |
|--------|------|
| SPY | S&P 500 |
| QQQ | Nasdaq 100 |
| IWM | Russell 2000 |
| DIA | Dow Jones |

### Sector ETFs (SPDR)

| Ticker | Sector |
|--------|--------|
| XLK | Technology |
| XLF | Financials |
| XLE | Energy |
| XLV | Healthcare |
| XLC | Communications |
| XLY | Consumer Discretionary |
| XLP | Consumer Staples |
| XLB | Materials |
| XLRE | Real Estate |
| XLU | Utilities |

### Bond ETFs

| Ticker | Name | Duration |
|--------|------|----------|
| TLT | iShares 20+ Year Treasury | Long |
| IEF | iShares 7-10 Year Treasury | Intermediate |
| SHY | iShares 1-3 Year Treasury | Short |
| LQD | iShares Investment Grade Corporate | Credit |
| HYG | iShares High Yield Corporate | Credit |
| AGG | iShares US Aggregate Bond | Broad |

### Commodity ETFs

| Ticker | Commodity |
|--------|----------|
| GLD | Gold |
| SLV | Silver |
| USO | Crude Oil |
| UNG | Natural Gas |

### Volatility ETFs

| Ticker | Name | Note |
|--------|------|------|
| VXX | iPath VIX Short-Term Futures | 1x |
| UVXY | ProShares Ultra VIX | 1.5x leveraged |

---

## Hong Kong Equities — `HK_EQUITIES`

> Subscription: HKSE L1 + HK Derivatives L1

### HSI Index Components

| Ticker | Name |
|--------|------|
| 0700.HK | Tencent |
| 0992.HK | Lenovo |
| 0005.HK | HSBC |
| 0941.HK | China Mobile |
| 0388.HK | HKEX |
| 0011.HK | Hang Seng Bank |
| 0001.HK | CK Hutchison |
| 0012.HK | Henderson Land |
| 0066.HK | MTR |
| 0019.A.HK | Swire Pacific |

### Tech / Growth

| Ticker | Name |
|--------|------|
| 1024.HK | Xiaomi |
| 3690.HK | Meituan |
| 6618.HK | JD Health |
| 9961.HK | Trip.com |

### Financials

| Ticker | Name |
|--------|------|
| 3988.HK | Bank of China |
| 0939.HK | CCB |
| 2388.HK | BOC Hong Kong |

### Properties

| Ticker | Name |
|--------|------|
| 0016.HK | Vanke |
| 1109.HK | China Resources Land |

---

## Forex — via IDEALPRO

> Pass pairs directly to `get_prices()`. Format: `"EURUSD"`, `"USDJPY"`, etc.

### Major Pairs — `FOREX_MAJOR`

| Pair | Description |
|------|-------------|
| EURUSD | Euro / US Dollar |
| GBPUSD | British Pound / US Dollar |
| USDJPY | US Dollar / Japanese Yen |
| USDCAD | US Dollar / Canadian Dollar |
| USDCHF | US Dollar / Swiss Franc |
| AUDUSD | Australian Dollar / US Dollar |
| NZDUSD | New Zealand Dollar / US Dollar |

### Minor Pairs — `FOREX_MINOR`

| Pair | Description |
|------|-------------|
| EURGBP | Euro / British Pound |
| EURJPY | Euro / Japanese Yen |
| GBPJPY | British Pound / Japanese Yen |
| EURCHF | Euro / Swiss Franc |
| AUDJPY | Australian Dollar / Japanese Yen |
| CADJPY | Canadian Dollar / Japanese Yen |
| CHFJPY | Swiss Franc / Japanese Yen |
| EURNOK | Euro / Norwegian Krone |
| EURSEK | Euro / Swedish Krona |
| EURPLN | Euro / Polish Zloty |
| EURHUF | Euro / Hungarian Forint |

### Emerging Market Pairs — `FOREX_EM`

| Pair | Description |
|------|-------------|
| USDTRY | US Dollar / Turkish Lira |
| USDZAR | US Dollar / South African Rand |
| USDBRL | US Dollar / Brazilian Real |
| USDMXN | US Dollar / Mexican Peso |
| USDINR | US Dollar / Indian Rupee |
| USDCNY | US Dollar / Chinese Yuan |
| USDHKD | US Dollar / Hong Kong Dollar |
| USDSGD | US Dollar / Singapore Dollar |

---

## Macro / FRED Series

> Use `get_macro_series(series_id, start=...)` or the shortcut `get_fred_shortcut(key, start=...)`.

### Shortcuts (via `get_fred_shortcut`)

| Shortcut | FRED Series | Description |
|----------|-------------|-------------|
| `vix` | VIXCLS | CBOE Volatility Index |
| `vvix` | VVIX | VIX of VIX |
| `dgs10` | DGS10 | 10-Year Treasury Yield |
| `dgs2` | DGS2 | 2-Year Treasury Yield |
| `dff` | DFF | Fed Funds Rate |
| `yield_curve` | T10Y2Y | 10Y-2Y Spread |
| `hy_spread` | BAMLH0A0HYM2 | HY Credit Spread |
| `ig_spread` | BAMLC0A0CM | IG Credit Spread |
| `unemployment` | UNRATE | Unemployment Rate |
| `cpi` | CPIAUCSL | CPI (All Urban) |
| `gdp` | GDP | US GDP |
| `fed_balance_sheet` | WALCL | Fed Balance Sheet |

### Datasets scanned automatically

| Dataset | Contents |
|---------|----------|
| `macro_indicators` | VIX, credit spreads, unemployment, CPI, GDP |
| `treasury_yields` | DGS2, DGS5, DGS10, DGS30 |
| `fed_liquidity` | Fed balance sheet, reserve balances |

---

## Futures — Not Active

Requires CME subscription (not currently enabled). Commented out in `ticker_universe.py`.

| Category | Examples |
|----------|----------|
| Index | ES (S&P 500), NQ (Nasdaq), YM (Dow), RTY (Russell) |
| Energy | CL (Crude), BZ (Brent), NG (Natural Gas) |
| Metals | GC (Gold), SI (Silver), HG (Copper) |
| Bonds | ZB (30Y), ZN (10Y), ZF (5Y), ZT (2Y) |

To activate: add CME subscription in IBKR and set `cme: true` in `config/ibkr_data_subscriptions.yaml`.

---

## Usage Examples

```python
from workstation.playground.shared.data_helpers import get_prices, get_macro_series, get_fred_shortcut

# Broad market snapshot
prices = get_prices(["SPY", "TLT", "GLD", "VXX"], start="2020-01-01")

# Sector rotation study
prices = get_prices(["XLK", "XLF", "XLE", "XLV", "XLC"], start="2018-01-01")

# FX carry basket
prices = get_prices(["AUDUSD", "NZDUSD", "USDJPY", "USDCHF"], start="2015-01-01")

# HK tech
prices = get_prices(["0700.HK", "3690.HK", "9961.HK"], start="2020-01-01")

# Macro backdrop
vix = get_fred_shortcut("vix", start="2015-01-01")
yc = get_fred_shortcut("yield_curve", start="2010-01-01")
credit = get_macro_series(["BAMLH0A0HYM2", "BAMLC0A0CM"], start="2010-01-01")
```

---

## Adding New Tickers

1. Add the ticker to the appropriate list in `config/ticker_universe.py`
2. Verify your IBKR subscription covers that market in `config/ibkr_data_subscriptions.yaml`
3. Pull data: `start_refresh_job(dataset="equities", identifiers=["NEW"], start="2020-01-01")`
4. Update `LAST_UPDATED` in `ticker_universe.py`
