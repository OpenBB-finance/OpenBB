"""Cboe Router."""

import json
from pathlib import Path

from openbb_core.app.router import Router

from openbb_cboe import (
    DERIVATIVES_INSTALLED,
    EQUITY_INSTALLED,
    INDEX_INSTALLED,
)
from openbb_cboe.routers.equity import router as equity_router
from openbb_cboe.routers.futures import router as futures_router
from openbb_cboe.routers.index import router as index_router
from openbb_cboe.routers.options import router as options_router

router = Router(prefix="", description="Cboe provider router.")

for _subrouter in (equity_router, index_router, options_router, futures_router):
    router.include_router(_subrouter)

_APPS_JSON = Path(__file__).parent / "assets" / "apps.json"

_STANDALONE_WIDGET_IDS: dict[str, tuple[str, bool]] = {
    "index_available_cboe_obb": ("cboe_index_available_cboe_obb", INDEX_INSTALLED),
    "index_search_cboe_obb": ("cboe_index_search_cboe_obb", INDEX_INSTALLED),
    "index_snapshots_cboe_obb": ("cboe_index_snapshots_cboe_obb", INDEX_INSTALLED),
    "index_constituents_cboe_obb": (
        "cboe_index_constituents_cboe_obb",
        INDEX_INSTALLED,
    ),
    "index_price_historical_cboe_obb": (
        "cboe_index_historical_cboe_obb",
        INDEX_INSTALLED,
    ),
    "equity_search_cboe_obb": ("cboe_equity_search_cboe_obb", EQUITY_INSTALLED),
    "equity_price_quote_cboe_obb": ("cboe_equity_quote_cboe_obb", EQUITY_INSTALLED),
    "equity_price_historical_cboe_obb": (
        "cboe_equity_historical_cboe_obb",
        EQUITY_INSTALLED,
    ),
    "derivatives_options_chains_cboe_obb": (
        "cboe_options_chains_cboe_obb",
        DERIVATIVES_INSTALLED,
    ),
}


def _resolve_widget_id(widget_id: str) -> str:
    """Return the widget ID that resolves against the active install."""
    standalone, installed = _STANDALONE_WIDGET_IDS.get(widget_id, (widget_id, True))

    return widget_id if installed else standalone


@router.api_router.get("/apps.json", include_in_schema=False)
async def cboe_apps() -> list:
    """Serve the bundled Cboe dashboard template (``assets/apps.json``)."""
    apps = json.loads(_APPS_JSON.read_text(encoding="utf-8"))

    for app in apps:
        for tab in app.get("tabs", {}).values():
            for widget in tab.get("layout", []):
                widget["i"] = _resolve_widget_id(widget["i"])

    return apps
