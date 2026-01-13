"""Production PyWry server demonstrating toolbar components and callbacks.

This example shows:
- Toolbar components (Button, Select, Slider)
- Bidirectional event callbacks (Python ↔ JavaScript)
- Plotly integration with dynamic chart updates
- AG Grid with row selection and bulk actions
- Clean URL routing

Configuration is loaded from the central configuration system:
- Built-in defaults → pyproject.toml → pywry.toml → env vars
"""

# ruff: noqa: I001
# pylint: disable=wrong-import-position,invalid-name
from typing import Any

import os

# Must set environment variables BEFORE importing pywry modules
# because configuration is loaded at import time
os.environ.setdefault("PYWRY_SERVER__HOST", "0.0.0.0")  # noqa: S104
os.environ.setdefault("PYWRY_SERVER__PORT", "8080")
os.environ.setdefault("PYWRY_SERVER__LOG_LEVEL", "info")

import pandas as pd  # type: ignore[import-untyped]
import plotly.express as px
from fastapi.responses import HTMLResponse

from pywry.inline import (
    deploy,
    get_server_app,
    get_widget_html,
    show_dataframe,
    show_plotly,
)
from pywry.toolbar import Button, Option, Select, Toolbar

# Get PyWry's FastAPI app
app = get_server_app()

# Store widget references for emitting updates
_widgets: dict[str, Any] = {}


# ═══════════════════════════════════════════════════════════
# SAMPLE DATA
# ═══════════════════════════════════════════════════════════


def get_sales_data(region: str = "all") -> pd.DataFrame:
    """Generate sales data filtered by region."""
    data = []
    regions = ["North", "South", "East", "West"] if region == "all" else [region]
    for r in regions:
        for year in range(2020, 2025):
            base = {"North": 100, "South": 80, "East": 120, "West": 90}[r]
            growth = (year - 2020) * 10
            data.append(
                {
                    "region": r,
                    "year": year,
                    "revenue": base + growth + (hash(f"{r}{year}") % 30),
                }
            )
    return pd.DataFrame(data)


def get_inventory_data() -> pd.DataFrame:
    """Generate inventory data."""
    return pd.DataFrame(
        {
            "sku": ["A001", "A002", "B001", "B002", "C001", "C002", "D001"],
            "product": [
                "Widget Pro",
                "Widget Lite",
                "Gadget X",
                "Gadget Y",
                "Tool Max",
                "Tool Mini",
                "Device Z",
            ],
            "category": ["Widgets", "Widgets", "Gadgets", "Gadgets", "Tools", "Tools", "Devices"],
            "quantity": [150, 230, 45, 89, 310, 125, 67],
            "price": [29.99, 19.99, 149.99, 99.99, 59.99, 39.99, 199.99],
            "warehouse": ["A", "A", "B", "B", "A", "B", "A"],
        }
    )


# ═══════════════════════════════════════════════════════════
# SALES DASHBOARD - Plotly with real dynamic updates
# ═══════════════════════════════════════════════════════════

sales_state = {"region": "all", "theme": "dark"}


def on_region_change(data: dict[str, Any], _event_type: str, _label: str) -> None:
    """Update chart when region filter changes."""
    sales_state["region"] = data.get("value", "all")

    # Build new figure with filtered data
    df = get_sales_data(sales_state["region"])
    template = "plotly_dark" if sales_state["theme"] == "dark" else "plotly_white"
    fig = px.bar(df, x="year", y="revenue", color="region", barmode="group", template=template)
    fig.update_layout(title=f"Sales Revenue - {sales_state['region'].title()}")

    # Use the widget's update_figure method
    widget = _widgets.get("sales")
    if widget:
        widget.update_figure(fig)


def on_toggle_theme(_data: dict[str, Any], _event_type: str, _label: str) -> None:
    """Toggle theme and update chart."""
    sales_state["theme"] = "light" if sales_state["theme"] == "dark" else "dark"
    # Update chart and page theme using proper methods
    widget = _widgets.get("sales")
    if widget:
        widget.emit("pywry:update_theme", {"theme": sales_state["theme"]})


def on_export_csv(_data: dict[str, Any], _event_type: str, _label: str) -> None:
    """Export current data to CSV - triggers browser download dialog."""
    df = get_sales_data(sales_state["region"])
    csv_data = df.to_csv(index=False)

    widget = _widgets.get("sales")
    if widget:
        widget.emit(
            "pywry:download",
            {
                "filename": f"sales_{sales_state['region']}.csv",
                "content": csv_data,
                "mimeType": "text/csv",
            },
        )


