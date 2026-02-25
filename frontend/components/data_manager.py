"""Data Manager tab — browse, pull, and preview stored market data.

Renders the Data tab in the main dashboard with three sections:
1. Data Catalog table
2. Pull Data form
3. Data Viewer / chart
"""

from datetime import datetime, timedelta

from dash import dcc, html
import dash_bootstrap_components as dbc

# Shared colour tokens (keep in sync with market_panels.py)
GREEN = "#3fb950"
RED = "#f85149"
BLUE = "#58a6ff"
MUTED = "#8b949e"
TEXT_PRIMARY = "#c9d1d9"
YELLOW = "#d29922"
PURPLE = "#a371f7"

_CARD_STYLE = "data-card"
_SECTION_TITLE = "section-title"

# Available asset classes for the pull form dropdowns
_YF_ASSET_OPTIONS = [
    {"label": "Equities", "value": "equities"},
    {"label": "FX", "value": "fx"},
    {"label": "Commodities", "value": "commodities"},
    {"label": "Rates (YF)", "value": "rates_yf"},
]

_FRED_CATEGORY_OPTIONS = [
    {"label": "Treasury Yields", "value": "treasury_yields"},
    {"label": "Macro Indicators", "value": "macro_indicators"},
    {"label": "Fed Liquidity", "value": "fed_liquidity"},
]


def _freshness_badge(last_updated: str | None):
    """Return a coloured badge indicating data freshness."""
    if not last_updated:
        return html.Span("No data", style={"color": MUTED, "fontSize": "0.75rem"})

    try:
        dt = datetime.fromisoformat(last_updated)
        age = datetime.utcnow() - dt
        if age < timedelta(hours=6):
            color, label = GREEN, "Fresh"
        elif age < timedelta(days=1):
            color, label = YELLOW, "Today"
        elif age < timedelta(days=7):
            color, label = YELLOW, f"{age.days}d ago"
        else:
            color, label = RED, f"{age.days}d ago"
    except Exception:
        color, label = MUTED, "?"

    return html.Span(
        label,
        style={
            "color": color,
            "fontSize": "0.75rem",
            "fontWeight": "600",
            "padding": "2px 8px",
            "borderRadius": "10px",
            "border": f"1px solid {color}44",
        },
    )


def _build_catalog_table(catalog: dict) -> html.Div:
    """Render a table showing every stored dataset."""
    if not catalog:
        return html.Div([
            html.P(
                "No data stored yet. Use the pull form below or click 'Update All' to populate the data lake.",
                style={"color": MUTED, "textAlign": "center", "padding": "2rem 0"},
            ),
        ])

    header = html.Thead(html.Tr([
        html.Th(h, style={"color": MUTED, "fontWeight": "500", "fontSize": "0.75rem", "textTransform": "uppercase", "letterSpacing": "0.5px"})
        for h in ["Dataset", "Source", "Tickers", "Date Range", "Rows", "Size", "Freshness"]
    ]))

    rows = []
    for key, entry in sorted(catalog.items()):
        tickers = entry.get("tickers", [])
        ticker_display = ", ".join(tickers[:5])
        if len(tickers) > 5:
            ticker_display += f" +{len(tickers) - 5} more"

        start = entry.get("start_date", "—")
        end_val = entry.get("end_date", "—")
        date_range = f"{start} → {end_val}" if start != "—" else "—"

        rows.append(html.Tr([
            html.Td(key, style={"color": BLUE, "fontWeight": "600"}),
            html.Td(entry.get("source", "—"), style={"color": PURPLE, "fontSize": "0.85rem"}),
            html.Td(
                ticker_display,
                style={"color": TEXT_PRIMARY, "fontSize": "0.8rem", "maxWidth": "250px", "overflow": "hidden", "textOverflow": "ellipsis"},
                title=", ".join(tickers),
            ),
            html.Td(date_range, style={"fontFamily": "'JetBrains Mono', monospace", "fontSize": "0.8rem", "color": TEXT_PRIMARY}),
            html.Td(f"{entry.get('row_count', 0):,}", style={"fontFamily": "'JetBrains Mono', monospace", "textAlign": "right", "color": TEXT_PRIMARY}),
            html.Td(f"{entry.get('file_size_mb', 0):.1f} MB", style={"fontFamily": "'JetBrains Mono', monospace", "textAlign": "right", "color": MUTED}),
            html.Td(_freshness_badge(entry.get("last_updated")), style={"textAlign": "center"}),
        ]))

    return html.Div(
        dbc.Table(
            [header, html.Tbody(rows)],
            bordered=False, dark=True, hover=True, size="sm",
        ),
        style={"overflowX": "auto"},
    )


