"""IBKR Analytics Dashboard - Modern Frontend."""
import dash
from dash import dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import requests
import logging
import os
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

# Initialize Dash app with a modern dark theme
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,  # Dark theme
        "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "mobile-web-app-capable", "content": "yes"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
    ],
)

app.title = "IBKR Portfolio Analytics"

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Custom CSS for modern styling
CUSTOM_STYLES = """
<style>
    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --bg-card: #21262d;
        --text-primary: #c9d1d9;
        --text-secondary: #8b949e;
        --accent-green: #3fb950;
        --accent-red: #f85149;
        --accent-blue: #58a6ff;
        --accent-purple: #a371f7;
        --accent-yellow: #d29922;
        --border-color: #30363d;
    }
    
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        color: var(--text-primary);
        min-height: 100vh;
    }
    
    .dashboard-header {
        background: linear-gradient(90deg, #21262d 0%, #0d1117 100%);
        border-bottom: 1px solid var(--border-color);
        padding: 1.5rem 0;
        margin-bottom: 2rem;
    }
    
    .dashboard-title {
        font-weight: 700;
        font-size: 1.75rem;
        background: linear-gradient(90deg, #58a6ff, #a371f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.25rem;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        border-color: var(--accent-blue);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(88, 166, 255, 0.15);
    }
    
    .metric-label {
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }
    
    .metric-value.positive { color: var(--accent-green); }
    .metric-value.negative { color: var(--accent-red); }
    .metric-value.neutral { color: var(--accent-blue); }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-title::before {
        content: '';
        width: 4px;
        height: 20px;
        background: linear-gradient(180deg, #58a6ff, #a371f7);
        border-radius: 2px;
    }
    
    .data-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .position-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .position-row:last-child {
        border-bottom: none;
    }
    
    .position-symbol {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: var(--accent-blue);
    }
    
    .position-details {
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    .nav-tabs .nav-link {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .nav-tabs .nav-link:hover {
        color: var(--text-primary);
        background: rgba(88, 166, 255, 0.1);
        border-radius: 8px;
    }
    
    .nav-tabs .nav-link.active {
        color: var(--accent-blue);
        background: rgba(88, 166, 255, 0.15);
        border-radius: 8px;
    }
    
    .refresh-btn {
        background: linear-gradient(90deg, #238636, #2ea043);
        border: none;
        color: white;
        font-weight: 500;
        padding: 0.5rem 1.25rem;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .refresh-btn:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(46, 160, 67, 0.3);
    }
    
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }
    
    .status-indicator.connected { background: var(--accent-green); }
    .status-indicator.disconnected { background: var(--accent-red); }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: var(--text-secondary);
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .dashboard-title {
            font-size: 1.25rem;
        }
        
        .metric-value {
            font-size: 1.25rem;
        }
        
        .data-card {
            padding: 1rem;
        }
        
        .dashboard-header {
            padding: 1rem 0;
        }
    }
    
    /* Print styles */
    @media print {
        .refresh-btn, .nav-tabs {
            display: none;
        }
    }
</style>
"""

# Import WebSocket client
from frontend.websocket_client import create_websocket_client_component

# App layout
app.layout = html.Div([
    # Inject custom styles
    html.Div(
        dangerously_allow_html=True,
        children=CUSTOM_STYLES,
    ) if hasattr(html.Div, 'dangerously_allow_html') else dcc.Markdown(CUSTOM_STYLES, dangerously_allow_html=True),
    
    # WebSocket client for real-time updates
    create_websocket_client_component(API_BASE_URL),
    
    # Stores for data
    dcc.Store(id='portfolio-data-store', data=None),
    dcc.Store(id='last-update-store', data=None),
    dcc.Store(id='flex-data-store', data=None),  # Separate store for Flex Query data
    dcc.Store(id='performance-date-range-store', data={'start_date': None, 'end_date': None}),  # Store for performance date range (None = all data)
    dcc.Store(id='realtime-updates-store', data=None),  # Store for real-time WebSocket updates
    
    # Toast notification for Flex Query
    dbc.Toast(
        id="flex-toast",
        header="Flex Query",
        is_open=False,
        dismissable=True,
        duration=5000,
        icon="info",
        style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 1050},
    ),
    
    # Auto-refresh interval
    dcc.Interval(
        id='auto-refresh-interval',
        interval=5*60*1000,  # 5 minutes
        n_intervals=0
    ),
    
    # Header
    html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("IBKR Portfolio Analytics", className="dashboard-title"),
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.Span(id='connection-status', children=[
                            html.Span(className="status-indicator connected", id='status-indicator'),
                            html.Span("Connected", id='connection-status-text', style={'fontSize': '0.85rem', 'color': '#8b949e'})
                        ]),
                        html.Span(id='last-update-text', style={
                            'fontSize': '0.75rem', 
                            'color': '#8b949e', 
                            'marginLeft': '1.5rem'
                        }),
                        dbc.Button(
                            [html.I(className="fas fa-sync-alt me-2"), "Refresh"],
                            id="refresh-btn",
                            className="refresh-btn ms-3",
                            size="sm",
                        ),
                        html.Span(
                            "(Auto-refresh every 5 min)",
                            style={
                                'fontSize': '0.7rem',
                                'color': '#8b949e',
                                'marginLeft': '0.5rem',
                                'fontStyle': 'italic'
                            }
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-download me-2"), "Fetch Flex Query"],
                            id="fetch-flex-btn",
                            className="ms-2",
                            size="sm",
                            color="info",
                            outline=True,
                        ),
                    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'flex-end'})
                ], width=6),
            ], align="center"),
        ], fluid=True),
    ], className="dashboard-header"),
    
    # Main content
    dbc.Container([
        # Summary metrics row
        dbc.Row(id='summary-metrics-row', className="mb-4"),
        
        # Main content tabs
        dbc.Tabs(
            id="main-tabs",
            active_tab="portfolio",
            children=[
                dbc.Tab(label="📊 Portfolio", tab_id="portfolio"),
                dbc.Tab(label="📈 Performance", tab_id="performance"),
                dbc.Tab(label="💹 Positions", tab_id="positions"),
                dbc.Tab(label="📋 History", tab_id="history"),
            ],
            className="mb-4",
        ),
        
        # Tab content
        html.Div(id="tab-content"),
        
        # Loading overlay
        dcc.Loading(
            id="loading",
            type="circle",
            color="#58a6ff",
            children=html.Div(id="loading-output"),
        ),
        
    ], fluid=True, style={'paddingBottom': '3rem'}),
])