def on_nav_inventory(_data: dict[str, Any], _event_type: str, _label: str) -> None:
    """Navigate to inventory view."""
    widget = _widgets.get("sales")
    if widget:
        widget.emit("pywry:navigate", {"url": "/inventory"})


def on_nav_home_sales(_data: dict[str, Any], _event_type: str, _label: str) -> None:
    """Navigate to home from sales."""
    widget = _widgets.get("sales")
    if widget:
        widget.emit("pywry:navigate", {"url": "/"})


def create_sales_widget() -> str:
    """Create sales dashboard with interactive toolbar."""
    df = get_sales_data(sales_state["region"])
    template = "plotly_dark" if sales_state["theme"] == "dark" else "plotly_white"

    fig = px.bar(df, x="year", y="revenue", color="region", barmode="group", template=template)
    fig.update_layout(
        title="Sales Revenue by Region",
        xaxis_title="Year",
        yaxis_title="Revenue ($K)",
    )

    nav_toolbar = Toolbar(
        position="top",
        items=[
            Button(label="🏠", event="nav:home", description="Back to Home", variant="ghost"),
            Button(label="Export CSV", event="sales:export"),
            Button(label="Toggle Theme", event="sales:theme", variant="secondary"),
            Button(
                label="Inventory →",
                event="nav:inventory",
                variant="ghost",
                style="margin-left:auto;",
            ),
        ],
    )

    filter_toolbar = Toolbar(
        position="left",
        items=[
            Select(
                label="Region:",
                event="sales:region",
                options=[
                    Option(label="All Regions", value="all"),
                    Option(label="North", value="North"),
                    Option(label="South", value="South"),
                    Option(label="East", value="East"),
                    Option(label="West", value="West"),
                ],
                selected=sales_state["region"],
            ),
        ],
    )

    widget = show_plotly(
        fig,
        title="Sales Dashboard",
        toolbars=[nav_toolbar, filter_toolbar],
        callbacks={
            "sales:region": on_region_change,
            "sales:export": on_export_csv,
            "sales:theme": on_toggle_theme,
            "nav:inventory": on_nav_inventory,
            "nav:home": on_nav_home_sales,
        },
    )
    _widgets["sales"] = widget
    return str(getattr(widget, "label", ""))


# ═══════════════════════════════════════════════════════════
# INVENTORY - AG Grid with row actions
# ═══════════════════════════════════════════════════════════

inventory_state = {"category": "all", "selected_skus": []}


def on_category_filter(data: dict[str, Any], _event_type: str, _label: str) -> None:
    """Filter grid by category."""
    inventory_state["category"] = data.get("value", "all")

    df = get_inventory_data()
    if inventory_state["category"] != "all":
        df = df[df["category"] == inventory_state["category"]]

    widget = _widgets.get("inventory")
    if widget:
        widget.update_data(df.to_dict(orient="records"))


def on_row_selected(data: dict[str, Any], _event_type: str, _label: str) -> None:
    """Track selected rows."""
    inventory_state["selected_skus"] = [row.get("sku") for row in data.get("rows", [])]


def on_restock(_data: dict[str, Any], _event_type: str, _label: str) -> None:
    """Send restock notice for selected items."""
    if not inventory_state["selected_skus"]:
        widget = _widgets.get("inventory")
        if widget:
            widget.emit("pywry:alert", {"message": "Please select items to restock first."})
        return

    # Send restock notice
    widget = _widgets.get("inventory")
    if widget:
        count = len(inventory_state["selected_skus"])
        widget.emit("pywry:alert", {"message": f"Restock notice sent for {count} item(s)!"})


def on_nav_sales(_data: dict[str, Any], _event_type: str, _label: str) -> None:
    """Navigate to sales view."""
    widget = _widgets.get("inventory")
    if widget:
        widget.emit("pywry:navigate", {"url": "/sales"})


def on_nav_home_inv(_data: dict[str, Any], _event_type: str, _label: str) -> None:
    """Navigate to home from inventory."""
    widget = _widgets.get("inventory")
    if widget:
        widget.emit("pywry:navigate", {"url": "/"})


