"""Test the FRED router, what it reaches and the widget ids it publishes."""

import pytest

from openbb_fred import ECONOMY_INSTALLED

economy_owned = pytest.mark.skipif(
    ECONOMY_INSTALLED,
    reason="openbb_economy owns the economy and survey commands when it is importable,"
    " so the FRED router neither routes them nor publishes their widgets",
)


class TestRouter:
    """The standalone router and the template it serves."""

    @economy_owned
    def test_every_fetcher_is_reachable(self):
        """A registered model with no command is unreachable."""
        from openbb_fred import fred_provider
        from openbb_fred.fred_router import router

        routed = {
            route.openapi_extra.get("model")
            for route in router.api_router.routes
            if getattr(route, "openapi_extra", None)
        }

        assert set(fred_provider.fetcher_dict) - routed == set()

    def test_the_template_is_served(self):
        from openbb_core.provider.utils.helpers import run_async

        from openbb_fred.fred_router import fred_apps

        apps = run_async(fred_apps)

        assert apps[0]["name"] == "FRED"
        assert list(apps[0]["tabs"]) == ["Search", "ReleaseTables", "InterestRates"]

    def test_a_widget_moves_with_the_router_that_serves_it(self, monkeypatch):
        """The id carries the namespace prefix of whichever router owns it."""
        from openbb_fred import fred_router

        monkeypatch.setattr(
            fred_router, "OWNERS", {"economy_": False, "fixedincome_": False}
        )

        assert fred_router.widget_id("economy_cpi_fred_obb") == (
            "fred_economy_cpi_fred_obb"
        )

        monkeypatch.setattr(
            fred_router, "OWNERS", {"economy_": True, "fixedincome_": True}
        )

        assert fred_router.widget_id("economy_cpi_fred_obb") == "economy_cpi_fred_obb"

    def test_an_unowned_widget_is_left_alone(self):
        from openbb_fred.fred_router import widget_id

        assert widget_id("custom_thing_fred_obb") == "custom_thing_fred_obb"

    @economy_owned
    def test_every_referenced_widget_is_published(self):
        from openbb_core.api.rest_api import app
        from openbb_core.provider.utils.helpers import run_async
        from openbb_platform_api.utils.widgets import build_json

        from openbb_fred.fred_router import fred_apps

        registry = set(build_json(app.openapi(), []))
        template = run_async(fred_apps)[0]
        referenced = {
            cell["i"] for tab in template["tabs"].values() for cell in tab["layout"]
        }

        assert referenced
        assert referenced - registry == set()
