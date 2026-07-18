"""Tests for the Pink Morsel Sales Dash app.

Uses the Flask test client to render the app and inspects the HTML output
with BeautifulSoup. This avoids requiring a browser / chromedriver.
"""
from __future__ import annotations

from pathlib import Path

import pytest

# Ensure app.py is importable
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app


@pytest.fixture
def client():
    """Yield the Flask test client with the Dash app server."""
    with app.server.test_client() as c:
        yield c


def _soup(client):
    """Return BeautifulSoup-parsed HTML for the app root."""
    from bs4 import BeautifulSoup

    resp = client.get("/")
    assert resp.status_code == 200
    return BeautifulSoup(resp.data, "html.parser")


def test_header_present(client):
    import json

    resp = client.get("/_dash-layout")
    assert resp.status_code == 200
    layout = json.loads(resp.data)

    def find_h1(node) -> str | None:
        if isinstance(node, dict):
            if node.get("type") == "H1":
                children = node.get("props", {}).get("children", "")
                if isinstance(children, list):
                    return "".join(str(c) for c in children)
                return str(children)
            if "children" in node.get("props", {}):
                children = node["props"]["children"]
                if isinstance(children, list):
                    for c in children:
                        result = find_h1(c)
                        if result:
                            return result
                else:
                    return find_h1(children)
        return None

    text = find_h1(layout)
    assert text is not None, "No H1 found in layout JSON"
    assert "Pink Morsel Sales" in text


def test_visualization_present(client):
    soup = _soup(client)
    # The graph div is rendered by Dash's React; it won't appear in the
    # static HTML (the page bootstrap contains a JS-driven layout).
    # Instead we verify the layout JSON (/_dash-layout) includes the Graph.
    import json

    resp = client.get("/_dash-layout")
    assert resp.status_code == 200
    layout = json.loads(resp.data)

    # Walk the layout tree looking for the sales-line graph.
    def find_graph(node) -> bool:
        if isinstance(node, dict):
            if node.get("type") == "Graph" and node.get("props", {}).get("id") == "sales-line":
                return True
            if "children" in node.get("props", {}):
                children = node["props"]["children"]
                if isinstance(children, list):
                    return any(find_graph(c) for c in children)
                return find_graph(children)
        return False

    assert find_graph(layout), "Graph(id='sales-line') not found in layout JSON"


def test_region_picker_present(client):
    soup = _soup(client)
    page_text = soup.get_text()

    # The RadioItems component is rendered client-side by React, so it
    # won't be in the static HTML.  Verify via the layout JSON instead.
    import json

    resp = client.get("/_dash-layout")
    layout = json.loads(resp.data)

    def find_radio(node) -> bool:
        if isinstance(node, dict):
            props = node.get("props", {})
            if node.get("type") == "RadioItems" and props.get("id") == "region-filter":
                return True
            if "children" in props:
                children = props["children"]
                if isinstance(children, list):
                    return any(find_radio(c) for c in children)
                return find_radio(children)
        return False

    assert find_radio(layout), "RadioItems(id='region-filter') not found in layout JSON"

    # Also verify the options list.
    def get_options(node):
        if isinstance(node, dict):
            props = node.get("props", {})
            if node.get("type") == "RadioItems" and props.get("id") == "region-filter":
                return props.get("value", ""), [o["value"] for o in props.get("options", [])]
            if "children" in props:
                children = props["children"]
                if isinstance(children, list):
                    for c in children:
                        result = get_options(c)
                        if result:
                            return result
                else:
                    return get_options(children)
        return None

    options = get_options(layout)
    assert options is not None, "Could not find region-filter options"
    default_value, option_values = options
    assert default_value == "all", f"Expected default 'all', got {default_value!r}"
    assert set(option_values) == {"all", "north", "east", "south", "west"}, \
        f"Unexpected options: {option_values}"
