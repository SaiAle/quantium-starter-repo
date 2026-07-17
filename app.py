"""
Dash application for Quantium Task 4.

Visualises the Pink Morsel daily sales produced in Task 2
(data/processed/sales_data.csv - columns: Sales, Date, Region) as an
interactive line chart so the answer to Soul Foods's question is obvious
at a glance:

    "Were sales higher before or after the Pink Morsel price increase
     on the 15th of January, 2021?"

The pink morsel price rose from $3.00 to $5.00 on 2021-01-15; a vertical
marker line and annotation call that event out on the chart.
A radio-button region filter (north / east / south / west / all) lets the
user drill into region-specific sales data with live KPI metrics.

Run from the project root with the venv active:
    .venv\\Scripts\\python.exe app.py
then open http://127.0.0.1:8050 in a browser.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output


# -- Paths -------------------------------------------------------------------
DATA_FILE = Path(__file__).parent / "data" / "processed" / "sales_data.csv"
PRICE_CHANGE_DATE = pd.Timestamp("2021-01-15")


# -- Load data ---------------------------------------------------------------
df = pd.read_csv(DATA_FILE)
df["Date"] = pd.to_datetime(df["Date"])
REGIONS = ["north", "east", "south", "west"]

# Pre-compute daily aggregates for all regions (used by KPIs + chart).
def daily_for_region(region: str) -> pd.DataFrame:
    if region == "all":
        subset = df
    else:
        subset = df[df["Region"] == region]
    return (
        subset.groupby("Date", as_index=False)["Sales"]
              .sum()
              .sort_values("Date")
              .reset_index(drop=True)
    )


# -- Compute KPI metrics ----------------------------------------------------
def compute_kpis(region: str) -> dict:
    d = daily_for_region(region)
    before = d[d["Date"] < PRICE_CHANGE_DATE]
    after  = d[d["Date"] >= PRICE_CHANGE_DATE]
    total_all = d["Sales"].sum()
    avg_before = before["Sales"].mean() if len(before) else 0
    avg_after  = after["Sales"].mean()  if len(after)  else 0
    pct_change = ((avg_after - avg_before) / avg_before * 100) if avg_before else 0
    return {
        "total": total_all,
        "avg_before": avg_before,
        "avg_after": avg_after,
        "pct_change": pct_change,
    }


# -- Build the line chart ---------------------------------------------------
ACCENT = "#f06292"
ACCENT_GLOW = "rgba(240, 98, 146, 0.18)"

def make_figure(region: str) -> go.Figure:
    d = daily_for_region(region)
    label = "All Regions" if region == "all" else region.title()

    fig = go.Figure()

    # Area fill underneath the line.
    fig.add_traces(go.Scatter(
        x=d["Date"], y=d["Sales"],
        mode="lines",
        name="Daily Sales",
        line=dict(color=ACCENT, width=2.5, shape="spline", smoothing=0.3),
        fill="tozeroy",
        fillcolor="rgba(240, 98, 146, 0.08)",
        hovertemplate="<b>%{x|%-d %b %Y}</b><br>Sales: $%{y:,.0f}<extra></extra>",
    ))

    # Pre/Post averages as faint horizontal reference lines.
    before = d[d["Date"] < PRICE_CHANGE_DATE]
    after  = d[d["Date"] >= PRICE_CHANGE_DATE]
    if len(before):
        avg_b = before["Sales"].mean()
        fig.add_hline(
            y=avg_b, line_dash="dot", line_color="rgba(255,255,255,0.15)",
            annotation_text=f"Before avg: ${avg_b:,.0f}",
            annotation_position="top right",
            annotation=dict(font_size=10, font_color="rgba(255,255,255,0.3)"),
        )
    if len(after):
        avg_a = after["Sales"].mean()
        fig.add_hline(
            y=avg_a, line_dash="dot", line_color="rgba(240,98,146,0.2)",
            annotation_text=f"After avg: ${avg_a:,.0f}",
            annotation_position="bottom right",
            annotation=dict(font_size=10, font_color="rgba(240,98,146,0.35)"),
        )

    fig.add_vline(
        x=pd.Timestamp(PRICE_CHANGE_DATE),
        line_dash="dash",
        line_color=ACCENT,
        line_width=2,
        annotation_text="Price rose $3 → $5",
        annotation_position="top left",
        annotation=dict(
            font_color=ACCENT, font_size=12, bgcolor="rgba(15,10,26,0.7)",
            bordercolor=ACCENT, borderwidth=1, borderpad=4,
        ),
    )

    fig.update_layout(
        title=dict(
            text=f"Daily Pink Morsel Sales — {label}",
            font=dict(size=16, color="rgba(241,238,246,0.85)", weight=600),
            x=0, xref="paper",
        ),
        xaxis=dict(
            title="", showgrid=True, gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(color="rgba(241,238,246,0.5)", size=11),
            zeroline=False,
        ),
        yaxis=dict(
            title="", showgrid=True, gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(color="rgba(241,238,246,0.5)", size=11),
            zeroline=False,
            tickprefix="$",
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=60, t=40, b=30),
        height=480,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(15,10,26,0.9)", font_color="white",
            font_size=12, bordercolor="rgba(255,255,255,0.1)",
        ),
        legend=dict(visible=False),
        dragmode=False,
    )

    return fig


# -- Dash app ----------------------------------------------------------------
app = Dash(__name__)
app.title = "Soul Foods — Pink Morsel Sales"

app.layout = html.Div(
    className="app-container",
    children=[

        # ── Brand Bar ──
        html.Div(
            className="brand-bar",
            children=[
                html.Div(
                    className="brand-left",
                    children=[
                        html.Div("P", className="brand-icon"),
                        html.Div(
                            className="brand-text",
                            children=[
                                html.H1("Pink Morsel Sales"),
                                html.Span("Soul Foods • Retail Analytics"),
                            ],
                        ),
                    ],
                ),
                html.Div("Price Rise: Jan 15, 2021", className="brand-badge"),
            ],
        ),

        # ── KPI Row ──
        html.Div(id="kpi-row", className="kpi-row"),

        # ── Controls ──
        html.Div(
            className="controls",
            children=[
                html.Span("Region", className="region-label"),
                dcc.RadioItems(
                    id="region-filter",
                    className="region-radio",
                    options=[
                        {"label": "All", "value": "all"},
                        {"label": "North", "value": "north"},
                        {"label": "East", "value": "east"},
                        {"label": "South", "value": "south"},
                        {"label": "West", "value": "west"},
                    ],
                    value="all",
                ),
            ],
        ),

        # ── Chart ──
        dcc.Graph(id="sales-line", className="graph-card"),

        # ── Footer ──
        html.Div(
            className="footer",
            children=[
                "Built with Dash & Plotly  ",
                html.Span("●"),
                "  Data: Soul Foods Pink Morsel Sales (2018–2022)",
            ],
        ),
    ],
)


@app.callback(
    [Output("sales-line", "figure"),
     Output("kpi-row", "children")],
    [Input("region-filter", "value")],
)
def update_dashboard(region: str):
    fig = make_figure(region)
    kpis = compute_kpis(region)
    label = "All Regions" if region == "all" else region.title()

    pct = kpis["pct_change"]
    pct_str = f"{pct:+.1f}%"
    pct_color = ACCENT if pct < 0 else "#66bb6a"
    arrow = "↓" if pct < 0 else "↑"

    kpi_cards = [
        html.Div(
            className="kpi-card accent",
            children=[
                html.Div("Total Revenue", className="kpi-label"),
                html.Div(f"${kpis['total']:,.0f}", className="kpi-value"),
                html.Div(f"All-time • {label}", className="kpi-sub"),
            ],
        ),
        html.Div(
            className="kpi-card",
            children=[
                html.Div("Avg Daily (Before)", className="kpi-label"),
                html.Div(f"${kpis['avg_before']:,.0f}", className="kpi-value"),
                html.Div("Prior to Jan 15, 2021", className="kpi-sub"),
            ],
        ),
        html.Div(
            className="kpi-card",
            children=[
                html.Div("Avg Daily (After)", className="kpi-label"),
                html.Div(f"${kpis['avg_after']:,.0f}", className="kpi-value"),
                html.Div("From Jan 15, 2021 onward", className="kpi-sub"),
            ],
        ),
        html.Div(
            className="kpi-card accent",
            style={"border-left": f"3px solid {pct_color}"},
            children=[
                html.Div("Change in Avg Daily", className="kpi-label"),
                html.Div(
                    f"{arrow} {pct_str}",
                    className="kpi-value",
                    style={"color": pct_color,
                           "-webkit-text-fill-color": pct_color},
                ),
                html.Div("Before vs after price rise", className="kpi-sub"),
            ],
        ),
    ]

    return fig, kpi_cards


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)
