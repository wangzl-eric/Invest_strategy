"""Research Cerebro panel: paper discovery, scoring, proposals, and provenance."""

import logging
import os
from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, State, callback, dash_table, dcc, html

logger = logging.getLogger(__name__)

# Professional lightweight palette (matches strategy_monitor.py)
GREEN = "#34d399"
RED = "#f87171"
BLUE = "#4da6ff"
YELLOW = "#fbbf24"
PURPLE = "#a78bfa"
MUTED = "#9094a1"
TEXT_PRIMARY = "#e4e6eb"
BORDER = "#2a2e35"
BG_CARD = "#181b1f"
BG_SECONDARY = "#14171c"

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")


# ------------------------------------------------------------------
# Stat card helper
# ------------------------------------------------------------------


def _stat_card(label: str, value: Any, color: str = BLUE) -> html.Div:
    """Build a single metric card."""
    return html.Div(
        [
            html.P(label, className="metric-label"),
            html.P(
                str(value), className="metric-value neutral", style={"color": color}
            ),
        ],
        className="metric-card",
    )


# ------------------------------------------------------------------
# Score bar helper
# ------------------------------------------------------------------


def _score_bar(label: str, value: Optional[float], max_val: float = 10.0) -> html.Div:
    """Render a labelled progress bar for a score dimension."""
    pct = min((value or 0) / max_val * 100, 100)
    color = GREEN if pct >= 70 else (YELLOW if pct >= 40 else RED)
    return html.Div(
        [
            html.Div(
                [
                    html.Span(label, style={"color": MUTED, "fontSize": "0.75rem"}),
                    html.Span(
                        f"{value or 0:.1f}",
                        style={
                            "color": TEXT_PRIMARY,
                            "fontSize": "0.75rem",
                            "fontFamily": "JetBrains Mono",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "marginBottom": "2px",
                },
            ),
            dbc.Progress(
                value=pct,
                color=None,
                style={"height": "6px", "backgroundColor": "#22262b"},
                bar_style={"backgroundColor": color},
            ),
        ],
        style={"marginBottom": "0.5rem"},
    )


# ------------------------------------------------------------------
# Provenance chain helper
# ------------------------------------------------------------------


def _provenance_chain(steps: List[Dict]) -> html.Div:
    """Render the paper -> signal -> backtest -> verdict provenance chain."""
    if not steps:
        return html.Div(
            "No provenance data", style={"color": MUTED, "fontSize": "0.85rem"}
        )

    items = []
    for i, step in enumerate(steps):
        stage = step.get("stage", "unknown")
        agent = step.get("agent", "-")
        verdict = step.get("verdict", "-")
        ts = step.get("timestamp", "")[:16] if step.get("timestamp") else "-"

        badge_color = {
            "discovered": "info",
            "scored": "primary",
            "summarized": "warning",
            "proposed": "success",
            "backtested": "success",
            "rejected": "danger",
        }.get(stage, "secondary")

        node = html.Div(
            [
                dbc.Badge(stage.upper(), color=badge_color, className="me-2"),
                html.Span(
                    f"{agent}", style={"color": TEXT_PRIMARY, "fontSize": "0.8rem"}
                ),
                html.Span(
                    f" | {verdict}", style={"color": MUTED, "fontSize": "0.8rem"}
                ),
                html.Span(
                    f"  {ts}",
                    style={
                        "color": MUTED,
                        "fontSize": "0.7rem",
                        "marginLeft": "0.5rem",
                    },
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "padding": "0.4rem 0",
                "borderLeft": f"2px solid {BLUE}"
                if i < len(steps) - 1
                else f"2px solid {GREEN}",
                "paddingLeft": "0.75rem",
                "marginLeft": "0.5rem",
            },
        )
        items.append(node)

    return html.Div(items)


# ------------------------------------------------------------------
# Main layout builder
# ------------------------------------------------------------------


def create_cerebro_tab() -> html.Div:
    """Build the Research Cerebro tab layout.

    Returns a complete Dash layout with papers table, detail panel,
    proposals list, provenance chain, discovery stats, and search.
    """
    # --- Discovery Stats ---
    stats_row = html.Div(
        id="cerebro-stats-row",
        children=[
            _stat_card("Total Papers", "-"),
            _stat_card("Scored", "-", GREEN),
            _stat_card("Proposed", "-", PURPLE),
            _stat_card("Avg Score", "-", YELLOW),
            _stat_card("Vector Docs", "-", BLUE),
        ],
        style={
            "display": "flex",
            "gap": "1rem",
            "flexWrap": "wrap",
            "marginBottom": "1.5rem",
        },
    )

    # --- Search + Discover controls ---
    controls = html.Div(
        [
            dbc.InputGroup(
                [
                    dbc.Input(
                        id="cerebro-search-input",
                        placeholder="Semantic search across papers...",
                        type="text",
                    ),
                    dbc.Button(
                        "Search", id="cerebro-search-btn", color="primary", size="sm"
                    ),
                ],
                style={"maxWidth": "500px"},
            ),
            dbc.Button(
                "Run Discovery",
                id="cerebro-discover-btn",
                color="secondary",
                outline=True,
                size="sm",
                className="ms-3",
            ),
            html.Span(
                id="cerebro-discover-status",
                style={"color": MUTED, "fontSize": "0.8rem", "marginLeft": "0.75rem"},
            ),
        ],
        style={
            "display": "flex",
            "alignItems": "center",
            "marginBottom": "1.5rem",
            "flexWrap": "wrap",
            "gap": "0.5rem",
        },
    )

    # --- Papers DataTable ---
    papers_table = html.Div(
        [
            html.Div("Discovered Papers", className="section-title"),
            dash_table.DataTable(
                id="cerebro-papers-table",
                columns=[
                    {"name": "ID", "id": "id", "type": "numeric"},
                    {"name": "Title", "id": "title", "type": "text"},
                    {"name": "Source", "id": "source", "type": "text"},
                    {
                        "name": "Score",
                        "id": "composite_score",
                        "type": "numeric",
                        "format": {"specifier": ".1f"},
                    },
                    {
                        "name": "Relevance",
                        "id": "relevance_score",
                        "type": "numeric",
                        "format": {"specifier": ".1f"},
                    },
                    {
                        "name": "Quality",
                        "id": "quality_score",
                        "type": "numeric",
                        "format": {"specifier": ".1f"},
                    },
                    {"name": "Status", "id": "status", "type": "text"},
                    {"name": "Date", "id": "published_date", "type": "text"},
                ],
                data=[],
                row_selectable="single",
                selected_rows=[],
                page_size=12,
                sort_action="native",
                filter_action="native",
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": BG_SECONDARY,
                    "color": MUTED,
                    "fontWeight": 500,
                    "fontSize": "0.7rem",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px",
                    "border": f"1px solid {BORDER}",
                },
                style_cell={
                    "backgroundColor": BG_CARD,
                    "color": TEXT_PRIMARY,
                    "border": f"1px solid #22262b",
                    "fontSize": "0.82rem",
                    "padding": "0.5rem 0.75rem",
                    "fontFamily": "Inter, sans-serif",
                    "textOverflow": "ellipsis",
                    "maxWidth": "300px",
                },
                style_cell_conditional=[
                    {
                        "if": {"column_id": "title"},
                        "textAlign": "left",
                        "minWidth": "250px",
                    },
                    {"if": {"column_id": "id"}, "width": "50px"},
                    {"if": {"column_id": "source"}, "width": "70px"},
                    {"if": {"column_id": "status"}, "width": "80px"},
                ],
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgba(255,255,255,0.01)",
                    },
                    {
                        "if": {"filter_query": "{composite_score} >= 7"},
                        "color": GREEN,
                        "fontWeight": 600,
                    },
                    {
                        "if": {"filter_query": "{composite_score} < 4"},
                        "color": RED,
                    },
                ],
                style_filter={
                    "backgroundColor": BG_SECONDARY,
                    "color": TEXT_PRIMARY,
                },
            ),
        ],
        className="data-card",
        style={"marginBottom": "1.5rem"},
    )

    # --- Paper Detail (hidden until selected) ---
    paper_detail = html.Div(
        id="cerebro-paper-detail",
        children=html.Div(
            "Select a paper from the table above to view details.",
            style={"color": MUTED},
        ),
        className="data-card",
        style={"marginBottom": "1.5rem"},
    )

    # --- Proposals Section ---
    proposals_section = html.Div(
        [
            html.Div("Strategy Proposals", className="section-title"),
            html.Div(id="cerebro-proposals-list", children=[]),
        ],
        className="data-card",
        style={"marginBottom": "1.5rem"},
    )

    # --- Full layout ---
    return html.Div(
        [
            html.H4(
                "Research Cerebro",
                style={"color": TEXT_PRIMARY, "marginBottom": "0.5rem"},
            ),
            html.P(
                "Automated paper discovery, LLM scoring, strategy proposals, and provenance tracking.",
                style={"color": MUTED, "marginBottom": "1.5rem"},
            ),
            stats_row,
            controls,
            papers_table,
            dbc.Row(
                [
                    dbc.Col(paper_detail, md=7),
                    dbc.Col(proposals_section, md=5),
                ]
            ),
        ]
    )


