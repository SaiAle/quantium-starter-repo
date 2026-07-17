"""
Dash application for Quantium Task 3.

Visualises the Pink Morsel daily sales produced in Task 2
(data/processed/sales_data.csv - columns: Sales, Date, Region) as a line
chart so the answer to Soul Foods's question is obvious at a glance:

    "Were sales higher before or after the Pink Morsel price increase
     on the 15th of January, 2021?"

The pink morsel price rose from $3.00 to $5.00 on 2021-01-15; a vertical
marker line and annotation call that event out on the chart.

Run from the project root with the venv active:
    .venv\\Scripts\\python.exe app.py
then open http://127.0.0.1:8050 in a browser.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html


# -- Paths -------------------------------------------------------------------
DATA_FILE = Path(__file__).parent / "data" / "processed" / "sales_data.csv"
PRICE_CHANGE_DATE = "2021-01-15"


# -- Load & shape ------------------------------------------------------------
# The processed file is Pink Morsels only, with one row per day per region.
# To chart overall daily sales we sum across regions for each date.
df = pd.read_csv(DATA_FILE)
df["Date"] = pd.to_datetime(df["Date"])
daily = (
    df.groupby("Date", as_index=False)["Sales"]
      .sum()
      .sort_values("Date")
)
assert daily["Sales"].notna().all(), "NaN in Sales"
assert daily["Date"].is_monotonic_increasing, "Date not sorted"


# -- Build the line chart ----------------------------------------------------
fig = px.line(
    daily,
    x="Date",
    y="Sales",
    title="Daily Pink Morsel Sales (all regions)",
)
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Sales (USD)",
    template="plotly_white",
    margin=dict(l=40, r=40, t=60, b=40),
    height=520,
)
# Mark the Pink Morsel price rise on 2021-01-15.
fig.add_vline(
    x=PRICE_CHANGE_DATE,
    line_dash="dash",
    line_color="crimson",
    line_width=2,
    annotation_text="Price rise: $3 -> $5 (15 Jan 2021)",
    annotation_position="top left",
    annotation=dict(font_color="crimson", font_size=12),
)


# -- Dash app ----------------------------------------------------------------
app = Dash(__name__)
app.title = "Pink Morsel Sales"

app.layout = html.Div(
    [
        html.H1("Pink Morsel Sales"),
        dcc.Graph(id="sales-line", figure=fig),
    ]
)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)
