"""Tests for the TMX routers and their registration."""

import pytest

from openbb_tmx.tmx_router import router as tmx_router


class TestRouterAssembly:
    """The assembled router surface."""

    def test_router_has_routes(self):
        assert len(tmx_router.api_router.routes) > 30

    def test_apps_json_is_served(self):
        paths = {getattr(r, "path", "") for r in tmx_router.api_router.routes}
        assert "/apps.json" in paths

    @pytest.mark.parametrize(
        "path",
        [
            "/equity/search",
            "/equity/quote",
            "/equity/profile",
            "/equity/historical",
            "/equity/screener",
            "/equity/filings",
            "/equity/gainers",
            "/equity/fundamental/income",
            "/equity/fundamental/balance",
            "/equity/fundamental/cash",
            "/equity/fundamental/dividends",
            "/equity/fundamental/splits",
            "/equity/calendar/earnings",
            "/equity/ownership/insider_trading",
            "/equity/estimates/consensus",
            "/etf/search",
            "/etf/info",
            "/etf/holdings",
            "/etf/sectors",
            "/etf/countries",
            "/etf/historical",
            "/index/available",
            "/index/constituents",
            "/index/sectors",
            "/index/snapshots",
            "/derivatives/options/chains",
            "/derivatives/options/covered_calls",
            "/derivatives/futures/instruments",
            "/derivatives/futures/historical",
            "/currency/historical",
            "/fixedincome/prices",
            "/fixedincome/trades",
            "/fixedincome/treasury_prices",
            "/markets/movers",
            "/markets/trades",
            "/markets/short_interest",
            "/derivatives/options/stats",
            "/derivatives/options/smile",
            "/derivatives/options/surface",
            "/derivatives/options/term_structure",
            "/derivatives/options/straddle",
            "/derivatives/options/strangle",
            "/derivatives/options/spreads",
            "/udf/config",
            "/udf/search",
            "/udf/symbols",
            "/udf/history",
            "/udf/time",
        ],
    )
    def test_route_is_registered(self, path):
        paths = {getattr(r, "path", "") for r in tmx_router.api_router.routes}
        assert path in paths

    async def test_apps_json_resolves(self):
        from openbb_tmx.tmx_router import tmx_apps

        apps = await tmx_apps()
        assert apps
        assert apps[0]["tabs"]


class TestAppsTemplate:
    """The bundled dashboard."""

    def test_a_group_only_binds_a_parameter(self):
        """Click grouping is declared on the column, never on the group."""
        import json
        from pathlib import Path

        import openbb_tmx

        apps = json.loads(
            (Path(openbb_tmx.__file__).parent / "assets" / "apps.json").read_text()
        )

        for app in apps:
            for group in app["groups"]:
                assert set(group) == {
                    "name",
                    "type",
                    "paramName",
                    "defaultValue",
                    "widgetIds",
                }

    def test_every_layout_widget_is_unique_per_tab(self):
        import json
        from pathlib import Path

        import openbb_tmx

        apps = json.loads(
            (Path(openbb_tmx.__file__).parent / "assets" / "apps.json").read_text()
        )

        for app in apps:
            for tab in app["tabs"].values():
                ids = [w["i"] for w in tab["layout"]]
                assert len(ids) == len(set(ids))
