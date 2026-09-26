"""Tests for the FINRA router and its dashboard template."""

import asyncio
from importlib import reload
from unittest.mock import patch

import openbb_finra
from openbb_finra import finra_router
from openbb_finra.routers import equity, fixedincome

STANDALONE_PATHS = {
    "/equity/securities",
    "/equity/search",
    "/equity/profile",
    "/equity/darkpool/otc",
    "/equity/shorts/short_interest",
    "/fixedincome/bond_prices",
    "/fixedincome/bond_historical",
    "/fixedincome/bonds",
    "/apps.json",
}


def _paths(router) -> set:
    """Return the paths a router serves."""
    from openbb_core.app.route_iter import iter_api_routes

    return {route.path for route in iter_api_routes(router.api_router)}


def _reload_with(installed: set):
    """Reload the package and its routers with a controlled install."""
    with patch(
        "importlib.util.find_spec",
        side_effect=lambda name: object() if name in installed else None,
    ):
        reload(openbb_finra)
        reload(equity)
        reload(fixedincome)

        return reload(finra_router)


def _restore():
    """Reload the package and its routers against the real install."""
    reload(openbb_finra)
    reload(equity)
    reload(fixedincome)
    reload(finra_router)


class TestRouterAssembly:
    """The router serves the standard commands only when their owner is absent."""

    def test_standalone(self):
        """Without the owners every command is served under /finra."""
        module = _reload_with(set())

        try:
            assert _paths(module.router) == STANDALONE_PATHS
        finally:
            _restore()

    def test_owners_installed(self):
        """With the owners installed only the FINRA-only commands remain."""
        module = _reload_with({"openbb_equity", "openbb_fixedincome"})

        try:
            assert _paths(module.router) == {
                "/equity/securities",
                "/fixedincome/bond_historical",
                "/fixedincome/bonds",
                "/apps.json",
            }
        finally:
            _restore()


class TestApps:
    """The dashboard template resolves its widget ids against the install."""

    def test_standalone_ids(self):
        """Standard ids are swapped for the /finra ids when the owners are absent."""
        module = _reload_with(set())

        try:
            apps = asyncio.run(module.finra_apps())
        finally:
            _restore()

        layout = [
            widget["i"] for tab in apps[0]["tabs"].values() for widget in tab["layout"]
        ]

        assert "finra_equity_profile_finra_obb" in layout
        assert "finra_fixedincome_bond_prices_finra_obb" in layout
        assert "finra_fixedincome_bond_historical_finra_obb" in layout
        assert all(widget.startswith("finra_") for widget in layout)
        assert apps[0]["groups"][0]["widgetIds"] == [
            "finra_equity_profile_finra_obb",
            "finra_equity_shorts_short_interest_finra_obb",
            "finra_equity_darkpool_otc_finra_obb",
        ]

    def test_installed_ids(self):
        """Standard ids are kept when the owners are installed."""
        module = _reload_with({"openbb_equity", "openbb_fixedincome"})

        try:
            apps = asyncio.run(module.finra_apps())
        finally:
            _restore()

        layout = [
            widget["i"] for tab in apps[0]["tabs"].values() for widget in tab["layout"]
        ]

        assert "equity_profile_finra_obb" in layout
        assert "fixedincome_corporate_bond_prices_finra_obb" in layout

    def test_unknown_ids_are_kept(self):
        """An id outside the standalone map is returned unchanged."""
        assert finra_router._resolve_widget_id("custom_widget") == "custom_widget"

    def test_app_without_groups(self, tmp_path, monkeypatch):
        """Apps without tabs or groups are served as they are."""
        template = tmp_path / "apps.json"
        template.write_text('[{"name": "Empty", "groups": [{"name": "g"}]}]')
        monkeypatch.setattr(finra_router, "_APPS_JSON", template)

        assert asyncio.run(finra_router.finra_apps()) == [
            {"name": "Empty", "groups": [{"name": "g", "widgetIds": []}]}
        ]