def create_inventory_widget() -> str:
    """Create inventory grid."""
    df = get_inventory_data()

    nav_toolbar = Toolbar(
        position="top",
        items=[
            Button(label="🏠", event="nav:home", description="Back to Home", variant="ghost"),
            Button(label="← Sales", event="nav:sales", variant="ghost"),
        ],
    )

    filter_toolbar = Toolbar(
        position="left",
        items=[
            Select(
                label="Category:",
                event="inv:category",
                options=[
                    Option(label="All", value="all"),
                    Option(label="Widgets", value="Widgets"),
                    Option(label="Gadgets", value="Gadgets"),
                    Option(label="Tools", value="Tools"),
                    Option(label="Devices", value="Devices"),
                ],
                selected="all",
            ),
            Button(
                label="📦 Restock",
                event="inv:restock",
                variant="outline",
                description="Send restock notice for selected items",
            ),
        ],
    )

    widget = show_dataframe(
        df,
        title="Inventory",
        toolbars=[nav_toolbar, filter_toolbar],
        row_selection=True,
        callbacks={
            "inv:category": on_category_filter,
            "inv:restock": on_restock,
            "grid:row_selected": on_row_selected,
            "nav:sales": on_nav_sales,
            "nav:home": on_nav_home_inv,
        },
    )
    _widgets["inventory"] = widget
    return str(getattr(widget, "label", ""))


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════

# Create widgets ONCE at module load (not per-request)
# This ensures the same widget_id is used for all clients
_sales_widget_id = create_sales_widget()
_inventory_widget_id = create_inventory_widget()


@app.get("/")
async def index() -> HTMLResponse:
    """Landing page with navigation to all demos."""
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="en" class="pywry-native dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyWry Demo Server</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #e0e0e0;
            padding: 2rem;
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle {
            color: #888;
            margin-bottom: 3rem;
            font-size: 1.1rem;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            max-width: 900px;
            width: 100%;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 2rem;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .card:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: #00d4ff;
            transform: translateY(-4px);
            box-shadow: 0 10px 40px rgba(0, 212, 255, 0.2);
        }
        .card-icon {
            font-size: 2.5rem;
        }
        .card-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: #fff;
        }
        .card-desc {
            color: #aaa;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .card-features {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: auto;
        }
        .tag {
            background: rgba(0, 212, 255, 0.15);
            color: #00d4ff;
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .footer {
            margin-top: 3rem;
            color: #666;
            font-size: 0.85rem;
        }
        .footer a { color: #00d4ff; text-decoration: none; }
        .footer a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>🚀 PyWry Demo</h1>
    <p class="subtitle">Interactive data visualization with Python + FastAPI</p>

    <div class="cards">
        <a href="/sales" class="card">
            <span class="card-icon">📊</span>
            <span class="card-title">Sales Dashboard</span>
            <span class="card-desc">
                Interactive Plotly bar chart with region filtering.
                Toggle themes and export data to CSV.
            </span>
            <div class="card-features">
                <span class="tag">Plotly</span>
                <span class="tag">Dropdown</span>
                <span class="tag">Theme Toggle</span>
                <span class="tag">CSV Export</span>
            </div>
        </a>

        <a href="/inventory" class="card">
            <span class="card-icon">📦</span>
            <span class="card-title">Inventory Manager</span>
            <span class="card-desc">
                AG Grid data table with category filtering,
                row selection, and bulk restock actions.
            </span>
            <div class="card-features">
                <span class="tag">AG Grid</span>
                <span class="tag">Row Selection</span>
                <span class="tag">Filtering</span>
                <span class="tag">Bulk Actions</span>
            </div>
        </a>
    </div>
    <p class="footer">
        Built with <a href="https://github.com/OpenBB-finance/OpenBB" target="_blank">PyWry 2.0</a> •
    </p>
</body>
</html>
""")


@app.get("/sales", response_class=HTMLResponse)
async def sales_dashboard() -> HTMLResponse:
    """Sales dashboard with Plotly chart and toolbar controls."""
    html = get_widget_html(_sales_widget_id)
    if not html:
        return HTMLResponse("<h1>Error loading widget</h1>", status_code=500)
    return HTMLResponse(html)


@app.get("/inventory", response_class=HTMLResponse)
async def inventory_view() -> HTMLResponse:
    """Inventory grid with filters and bulk actions."""
    html = get_widget_html(_inventory_widget_id)
    if not html:
        return HTMLResponse("<h1>Error loading widget</h1>", status_code=500)
    return HTMLResponse(html)


if __name__ == "__main__":
    deploy()
