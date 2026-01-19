"""Production PyWry Server - Deploy Mode Demo.

This example demonstrates PyWry's deploy mode with:
- Scalable state management (memory or Redis backend)
- Toolbar components (Button, Select)
- Bidirectional callbacks (Python ↔ JavaScript)
- Plotly charts with dynamic updates
- AG Grid with row selection and bulk actions
- Clean URL routing

Run with:
    python pywry_demo_deploy.py

Or with Redis backend:
    PYWRY_DEPLOY__STATE_BACKEND=redis PYWRY_DEPLOY__REDIS_URL=redis://localhost:6379/0 python pywry_demo_deploy.py
"""
# pylint: disable=wrong-import-position,redefined-outer-name,ungrouped-imports

from __future__ import annotations

import os

from typing import TYPE_CHECKING, Any, cast


# Configure for production BEFORE importing pywry
os.environ.setdefault("PYWRY_SERVER__HOST", "0.0.0.0")  # noqa: S104
os.environ.setdefault("PYWRY_SERVER__PORT", "8080")

import pandas as pd  # type: ignore[import-untyped]
import plotly.express as px

from fastapi.responses import HTMLResponse

from pywry.inline import (
    InlineWidget,
    deploy,
    get_server_app,
    get_widget_html_async,
    show,
    show_dataframe,
    show_plotly,
)
from pywry.toolbar import Button, Option, Select, Toolbar


if TYPE_CHECKING:
    from plotly.graph_objects import Figure


# Get PyWry's FastAPI app
app = get_server_app()


# ═══════════════════════════════════════════════════════════
# SAMPLE DATA GENERATORS
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


def get_inventory_data(category: str = "all") -> pd.DataFrame:
    """Generate inventory data filtered by category."""
    df = pd.DataFrame(
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
            "category": [
                "Widgets",
                "Widgets",
                "Gadgets",
                "Gadgets",
                "Tools",
                "Tools",
                "Devices",
            ],
            "quantity": [150, 230, 45, 89, 310, 125, 67],
            "price": [29.99, 19.99, 149.99, 99.99, 59.99, 39.99, 199.99],
            "warehouse": ["A", "A", "B", "B", "A", "B", "A"],
        }
    )
    if category != "all":
        df = df[df["category"] == category]
    return df


# ═══════════════════════════════════════════════════════════
# SALES DASHBOARD WIDGET
# ═══════════════════════════════════════════════════════════