def create_metric_card(label, value, value_class="neutral", prefix="", suffix=""):
    """Create a styled metric card."""
    return html.Div([
        html.P(label, className="metric-label"),
        html.P(f"{prefix}{value}{suffix}", className=f"metric-value {value_class}"),
    ], className="metric-card")


def fetch_flex_data():
    """Fetch ALL configured Flex Query reports from IBKR (on-demand only)."""
    try:
        # Call the endpoint that fetches all configured reports
        response = requests.post(f"{API_BASE_URL}/flex-query/fetch-all-reports", timeout=180)
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Flex Query API returned {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error fetching Flex data: {e}")
        return None


def fetch_db_data():
    """Fetch data from database APIs as fallback."""
    data = {}
    try:
        # Account summary
        resp = requests.get(f"{API_BASE_URL}/account/summary", timeout=10)
        if resp.status_code == 200:
            data['account'] = resp.json()
        
        # Positions
        resp = requests.get(f"{API_BASE_URL}/positions", timeout=10)
        if resp.status_code == 200:
            data['positions'] = resp.json()
        
        # PnL history (get more data for analytics)
        resp = requests.get(f"{API_BASE_URL}/pnl?limit=365", timeout=10)
        if resp.status_code == 200:
            data['pnl_history'] = resp.json()
        
        # Performance metrics (Sharpe, Sortino, max drawdown, etc.)
        resp = requests.get(f"{API_BASE_URL}/performance?limit=365", timeout=10)
        if resp.status_code == 200:
            data['performance'] = resp.json()
            
    except Exception as e:
        logger.error(f"Error fetching DB data: {e}")
    
    return data


def fetch_fresh_data_from_ibkr():
    """Fetch fresh data from IBKR TWS/Gateway for display (does NOT store PnL records)."""
    try:
        # Trigger a fresh fetch from IBKR (store_pnl=False means don't store PnL)
        resp = requests.post(f"{API_BASE_URL}/fetch-data?store_pnl=false", timeout=60)
        if resp.status_code == 200:
            result = resp.json()
            logger.info(f"Successfully fetched fresh data from IBKR (PnL not stored): {result}")
            return True
        else:
            logger.warning(f"Failed to fetch from IBKR: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Error fetching fresh data from IBKR: {e}")
        return False


@callback(
    Output('realtime-updates-store', 'data'),
    Input('realtime-updates-store', 'data'),
    prevent_initial_call=True
)
def handle_realtime_updates(data):
    """Handle real-time WebSocket updates and trigger UI refresh."""
    if data:
        update_type = data.get('type')
        logger.info(f"Received real-time update: {update_type}")
        
        # Trigger a refresh of the relevant data
        # This will be handled by the existing refresh mechanism
        return data
    return None


@callback(
    [Output('portfolio-data-store', 'data'),
     Output('last-update-store', 'data'),
     Output('loading-output', 'children')],
    [Input('refresh-btn', 'n_clicks'),
     Input('auto-refresh-interval', 'n_intervals'),
     Input('realtime-updates-store', 'data')],  # Also trigger on real-time updates
    [State('flex-data-store', 'data')],
    prevent_initial_call=False
)
def refresh_data(n_clicks, n_intervals, realtime_update, flex_data):
    """Refresh portfolio data. 
    
    Both manual refresh (button click) and auto-refresh fetch fresh data from IBKR
    but do NOT store PnL records (for display only).
    Real-time updates from WebSocket also trigger a refresh.
    """
    # Check if this is a manual refresh (button click), auto-refresh, or real-time update
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # If triggered by real-time update, we can use cached data (already fresh from WebSocket)
    if trigger_id == 'realtime-updates-store' and realtime_update:
        # Real-time update received - data is already fresh, just read from DB
        logger.info(f"Real-time update received: {realtime_update.get('type')}")
    
    # Both manual and auto-refresh fetch fresh data from IBKR (but don't store PnL)
    if trigger_id in ['refresh-btn', 'auto-refresh-interval']:
        if trigger_id == 'refresh-btn' and n_clicks:
            logger.info("Manual refresh triggered - fetching fresh data from IBKR (no PnL storage)...")
        elif trigger_id == 'auto-refresh-interval' and n_intervals:
            logger.info(f"Auto-refresh triggered (interval {n_intervals}) - fetching fresh data from IBKR (no PnL storage)...")
        
        fetch_fresh_data_from_ibkr()
        # Small delay to allow database to update (for positions/trades)
        import time
        time.sleep(0.5)
    
    # Always read from database (either after fresh fetch or for auto-refresh)
    db_data = fetch_db_data()
    
    combined_data = {
        'flex': flex_data,  # Use existing Flex data from store
        'db': db_data,
    }
    
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return combined_data, update_time, ""


@callback(
    [Output('flex-data-store', 'data'),
     Output('flex-toast', 'children'),
     Output('flex-toast', 'is_open'),
     Output('flex-toast', 'icon')],
    Input('fetch-flex-btn', 'n_clicks'),
    prevent_initial_call=True
)
def fetch_flex_query_on_demand(n_clicks):
    """Fetch ALL configured Flex Query reports when button is clicked."""
    if not n_clicks:
        return None, "", False, "info"
    
    flex_data = fetch_flex_data()
    
    if flex_data:
        # Handle new multi-report response format
        successful = flex_data.get('successful', 0)
        total = flex_data.get('total_queries', 0)
        results = flex_data.get('results', [])
        db_stats = flex_data.get('database', {})
        
        # Build summary message with database import stats
        imported = db_stats.get('new_trades_imported', 0)
        skipped = db_stats.get('duplicates_skipped', 0)
        
        if imported > 0:
            msg = f"✓ Fetched {successful}/{total} reports! 📊 {imported} new trades imported to DB"
            if skipped > 0:
                msg += f" ({skipped} duplicates skipped)"
        elif skipped > 0:
            msg = f"✓ Fetched {successful}/{total} reports. No new trades ({skipped} already in DB)"
        else:
            msg = f"✓ Fetched {successful}/{total} reports!"
        
        return flex_data, msg, True, "success"
    else:
        return None, "✗ Failed to fetch Flex Query data. Check backend logs.", True, "danger"


@callback(
    Output('last-update-text', 'children'),
    Input('last-update-store', 'data')
)
def update_last_update_text(update_time):
    """Update the last update text."""
    if update_time:
        return f"Last updated: {update_time}"
    return ""


@callback(
    [Output('performance-date-range-store', 'data'),
     Output('performance-date-picker', 'start_date'),
     Output('performance-date-picker', 'end_date')],
    [Input('date-range-1w', 'n_clicks'),
     Input('date-range-1m', 'n_clicks'),
     Input('date-range-6m', 'n_clicks'),
     Input('date-range-12m', 'n_clicks'),
     Input('date-range-all', 'n_clicks'),
     Input('apply-date-range', 'n_clicks')],
    [State('performance-date-picker', 'start_date'),
     State('performance-date-picker', 'end_date')],
    prevent_initial_call=True
)
def update_performance_date_range(btn_1w, btn_1m, btn_6m, btn_12m, btn_all, btn_apply, picker_start, picker_end):
    """Update performance date range based on button clicks or date picker."""
    from datetime import datetime, timedelta
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return {'start_date': None, 'end_date': None}, None, None
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    today = datetime.now()
    
    if trigger_id == 'date-range-1w':
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif trigger_id == 'date-range-1m':
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif trigger_id == 'date-range-6m':
        start_date = (today - timedelta(days=180)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif trigger_id == 'date-range-12m':
        start_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif trigger_id == 'date-range-all':
        start_date = None
        end_date = None
    elif trigger_id == 'apply-date-range':
        # Use dates from date picker
        start_date = picker_start
        end_date = picker_end
    else:
        return {'start_date': None, 'end_date': None}, picker_start, picker_end
    
    logger.info(f"Date range updated: {trigger_id} -> {start_date} to {end_date}")
    
    # Update date picker to match selected range
    return {'start_date': start_date, 'end_date': end_date}, start_date, end_date


@callback(
    Output('summary-metrics-row', 'children'),
    [Input('portfolio-data-store', 'data'),
     Input('flex-data-store', 'data')]
)
def update_summary_metrics(data, flex_store):
    """Update the summary metrics cards."""
    if not data and not flex_store:
        return []
    
    data = data or {}
    
    # Use flex from dedicated store if available, otherwise from portfolio store
    flex = flex_store or data.get('flex') or {}
    db = data.get('db') or {}
    account = db.get('account') or {}
    
    # Extract values with fallbacks
    net_liq = flex.get('summary', {}).get('net_liquidation') or account.get('net_liquidation', 0)
    total_cash = flex.get('summary', {}).get('total_cash') or account.get('total_cash_value', 0)
    total_positions = flex.get('summary', {}).get('total_positions') or len(db.get('positions', []))
    
    # Calculate P&L
    pnl_history = db.get('pnl_history', [])
    if pnl_history:
        latest_pnl = pnl_history[0]
        total_pnl = latest_pnl.get('total_pnl', 0) or 0
        unrealized_pnl = latest_pnl.get('unrealized_pnl', 0) or 0
    else:
        total_pnl = 0
        unrealized_pnl = 0
    
    # Format values
    def format_currency(val):
        if val is None:
            return "N/A"
        return f"${val:,.2f}"
    
    return [
        dbc.Col([
            create_metric_card(
                "Net Liquidation",
                format_currency(net_liq),
                value_class="neutral"
            )
        ], xs=12, sm=6, md=3),
        dbc.Col([
            create_metric_card(
                "Total Cash",
                format_currency(total_cash),
                value_class="neutral"
            )
        ], xs=12, sm=6, md=3),
        dbc.Col([
            create_metric_card(
                "Total P&L",
                format_currency(total_pnl),
                value_class="positive" if total_pnl > 0 else "negative" if total_pnl < 0 else "neutral"
            )
        ], xs=12, sm=6, md=3),
        dbc.Col([
            create_metric_card(
                "Positions",
                str(total_positions),
                value_class="neutral"
            )
        ], xs=12, sm=6, md=3),
    ]


@callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('portfolio-data-store', 'data'),
     Input('flex-data-store', 'data'),
     Input('performance-date-range-store', 'data')]
)
def render_tab_content(active_tab, data, flex_store, date_range):
    """Render content based on active tab."""
    # Merge flex data from dedicated store into data for tab functions
    data = data or {'flex': None, 'db': {}}
    if flex_store:
        data['flex'] = flex_store
    
    # Extract date range for performance tab
    start_date = date_range.get('start_date') if date_range else None
    end_date = date_range.get('end_date') if date_range else None
    
    # Log date range changes for debugging
    if active_tab == 'performance':
        logger.info(f"Rendering performance tab with date range: {start_date} to {end_date}")
    
    # Check if we have any meaningful data
    db_data = data.get('db') or {}
    flex_data = data.get('flex') or {}
    has_positions = bool(db_data.get('positions') or flex_data.get('positions'))
    has_pnl = bool(db_data.get('pnl_history') or db_data.get('performance'))
    has_account = bool(db_data.get('account'))
    has_any_data = has_positions or has_pnl or has_account or bool(flex_data)
    
    if not has_any_data:
        return html.Div([
            html.Div("📊", className="empty-state-icon"),
            html.H4("No portfolio data loaded."),
            html.P("Click 'Refresh' to load from database, or 'Fetch Flex Query' to retrieve from IBKR."),
        ], className="empty-state")
    
    if active_tab == "portfolio":
        return create_portfolio_tab(data)
    elif active_tab == "performance":
        return create_performance_tab(data, start_date=start_date, end_date=end_date)
    elif active_tab == "positions":
        return create_positions_tab(data)
    elif active_tab == "history":
        return create_history_tab(data)
    
    return html.Div("Select a tab")


