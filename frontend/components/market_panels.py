"""Reusable Dash components for the cross-asset Markets tab.

Each function returns a Dash layout fragment that can be placed inside a
dbc.Col / dbc.Row in app.py.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# ---------------------------------------------------------------------------
# Shared styling helpers
# ---------------------------------------------------------------------------

_CARD_STYLE = "data-card"
_SECTION_TITLE = "section-title"

GREEN = "#3fb950"
RED = "#f85149"
BLUE = "#58a6ff"
MUTED = "#8b949e"
TEXT_PRIMARY = "#c9d1d9"
YELLOW = "#d29922"
PURPLE = "#a371f7"

# ---------------------------------------------------------------------------
# Instrument definitions (shown as browser tooltip on hover)
# ---------------------------------------------------------------------------

DEFINITIONS: dict[str, str] = {
    # Treasuries
    "1-Month Treasury": "US Treasury constant maturity yield, 1-month tenor.",
    "3-Month Treasury": "US Treasury constant maturity yield, 3-month tenor. Key short-rate benchmark.",
    "6-Month Treasury": "US Treasury constant maturity yield, 6-month tenor.",
    "1-Year Treasury": "US Treasury constant maturity yield, 1-year tenor.",
    "2-Year Treasury": "US Treasury constant maturity yield. Highly sensitive to Fed policy expectations.",
    "3-Year Treasury": "US Treasury constant maturity yield, 3-year tenor.",
    "5-Year Treasury": "US Treasury constant maturity yield. Reflects medium-term growth and inflation expectations.",
    "7-Year Treasury": "US Treasury constant maturity yield, 7-year tenor.",
    "10-Year Treasury": "US Treasury constant maturity yield. The most-watched global benchmark rate; key driver of mortgage rates.",
    "20-Year Treasury": "US Treasury constant maturity yield, 20-year tenor.",
    "30-Year Treasury": "US Treasury constant maturity yield, long-end benchmark. Reflects long-term inflation expectations and term premium.",
    # Curve spreads
    "10Y-2Y Spread": "Difference between 10Y and 2Y Treasury yields. Classic recession indicator — inversions have preceded every US recession since 1970.",
    "10Y-3M Spread": "Difference between 10Y and 3M Treasury yields. The NY Fed's preferred recession probability signal.",
    # Policy rates
    "Fed Funds Target (Upper)": "Upper bound of the Federal Reserve's target rate range. The primary tool of US monetary policy.",
    "SOFR": "Secured Overnight Financing Rate. Broad measure of overnight Treasury repo rates; replaced LIBOR as the USD benchmark.",
    # Inflation
    "5Y Breakeven Inflation": "Market-implied 5-year average inflation. Derived from nominal-minus-TIPS yield spread.",
    "10Y Breakeven Inflation": "Market-implied 10-year average inflation. Derived from nominal-minus-TIPS yield spread.",
    "5Y5Y Forward Inflation": "Expected average inflation over 5 years starting 5 years from now. The Fed's preferred long-term inflation expectations gauge.",
    # Real yields
    "5Y Real Yield (TIPS)": "5-Year Treasury Inflation-Protected Securities yield. The real (inflation-adjusted) cost of borrowing. Negative = accommodative real policy.",
    "10Y Real Yield (TIPS)": "10-Year TIPS yield. The most important real rate benchmark — drives equity valuations, gold, and real asset pricing.",
    "30Y Real Yield (TIPS)": "30-Year TIPS yield. Long-end real rate; reflects long-term real growth expectations and term premium.",
    # Macro fallback
    "VIX (Equity Volatility)": "CBOE Volatility Index — 30-day S&P 500 implied vol. Below 15 = complacent, above 25 = stressed.",
    "HY Credit ETF (HYG)": "iShares iBoxx $ High Yield Corporate Bond ETF. Falling prices = widening HY spreads = risk-off.",
    "IG Credit ETF (LQD)": "iShares iBoxx $ Investment Grade Corporate Bond ETF. Proxy for IG credit conditions.",
    "TIPS Bond ETF (TIP)": "iShares TIPS Bond ETF. Rising = higher inflation expectations or lower real yields.",
    "7-10Y Treasury ETF (IEF)": "iShares 7-10 Year Treasury Bond ETF. Proxy for intermediate-term rate expectations.",
    "Gold ETF (GLD)": "SPDR Gold Shares. Traditional safe haven and inflation hedge.",
    # Macro FRED
    "Unemployment Rate": "Total civilian unemployment rate (U-3). Headline labor market indicator published monthly by BLS.",
    "CPI (All Urban)": "Consumer Price Index for All Urban Consumers. Primary US headline inflation measure.",
    "Real GDP": "Real Gross Domestic Product in billions of chained 2017 dollars. Published quarterly by BEA.",
    "Consumer Sentiment": "University of Michigan Consumer Sentiment Index. Leading indicator of consumer spending.",
    "Chicago Fed NFCI": "National Financial Conditions Index (weekly). Negative = looser than average, positive = tighter.",
    "HY OAS Spread": "ICE BofA US High Yield Option-Adjusted Spread. Credit risk premium for sub-IG bonds over Treasuries.",
    # Fed balance sheet / QE-QT
    "Fed Total Assets": "Total assets on the Federal Reserve's balance sheet (WALCL). Rising = QE (asset purchases), falling = QT (balance sheet runoff). The single most important measure of Fed liquidity injection.",
    "ON Reverse Repo (RRP)": "Overnight Reverse Repo facility usage. Cash parked at the Fed by money market funds and GSEs. High RRP = excess liquidity seeking safe overnight return. Declining RRP during QT signals reserves are being drained from the financial system.",
    "Reserve Balances": "Deposits held by depository institutions at Federal Reserve Banks. The purest measure of banking system liquidity. QT drains reserves; when they fall to 'ample' (vs abundant), funding stress can emerge.",
    "Treasury General Account (TGA)": "The US Treasury's checking account at the Fed. TGA buildups (e.g., post-debt-ceiling, tax season) drain liquidity from the banking system. TGA drawdowns inject liquidity. Key swing factor for short-term funding conditions.",
    "Fed Holdings: Treasuries": "US Treasury securities held outright by the Fed (SOMA portfolio). The largest component of Fed assets. QT reduces this via maturity runoff without reinvestment.",
    "Fed Holdings: MBS": "Agency mortgage-backed securities held by the Fed. QT lets MBS run off via principal payments. Slower to shrink than Treasuries due to prepayment dynamics.",
    "Net Liquidity": "Fed Total Assets minus TGA minus RRP. A widely-tracked proxy for the effective liquidity the Fed is injecting into the financial system. Correlated with risk asset performance.",
    # Central bank meeting tracker
    "2Y-FF Spread": "2-Year Treasury yield minus Fed Funds target. Negative = market prices more cuts than hikes over 2Y. Proxy for OIS-implied rate path.",
}

# Category display order and labels for the rates table
CATEGORY_ORDER = [
    ("treasury", "Treasury Yields"),
    ("curve_spread", "Yield Curve Spreads"),
    ("policy", "Policy Rates"),
    ("real_yield", "Real Yields (TIPS)"),
    ("inflation", "Inflation Expectations"),
    ("swap", "Swap Rates"),
    ("swap_spread", "Swap Spreads"),
    ("asset_swap", "Asset Swap Spreads"),
]


def _change_color(val):
    if val is None:
        return MUTED
    return GREEN if val > 0 else RED if val < 0 else MUTED


def _format_change(val, suffix=""):
    if val is None:
        return "—"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}{suffix}"


def _format_price(val, decimals=2):
    if val is None:
        return "—"
    return f"{val:,.{decimals}f}"


def _mono(text, color=TEXT_PRIMARY, bold=False):
    return html.Span(
        text,
        style={
            "fontFamily": "'JetBrains Mono', monospace",
            "color": color,
            "fontWeight": "600" if bold else "400",
        },
    )


def _table_row(cells, header=False):
    """Build an html.Tr from a list of (text, style_dict) tuples."""
    tag = html.Th if header else html.Td
    return html.Tr([tag(text, style=style) for text, style in cells])


def _data_table(headers, rows):
    """Build a styled html.Table."""
    header_cells = [(h, {"color": MUTED, "fontWeight": "500", "fontSize": "0.75rem", "textTransform": "uppercase", "letterSpacing": "0.5px", "paddingBottom": "0.75rem"}) for h in headers]
    return html.Table(
        [html.Thead(_table_row(header_cells, header=True)), html.Tbody(rows)],
        style={"width": "100%", "borderCollapse": "collapse", "fontSize": "0.9rem"},
    )


def _tooltip_name(name: str, fallback: str = "", ticker: str = "") -> html.Span:
    """Instrument name with a native browser tooltip showing its definition.

    When *ticker* is provided the span gets an id that the click-to-expand
    callback can target.
    """
    display = name or fallback
    defn = DEFINITIONS.get(display, "")
    style: dict = {"color": TEXT_PRIMARY, "fontWeight": "500"}
    if defn:
        style["borderBottom"] = f"1px dotted {MUTED}"
        style["cursor"] = "help"
    props: dict = {"style": style}
    if ticker:
        props["id"] = {"type": "instrument-name", "index": ticker}
        style["cursor"] = "pointer"
    return html.Span(display, title=defn, **props)


# ---------------------------------------------------------------------------
# Sparkline + period-change helpers
# ---------------------------------------------------------------------------

def _build_sparkline(points, width=100, height=28):
    """Tiny line chart from a list of {date, close/value} dicts."""
    if not points or len(points) < 2:
        return html.Span("—", style={"color": MUTED, "fontSize": "0.75rem"})

    vals = [p.get("close") or p.get("value") for p in points]
    vals = [v for v in vals if v is not None]
    if len(vals) < 2:
        return html.Span("—", style={"color": MUTED, "fontSize": "0.75rem"})

    color = GREEN if vals[-1] >= vals[0] else RED

    fig = go.Figure(go.Scatter(
        y=vals, mode="lines",
        line=dict(color=color, width=1.5),
        fill="tozeroy",
        fillcolor=f"{color}15",
    ))
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=height,
        width=width,
        showlegend=False,
        hovermode=False,
    )
    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": False, "staticPlot": True},
        style={"height": f"{height}px", "width": f"{width}px", "display": "inline-block"},
    )


def _period_changes(points, is_yield=False):
    """Return (1W_change, 1M_change) from a sparkline series.

    *is_yield*: True for rates/yields — returns absolute diff;
                False for prices — returns percentage change.
    """
    if not points or len(points) < 2:
        return None, None

    vals = [p.get("close") or p.get("value") for p in points]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None, None

    last = vals[-1]
    w1, m1 = None, None

    if last is not None:
        if len(vals) >= 6:
            ref = vals[-6]
            if ref is not None and ref != 0:
                w1 = (last - ref) if is_yield else ((last / ref - 1) * 100)
        if len(vals) >= 22:
            ref = vals[-22]
            if ref is not None and ref != 0:
                m1 = (last - ref) if is_yield else ((last / ref - 1) * 100)
        elif len(vals) >= 2:
            ref = vals[0]
            if ref is not None and ref != 0:
                m1 = (last - ref) if is_yield else ((last / ref - 1) * 100)

    return _safe_round(w1), _safe_round(m1)


def _safe_round(v, digits=2):
    if v is None:
        return None
    try:
        return round(float(v), digits)
    except (ValueError, TypeError):
        return None


_CHG_COL = {
    "color": MUTED,
    "fontFamily": "'JetBrains Mono', monospace",
    "textAlign": "right",
    "fontSize": "0.8rem",
    "whiteSpace": "nowrap",
}


# ---------------------------------------------------------------------------
# Panel builders
# ---------------------------------------------------------------------------

def build_rates_panel(data: dict, sparklines: dict | None = None) -> html.Div:
    """UST yields, swap rates, swap spreads, asset swap spreads — grouped by category."""
    yf_yields = data.get("yields") or []
    fred_rates = data.get("fred") or []
    sparklines = sparklines or {}

    if fred_rates:
        by_cat: dict[str, list] = {}
        for item in fred_rates:
            cat = item.get("category", "other")
            by_cat.setdefault(cat, []).append(item)

        sections = []
        for cat_key, cat_label in CATEGORY_ORDER:
            items = by_cat.get(cat_key, [])
            if not items:
                continue
            rows = []
            for item in items:
                val = item.get("value")
                chg = item.get("change")
                unit = item.get("unit", "")
                decimals = 1 if unit == "bp" else 3
                val_display = _format_price(val, decimals)
                if unit == "bp":
                    val_display += " bp"
                hist = item.get("history") or []
                w1, m1 = _period_changes(hist, is_yield=True)
                rows.append(_table_row([
                    (_tooltip_name(item.get("name", item.get("series", "")), ticker=item.get("series", "")), {}),
                    (item.get("tenor", ""), {"color": MUTED, "textAlign": "center", "fontSize": "0.85rem"}),
                    (val_display, {"color": BLUE, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
                    (_format_change(chg), {"color": _change_color(chg), "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
                    (_format_change(w1), {**_CHG_COL, "color": _change_color(w1)}),
                    (_format_change(m1), {**_CHG_COL, "color": _change_color(m1)}),
                    (_build_sparkline(hist), {"textAlign": "center", "padding": "2px 0"}),
                    (item.get("date", ""), {"color": MUTED, "fontSize": "0.8rem", "textAlign": "right"}),
                ]))

            sections.append(html.Div([
                html.Div(cat_label, style={"color": PURPLE, "fontSize": "0.75rem", "fontWeight": "600", "textTransform": "uppercase", "letterSpacing": "0.5px", "padding": "0.5rem 0 0.25rem 0", "borderBottom": f"1px solid {MUTED}33", "marginTop": "0.5rem"}),
                _data_table(["Instrument", "Tenor", "Value", "1D", "1W", "1M", "30d", "Date"], rows),
            ]))

        table_content = html.Div(sections) if sections else html.P("No rates data available", style={"color": MUTED})
    elif yf_yields:
        rows = []
        for item in yf_yields:
            val = item.get("price")
            chg = item.get("change")
            ticker = item.get("ticker", "")
            pts = sparklines.get(ticker, [])
            w1, m1 = _period_changes(pts, is_yield=True)
            rows.append(_table_row([
                (_tooltip_name(item.get("name", ticker), ticker=ticker), {}),
                (item.get("tenor", ""), {"color": MUTED, "textAlign": "center"}),
                (_format_price(val, 3), {"color": BLUE, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
                (_format_change(chg), {"color": _change_color(chg), "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
                (_format_change(w1), {**_CHG_COL, "color": _change_color(w1)}),
                (_format_change(m1), {**_CHG_COL, "color": _change_color(m1)}),
                (_build_sparkline(pts), {"textAlign": "center", "padding": "2px 0"}),
                (item.get("date", ""), {"color": MUTED, "fontSize": "0.8rem", "textAlign": "right"}),
            ]))
        table_content = _data_table(["Instrument", "Tenor", "Yield", "1D", "1W", "1M", "30d", "Date"], rows)
    else:
        table_content = html.P("No rates data available", style={"color": MUTED})

    return html.Div([
        html.H5("Rates", className=_SECTION_TITLE),
        html.Div(table_content, style={"overflowX": "auto"}),
    ], className=_CARD_STYLE)


def build_fx_panel(data: dict, sparklines: dict | None = None) -> html.Div:
    """G10 FX pairs with DXY headline."""
    pairs = data.get("pairs") or []
    sparklines = sparklines or {}

    dxy = next((p for p in pairs if p.get("pair") == "DXY"), None)

    rows = []
    for item in pairs:
        price = item.get("price")
        chg = item.get("change")
        chg_pct = item.get("change_pct")
        ticker = item.get("ticker", "")
        pts = sparklines.get(ticker, [])
        w1, m1 = _period_changes(pts)
        rows.append(_table_row([
            (item.get("pair", ticker), {"color": BLUE, "fontWeight": "600", "fontFamily": "'JetBrains Mono', monospace"}),
            (_tooltip_name(item.get("name", ""), ticker=ticker), {}),
            (_format_price(price, 4), {"color": TEXT_PRIMARY, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (_format_change(chg_pct, "%"), {"color": _change_color(chg_pct), "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (_format_change(w1, "%"), {**_CHG_COL, "color": _change_color(w1)}),
            (_format_change(m1, "%"), {**_CHG_COL, "color": _change_color(m1)}),
            (_build_sparkline(pts), {"textAlign": "center", "padding": "2px 0"}),
            (item.get("date", ""), {"color": MUTED, "fontSize": "0.8rem", "textAlign": "right"}),
        ]))

    headline = []
    if dxy:
        dxy_chg = dxy.get("change_pct")
        headline = [
            html.Div([
                html.Span("DXY ", style={"color": MUTED, "fontSize": "0.85rem"}),
                _mono(_format_price(dxy.get("price"), 2), BLUE, bold=True),
                html.Span(f" {_format_change(dxy_chg, '%')}", style={"color": _change_color(dxy_chg), "fontSize": "0.85rem", "marginLeft": "0.5rem"}),
            ], style={"marginBottom": "0.75rem"}),
        ]

    table = _data_table(["Pair", "Name", "Spot", "1D%", "1W%", "1M%", "30d", "Date"], rows) if rows else html.P("No FX data available", style={"color": MUTED})

    return html.Div([
        html.H5("Foreign Exchange", className=_SECTION_TITLE),
        *headline,
        html.Div(table, style={"overflowX": "auto"}),
    ], className=_CARD_STYLE)


def build_equities_panel(data: dict, sparklines: dict | None = None) -> html.Div:
    """Major equity indices and VIX."""
    indices = data.get("indices") or []
    sparklines = sparklines or {}

    rows = []
    for item in indices:
        price = item.get("price")
        chg_pct = item.get("change_pct")
        name = item.get("name", item.get("ticker", ""))
        ticker = item.get("ticker", "")
        is_vix = "VIX" in name.upper()
        color = YELLOW if is_vix else TEXT_PRIMARY
        pts = sparklines.get(ticker, [])
        w1, m1 = _period_changes(pts)
        rows.append(_table_row([
            (_tooltip_name(name, ticker=ticker), {"color": color, "fontWeight": "600"}),
            (item.get("region", ""), {"color": MUTED, "textAlign": "center"}),
            (_format_price(price, 2), {"color": TEXT_PRIMARY, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (_format_change(chg_pct, "%"), {"color": _change_color(chg_pct), "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (_format_change(w1, "%"), {**_CHG_COL, "color": _change_color(w1)}),
            (_format_change(m1, "%"), {**_CHG_COL, "color": _change_color(m1)}),
            (_build_sparkline(pts), {"textAlign": "center", "padding": "2px 0"}),
            (item.get("date", ""), {"color": MUTED, "fontSize": "0.8rem", "textAlign": "right"}),
        ]))

    table = _data_table(["Index", "Region", "Level", "1D%", "1W%", "1M%", "30d", "Date"], rows) if rows else html.P("No equities data available", style={"color": MUTED})

    return html.Div([
        html.H5("Equities", className=_SECTION_TITLE),
        html.Div(table, style={"overflowX": "auto"}),
    ], className=_CARD_STYLE)


def build_commodities_panel(data: dict, sparklines: dict | None = None) -> html.Div:
    """Energy and metals commodities."""
    items = data.get("commodities") or []
    sparklines = sparklines or {}

    rows = []
    for item in items:
        price = item.get("price")
        chg_pct = item.get("change_pct")
        ticker = item.get("ticker", "")
        pts = sparklines.get(ticker, [])
        w1, m1 = _period_changes(pts)
        rows.append(_table_row([
            (_tooltip_name(item.get("name", ticker), ticker=ticker), {"fontWeight": "500"}),
            (item.get("group", ""), {"color": MUTED, "textAlign": "center"}),
            (f"${_format_price(price, 2)}", {"color": TEXT_PRIMARY, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (_format_change(chg_pct, "%"), {"color": _change_color(chg_pct), "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (_format_change(w1, "%"), {**_CHG_COL, "color": _change_color(w1)}),
            (_format_change(m1, "%"), {**_CHG_COL, "color": _change_color(m1)}),
            (_build_sparkline(pts), {"textAlign": "center", "padding": "2px 0"}),
            (item.get("date", ""), {"color": MUTED, "fontSize": "0.8rem", "textAlign": "right"}),
        ]))

    table = _data_table(["Commodity", "Group", "Price", "1D%", "1W%", "1M%", "30d", "Date"], rows) if rows else html.P("No commodities data available", style={"color": MUTED})

    return html.Div([
        html.H5("Commodities", className=_SECTION_TITLE),
        html.Div(table, style={"overflowX": "auto"}),
    ], className=_CARD_STYLE)


def build_macro_panel(data: dict) -> html.Div:
    """Latest FRED macro indicators or yfinance fallback."""
    indicators = data.get("indicators") or []
    note = data.get("note")

    if not indicators and note:
        return html.Div([
            html.H5("Macro Pulse", className=_SECTION_TITLE),
            html.P(note, style={"color": YELLOW, "fontSize": "0.85rem"}),
        ], className=_CARD_STYLE)

    rows = []
    for item in indicators:
        val = item.get("value")
        chg = item.get("change")
        unit = item.get("unit", "")
        rows.append(_table_row([
            (_tooltip_name(item.get("name", item.get("series", ""))), {}),
            (f"{_format_price(val, 2)} {unit}", {"color": BLUE, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (_format_change(chg), {"color": _change_color(chg), "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (item.get("freq", ""), {"color": MUTED, "textAlign": "center", "fontSize": "0.8rem"}),
            (item.get("date", ""), {"color": MUTED, "fontSize": "0.8rem", "textAlign": "right"}),
        ]))

    table = _data_table(["Indicator", "Value", "Change", "Freq", "As Of"], rows) if rows else html.P("No macro data available", style={"color": MUTED})

    banner = []
    if note:
        banner = [html.P(note, style={"color": YELLOW, "fontSize": "0.8rem", "marginBottom": "0.75rem"})]

    return html.Div([
        html.H5("Macro Pulse", className=_SECTION_TITLE),
        *banner,
        html.Div(table, style={"overflowX": "auto"}),
    ], className=_CARD_STYLE)


def build_what_changed_panel(data: dict) -> html.Div:
    """Cross-asset movers ranked by z-score."""
    movers = data.get("movers") or []
    threshold = data.get("threshold", 1.5)

    if not movers:
        return html.Div([
            html.H5("What Changed", className=_SECTION_TITLE),
            html.Div([
                html.P(
                    f"No cross-asset moves exceeding {threshold:.1f} sigma today.",
                    style={"color": MUTED, "textAlign": "center", "padding": "1.5rem 0"},
                ),
                html.P(
                    "This panel highlights instruments whose daily return exceeds the threshold vs their 20-day realized volatility.",
                    style={"color": MUTED, "fontSize": "0.8rem", "textAlign": "center"},
                ),
            ]),
        ], className=_CARD_STYLE)

    rows = []
    for item in movers:
        z = item.get("z_score", 0)
        direction = item.get("direction", "")
        arrow = "\u25B2" if direction == "up" else "\u25BC"
        arrow_color = GREEN if direction == "up" else RED
        ret_pct = item.get("return_pct")

        z_abs = abs(z) if z else 0
        if z_abs >= 3:
            z_color = RED if direction == "down" else GREEN
            z_style = {"fontWeight": "700"}
        elif z_abs >= 2:
            z_color = RED if direction == "down" else GREEN
            z_style = {"fontWeight": "600"}
        else:
            z_color = _change_color(z)
            z_style = {}

        rows.append(_table_row([
            (f"{arrow}", {"color": arrow_color, "fontSize": "0.9rem", "textAlign": "center"}),
            (item.get("name", item.get("ticker", "")), {"color": TEXT_PRIMARY, "fontWeight": "500"}),
            (item.get("asset_class", ""), {"color": PURPLE, "fontSize": "0.8rem", "textAlign": "center"}),
            (_format_price(item.get("price"), 2), {"color": TEXT_PRIMARY, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (_format_change(ret_pct, "%"), {"color": _change_color(ret_pct), "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (f"{z:.2f}\u03C3" if z is not None else "—", {"color": z_color, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right", **z_style}),
        ]))

    table = _data_table(["", "Instrument", "Class", "Price", "Return", "Z-Score"], rows)

    return html.Div([
        html.H5("What Changed", className=_SECTION_TITLE),
        html.P(
            f"Instruments with |z-score| > {threshold:.1f}\u03C3 vs 20-day realized vol, ranked by magnitude",
            style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "0.75rem"},
        ),
        html.Div(table, style={"overflowX": "auto"}),
    ], className=_CARD_STYLE)


# ---------------------------------------------------------------------------
# Curves chart panel
# ---------------------------------------------------------------------------

_CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_PRIMARY, family="Inter, sans-serif"),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        font=dict(color=TEXT_PRIMARY, size=11),
    ),
    xaxis=dict(gridcolor="rgba(48,54,61,0.5)", tickfont=dict(color=MUTED)),
    yaxis=dict(gridcolor="rgba(48,54,61,0.5)", tickfont=dict(color=MUTED)),
    margin=dict(t=35, b=40, l=55, r=20),
    hovermode="x unified",
)


def build_curves_panel(curves: dict) -> html.Div:
    """Yield curve, swap curve, swap spread, and forward rates charts."""
    if not curves:
        return html.Div()

    yc = curves.get("yield_curve", {})
    sc = curves.get("swap_curve", {})
    ss = curves.get("swap_spreads", {})
    fwd = curves.get("forward_rates", {})

    charts = []

    # --- Yield curve + Swap curve overlay ---
    if yc.get("tenors"):
        fig_yc = go.Figure()
        fig_yc.add_trace(go.Scatter(
            x=yc["tenors"], y=yc["yields"],
            mode="lines+markers", name="Treasury Yield Curve",
            line=dict(color=BLUE, width=2.5),
            marker=dict(size=6),
            hovertemplate="%{x}: %{y:.3f}%<extra>Treasury</extra>",
        ))
        if sc.get("tenors"):
            fig_yc.add_trace(go.Scatter(
                x=sc["tenors"], y=sc["rates"],
                mode="lines+markers", name="USD Swap Curve",
                line=dict(color=PURPLE, width=2.5, dash="dash"),
                marker=dict(size=6, symbol="diamond"),
                hovertemplate="%{x}: %{y:.3f}%<extra>Swap</extra>",
            ))
        fig_yc.update_layout(
            **_CHART_LAYOUT,
            height=310,
            yaxis_title="Rate (%)",
            yaxis_ticksuffix="%",
        )
        date_label = yc.get("date", "")
        charts.append(html.Div([
            html.Div([
                html.Span("Yield & Swap Curves", style={"fontWeight": "600", "fontSize": "0.95rem"}),
                html.Span(f"  as of {date_label}" if date_label else "", style={"color": MUTED, "fontSize": "0.8rem", "marginLeft": "0.75rem"}),
            ], style={"marginBottom": "0.5rem"}),
            dcc.Graph(figure=fig_yc, config={"displayModeBar": False}),
        ]))

    # --- Swap spread bar chart ---
    if ss.get("tenors"):
        colors = [GREEN if v >= 0 else RED for v in ss["spreads_bp"]]
        fig_ss = go.Figure()
        fig_ss.add_trace(go.Bar(
            x=ss["tenors"], y=ss["spreads_bp"],
            marker_color=colors, name="Swap Spread",
            hovertemplate="%{x}: %{y:.1f} bp<extra></extra>",
        ))
        fig_ss.add_hline(y=0, line_dash="dot", line_color=MUTED, line_width=1)
        fig_ss.update_layout(
            **_CHART_LAYOUT,
            height=260,
            yaxis_title="Spread (bp)",
            showlegend=False,
        )
        charts.append(html.Div([
            html.Div([
                html.Span("Swap Spreads", style={"fontWeight": "600", "fontSize": "0.95rem"}),
                html.Span(" (Swap Rate − Treasury Yield)", style={"color": MUTED, "fontSize": "0.8rem"}),
            ], style={"marginBottom": "0.5rem"}),
            dcc.Graph(figure=fig_ss, config={"displayModeBar": False}),
        ]))

    # --- Forward rates ---
    if fwd.get("labels"):
        fig_fwd = go.Figure()
        fig_fwd.add_trace(go.Scatter(
            x=fwd["labels"], y=fwd["rates"],
            mode="lines+markers", name="Implied Forward Rate",
            line=dict(color=YELLOW, width=2.5),
            marker=dict(size=6),
            hovertemplate="%{x}: %{y:.3f}%<extra></extra>",
        ))
        fig_fwd.update_layout(
            **_CHART_LAYOUT,
            height=260,
            yaxis_title="Rate (%)",
            yaxis_ticksuffix="%",
            showlegend=False,
        )
        charts.append(html.Div([
            html.Div("Implied Forward Rates", style={"fontWeight": "600", "fontSize": "0.95rem", "marginBottom": "0.5rem"}),
            dcc.Graph(figure=fig_fwd, config={"displayModeBar": False}),
        ]))

    if not charts:
        return html.Div()

    return html.Div([
        html.H5("Rate Curves", className=_SECTION_TITLE),
        html.Div(charts),
    ], className=_CARD_STYLE)


# ---------------------------------------------------------------------------
# Fed Balance Sheet / QE-QT Monitor
# ---------------------------------------------------------------------------

_FED_SERIES_COLORS = {
    "WALCL": BLUE,
    "RRPONTSYD": YELLOW,
    "WRESBAL": GREEN,
    "WTREGEN": PURPLE,
    "TREAST": "#79c0ff",
    "WSHOMCB": "#f0883e",
}


def build_fed_liquidity_panel(data: dict) -> html.Div:
    """Fed balance sheet snapshot table + 2-year historical chart with Net Liquidity."""
    if not data:
        return html.Div()

    snapshot = data.get("snapshot") or []
    history = data.get("history") or {}
    net_liq = data.get("net_liquidity") or []

    # --- Snapshot table ---
    rows = []
    for item in snapshot:
        val = item.get("value")
        chg = item.get("change")
        rows.append(_table_row([
            (_tooltip_name(item.get("name", item.get("series", ""))), {}),
            (f"{_format_price(val, 3)} T$" if val is not None else "—", {"color": BLUE, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (_format_change(chg, " T$") if chg is not None else "—", {"color": _change_color(chg), "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
            (item.get("freq", ""), {"color": MUTED, "textAlign": "center", "fontSize": "0.8rem"}),
            (item.get("date", ""), {"color": MUTED, "fontSize": "0.8rem", "textAlign": "right"}),
        ]))

    table = _data_table(["Component", "Level (T$)", "Change", "Freq", "As Of"], rows) if rows else html.P("No data", style={"color": MUTED})

    # --- Historical chart ---
    charts = []

    # Main components chart
    fig_main = go.Figure()
    primary_series = ["WALCL", "RRPONTSYD", "WRESBAL", "WTREGEN"]
    names_map = {
        "WALCL": "Fed Total Assets",
        "RRPONTSYD": "ON RRP",
        "WRESBAL": "Reserves",
        "WTREGEN": "TGA",
    }
    for sid in primary_series:
        pts = history.get(sid, [])
        if not pts:
            continue
        dates = [p["date"] for p in pts]
        vals = [p["value"] for p in pts]
        fig_main.add_trace(go.Scatter(
            x=dates, y=vals,
            mode="lines", name=names_map.get(sid, sid),
            line=dict(color=_FED_SERIES_COLORS.get(sid, MUTED), width=2),
            hovertemplate=f"<b>{names_map.get(sid, sid)}</b><br>%{{x}}<br>%{{y:.3f}} T$<extra></extra>",
        ))

    if net_liq:
        dates = [p["date"] for p in net_liq]
        vals = [p["value"] for p in net_liq]
        fig_main.add_trace(go.Scatter(
            x=dates, y=vals,
            mode="lines", name="Net Liquidity",
            line=dict(color=RED, width=2.5, dash="dot"),
            hovertemplate="<b>Net Liquidity</b><br>%{x}<br>%{y:.3f} T$<extra></extra>",
        ))

    if fig_main.data:
        fig_main.update_layout(
            **_CHART_LAYOUT,
            height=370,
            yaxis_title="Trillions USD",
            yaxis_tickprefix="$",
            yaxis_ticksuffix="T",
        )
        charts.append(html.Div([
            html.Div([
                html.Span("Fed Balance Sheet Components", style={"fontWeight": "600", "fontSize": "0.95rem"}),
                html.Span(" (2-year history)", style={"color": MUTED, "fontSize": "0.8rem"}),
            ], style={"marginBottom": "0.5rem"}),
            dcc.Graph(figure=fig_main, config={"displayModeBar": False}),
        ]))

    # SOMA holdings breakdown (Treasuries + MBS)
    fig_soma = go.Figure()
    soma_map = {"TREAST": "Treasuries", "WSHOMCB": "MBS"}
    for sid, label in soma_map.items():
        pts = history.get(sid, [])
        if not pts:
            continue
        dates = [p["date"] for p in pts]
        vals = [p["value"] for p in pts]
        fig_soma.add_trace(go.Scatter(
            x=dates, y=vals,
            mode="lines", name=label,
            line=dict(color=_FED_SERIES_COLORS.get(sid, MUTED), width=2),
            stackgroup="soma",
            hovertemplate=f"<b>{label}</b><br>%{{x}}<br>%{{y:.3f}} T$<extra></extra>",
        ))

    if fig_soma.data:
        fig_soma.update_layout(
            **_CHART_LAYOUT,
            height=280,
            yaxis_title="Trillions USD",
            yaxis_tickprefix="$",
            yaxis_ticksuffix="T",
        )
        charts.append(html.Div([
            html.Div([
                html.Span("SOMA Holdings", style={"fontWeight": "600", "fontSize": "0.95rem"}),
                html.Span(" (Treasuries + MBS)", style={"color": MUTED, "fontSize": "0.8rem"}),
            ], style={"marginBottom": "0.5rem"}),
            dcc.Graph(figure=fig_soma, config={"displayModeBar": False}),
        ]))

    return html.Div([
        html.H5("Fed QE / QT Monitor", className=_SECTION_TITLE),
        html.P(
            "Net Liquidity = Fed Assets − TGA − RRP  |  Hover instrument names for definitions",
            style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "0.75rem"},
        ),
        html.Div(table, style={"overflowX": "auto", "marginBottom": "1.5rem"}),
        html.Div(charts),
    ], className=_CARD_STYLE)


# ---------------------------------------------------------------------------
# Central Bank Meeting Tracker
# ---------------------------------------------------------------------------

def build_cb_meeting_panel(data: dict) -> html.Div:
    """FOMC meeting countdown with policy rates and implied path proxy."""
    if not data:
        return html.Div()

    fed = data.get("fed") or {}
    upcoming = data.get("upcoming") or []

    if not fed and not upcoming:
        return html.Div()

    # Countdown row
    countdown_parts = []
    next_date = fed.get("next_meeting_date")
    days = fed.get("days_until")
    if next_date is not None and days is not None:
        label = fed.get("label", next_date)
        if days == 0:
            countdown_parts.append(html.Span("Today", style={"color": YELLOW, "fontWeight": "600"}))
        elif days == 1:
            countdown_parts.append(html.Span("Tomorrow", style={"color": YELLOW, "fontWeight": "600"}))
        elif days < 0:
            countdown_parts.append(html.Span("Past", style={"color": MUTED}))
        else:
            countdown_parts.append(html.Span(f"{days} days", style={"color": BLUE, "fontWeight": "600"}))
        countdown_parts.append(html.Span(f" until {label}", style={"color": TEXT_PRIMARY}))
    elif upcoming:
        # Fallback: use first upcoming
        first = upcoming[0]
        d = first.get("days_until", 0)
        lbl = first.get("label", first.get("date", ""))
        countdown_parts.append(html.Span(f"{d} days", style={"color": BLUE, "fontWeight": "600"}))
        countdown_parts.append(html.Span(f" until {lbl}", style={"color": TEXT_PRIMARY}))

    # Policy rates table
    rate_rows = []
    target = fed.get("target_upper")
    sofr = fed.get("sofr")
    effr = fed.get("effr")
    two_y = fed.get("two_year_yield")
    spread = fed.get("two_y_minus_target")

    if target is not None:
        rate_rows.append(_table_row([
            (_tooltip_name("Fed Funds Target (Upper)"), {}),
            (f"{target:.2f}%", {"color": BLUE, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
        ]))
    if sofr is not None:
        rate_rows.append(_table_row([
            (_tooltip_name("SOFR"), {}),
            (f"{sofr:.2f}%", {"color": TEXT_PRIMARY, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
        ]))
    if effr is not None:
        rate_rows.append(_table_row([
            (html.Span("EFFR", title="Effective Fed Funds Rate — actual trading rate"), {}),
            (f"{effr:.2f}%", {"color": TEXT_PRIMARY, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
        ]))
    if two_y is not None:
        rate_rows.append(_table_row([
            (html.Span("2Y Treasury", title="Proxy for market-implied path over 2Y"), {}),
            (f"{two_y:.2f}%", {"color": TEXT_PRIMARY, "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
        ]))
    if spread is not None:
        rate_rows.append(_table_row([
            (_tooltip_name("2Y-FF Spread"), {}),
            (f"{spread:+.2f}%", {"color": _change_color(spread), "fontFamily": "'JetBrains Mono', monospace", "textAlign": "right"}),
        ]))

    rate_table = _data_table(["Rate", "Level"], rate_rows) if rate_rows else html.Div()

    # Upcoming meetings list
    meeting_list = []
    for m in upcoming[:4]:
        d = m.get("days_until", 0)
        lbl = m.get("label", m.get("date", ""))
        sep = " (SEP)" if m.get("has_sep") else ""
        meeting_list.append(html.Div([
            html.Span(f"{d}d", style={"color": MUTED, "fontSize": "0.75rem", "minWidth": "28px", "display": "inline-block"}),
            html.Span(lbl, style={"color": TEXT_PRIMARY, "fontSize": "0.85rem"}),
        ], style={"display": "flex", "gap": "0.5rem", "marginBottom": "0.25rem"}))

    return html.Div([
        html.H5("Central Bank Meeting Tracker", className=_SECTION_TITLE),
        html.P(
            "FOMC countdown | Policy rates | 2Y-FF spread as proxy for implied path. Meeting-specific probabilities require CME Fed Funds futures.",
            style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "0.75rem"},
        ),
        html.Div([
            html.Div([
                html.Div([
                    html.Span("Next FOMC: ", style={"color": MUTED, "fontSize": "0.9rem"}),
                    *countdown_parts,
                ], style={"marginBottom": "1rem"}),
                html.Div(rate_table, style={"overflowX": "auto"}),
            ], style={"flex": 1, "minWidth": "200px"}),
            html.Div([
                html.Span("Upcoming", style={"color": MUTED, "fontSize": "0.75rem", "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "0.5rem", "display": "block"}),
                html.Div(meeting_list),
            ], style={"flex": 0, "minWidth": "140px"}),
        ], style={"display": "flex", "gap": "2rem", "flexWrap": "wrap", "alignItems": "flex-start"}),
    ], className=_CARD_STYLE)


# ---------------------------------------------------------------------------
# Full Markets layout builder
# ---------------------------------------------------------------------------

def build_markets_layout(overview: dict) -> html.Div:
    """Assemble the full Markets tab layout from an overview API response."""
    rates_data = overview.get("rates") or {}
    fx_data = overview.get("fx") or {}
    equities_data = overview.get("equities") or {}
    commodities_data = overview.get("commodities") or {}
    macro_data = overview.get("macro") or {}
    what_changed_data = overview.get("what_changed") or {}
    curves_data = overview.get("curves") or {}
    fed_liq_data = overview.get("fed_liquidity") or {}
    cb_meetings_data = overview.get("cb_meetings") or {}
    sparklines = overview.get("sparklines") or {}

    timestamp = overview.get("timestamp", "")

    return html.Div([
        html.Div([
            html.Span("Market data as of ", style={"color": MUTED, "fontSize": "0.8rem"}),
            html.Span(timestamp[:19].replace("T", " ") if timestamp else "—", style={"color": BLUE, "fontSize": "0.8rem"}),
        ], style={"marginBottom": "1rem", "textAlign": "right"}),

        # Row 1: What Changed (full width)
        dbc.Row([
            dbc.Col(build_what_changed_panel(what_changed_data), xs=12),
        ], className="mb-3"),

        # Row 2: Rates + FX
        dbc.Row([
            dbc.Col(build_rates_panel(rates_data, sparklines), xs=12, lg=6),
            dbc.Col(build_fx_panel(fx_data, sparklines), xs=12, lg=6),
        ], className="mb-3"),

        # Row 3: Equities + Commodities
        dbc.Row([
            dbc.Col(build_equities_panel(equities_data, sparklines), xs=12, lg=6),
            dbc.Col(build_commodities_panel(commodities_data, sparklines), xs=12, lg=6),
        ], className="mb-3"),

        # Expandable historical chart container
        dbc.Row([
            dbc.Col(
                dcc.Loading(
                    html.Div(id="historical-chart-container"),
                    type="dot",
                    color=BLUE,
                ),
                xs=12,
            ),
        ], className="mb-3"),

        # Row 4: Curves (full width)
        dbc.Row([
            dbc.Col(build_curves_panel(curves_data), xs=12),
        ], className="mb-3") if curves_data else html.Div(),

        # Row 5: Fed QE/QT Monitor (full width)
        dbc.Row([
            dbc.Col(build_fed_liquidity_panel(fed_liq_data), xs=12),
        ], className="mb-3") if fed_liq_data else html.Div(),

        # Row 5b: Central Bank Meeting Tracker (full width)
        dbc.Row([
            dbc.Col(build_cb_meeting_panel(cb_meetings_data), xs=12),
        ], className="mb-3") if cb_meetings_data else html.Div(),

        # Row 6: Macro Pulse (full width)
        dbc.Row([
            dbc.Col(build_macro_panel(macro_data), xs=12),
        ]),

        dcc.Store(id="selected-instrument-store"),
    ])
