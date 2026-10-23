"""Deribit Router."""

import json
from pathlib import Path

from openbb_core.app.router import Router

from openbb_deribit import DERIVATIVES_INSTALLED
from openbb_deribit.routers.futures import router as futures_router
from openbb_deribit.routers.index import router as index_router
from openbb_deribit.routers.market import router as market_router
from openbb_deribit.routers.options import router as options_router
from openbb_deribit.routers.rates import router as rates_router
from openbb_deribit.routers.reference import router as reference_router
from openbb_deribit.routers.volatility import router as volatility_router

router = Router(prefix="", description="Deribit provider router.")

for _subrouter in (
    reference_router,
    market_router,
    index_router,
    rates_router,
    volatility_router,
    futures_router,
    options_router,
):
    router.include_router(_subrouter)

_APPS_JSON = Path(__file__).parent / "assets" / "apps.json"

_STANDALONE_WIDGET_IDS: dict[str, tuple[str, bool]] = {
    "derivatives_futures_curve_deribit_obb": (
        "deribit_futures_curve_deribit_obb",
        DERIVATIVES_INSTALLED,
    ),
    "derivatives_futures_historical_deribit_obb": (
        "deribit_futures_historical_deribit_obb",
        DERIVATIVES_INSTALLED,
    ),
    "derivatives_futures_info_deribit_obb": (
        "deribit_futures_info_deribit_obb",
        DERIVATIVES_INSTALLED,
    ),
    "derivatives_futures_instruments_deribit_obb": (
        "deribit_futures_instruments_deribit_obb",
        DERIVATIVES_INSTALLED,
    ),
    "derivatives_options_chains_deribit_obb": (
        "deribit_options_chains_deribit_obb",
        DERIVATIVES_INSTALLED,
    ),
}


def _resolve_widget_id(widget_id: str) -> str:
    """Return the widget ID that resolves against the active install."""
    standalone, installed = _STANDALONE_WIDGET_IDS.get(widget_id, (widget_id, True))

    return widget_id if installed else standalone


@router.api_router.get("/apps.json", include_in_schema=False)
async def deribit_apps() -> list:
    """Serve the bundled Deribit dashboard template (``assets/apps.json``).

    A parameter group names the widgets it binds, so its identifiers are
    resolved against the active install the same way the layout's are.
    """
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
