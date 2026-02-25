"""Strategy Monitor panel: active strategies, target weights vs positions, paper PnL, order log."""

from dash import html
import dash_bootstrap_components as dbc

GREEN = "#3fb950"
RED = "#f85149"
BLUE = "#58a6ff"
MUTED = "#8b949e"
TEXT_PRIMARY = "#c9d1d9"
BORDER = "#30363d"
BG_CARD = "#21262d"


def build_strategy_monitor_layout(data: dict) -> html.Div:
    """Build the Strategy Monitor layout from API data."""
    if not data:
        return html.Div([
            html.Div("📊", style={"fontSize": "3rem", "marginBottom": "1rem", "opacity": 0.5}),
            html.H4("No strategy data", style={"color": TEXT_PRIMARY}),
            html.P("Run the strategy runner to submit paper orders. Data will appear here.", style={"color": MUTED}),
        ], style={"textAlign": "center", "padding": "3rem", "color": MUTED})

    positions = data.get("positions") or []
    total_mv = data.get("total_market_value") or 0
    pnl_summary = data.get("pnl_summary") or {}
    orders = data.get("orders") or []
    fills = data.get("fills") or []

    # Positions table
    pos_rows = []
    for p in positions[:20]:
        qty = p.get("quantity", 0)
        mv = p.get("market_value", 0)
        px = p.get("market_price", 0)
        sym = p.get("symbol", "")
        weight_pct = (abs(mv) / total_mv * 100) if total_mv > 0 else 0
        pos_rows.append(html.Tr([
            html.Td(sym, style={"fontFamily": "JetBrains Mono", "fontWeight": 600}),
            html.Td(f"{qty:,.2f}", style={"fontFamily": "JetBrains Mono"}),
            html.Td(f"${px:,.2f}", style={"fontFamily": "JetBrains Mono"}),
            html.Td(f"${mv:,.2f}", style={"fontFamily": "JetBrains Mono"}),
            html.Td(f"{weight_pct:.1f}%", style={"fontFamily": "JetBrains Mono", "color": MUTED}),
        ]))

    positions_table = html.Div([
        html.Div("Current Positions", className="section-title", style={"marginBottom": "0.75rem"}),
        dbc.Table(
            [html.Thead(html.Tr([
                html.Th("Symbol"),
                html.Th("Qty"),
                html.Th("Price"),
                html.Th("Market Value"),
                html.Th("Weight"),
            ])), html.Tbody(pos_rows or [html.Tr(html.Td("No positions", colSpan=5, style={"color": MUTED}))])],
            bordered=False,
            dark=True,
            hover=True,
            size="sm",
        ),
    ], className="data-card", style={"marginBottom": "1.5rem"})

    # PnL summary
    daily_pnl = pnl_summary.get("daily") or []
    total_recent = pnl_summary.get("total_recent") or 0
    pnl_class = "positive" if total_recent >= 0 else "negative"
    pnl_cards = html.Div([
        html.Div([
            html.P("Recent PnL (7d)", className="metric-label"),
            html.P(f"${total_recent:,.2f}", className=f"metric-value {pnl_class}"),
        ], className="metric-card"),
        html.Div([
            html.P("Portfolio Value", className="metric-label"),
            html.P(f"${total_mv:,.2f}", className="metric-value neutral"),
        ], className="metric-card"),
    ], style={"display": "flex", "gap": "1rem", "marginBottom": "1.5rem", "flexWrap": "wrap"})

    # Order log
    order_rows = []
    for o in orders[:15]:
        status = o.get("status", "")
        status_color = GREEN if status == "filled" else (RED if status == "rejected" else MUTED)
        order_rows.append(html.Tr([
            html.Td(o.get("created_at", "")[:19] if o.get("created_at") else "-", style={"fontSize": "0.8rem"}),
            html.Td(o.get("symbol", ""), style={"fontFamily": "JetBrains Mono"}),
            html.Td(o.get("side", ""), style={"color": GREEN if o.get("side") == "BUY" else RED}),
            html.Td(f"{o.get('quantity', 0):,.2f}", style={"fontFamily": "JetBrains Mono"}),
            html.Td(status, style={"color": status_color}),
        ]))

    orders_section = html.Div([
        html.Div("Order Log", className="section-title", style={"marginBottom": "0.75rem"}),
        dbc.Table(
            [html.Thead(html.Tr([
                html.Th("Time"),
                html.Th("Symbol"),
                html.Th("Side"),
                html.Th("Qty"),
                html.Th("Status"),
            ])), html.Tbody(order_rows or [html.Tr(html.Td("No orders", colSpan=5, style={"color": MUTED}))])],
            bordered=False,
            dark=True,
            hover=True,
            size="sm",
        ),
    ], className="data-card", style={"marginBottom": "1.5rem"})

    # Fills
    fill_rows = []
    for f in fills[:15]:
        fill_rows.append(html.Tr([
            html.Td(f.get("created_at", "")[:19] if f.get("created_at") else "-", style={"fontSize": "0.8rem"}),
            html.Td(f.get("symbol", ""), style={"fontFamily": "JetBrains Mono"}),
            html.Td(f.get("side", ""), style={"color": GREEN if f.get("side") == "BUY" else RED}),
            html.Td(f"{f.get('quantity', 0):,.2f}", style={"fontFamily": "JetBrains Mono"}),
            html.Td(f"${f.get('fill_price', 0):,.2f}", style={"fontFamily": "JetBrains Mono"}),
        ]))

    fills_section = html.Div([
        html.Div("Recent Fills", className="section-title", style={"marginBottom": "0.75rem"}),
        dbc.Table(
            [html.Thead(html.Tr([
                html.Th("Time"),
                html.Th("Symbol"),
                html.Th("Side"),
                html.Th("Qty"),
                html.Th("Price"),
            ])), html.Tbody(fill_rows or [html.Tr(html.Td("No fills", colSpan=5, style={"color": MUTED}))])],
            bordered=False,
            dark=True,
            hover=True,
            size="sm",
        ),
    ], className="data-card")

    return html.Div([
        html.H4("Strategy Monitor", style={"color": TEXT_PRIMARY, "marginBottom": "1.5rem"}),
        html.P("Active paper strategies, current positions, PnL, and execution audit trail.", style={"color": MUTED, "marginBottom": "1.5rem"}),
        pnl_cards,
        dbc.Row([
            dbc.Col(positions_table, md=6),
            dbc.Col(orders_section, md=6),
        ]),
        dbc.Row([
            dbc.Col(fills_section, md=12),
        ]),
    ])