def _build_pull_form() -> html.Div:
    """Render the data pull form."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    two_years_ago = (datetime.utcnow() - timedelta(days=730)).strftime("%Y-%m-%d")

    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("Source", style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "4px"}),
                dcc.Dropdown(
                    id="data-source-select",
                    options=[
                        {"label": "Yahoo Finance", "value": "yfinance"},
                        {"label": "FRED", "value": "fred"},
                    ],
                    value="yfinance",
                    clearable=False,
                    style={"backgroundColor": "#21262d", "color": TEXT_PRIMARY},
                ),
            ], xs=12, md=2),
            dbc.Col([
                html.Label("Asset Class / Category", style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "4px"}),
                dcc.Dropdown(
                    id="data-asset-select",
                    options=_YF_ASSET_OPTIONS + _FRED_CATEGORY_OPTIONS,
                    value="equities",
                    clearable=False,
                    style={"backgroundColor": "#21262d", "color": TEXT_PRIMARY},
                ),
            ], xs=12, md=2),
            dbc.Col([
                html.Label("Tickers (comma-separated)", style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "4px"}),
                dbc.Input(
                    id="data-tickers-input",
                    placeholder="e.g. ^GSPC, ^NDX, AAPL",
                    value="",
                    style={"backgroundColor": "#21262d", "color": TEXT_PRIMARY, "border": "1px solid #30363d"},
                ),
            ], xs=12, md=3),
            dbc.Col([
                html.Label("Start Date", style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "4px"}),
                dcc.DatePickerSingle(
                    id="data-start-date",
                    date=two_years_ago,
                    display_format="YYYY-MM-DD",
                    style={"backgroundColor": "#21262d"},
                ),
            ], xs=6, md=2),
            dbc.Col([
                html.Label("End Date", style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "4px"}),
                dcc.DatePickerSingle(
                    id="data-end-date",
                    date=today,
                    display_format="YYYY-MM-DD",
                    style={"backgroundColor": "#21262d"},
                ),
            ], xs=6, md=2),
            dbc.Col([
                html.Label("\u00A0", style={"display": "block", "fontSize": "0.8rem", "marginBottom": "4px"}),
                dbc.Button("Pull Data", id="data-pull-btn", color="primary", size="sm", className="w-100"),
            ], xs=12, md=1),
        ], className="g-2 align-items-end"),
        html.Div(id="data-pull-status", style={"marginTop": "0.5rem"}),
    ])


def _build_preview_form() -> html.Div:
    """Render the data preview / query section."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("Dataset", style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "4px"}),
                dcc.Dropdown(
                    id="data-preview-asset",
                    options=_YF_ASSET_OPTIONS + _FRED_CATEGORY_OPTIONS,
                    value="equities",
                    clearable=False,
                    style={"backgroundColor": "#21262d", "color": TEXT_PRIMARY},
                ),
            ], xs=12, md=3),
            dbc.Col([
                html.Label("Tickers (optional)", style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "4px"}),
                dbc.Input(
                    id="data-preview-tickers",
                    placeholder="e.g. ^GSPC, ^NDX",
                    value="",
                    style={"backgroundColor": "#21262d", "color": TEXT_PRIMARY, "border": "1px solid #30363d"},
                ),
            ], xs=12, md=3),
            dbc.Col([
                html.Label("Start", style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "4px"}),
                dcc.DatePickerSingle(id="data-preview-start", date=None, display_format="YYYY-MM-DD"),
            ], xs=6, md=2),
            dbc.Col([
                html.Label("End", style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "4px"}),
                dcc.DatePickerSingle(id="data-preview-end", date=None, display_format="YYYY-MM-DD"),
            ], xs=6, md=2),
            dbc.Col([
                html.Label("\u00A0", style={"display": "block", "fontSize": "0.8rem", "marginBottom": "4px"}),
                dbc.Button("Preview", id="data-preview-btn", color="info", size="sm", outline=True, className="w-100"),
            ], xs=12, md=2),
        ], className="g-2 align-items-end"),
        dcc.Loading(
            html.Div(id="data-preview-container", style={"marginTop": "1rem"}),
            type="dot",
            color=BLUE,
        ),
    ])


# ---------------------------------------------------------------------------
# Main layout builder
# ---------------------------------------------------------------------------

def build_data_manager_layout(catalog: dict) -> html.Div:
    """Assemble the full Data Manager tab."""
    return html.Div([
        # Header
        html.Div([
            html.H4("Data Manager", style={"color": TEXT_PRIMARY, "marginBottom": "0.25rem"}),
            html.P(
                "Browse stored market data, trigger new pulls, and preview time series.",
                style={"color": MUTED, "fontSize": "0.85rem", "marginBottom": "0"},
            ),
        ], style={"marginBottom": "1.5rem"}),

        # Section 1: Catalog
        html.Div([
            html.Div([
                html.H5("Data Catalog", className=_SECTION_TITLE, style={"display": "inline-block"}),
                dbc.Button(
                    "Update All",
                    id="data-update-all-btn",
                    color="success",
                    size="sm",
                    outline=True,
                    style={"float": "right"},
                ),
            ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),
            html.Div(id="data-update-all-status", style={"marginBottom": "0.5rem"}),
            _build_catalog_table(catalog),
        ], className=_CARD_STYLE, style={"marginBottom": "1.5rem"}),

        # Section 2: Pull Data
        html.Div([
            html.H5("Pull Data", className=_SECTION_TITLE),
            html.P(
                "Download historical data from yfinance or FRED and store in the Parquet data lake.",
                style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "0.75rem"},
            ),
            _build_pull_form(),
        ], className=_CARD_STYLE, style={"marginBottom": "1.5rem"}),

        # Section 3: Data Viewer
        html.Div([
            html.H5("Data Viewer", className=_SECTION_TITLE),
            html.P(
                "Query and visualise stored time series.",
                style={"color": MUTED, "fontSize": "0.8rem", "marginBottom": "0.75rem"},
            ),
            _build_preview_form(),
        ], className=_CARD_STYLE),
    ])