def create_portfolio_tab(data):
    """Create portfolio overview tab."""
    flex = data.get('flex') or {}
    db = data.get('db') or {}
    
    # Get positions
    positions = flex.get('positions') or db.get('positions') or []
    
    # Create allocation chart
    if positions:
        # Group by asset type
        allocation_data = {}
        for pos in positions:
            sec_type = pos.get('sec_type', 'OTHER')
            market_value = abs(pos.get('market_value') or pos.get('quantity', 0) * (pos.get('market_price') or 0))
            if sec_type in allocation_data:
                allocation_data[sec_type] += market_value
            else:
                allocation_data[sec_type] = market_value
        
        # Create pie chart
        colors = ['#58a6ff', '#3fb950', '#a371f7', '#d29922', '#f85149', '#8b949e']
        fig_allocation = go.Figure(data=[go.Pie(
            labels=list(allocation_data.keys()),
            values=list(allocation_data.values()),
            hole=0.6,
            marker=dict(colors=colors[:len(allocation_data)]),
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(color='#c9d1d9', size=12),
        )])
        fig_allocation.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
            annotations=[dict(
                text=f"<b>{len(positions)}</b><br>Holdings",
                x=0.5, y=0.5,
                font_size=14,
                font_color='#c9d1d9',
                showarrow=False
            )]
        )
        allocation_chart = dcc.Graph(figure=fig_allocation, config={'displayModeBar': False})
    else:
        allocation_chart = html.Div("No position data available", className="empty-state")
    
    # Top holdings list
    top_holdings = sorted(
        [p for p in positions if p.get('quantity', 0) != 0],
        key=lambda x: abs(x.get('market_value') or x.get('quantity', 0) * (x.get('market_price') or 0)),
        reverse=True
    )[:10]
    
    holdings_list = []
    for pos in top_holdings:
        symbol = pos.get('symbol', 'N/A')
        qty = pos.get('quantity', 0)
        price = pos.get('market_price', 0) or 0
        value = qty * price if price else pos.get('market_value', 0) or 0
        pnl = pos.get('unrealized_pnl', 0) or 0
        
        holdings_list.append(html.Div([
            html.Div([
                html.Span(symbol, className="position-symbol"),
                html.Span(f" • {pos.get('sec_type', 'STK')}", className="position-details"),
            ]),
            html.Div([
                html.Span(f"{qty:,.2f} @ ${price:,.2f}", className="position-details"),
                html.Span(
                    f" • ${value:,.2f}",
                    style={'color': '#c9d1d9', 'fontWeight': '500', 'marginLeft': '0.5rem'}
                ),
            ]),
        ], className="position-row"))
    
    # Account info from flex
    account_info = html.Div([
        html.P([
            html.Strong("Account: "), 
            html.Span(flex.get('account_id', 'N/A'), style={'color': '#58a6ff'})
        ]),
        html.P([
            html.Strong("Period: "), 
            html.Span(f"{flex.get('from_date', 'N/A')[:10] if flex.get('from_date') else 'N/A'} to {flex.get('to_date', 'N/A')[:10] if flex.get('to_date') else 'N/A'}")
        ]),
    ], style={'fontSize': '0.85rem', 'color': '#8b949e'}) if flex else html.Div()
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Asset Allocation", className="section-title"),
                    allocation_chart,
                ], className="data-card"),
            ], md=5),
            dbc.Col([
                html.Div([
                    html.H5("Top Holdings", className="section-title"),
                    html.Div(holdings_list) if holdings_list else html.P("No holdings data", className="text-muted"),
                ], className="data-card"),
            ], md=7),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Account Information", className="section-title"),
                    account_info,
                ], className="data-card"),
            ]),
        ]),
    ])


