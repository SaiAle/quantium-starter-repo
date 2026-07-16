"""Smoke test for the Quantium Dash workbench.

Verifies the Dash app can be constructed, imports work, and the dev
server boots without errors. Run with the project's virtual env active:

    .venv\\Scripts\\python.exe smoke_test.py
"""
from __future__ import annotations

import sys

import dash
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html


def build_app() -> Dash:
    """Build a minimal Dash app so we can confirm the workbench is healthy."""
    sample = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=7, freq="D"),
            "sales": [10, 12, 9, 15, 18, 14, 20],
        }
    )
    fig = px.line(sample, x="date", y="sales", title="Workbench OK")

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.H1("Quantium Dash workbench — smoke test"),
            dcc.Graph(figure=fig),
        ]
    )
    return app


def main() -> int:
    print(f"dash     {dash.__version__}")
    print(f"pandas   {pd.__version__}")

    app = build_app()
    print(f"app      {app.title!r} built OK")

    # Start the dev server briefly to make sure the WSGI pipeline is happy.
    # We run in a background thread so the test exits cleanly.
    import threading
    import time

    from werkzeug.serving import make_server

    server = make_server("127.0.0.1", 0, app.server)  # port 0 = auto-pick
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    server.shutdown()

    print(f"server   bound to 127.0.0.1:{port} and shut down cleanly")
    print("ALL OK — workbench is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