class SalesDashboard:
    """Sales dashboard with Plotly chart and interactive controls."""

    def __init__(self) -> None:
        self.region = "all"
        self.theme = "dark"
        self.widget: InlineWidget | None = None
        self.widget_id: str | None = None

    def create_figure(self) -> Figure:
        """Create Plotly figure with current state."""
        df = get_sales_data(self.region)
        template = "plotly_dark" if self.theme == "dark" else "plotly_white"
        fig = px.bar(
            df,
            x="year",
            y="revenue",
            color="region",
            barmode="group",
            template=template,
        )
        fig.update_layout(
            title=f"Sales Revenue - {self.region.title()}",
            xaxis_title="Year",
            yaxis_title="Revenue ($K)",
        )
        return fig

    def on_region_change(self, data: dict[str, Any], _event_type: str, _widget_id: str) -> None:
        """Handle region filter change."""
        self.region = data.get("value", "all")
        if self.widget:
            self.widget.update_figure(self.create_figure())

    def on_toggle_theme(self, _data: dict[str, Any], _event_type: str, _widget_id: str) -> None:
        """Toggle between dark and light theme."""
        self.theme = "light" if self.theme == "dark" else "dark"
        if self.widget:
            # Update chart with new theme
            self.widget.update_figure(self.create_figure())
            # Also update page theme
            self.widget.emit("pywry:update-theme", {"theme": self.theme})

    def on_export_csv(self, _data: dict[str, Any], _event_type: str, _widget_id: str) -> None:
        """Export current data to CSV via browser download."""
        df = get_sales_data(self.region)
        csv_data = df.to_csv(index=False)
        if self.widget:
            self.widget.emit(
                "pywry:download",
                {
                    "filename": f"sales_{self.region}.csv",
                    "content": csv_data,
                    "mimeType": "text/csv",
                },
            )

    def on_nav_inventory(self, _data: dict[str, Any], _event_type: str, _widget_id: str) -> None:
        """Navigate to inventory page."""
        if self.widget:
            self.widget.emit("pywry:navigate", {"url": "/inventory"})

    def on_nav_home(self, _data: dict[str, Any], _event_type: str, _widget_id: str) -> None:
        """Navigate to home page."""
        if self.widget:
            self.widget.emit("pywry:navigate", {"url": "/"})

    def create_widget(self) -> str:
        """Create the sales widget and return its ID."""
        nav_toolbar = Toolbar(
            position="top",
            items=[
                Button(
                    label="🏠",
                    event="nav:home",
                    description="Back to Home",
                    variant="ghost",
                ),
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
                    selected=self.region,
                ),
            ],
        )

        self.widget = cast(
            "InlineWidget",
            show_plotly(
                self.create_figure(),
                title="Sales Dashboard",
                toolbars=[nav_toolbar, filter_toolbar],
                callbacks={
                    "sales:region": self.on_region_change,
                    "sales:export": self.on_export_csv,
                    "sales:theme": self.on_toggle_theme,
                    "nav:inventory": self.on_nav_inventory,
                    "nav:home": self.on_nav_home,
                },
            ),
        )
        self.widget_id = self.widget.label
        return self.widget_id


# ═══════════════════════════════════════════════════════════
# INVENTORY MANAGER WIDGET
# ═══════════════════════════════════════════════════════════