def fetch_performance_analytics(start_date=None, end_date=None):
    """Fetch comprehensive performance analytics from backend with optional date range.
    
    Args:
        start_date: Start date string in format 'YYYY-MM-DD' or None
        end_date: End date string in format 'YYYY-MM-DD' or None
    """
    try:
        params = {}
        if start_date:
            # FastAPI expects ISO format datetime strings
            # Convert 'YYYY-MM-DD' to 'YYYY-MM-DDTHH:MM:SS' format
            if isinstance(start_date, str) and len(start_date) == 10:
                params['start_date'] = f"{start_date}T00:00:00"
            else:
                params['start_date'] = start_date
        if end_date:
            # FastAPI expects ISO format datetime strings
            if isinstance(end_date, str) and len(end_date) == 10:
                params['end_date'] = f"{end_date}T23:59:59"
            else:
                params['end_date'] = end_date
        
        logger.info(f"Fetching performance analytics with date range: {start_date} to {end_date}")
        resp = requests.get(f"{API_BASE_URL}/performance/analytics", params=params, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            logger.info(f"Successfully fetched analytics: {result.get('data_points', 0)} data points")
            return result
        else:
            logger.warning(f"Performance analytics API returned {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"Error fetching performance analytics: {e}", exc_info=True)
    return None


def create_performance_tab(data, start_date=None, end_date=None):
    """Create enhanced performance tab with metrics, charts, and benchmark comparison.
    
    Args:
        data: Portfolio data dictionary
        start_date: Optional start date string (YYYY-MM-DD) for filtering
        end_date: Optional end date string (YYYY-MM-DD) for filtering
    """
    db = data.get('db') or {}
    pnl_history = db.get('pnl_history') or []
    performance_data = db.get('performance') or []
    
    # Try to fetch comprehensive analytics from the new endpoint with date range
    analytics = fetch_performance_analytics(start_date=start_date, end_date=end_date)
    
    # Check if we have any data at all
    has_any_data = bool(
        (analytics and (analytics.get('returns_series') or analytics.get('equity_series'))) or
        pnl_history or
        performance_data
    )
    
    if not has_any_data:
        return html.Div([
            html.Div("📈", className="empty-state-icon"),
            html.H4("No performance data available"),
            html.P("Historical P&L data will appear here once available."),
            html.P([
                "Click 'Refresh' to fetch fresh data from IBKR TWS/Gateway, or ",
                html.Br(),
                "ensure you have PnL history records in the database."
            ], style={'fontSize': '0.9rem', 'color': '#8b949e', 'marginTop': '1rem'}),
        ], className="empty-state")
    
    # Prepare data for charts
    df = pd.DataFrame(pnl_history) if pnl_history else pd.DataFrame()
    if not df.empty:
        # Handle mixed datetime formats (with and without microseconds)
        df['date'] = pd.to_datetime(df['date'], format='ISO8601', errors='coerce')
        # Drop any rows where date parsing failed
        df = df.dropna(subset=['date'])
        df = df.sort_values('date')
        # Calculate daily returns if not present
        if 'net_liquidation' in df.columns:
            df['daily_return'] = df['net_liquidation'].pct_change()
            df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
    
    # Extract metrics from analytics (always prefer fresh analytics over cached performance_data)
    # Analytics are recalculated based on date range, so they should always be used when available
    if analytics and not analytics.get('error'):
        sharpe = analytics.get('sharpe_ratio', 0) or 0
        sortino = analytics.get('sortino_ratio', 0) or 0
        max_dd = analytics.get('max_drawdown', 0) or 0
        volatility = analytics.get('volatility', 0) or 0
        total_return = analytics.get('total_return', 0) or 0
        annualized_return = analytics.get('annualized_return', 0) or 0
        logger.info(f"Using analytics metrics: Sharpe={sharpe:.2f}, Sortino={sortino:.2f}, Total Return={total_return:.2%}")
    elif performance_data and len(performance_data) > 0:
        # Fallback to cached performance data if analytics not available
        latest = performance_data[0]
        sharpe = latest.get('sharpe_ratio', 0) or 0
        sortino = latest.get('sortino_ratio', 0) or 0
        max_dd = latest.get('max_drawdown', 0) or 0
        total_return = latest.get('cumulative_return', 0) or 0
        volatility = 0
        annualized_return = 0
        logger.warning("Using cached performance_data instead of fresh analytics")
    else:
        sharpe = sortino = max_dd = volatility = total_return = annualized_return = 0
        logger.warning("No performance metrics available")
    
    # =========================================================================
    # Metrics Cards Row
    # =========================================================================
    def format_metric(value, is_percent=False, is_ratio=False):
        if value is None:
            return "N/A"
        if is_percent:
            return f"{value * 100:.2f}%"
        if is_ratio:
            return f"{value:.2f}"
        return f"{value:.4f}"
    
    def metric_color(value, invert=False):
        if value is None:
            return "neutral"
        if invert:
            return "positive" if value < 0 else "negative" if value > 0 else "neutral"
        return "positive" if value > 0 else "negative" if value < 0 else "neutral"
    
    metrics_row = dbc.Row([
        dbc.Col([
            create_metric_card("Sharpe Ratio", format_metric(sharpe, is_ratio=True), metric_color(sharpe))
        ], xs=6, sm=4, md=2),
        dbc.Col([
            create_metric_card("Sortino Ratio", format_metric(sortino, is_ratio=True), metric_color(sortino))
        ], xs=6, sm=4, md=2),
        dbc.Col([
            create_metric_card("Max Drawdown", format_metric(max_dd, is_percent=True), metric_color(max_dd, invert=True))
        ], xs=6, sm=4, md=2),
        dbc.Col([
            create_metric_card("Volatility", format_metric(volatility, is_percent=True), "neutral")
        ], xs=6, sm=4, md=2),
        dbc.Col([
            create_metric_card("Total Return", format_metric(total_return, is_percent=True), metric_color(total_return))
        ], xs=6, sm=4, md=2),
        dbc.Col([
            create_metric_card("Ann. Return", format_metric(annualized_return, is_percent=True), metric_color(annualized_return))
        ], xs=6, sm=4, md=2),
    ], className="mb-4")
    
    # =========================================================================
    # Cumulative Returns Chart (Portfolio vs S&P 500)
    # =========================================================================
    fig_returns = go.Figure()
    
    has_portfolio_data = False
    has_benchmark_data = False
    
    portfolio_dates = []
    portfolio_cum_returns = []
    benchmark_dates = []
    benchmark_cum_returns = []
    
    # Try to get portfolio cumulative returns from analytics returns_series first
    if analytics and analytics.get('returns_series'):
        returns_series = analytics['returns_series']
        if returns_series and len(returns_series) > 0:
            try:
                portfolio_dates = [item.get('date') for item in returns_series if item.get('date')]
                # Ensure we're using cumulative_return, not NAV or other values
                portfolio_cum_returns = [item.get('cumulative_return', 0) * 100 for item in returns_series if item.get('date')]  # Convert to percentage
                
                if portfolio_dates and portfolio_cum_returns and len(portfolio_dates) == len(portfolio_cum_returns):
                    has_portfolio_data = True
            except Exception as e:
                logger.error(f"Error processing returns_series: {e}")
    
    # Get benchmark cumulative returns if available (from analytics which is recalculated with date range)
    if analytics and analytics.get('benchmark_comparison'):
        bc = analytics['benchmark_comparison']
        # Check if there's an error in benchmark comparison
        if not bc.get('error') and bc.get('time_series'):
            ts = bc['time_series']
            benchmark_dates = ts.get('dates', [])
            # Ensure we're using benchmark_cumulative (cumulative return), not price values
            benchmark_cum_returns = [r * 100 for r in ts.get('benchmark_cumulative', [])]  # Convert to percentage
            
            if benchmark_dates and benchmark_cum_returns and len(benchmark_dates) == len(benchmark_cum_returns):
                has_benchmark_data = True
                logger.info(f"Benchmark data available: {len(benchmark_dates)} data points")
            else:
                logger.warning(f"Benchmark time series data incomplete: dates={len(benchmark_dates)}, returns={len(benchmark_cum_returns)}")
        else:
            logger.warning(f"Benchmark comparison error or missing: {bc.get('error', 'No time_series data')}")
    
    # Fallback: use pnl_history data if analytics doesn't have returns_series
    if not has_portfolio_data and not df.empty and 'cumulative_return' in df.columns:
        portfolio_dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
        portfolio_cum_returns = (df['cumulative_return'] * 100).tolist()
        has_portfolio_data = True
    
    # Plot portfolio cumulative returns
    if has_portfolio_data and portfolio_dates and portfolio_cum_returns:
        fig_returns.add_trace(go.Scatter(
            x=portfolio_dates,
            y=portfolio_cum_returns,
            mode='lines',
            name='Portfolio (Cumulative Return)',
            line=dict(color='#58a6ff', width=2),
            fill='tozeroy',
            fillcolor='rgba(88, 166, 255, 0.1)',
        ))
    
    # Plot benchmark cumulative returns (S&P 500)
    if has_benchmark_data and benchmark_dates and benchmark_cum_returns:
        fig_returns.add_trace(go.Scatter(
            x=benchmark_dates,
            y=benchmark_cum_returns,
            mode='lines',
            name='S&P 500 (Cumulative Return)',
            line=dict(color='#f85149', width=2, dash='dash'),
        ))
    
    # If still no data, show empty chart with message
    if not has_portfolio_data:
        fig_returns.add_annotation(
            text="No return data available. Please fetch data from IBKR.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color='#8b949e')
        )
    
    fig_returns.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#c9d1d9'),
        ),
        xaxis=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
        ),
        yaxis=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
            ticksuffix='%',
            title=dict(text='Cumulative Return', font=dict(color='#8b949e')),
        ),
        margin=dict(t=40, b=40, l=60, r=20),
        height=350,
        hovermode='x unified',
    )
    
    # =========================================================================
    # Returns Distribution Histogram
    # =========================================================================
    fig_dist = go.Figure()
    
    if analytics and analytics.get('distribution'):
        dist = analytics['distribution']
        hist = dist.get('histogram', {})
        stats = dist.get('statistics', {})
        
        bins = hist.get('bins', [])
        counts = hist.get('counts', [])
        
        if bins and counts:
            fig_dist.add_trace(go.Bar(
                x=[b * 100 for b in bins],  # Convert to percentage
                y=counts,
                name='Daily Returns',
                marker_color='#58a6ff',
                opacity=0.7,
            ))
            
            # Add VaR line
            var_95 = stats.get('var_95', 0)
            if var_95:
                fig_dist.add_vline(
                    x=var_95 * 100,
                    line_dash="dash",
                    line_color="#f85149",
                    annotation_text=f"VaR 95%: {var_95*100:.2f}%",
                    annotation_position="top right",
                    annotation_font_color="#f85149",
                )
    elif not df.empty and 'daily_return' in df.columns:
        returns = df['daily_return'].dropna() * 100
        fig_dist.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,
            name='Daily Returns',
            marker_color='#58a6ff',
            opacity=0.7,
        ))
    
    fig_dist.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
            ticksuffix='%',
            title=dict(text='Daily Return', font=dict(color='#8b949e')),
        ),
        yaxis=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
            title=dict(text='Frequency', font=dict(color='#8b949e')),
        ),
        margin=dict(t=20, b=40, l=60, r=20),
        height=300,
        showlegend=False,
    )
    
    # =========================================================================
    # Net Liquidation / Equity Chart
    # =========================================================================
    fig_equity = go.Figure()
    
    if not df.empty and 'net_liquidation' in df.columns:
        fig_equity.add_trace(go.Scatter(
            x=df['date'],
            y=df['net_liquidation'],
            mode='lines',
            name='Net Liquidation',
            line=dict(color='#3fb950', width=2),
            fill='tozeroy',
            fillcolor='rgba(63, 185, 80, 0.1)',
        ))
    
    fig_equity.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
        ),
        yaxis=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
            tickprefix='$',
            title=dict(text='Account Value', font=dict(color='#8b949e')),
        ),
        margin=dict(t=20, b=40, l=60, r=20),
        height=300,
        hovermode='x unified',
    )
    
    # =========================================================================
    # Rolling Metrics Chart
    # =========================================================================
    fig_rolling = go.Figure()
    
    if analytics and analytics.get('rolling_metrics'):
        rm = analytics['rolling_metrics']
        dates = rm.get('dates', [])
        rolling_sharpe = rm.get('rolling_sharpe', [])
        rolling_vol = rm.get('rolling_volatility', [])
        
        if dates and rolling_sharpe:
            fig_rolling.add_trace(go.Scatter(
                x=dates,
                y=rolling_sharpe,
                mode='lines',
                name='30-Day Rolling Sharpe',
                line=dict(color='#58a6ff', width=2.5),  # Blue, thicker line
                yaxis='y',
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Sharpe: %{y:.2f}<extra></extra>',
            ))
        
        if dates and rolling_vol:
            fig_rolling.add_trace(go.Scatter(
                x=dates,
                y=[v * 100 for v in rolling_vol],  # Convert to percentage
                mode='lines',
                name='30-Day Rolling Volatility',
                line=dict(color='#f85149', width=2.5, dash='dot'),  # Red, dotted line, different from Sharpe
                yaxis='y2',
                hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Volatility: %{y:.2f}%<extra></extra>',
            ))
    
    fig_rolling.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#c9d1d9'),
        ),
        xaxis=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
        ),
        yaxis=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
            title=dict(text='Sharpe Ratio', font=dict(color='#58a6ff')),
        ),
        yaxis2=dict(
            gridcolor='rgba(48, 54, 61, 0.5)',
            tickfont=dict(color='#8b949e'),
            ticksuffix='%',
            title=dict(text='Volatility', font=dict(color='#f85149')),  # Match line color
            overlaying='y',
            side='right',
        ),
        margin=dict(t=40, b=40, l=60, r=60),
        height=300,
        hovermode='x unified',
    )
    
    # =========================================================================
    # Benchmark Comparison Stats Card
    # =========================================================================
    benchmark_card = None
    if analytics and analytics.get('benchmark_comparison'):
        bc = analytics['benchmark_comparison']
        if not bc.get('error'):
            benchmark_card = html.Div([
                html.H5("Benchmark Comparison (vs S&P 500)", className="section-title"),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Span("Beta: ", style={'color': '#8b949e'}),
                            html.Span(f"{bc.get('beta', 0):.2f}", style={'color': '#c9d1d9', 'fontWeight': '600'}),
                        ]),
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.Span("Alpha: ", style={'color': '#8b949e'}),
                            html.Span(
                                f"{bc.get('alpha', 0)*100:.2f}%",
                                style={'color': '#3fb950' if (bc.get('alpha', 0) or 0) > 0 else '#f85149', 'fontWeight': '600'}
                            ),
                        ]),
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.Span("Correlation: ", style={'color': '#8b949e'}),
                            html.Span(f"{bc.get('correlation', 0):.2f}", style={'color': '#c9d1d9', 'fontWeight': '600'}),
                        ]),
                    ], width=4),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Span("Info Ratio: ", style={'color': '#8b949e'}),
                            html.Span(f"{bc.get('information_ratio', 0):.2f}", style={'color': '#c9d1d9', 'fontWeight': '600'}),
                        ]),
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.Span("Tracking Error: ", style={'color': '#8b949e'}),
                            html.Span(f"{(bc.get('tracking_error', 0) or 0)*100:.2f}%", style={'color': '#c9d1d9', 'fontWeight': '600'}),
                        ]),
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.Span("S&P 500 Return: ", style={'color': '#8b949e'}),
                            html.Span(
                                f"{(bc.get('benchmark_cumulative_return', 0) or 0)*100:.2f}%",
                                style={'color': '#3fb950' if (bc.get('benchmark_cumulative_return', 0) or 0) > 0 else '#f85149', 'fontWeight': '600'}
                            ),
                        ]),
                    ], width=4),
                ], className="mt-2"),
            ], className="data-card", style={'marginTop': '1rem'})
    
    # =========================================================================
    # Date Range Controls
    # =========================================================================
    from datetime import datetime, timedelta
    
    # Calculate default date ranges
    today = datetime.now()
    
    # Display current date range
    date_range_display = ""
    if start_date and end_date:
        date_range_display = f"Showing: {start_date} to {end_date}"
    elif start_date:
        date_range_display = f"From: {start_date}"
    elif end_date:
        date_range_display = f"Until: {end_date}"
    else:
        date_range_display = "Showing: All data"
    
    date_range_controls = dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.Label("Quick Select:", style={'fontSize': '0.85rem', 'color': '#8b949e', 'marginRight': '0.5rem', 'fontWeight': '500'}),
                    dbc.ButtonGroup([
                        dbc.Button("1W", id="date-range-1w", size="sm", outline=True, color="secondary", className="me-1"),
                        dbc.Button("1M", id="date-range-1m", size="sm", outline=True, color="secondary", className="me-1"),
                        dbc.Button("6M", id="date-range-6m", size="sm", outline=True, color="secondary", className="me-1"),
                        dbc.Button("12M", id="date-range-12m", size="sm", outline=True, color="secondary", className="me-1"),
                        dbc.Button("All", id="date-range-all", size="sm", outline=True, color="secondary"),
                    ], className="me-3"),
                    html.Label("Custom Range:", style={'fontSize': '0.85rem', 'color': '#8b949e', 'marginRight': '0.5rem', 'marginLeft': '1rem', 'fontWeight': '500'}),
                    dcc.DatePickerRange(
                        id='performance-date-picker',
                        start_date=start_date,
                        end_date=end_date,
                        display_format='YYYY-MM-DD',
                        style={'fontSize': '0.85rem'},
                        className="me-2"
                    ),
                    dbc.Button(
                        "Apply", 
                        id="apply-date-range", 
                        size="sm", 
                        color="primary",
                        className="ms-2"
                    ),
                ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '0.5rem'}),
                html.Div([
                    html.Span(
                        date_range_display,
                        style={'fontSize': '0.75rem', 'color': '#58a6ff', 'fontStyle': 'italic', 'marginTop': '0.5rem'}
                    )
                ], style={'marginTop': '0.5rem'})
            ], style={
                'padding': '1rem',
                'background': 'rgba(33, 38, 45, 0.5)',
                'borderRadius': '8px',
                'marginBottom': '1.5rem'
            })
        ], width=12),
    ])
    
    # =========================================================================
    # Assemble the Layout
    # =========================================================================
    # Determine chart title based on available data
    if has_benchmark_data:
        chart_title = "Cumulative Returns (Portfolio vs S&P 500)"
    elif has_portfolio_data:
        chart_title = "Cumulative Returns (Portfolio)"
    else:
        chart_title = "Cumulative Returns"
    
    return html.Div([
        # Date Range Controls
        date_range_controls,
        
        # Metrics Cards
        metrics_row,
        
        # Cumulative Returns Chart
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5(chart_title, className="section-title"),
                    html.P(
                        "Both lines show cumulative returns (%) from the start of the period",
                        style={'fontSize': '0.75rem', 'color': '#8b949e', 'marginBottom': '0.5rem', 'fontStyle': 'italic'}
                    ),
                    dcc.Graph(figure=fig_returns, config={'displayModeBar': False}),
                ], className="data-card"),
            ]),
        ]),
        
        # Benchmark stats card
        benchmark_card if benchmark_card else html.Div(),
        
        # Two column layout for distribution and equity
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Returns Distribution", className="section-title"),
                    dcc.Graph(figure=fig_dist, config={'displayModeBar': False}),
                ], className="data-card"),
            ], md=6),
            dbc.Col([
                html.Div([
                    html.H5("Account Value Over Time", className="section-title"),
                    dcc.Graph(figure=fig_equity, config={'displayModeBar': False}),
                ], className="data-card"),
            ], md=6),
        ]),
        
        # Rolling Metrics
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Rolling Performance Metrics (30-Day)", className="section-title"),
                    dcc.Graph(figure=fig_rolling, config={'displayModeBar': False}),
                ], className="data-card"),
            ]),
        ]) if analytics and analytics.get('rolling_metrics') and analytics['rolling_metrics'].get('dates') else html.Div(),
    ])


