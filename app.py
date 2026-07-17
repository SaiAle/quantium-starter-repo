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
user drill into region-specific sales data.

Run from the project root with the venv active:
    .venv\\Scripts\\python.exe app.py
then open http://127.0.0.1:8050 in a browser.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


# -- Paths -------------------------------------------------------------------
DATA_FILE = Path(__file__).parent / "data" / "processed" / "sales_data.csv"
PRICE_CHANGE_DATE = "2021-01-15"
REGIONS = ["north", "east", "south", "west"]


# -- Load data ---------------------------------------------------------------
# The processed file is Pink Morsels only, with one row per day per region.
df = pd.read_csv(DATA_FILE)
df["Date"] = pd.to_datetime(df["Date"])


# -- Build the line chart (called by callback) --------------------------------
def make_figure(region: str) -> px.line:
    """Build a line chart of daily Pink Morsel sales for *region*.

    When *region* is ``'all'`` sales are summed across all regions per day;
    otherwise the data is filtered to that single region.
    """
    if region == "all":
        daily = (
            df.groupby("Date", as_index=False)["Sales"]
              .sum()
              .sort_values("Date")
        )
        title = "Daily Pink Morsel Sales (all regions)"
    else:
        subset = df[df["Region"] == region]
        daily = (
            subset.groupby("Date", as_index=False)["Sales"]
                  .sum()
                  .sort_values("Date")
        )
        title = f"Daily Pink Morsel Sales — {region.title()}"

    assert daily["Sales"].notna().all(), "NaN in Sales"
    assert daily["Date"].is_monotonic_increasing, "Date not sorted"

    fig = px.line(
        daily,
        x="Date",
        y="Sales",
        title=title,
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sales (USD)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
        height=520,
    )
    fig.add_vline(
        x=PRICE_CHANGE_DATE,
        line_dash="dash",
        line_color="crimson",
        line_width=2,
        annotation_text="Price rise: $3 -> $5 (15 Jan 2021)",
        annotation_position="top left",
        annotation=dict(font_color="crimson", font_size=12),
    )
    return fig


# -- Dash app ----------------------------------------------------------------
app = Dash(__name__)
app.title = "Pink Morsel Sales"

app.layout = html.Div(
    className="app-container",
    children=[
        html.H1("Pink Morsel Sales", className="header"),
        html.Div(
            className="controls",
            children=[
                html.Label("Region", className="region-label"),
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
                    labelStyle={
                        "display": "inline-flex",
                        "align-items": "center",
                        "gap": "0.3rem",
                    },
                ),
            ],
        ),
        dcc.Graph(id="sales-line", className="graph-card"),
    ],
)


@app.callback(
    Output("sales-line", "figure"),
    [Input("region-filter", "value")],
)
def update_chart(region: str) -> px.line:
    return make_figure(region)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)
