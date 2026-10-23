"""FINRA Router."""

import json
from pathlib import Path

from openbb_core.app.router import Router

from openbb_finra import EQUITY_INSTALLED, FIXEDINCOME_INSTALLED
from openbb_finra.routers.equity import router as equity_router
from openbb_finra.routers.fixedincome import router as fixedincome_router

router = Router(prefix="", description="FINRA provider router.")
router.include_router(equity_router)
router.include_router(fixedincome_router)

_APPS_JSON = Path(__file__).parent / "assets" / "apps.json"

_STANDALONE_WIDGET_IDS: dict[str, tuple[str, bool]] = {
    "equity_search_finra_obb": ("finra_equity_search_finra_obb", EQUITY_INSTALLED),
    "equity_profile_finra_obb": ("finra_equity_profile_finra_obb", EQUITY_INSTALLED),
    "equity_darkpool_otc_finra_obb": (
        "finra_equity_darkpool_otc_finra_obb",
        EQUITY_INSTALLED,
    ),
    "equity_shorts_short_interest_finra_obb": (
        "finra_equity_shorts_short_interest_finra_obb",
        EQUITY_INSTALLED,
    ),
    "fixedincome_corporate_bond_prices_finra_obb": (
        "finra_fixedincome_bond_prices_finra_obb",
        FIXEDINCOME_INSTALLED,
    ),
}


def _resolve_widget_id(widget_id: str) -> str:
    """Return the widget ID that resolves against the active install."""
    standalone, installed = _STANDALONE_WIDGET_IDS.get(widget_id, (widget_id, True))

    return widget_id if installed else standalone


@router.api_router.get("/apps.json", include_in_schema=False)
async def finra_apps() -> list:
    """Serve the bundled FINRA dashboard template."""
    apps = json.loads(_APPS_JSON.read_text(encoding="utf-8"))

    for app in apps:
        for tab in app.get("tabs", {}).values():
            for widget in tab.get("layout", []):
                widget["i"] = _resolve_widget_id(widget["i"])

        for group in app.get("groups", []):
            group["widgetIds"] = [
                _resolve_widget_id(widget_id)
                for widget_id in group.get("widgetIds", [])
            ]

    return apps