def create_positions_tab(data):
    """Create detailed positions tab."""
    flex = data.get('flex') or {}
    db = data.get('db') or {}
    
    # Determine data source
    positions = flex.get('positions') or db.get('positions') or []
    data_source = "Flex Query" if flex.get('positions') else "Database (IBKR TWS/Gateway)"
    
    # Get latest position timestamp if available
    latest_timestamp = None
    if positions:
        timestamps = []
        for p in positions:
            ts = p.get('timestamp')
            if ts:
                try:
                    # Handle both string and datetime objects
                    if isinstance(ts, str):
                        # Try parsing ISO format
                        ts_str = ts.replace('Z', '+00:00') if 'Z' in ts else ts
                        timestamps.append(datetime.fromisoformat(ts_str))
                    elif isinstance(ts, datetime):
                        timestamps.append(ts)
                except Exception as e:
                    logger.debug(f"Could not parse timestamp {ts}: {e}")
                    pass
        
        if timestamps:
            latest_timestamp = max(timestamps)
    
    if not positions:
        return html.Div([
            html.Div("📋", className="empty-state-icon"),
            html.H4("No positions found"),
            html.P("Your current positions will appear here."),
            html.P([
                "Click 'Refresh' to fetch fresh data from IBKR TWS/Gateway, or ",
                html.Br(),
                "click 'Fetch Flex Query' to get historical positions from IBKR Flex Query."
            ], style={'fontSize': '0.9rem', 'color': '#8b949e', 'marginTop': '1rem'}),
        ], className="empty-state")
    
    # Group by asset class
    positions_by_class = {}
    for pos in positions:
        sec_type = pos.get('sec_type', 'OTHER')
        if sec_type not in positions_by_class:
            positions_by_class[sec_type] = []
        positions_by_class[sec_type].append(pos)
    
    sections = []
    for sec_type, pos_list in positions_by_class.items():
        # Create table for this asset class
        rows = []
        for pos in sorted(pos_list, key=lambda x: x.get('symbol', '')):
            symbol = pos.get('symbol', 'N/A')
            qty = pos.get('quantity', 0)
            if qty == 0:
                continue
                
            price = pos.get('market_price', 0) or pos.get('avg_cost', 0) or 0
            value = pos.get('market_value') or (qty * price)
            pnl = pos.get('unrealized_pnl')  # Keep None if not present
            currency = pos.get('currency', 'USD')
            
            # Determine P&L display class (handle None explicitly)
            if pnl is not None:
                pnl_class = 'positive' if pnl > 0 else 'negative' if pnl < 0 else 'neutral'
                pnl_display = f"${pnl:,.2f}"
                pnl_color = '#3fb950' if pnl > 0 else '#f85149' if pnl < 0 else '#8b949e'
            else:
                pnl_class = 'neutral'
                pnl_display = "N/A"
                pnl_color = '#8b949e'
            
            rows.append(html.Tr([
                html.Td(symbol, style={'fontWeight': '600', 'color': '#58a6ff'}),
                html.Td(f"{qty:,.4f}"),
                html.Td(f"${price:,.2f}"),
                html.Td(f"${value:,.2f}" if value else "N/A"),
                html.Td(pnl_display, style={'color': pnl_color}),
                html.Td(currency, style={'color': '#8b949e'}),
            ]))
        
        if rows:
            table = html.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Symbol"),
                        html.Th("Quantity"),
                        html.Th("Price"),
                        html.Th("Value"),
                        html.Th("P&L"),
                        html.Th("CCY"),
                    ])
                ]),
                html.Tbody(rows)
            ], style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'fontSize': '0.9rem',
            })
            
            # Add custom styling for table
            table_card = html.Div([
                html.H5(f"{sec_type} ({len(rows)})", className="section-title"),
                html.Div(table, style={'overflowX': 'auto'}),
            ], className="data-card")
            
            sections.append(dbc.Col([table_card], xs=12, lg=6))
    
    # Add data source info at the top
    data_source_info = html.Div([
        html.P([
            html.Span("Data source: ", style={'color': '#8b949e', 'fontSize': '0.85rem'}),
            html.Span(data_source, style={'color': '#58a6ff', 'fontSize': '0.85rem', 'fontWeight': '500'}),
            html.Span(
                f" • Last updated: {latest_timestamp.strftime('%Y-%m-%d %H:%M:%S')}" if latest_timestamp else "",
                style={'color': '#8b949e', 'fontSize': '0.85rem', 'marginLeft': '1rem'}
            ),
        ]),
    ], style={'marginBottom': '1rem', 'padding': '0.5rem 1rem', 'background': 'rgba(88, 166, 255, 0.1)', 'borderRadius': '8px'})
    
    return html.Div([
        data_source_info,
        dbc.Row(sections)
    ])


