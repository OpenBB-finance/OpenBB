"""Tests for the JODI router commands."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from openbb_jodi import gas_router, oil_router

COMMANDS = [
    (oil_router, oil_router.balance),
    (oil_router, oil_router.production),
    (oil_router, oil_router.demand),
    (oil_router, oil_router.demand_by_product),
    (oil_router, oil_router.imports),
    (oil_router, oil_router.exports),
    (oil_router, oil_router.stocks),
    (gas_router, gas_router.balance),
    (gas_router, gas_router.production),
    (gas_router, gas_router.demand),
    (gas_router, gas_router.imports),
    (gas_router, gas_router.exports),
    (gas_router, gas_router.stocks),
]


@pytest.mark.parametrize("module, command", COMMANDS)
def test_model_backed_commands(module, command):
    """Each command delegates to OBBject.from_query(OpenBBQuery(...))."""
    sentinel = object()

    with (
        patch.object(module, "OBBject") as mock_obbject,
        patch.object(module, "OpenBBQuery") as mock_query,
    ):
        mock_obbject.from_query = AsyncMock(return_value=sentinel)

        result = asyncio.run(
            command(
                cc=None,
                provider_choices=None,
                standard_params=None,
                extra_params=None,
            )
        )

    assert result is sentinel
    assert mock_query.called
    mock_obbject.from_query.assert_awaited_once()


WIDGET_IDS = {
    "jodi_oil_balance_jodi_obb",
    "jodi_oil_production_jodi_obb",
    "jodi_oil_demand_jodi_obb",
    "jodi_oil_demand_by_product_jodi_obb",
    "jodi_oil_imports_jodi_obb",
    "jodi_oil_exports_jodi_obb",
    "jodi_oil_stocks_jodi_obb",
    "jodi_gas_balance_jodi_obb",
    "jodi_gas_production_jodi_obb",
    "jodi_gas_demand_jodi_obb",
    "jodi_gas_imports_jodi_obb",
    "jodi_gas_exports_jodi_obb",
    "jodi_gas_stocks_jodi_obb",
}


def test_apps_json():
    """The served app template is a valid Workspace apps.json fragment."""
    from openbb_jodi.jodi_router import jodi_apps

    apps = asyncio.run(jodi_apps())
    assert isinstance(apps, list)
    for app in apps:
        assert app["name"]
        assert app["description"]
        assert app["img"]
        assert isinstance(app["allowCustomization"], bool)
        assert isinstance(app["groups"], list)
        assert isinstance(app["prompts"], list)
        laid_out: set[str] = set()
        for tab_id, tab in app["tabs"].items():
            assert tab["id"] == tab_id
            assert "name" in tab
            occupied: set[tuple[int, int]] = set()
            for item in tab["layout"]:
                assert item["i"] in WIDGET_IDS
                laid_out.add(item["i"])
                assert item["x"] >= 0 and item["x"] + item["w"] <= 40
                assert item["y"] >= 0 and item["h"] >= 4
                cells = {
                    (col, row)
                    for col in range(item["x"], item["x"] + item["w"])
                    for row in range(item["y"], item["y"] + item["h"])
                }
                assert not cells & occupied, f"widgets overlap in tab {tab_id}"
                occupied |= cells
        assert laid_out == WIDGET_IDS  # every view is on a dashboard
        for group in app["groups"]:
            assert group["name"].startswith("Group ")
            assert group["type"] in {"param", "endpointParam", "ticker"}
            for widget_id in group["widgetIds"]:
                assert widget_id in laid_out
                item = next(
                    item
                    for tab in app["tabs"].values()
                    for item in tab["layout"]
                    if item["i"] == widget_id
                )
                assert group["name"] in item.get("groups", [])


def test_router_lifespan(monkeypatch):
    """The router lifespan starts the cache prefetch at application startup."""
    from fastapi import FastAPI

    from openbb_jodi.jodi_router import router
    from openbb_jodi.utils import helpers

    prefetches: list[bool] = []
    monkeypatch.setattr(helpers, "start_prefetch", lambda: prefetches.append(True))
    app = FastAPI()
    # include_router merges the jodi lifespan into the application lifespan.
    app.include_router(router.api_router)

    async def startup():
        async with app.router.lifespan_context(app):
            assert prefetches == [True]

    asyncio.run(startup())


def test_router_paths():
    """Each view is mounted under its oil or gas sub-router."""
    from openbb_jodi.jodi_router import router

    # The oil and gas sub-routers, plus the apps.json route.
    assert len(router.api_router.routes) == 3
    paths = {
        route.path
        for sub_router in (oil_router.router, gas_router.router)
        for route in sub_router.api_router.routes
    }
    assert paths == {
        "/oil/balance",
        "/oil/production",
        "/oil/demand",
        "/oil/demand_by_product",
        "/oil/imports",
        "/oil/exports",
        "/oil/stocks",
        "/gas/balance",
        "/gas/production",
        "/gas/demand",
        "/gas/imports",
        "/gas/exports",
        "/gas/stocks",
    }