# ------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------


def register_cerebro_callbacks(app):
    """Register all Cerebro callbacks on the Dash app.

    Called from app.py after app creation, following the existing pattern
    where callbacks are registered via function call.
    """

    @app.callback(
        [
            Output("cerebro-stats-row", "children"),
            Output("cerebro-papers-table", "data"),
            Output("cerebro-proposals-list", "children"),
        ],
        Input("main-tabs", "active_tab"),
    )
    def update_cerebro_data(active_tab):
        """Fetch papers, stats, and proposals when the cerebro tab is active."""
        if active_tab != "cerebro":
            from dash import no_update

            return no_update, no_update, no_update

        stats_cards = [
            _stat_card("Total Papers", "-"),
            _stat_card("Scored", "-", GREEN),
            _stat_card("Proposed", "-", PURPLE),
            _stat_card("Avg Score", "-", YELLOW),
            _stat_card("Vector Docs", "-", BLUE),
        ]
        papers_data = []
        proposals_children = []

        # Fetch stats
        try:
            resp = requests.get(f"{API_BASE_URL}/cerebro/stats", timeout=5)
            if resp.ok:
                s = resp.json().get("data", {})
                db = s.get("db", {})
                vs = s.get("vector_store", {})
                stats_cards = [
                    _stat_card("Total Papers", db.get("total_papers", 0)),
                    _stat_card("Scored", db.get("scored_papers", 0), GREEN),
                    _stat_card("Proposed", db.get("proposed_papers", 0), PURPLE),
                    _stat_card(
                        "Avg Score", db.get("avg_composite_score") or "-", YELLOW
                    ),
                    _stat_card("Vector Docs", vs.get("document_count", 0), BLUE),
                ]
        except Exception as exc:
            logger.warning("Failed to fetch cerebro stats: %s", exc)

        # Fetch papers
        try:
            resp = requests.get(f"{API_BASE_URL}/cerebro/papers?per_page=50", timeout=5)
            if resp.ok:
                body = resp.json()
                papers_data = body.get("data", [])
                # Truncate title for table display
                for p in papers_data:
                    if p.get("title") and len(p["title"]) > 80:
                        p["title"] = p["title"][:77] + "..."
                    # Shorten published_date to YYYY-MM-DD
                    if p.get("published_date"):
                        p["published_date"] = p["published_date"][:10]
        except Exception as exc:
            logger.warning("Failed to fetch cerebro papers: %s", exc)

        # Fetch proposals
        try:
            resp = requests.get(f"{API_BASE_URL}/cerebro/proposals", timeout=5)
            if resp.ok:
                props = resp.json().get("data", [])
                if not props:
                    proposals_children = [
                        html.Div(
                            "No proposals generated yet.",
                            style={"color": MUTED, "fontSize": "0.85rem"},
                        )
                    ]
                else:
                    proposals_children = _build_proposal_rows(props)
        except Exception as exc:
            logger.warning("Failed to fetch cerebro proposals: %s", exc)
            proposals_children = [
                html.Div(
                    "Could not load proposals.",
                    style={"color": RED, "fontSize": "0.85rem"},
                )
            ]

        if not proposals_children:
            proposals_children = [
                html.Div(
                    "No proposals generated yet.",
                    style={"color": MUTED, "fontSize": "0.85rem"},
                )
            ]

        return stats_cards, papers_data, proposals_children

    @app.callback(
        Output("cerebro-paper-detail", "children"),
        Input("cerebro-papers-table", "selected_rows"),
        State("cerebro-papers-table", "data"),
    )
    def show_paper_detail(selected_rows, table_data):
        """Display full detail for the selected paper row."""
        if not selected_rows or not table_data:
            return html.Div(
                "Select a paper from the table above to view details.",
                style={"color": MUTED},
            )

        row = table_data[selected_rows[0]]
        paper_id = row.get("id")

        # Fetch full paper with provenance
        detail = dict(row)
        provenance = []
        try:
            resp = requests.get(f"{API_BASE_URL}/cerebro/papers/{paper_id}", timeout=5)
            if resp.ok:
                full = resp.json().get("data", {})
                detail = full
                provenance = full.get("provenance", [])
        except Exception as exc:
            logger.warning("Failed to fetch paper detail %s: %s", paper_id, exc)

        # Build detail layout
        title = detail.get("title", "Untitled")
        authors = detail.get("authors", "-")
        abstract = (
            detail.get("abstract") or detail.get("one_line") or "No abstract available."
        )
        methodology = detail.get("methodology") or "-"
        url = detail.get("url") or ""
        asset_class = detail.get("asset_class") or "-"
        complexity = detail.get("implementation_complexity") or "-"
        key_findings = detail.get("key_findings") or "-"
        limitations = detail.get("limitations") or "-"

        return html.Div(
            [
                html.Div("Paper Detail", className="section-title"),
                html.H5(
                    title, style={"color": TEXT_PRIMARY, "marginBottom": "0.25rem"}
                ),
                html.P(
                    authors,
                    style={
                        "color": MUTED,
                        "fontSize": "0.8rem",
                        "marginBottom": "0.75rem",
                    },
                ),
                html.A(
                    "View original",
                    href=url,
                    target="_blank",
                    style={"color": BLUE, "fontSize": "0.8rem"},
                )
                if url
                else html.Span(),
                html.Hr(style={"borderColor": BORDER, "margin": "0.75rem 0"}),
                # Scores breakdown
                html.Div(
                    "Scores", className="section-title", style={"marginTop": "0.5rem"}
                ),
                _score_bar("Relevance", detail.get("relevance_score")),
                _score_bar("Quality", detail.get("quality_score")),
                _score_bar("Novelty", detail.get("novelty_score")),
                _score_bar("Feasibility", detail.get("feasibility_score")),
                _score_bar("Composite", detail.get("composite_score")),
                html.Hr(style={"borderColor": BORDER, "margin": "0.75rem 0"}),
                # Metadata
                html.Div(
                    [
                        html.Span(
                            "Asset class: ",
                            style={"color": MUTED, "fontSize": "0.8rem"},
                        ),
                        html.Span(
                            asset_class,
                            style={"color": TEXT_PRIMARY, "fontSize": "0.8rem"},
                        ),
                        html.Span(
                            " | Complexity: ",
                            style={
                                "color": MUTED,
                                "fontSize": "0.8rem",
                                "marginLeft": "1rem",
                            },
                        ),
                        html.Span(
                            complexity,
                            style={"color": TEXT_PRIMARY, "fontSize": "0.8rem"},
                        ),
                    ],
                    style={"marginBottom": "0.75rem"},
                ),
                # Summary sections
                html.Div("Abstract", className="section-title"),
                html.P(
                    abstract,
                    style={
                        "color": TEXT_PRIMARY,
                        "fontSize": "0.82rem",
                        "lineHeight": "1.5",
                    },
                ),
                html.Div("Methodology", className="section-title"),
                html.P(
                    methodology,
                    style={
                        "color": TEXT_PRIMARY,
                        "fontSize": "0.82rem",
                        "lineHeight": "1.5",
                    },
                ),
                html.Div("Key Findings", className="section-title"),
                html.P(
                    key_findings,
                    style={
                        "color": TEXT_PRIMARY,
                        "fontSize": "0.82rem",
                        "lineHeight": "1.5",
                    },
                ),
                html.Div("Limitations", className="section-title"),
                html.P(
                    limitations,
                    style={
                        "color": TEXT_PRIMARY,
                        "fontSize": "0.82rem",
                        "lineHeight": "1.5",
                    },
                ),
                # Provenance chain
                html.Hr(style={"borderColor": BORDER, "margin": "0.75rem 0"}),
                html.Div("Provenance Chain", className="section-title"),
                _provenance_chain(provenance),
            ]
        )

    @app.callback(
        Output("cerebro-discover-status", "children"),
        Input("cerebro-discover-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def trigger_discovery(n_clicks):
        """Manually trigger a discovery pipeline run."""
        if not n_clicks:
            from dash import no_update

            return no_update

        try:
            resp = requests.post(
                f"{API_BASE_URL}/cerebro/discover?limit=50&days_back=7", timeout=10
            )
            if resp.ok:
                msg = resp.json().get("message", "Discovery started")
                return html.Span(msg, style={"color": GREEN})
            return html.Span(f"Error: {resp.status_code}", style={"color": RED})
        except Exception as exc:
            return html.Span(f"Failed: {exc}", style={"color": RED})

    @app.callback(
        Output("cerebro-papers-table", "data", allow_duplicate=True),
        Input("cerebro-search-btn", "n_clicks"),
        State("cerebro-search-input", "value"),
        prevent_initial_call=True,
    )
    def search_papers(n_clicks, query):
        """Run semantic search and update the papers table."""
        if not n_clicks or not query:
            from dash import no_update

            return no_update

        try:
            resp = requests.get(
                f"{API_BASE_URL}/cerebro/search",
                params={"q": query, "n_results": 20},
                timeout=10,
            )
            if resp.ok:
                results = resp.json().get("data", [])
                # Normalise search results to match table columns
                rows = []
                for r in results:
                    rows.append(
                        {
                            "id": r.get("id", ""),
                            "title": (r.get("title", "")[:77] + "...")
                            if len(r.get("title", "")) > 80
                            else r.get("title", ""),
                            "source": r.get("source", ""),
                            "composite_score": r.get("composite_score"),
                            "relevance_score": r.get("relevance_score"),
                            "quality_score": r.get("quality_score"),
                            "status": r.get("status", ""),
                            "published_date": (r.get("published_date") or "")[:10],
                        }
                    )
                return rows
        except Exception as exc:
            logger.warning("Cerebro search failed: %s", exc)

        from dash import no_update

        return no_update


# ------------------------------------------------------------------
# Proposal row builder
# ------------------------------------------------------------------


def _build_proposal_rows(proposals: List[Dict]) -> List[html.Div]:
    """Build styled rows for each strategy proposal."""
    rows = []
    for p in proposals:
        title = p.get("title") or p.get("filename", "Unknown")
        created = (p.get("created_at") or "")[:10]
        source_line = p.get("source_line", "")

        rows.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                title,
                                style={
                                    "color": TEXT_PRIMARY,
                                    "fontWeight": 500,
                                    "fontSize": "0.85rem",
                                },
                            ),
                            html.Br(),
                            html.Span(
                                source_line,
                                style={"color": MUTED, "fontSize": "0.72rem"},
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Span(
                        created,
                        style={
                            "color": MUTED,
                            "fontSize": "0.75rem",
                            "fontFamily": "JetBrains Mono",
                            "whiteSpace": "nowrap",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "flex-start",
                    "padding": "0.5rem 0",
                    "borderBottom": f"1px solid #22262b",
                },
            )
        )
    return rows
