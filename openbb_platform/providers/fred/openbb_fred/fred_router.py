"""FRED Router."""

import json
from pathlib import Path

from openbb_core.app.router import Router

from openbb_fred import (
    COMMODITY_INSTALLED,
    ECONOMY_INSTALLED,
    FIXEDINCOME_INSTALLED,
)
from openbb_fred.routers.commodity import router as commodity_router
from openbb_fred.routers.corporate import router as corporate_router
from openbb_fred.routers.economy import router as economy_router
from openbb_fred.routers.fixedincome import router as fixedincome_router
from openbb_fred.routers.government import router as government_router
from openbb_fred.routers.rate import router as rate_router
from openbb_fred.routers.spreads import router as spreads_router
from openbb_fred.routers.survey import router as survey_router

router = Router(prefix="", description="FRED provider router.")

for sub_router in (
    commodity_router,
    corporate_router,
    economy_router,
    fixedincome_router,
    government_router,
    rate_router,
    spreads_router,
    survey_router,
):
    router.include_router(sub_router)

_APPS_JSON = Path(__file__).parent / "assets" / "apps.json"

OWNERS = {
    "commodity_": COMMODITY_INSTALLED,
    "economy_": ECONOMY_INSTALLED,
    "fixedincome_": FIXEDINCOME_INSTALLED,
}


def widget_id(declared: str) -> str:
    """Return the id a widget carries in this installation.

    Parameters
    ----------
    declared : str
        The widget id as written in the packaged template.

    Returns
    -------
    str
        The id the API actually publishes.
    """
    for namespace, installed in OWNERS.items():
        if declared.startswith(namespace) and not installed:
            return f"fred_{declared}"

    return declared


def _remap(apps: list) -> list:
    """Rewrite every widget reference in the template to its served id."""
    for app in apps:
        for group in app.get("groups") or []:
            group["widgetIds"] = [widget_id(w) for w in group.get("widgetIds") or []]

        for tab in (app.get("tabs") or {}).values():
            for cell in tab.get("layout") or []:
                cell["i"] = widget_id(cell["i"])

    return apps


@router.api_router.get("/apps.json", include_in_schema=False)
async def fred_apps() -> list:
    """Serve the bundled FRED dashboard template."""
    return _remap(json.loads(_APPS_JSON.read_text(encoding="utf-8")))