def create_history_tab(data):
    """Create trade history tab."""
    flex = data.get('flex') or {}
    
    recent_trades = flex.get('recent_trades') or []
    
    if not recent_trades:
        return html.Div([
            html.Div("📜", className="empty-state-icon"),
            html.H4("No trade history available"),
            html.P("Your recent trades will appear here once you configure a Flex Query with trade data."),
            html.Hr(),
            html.P([
                "To enable trade history:",
                html.Br(),
                "1. Log into IBKR Account Management",
                html.Br(),
                "2. Go to Performance & Reports → Flex Queries",
                html.Br(),
                "3. Create/Edit query to include 'Trades' section",
            ], style={'fontSize': '0.9rem', 'color': '#8b949e'}),
        ], className="empty-state")
    
    # Create trades table
    rows = []
    for trade in recent_trades:
        side = trade.get('side', 'N/A')
        side_color = '#3fb950' if side == 'BUY' else '#f85149'
        
        rows.append(html.Tr([
            html.Td(trade.get('trade_date', 'N/A')[:10] if trade.get('trade_date') else 'N/A'),
            html.Td(trade.get('symbol', 'N/A'), style={'fontWeight': '600', 'color': '#58a6ff'}),
            html.Td(side, style={'color': side_color, 'fontWeight': '600'}),
            html.Td(f"{trade.get('quantity', 0):,.2f}"),
            html.Td(f"${trade.get('price', 0):,.2f}"),
            html.Td(f"${trade.get('commission', 0):,.2f}", style={'color': '#f85149'}),
            html.Td(
                f"${trade.get('realized_pnl', 0):,.2f}" if trade.get('realized_pnl') else "N/A",
                style={'color': '#3fb950' if (trade.get('realized_pnl') or 0) > 0 else '#f85149'}
            ),
        ]))
    
    table = html.Table([
        html.Thead([
            html.Tr([
                html.Th("Date"),
                html.Th("Symbol"),
                html.Th("Side"),
                html.Th("Qty"),
                html.Th("Price"),
                html.Th("Commission"),
                html.Th("Realized P&L"),
            ])
        ]),
        html.Tbody(rows)
    ], style={
        'width': '100%',
        'borderCollapse': 'collapse',
        'fontSize': '0.9rem',
    })
    
    return html.Div([
        html.Div([
            html.H5("Recent Trades", className="section-title"),
            html.Div(table, style={'overflowX': 'auto'}),
        ], className="data-card"),
    ])


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