class InventoryManager:
    """Inventory grid with filtering and bulk actions."""

    def __init__(self) -> None:
        self.category = "all"
        self.selected_skus: list[str] = []
        self.widget: InlineWidget | None = None
        self.widget_id: str | None = None

    def on_category_filter(self, data: dict[str, Any], _event_type: str, _widget_id: str) -> None:
        """Handle category filter change."""
        self.category = data.get("value", "all")
        df = get_inventory_data(self.category)
        if self.widget:
            self.widget.update_data(df.to_dict(orient="records"))

    def on_row_selected(self, data: dict[str, Any], _event_type: str, _widget_id: str) -> None:
        """Track selected rows."""
        self.selected_skus = [row.get("sku") for row in data.get("rows", [])]

    def on_restock(self, _data: dict[str, Any], _event_type: str, _widget_id: str) -> None:
        """Send restock notice for selected items."""
        if not self.selected_skus:
            if self.widget:
                self.widget.alert("Please select items to restock first.")
            return

        count = len(self.selected_skus)
        if self.widget:
            self.widget.alert(f"Restock notice sent for {count} item(s)!")

    def on_nav_sales(self, _data: dict[str, Any], _event_type: str, _widget_id: str) -> None:
        """Navigate to sales page."""
        if self.widget:
            self.widget.emit("pywry:navigate", {"url": "/sales"})

    def on_nav_home(self, _data: dict[str, Any], _event_type: str, _widget_id: str) -> None:
        """Navigate to home page."""
        if self.widget:
            self.widget.emit("pywry:navigate", {"url": "/"})

    def create_widget(self) -> str:
        """Create the inventory widget and return its ID."""
        nav_toolbar = Toolbar(
            position="top",
            items=[
                Button(
                    label="🏠",
                    event="nav:home",
                    description="Back to Home",
                    variant="ghost",
                ),
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

        self.widget = cast(
            "InlineWidget",
            show_dataframe(
                get_inventory_data(self.category),
                title="Inventory Manager",
                toolbars=[nav_toolbar, filter_toolbar],
                row_selection=True,
                callbacks={
                    "inv:category": self.on_category_filter,
                    "inv:restock": self.on_restock,
                    "grid:row-selected": self.on_row_selected,
                    "nav:sales": self.on_nav_sales,
                    "nav:home": self.on_nav_home,
                },
            ),
        )
        self.widget_id = self.widget.label
        return self.widget_id


# ═══════════════════════════════════════════════════════════
# HOME PAGE WIDGET
# ═══════════════════════════════════════════════════════════


class HomePage:
    """Home page with navigation cards."""

    def __init__(self) -> None:
        self.widget: InlineWidget | None = None
        self.widget_id: str | None = None

    def create_widget(self) -> str:
        """Create the home page widget and return its ID."""
        from pywry.state import get_state_backend, get_worker_id

        state_backend = get_state_backend().value.upper()
        worker_id = get_worker_id()

        # Build content HTML - cards are direct links, no toolbar needed
        content = f"""
        <style>
            .demo-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 80vh;
                padding: 2rem;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            }}
            .demo-title {{
                font-size: 3rem;
                margin-bottom: 0.5rem;
                background: linear-gradient(90deg, #00d4ff, #7b2cbf);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .demo-subtitle {{
                color: #888;
                margin-bottom: 1rem;
                font-size: 1.1rem;
            }}
            .demo-status-badge {{
                background: rgba(0, 212, 255, 0.2);
                color: #00d4ff;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.9rem;
                border: 1px solid rgba(0, 212, 255, 0.3);
                display: inline-block;
                margin-bottom: 2rem;
            }}
            .demo-cards-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                max-width: 900px;
                width: 100%;
            }}
            .demo-card {{
                display: block;
                text-decoration: none;
                color: inherit;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 2rem;
                transition: all 0.3s ease;
                cursor: pointer;
            }}
            .demo-card:hover {{
                background: rgba(255, 255, 255, 0.1);
                border-color: #00d4ff;
                transform: translateY(-4px);
                box-shadow: 0 10px 40px rgba(0, 212, 255, 0.2);
            }}
            .demo-card-icon {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
            .demo-card-title {{ font-size: 1.4rem; font-weight: 600; color: #fff; margin-bottom: 0.5rem; }}
            .demo-card-desc {{ color: #aaa; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1rem; }}
            .demo-card-features {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
            .demo-tag {{
                background: rgba(0, 212, 255, 0.15);
                color: #00d4ff;
                padding: 0.25rem 0.6rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 500;
            }}
            .demo-footer {{
                margin-top: 2rem;
                color: #666;
                font-size: 0.85rem;
                text-align: center;
            }}
            .demo-footer a {{ color: #00d4ff; text-decoration: none; }}
        </style>
        <div class="demo-container">
            <h1 class="demo-title">🚀 PyWry Deploy Mode</h1>
            <p class="demo-subtitle">Scalable data visualization with Python + FastAPI</p>
            <div class="demo-status-badge">
                State Backend: <strong>{state_backend}</strong> |
                Worker ID: <strong>{worker_id}</strong>
            </div>

            <div class="demo-cards-grid">
                <a href="/sales" class="demo-card">
                    <div class="demo-card-icon">📊</div>
                    <div class="demo-card-title">Sales Dashboard</div>
                    <div class="demo-card-desc">
                        Interactive Plotly bar chart with region filtering.
                        Toggle themes and export data to CSV.
                    </div>
                    <div class="demo-card-features">
                        <span class="demo-tag">Plotly</span>
                        <span class="demo-tag">Dropdown</span>
                        <span class="demo-tag">Theme Toggle</span>
                        <span class="demo-tag">CSV Export</span>
                    </div>
                </a>

                <a href="/inventory" class="demo-card">
                    <div class="demo-card-icon">📦</div>
                    <div class="demo-card-title">Inventory Manager</div>
                    <div class="demo-card-desc">
                        AG Grid data table with category filtering,
                        row selection, and bulk restock actions.
                    </div>
                    <div class="demo-card-features">
                        <span class="demo-tag">AG Grid</span>
                        <span class="demo-tag">Row Selection</span>
                        <span class="demo-tag">Filtering</span>
                        <span class="demo-tag">Bulk Actions</span>
                    </div>
                </a>
            </div>

            <p class="demo-footer">
                Built with <a href="https://github.com/OpenBB-finance/OpenBB">PyWry 2.0</a>
            </p>
        </div>
        """

        self.widget = show(
            content,
            title="PyWry Deploy Mode Demo",
            widget_id="home-page",
        )
        self.widget_id = self.widget.label
        return self.widget_id


# ═══════════════════════════════════════════════════════════
# WIDGET INSTANCES (created once at module load)
# ═══════════════════════════════════════════════════════════

home_page = HomePage()
sales_dashboard = SalesDashboard()
inventory_manager = InventoryManager()

# Create widgets - these will use the configured state backend
_home_widget_id = home_page.create_widget()
_sales_widget_id = sales_dashboard.create_widget()
_inventory_widget_id = inventory_manager.create_widget()


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════


@app.get("/")
async def index() -> HTMLResponse:
    """Landing page showing deploy mode status."""
    widget_id = home_page.widget_id
    if widget_id is None:
        return HTMLResponse("<h1>Error: No widget ID</h1>", status_code=500)
    html = await get_widget_html_async(widget_id)
    if not html:
        # Widget was lost (e.g., restart) - recreate it
        global _home_widget_id  # noqa: PLW0603
        _home_widget_id = home_page.create_widget()
        new_widget_id = home_page.widget_id
        if new_widget_id is not None:
            html = await get_widget_html_async(new_widget_id)

    if not html:
        return HTMLResponse("<h1>Error loading widget</h1>", status_code=500)
    return HTMLResponse(html)


@app.get("/sales", response_class=HTMLResponse)
async def sales_view() -> HTMLResponse:
    """Sales dashboard route."""
    widget_id = sales_dashboard.widget_id
    if widget_id is None:
        return HTMLResponse("<h1>Error: No widget ID</h1>", status_code=500)
    html = await get_widget_html_async(widget_id)
    if not html:
        # Widget was lost (e.g., restart) - recreate it
        global _sales_widget_id  # noqa: PLW0603
        _sales_widget_id = sales_dashboard.create_widget()
        new_widget_id = sales_dashboard.widget_id
        if new_widget_id is not None:
            html = await get_widget_html_async(new_widget_id)

    if not html:
        return HTMLResponse("<h1>Error loading widget</h1>", status_code=500)
    return HTMLResponse(html)


@app.get("/inventory", response_class=HTMLResponse)
async def inventory_view() -> HTMLResponse:
    """Inventory manager route."""
    widget_id = inventory_manager.widget_id
    if widget_id is None:
        return HTMLResponse("<h1>Error: No widget ID</h1>", status_code=500)
    html = await get_widget_html_async(widget_id)
    if not html:
        # Widget was lost (e.g., restart) - recreate it
        global _inventory_widget_id  # noqa: PLW0603
        _inventory_widget_id = inventory_manager.create_widget()
        new_widget_id = inventory_manager.widget_id
        if new_widget_id is not None:
            html = await get_widget_html_async(new_widget_id)

    if not html:
        return HTMLResponse("<h1>Error loading widget</h1>", status_code=500)
    return HTMLResponse(html)


if __name__ == "__main__":
    print("=" * 60)
    print("PyWry Deploy Mode Demo")
    print("=" * 60)

    from pywry.state import get_state_backend, get_worker_id, is_deploy_mode

    print(f"Deploy Mode: {is_deploy_mode()}")
    print(f"State Backend: {get_state_backend().value}")
    print(f"Worker ID: {get_worker_id()}")
    print()
    print("To enable Redis backend:")
    print("  PYWRY_DEPLOY__STATE_BACKEND=redis \\")
    print("  PYWRY_DEPLOY__REDIS_URL=redis://localhost:6379/0 \\")
    print("  python pywry_demo_deploy.py")
    print("=" * 60)

    deploy()
