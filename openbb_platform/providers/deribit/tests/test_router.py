"""Tests for the Deribit router and its bundled dashboard."""

import asyncio
import json
from importlib import reload
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

import openbb_deribit
from openbb_deribit import deribit_router
from openbb_deribit.routers import (
    futures,
    index,
    market,
    options,
    rates,
    reference,
    volatility,
)

APPS_JSON = Path(openbb_deribit.__file__).parent / "assets" / "apps.json"

SUBROUTERS = {
    "reference",
    "market",
    "index",
    "rates",
    "volatility",
    "futures",
    "options",
}


def _paths(router):
    """Return every route the router and its sub-routers register."""
    found = set()

    for sub in router.routers.values():
        for route in sub.api_router.routes:
            found.add(route.path)

    return found


def _widget_ids(router):
    """Return the widget identifier of every registered route.

    A command backed by a provider model is published under the provider's
    name; one that computes its own answer is published as a custom widget.
    """
    found = set()

    for sub in router.routers.values():
        for route in sub.api_router.routes:
            extra = getattr(route, "openapi_extra", None) or {}
            suffix = "deribit" if extra.get("model") else "custom"
            found.add(f"deribit{route.path}".replace("/", "_") + f"_{suffix}_obb")

    return found


MODEL_COMMANDS = [
    reference.currencies,
    reference.instruments,
    reference.expirations,
    reference.combos,
    reference.announcements,
    market.book_summary,
    market.order_book,
    market.ticker,
    market.trades,
    market.trade_volumes,
    market.block_rfq_trades,
    market.settlements,
    index.price,
    index.historical,
    index.delivery_prices,
    rates.funding_history,
    rates.funding_chart,
    rates.apr_history,
    volatility.realized,
    volatility.index,
    futures.curve,
    futures.historical,
    futures.info,
    futures.instruments,
    options.chains,
]


class TestModelCommands:
    """Model-backed commands hand off to the query pipeline."""

    @pytest.mark.parametrize("command", MODEL_COMMANDS)
    def test_delegates_to_from_query(self, command):
        """Each command hands off to ``OBBject.from_query``."""
        module = __import__(command.__module__, fromlist=["OBBject"])
        sentinel = object()

        with (
            patch.object(module, "OBBject") as mock_obbject,
            patch.object(module, "OBBQuery") as mock_query,
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


class TestAssembly:
    """The router gathers every sub-router under the provider prefix."""

    def test_subrouters(self):
        """Each sub-router is mounted once, under its own prefix."""
        assert set(deribit_router.router.routers) == SUBROUTERS

    def test_every_model_is_reachable(self):
        """Every Deribit-only model has a route."""
        paths = _paths(deribit_router.router)

        assert "/reference/currencies" in paths
        assert "/market/order_book" in paths
        assert "/index/delivery_prices" in paths
        assert "/rates/apr_history" in paths
        assert "/volatility/index" in paths

    def test_choice_feeds_are_hidden(self):
        """A choice feed is served but kept out of the widget listing."""
        for router, name in (
            (reference.router, "currency_choices"),
            (futures.router, "curve_choices"),
            (options.router, "underlying_choices"),
        ):
            route = next(r for r in router.api_router.routes if r.path.endswith(name))

            assert route.openapi_extra["widget_config"]["exclude"] is True


class TestStandaloneRegistration:
    """The shared commands are served only when nothing else owns them."""

    def test_served_without_derivatives(self):
        """With no derivatives extension, the shared commands are ours."""
        paths = _paths(deribit_router.router)

        assert openbb_deribit.DERIVATIVES_INSTALLED is False
        assert {"/futures/curve", "/options/chains"} <= paths

    def test_withheld_when_derivatives_is_installed(self):
        """With the derivatives extension, the shared commands are not ours."""
        with patch(
            "importlib.util.find_spec",
            side_effect=lambda name: object() if name == "openbb_derivatives" else None,
        ):
            reload(openbb_deribit)
            reloaded = reload(futures)

        try:
            paths = {route.path for route in reloaded.router.api_router.routes}

            assert "/futures/curve" not in paths
            assert "/futures/curve_choices" in paths
        finally:
            reload(openbb_deribit)
            reload(futures)
            reload(options)
            reload(rates)
            reload(reference)
            reload(deribit_router)


class TestWidgetIds:
    """The dashboard names widgets the install actually serves."""

    def test_mapping_targets_exist(self):
        """Every remapped identifier resolves to a route we serve."""
        served = _widget_ids(deribit_router.router)

        for standalone, _ in deribit_router._STANDALONE_WIDGET_IDS.values():
            assert standalone in served

    def test_resolve_passes_unknown_ids_through(self):
        """An identifier the mapping does not know is left alone."""
        assert deribit_router._resolve_widget_id("something_else") == ("something_else")

    def test_resolve_swaps_when_the_owner_is_missing(self):
        """A shared identifier is swapped for ours when nothing owns it."""
        assert (
            deribit_router._resolve_widget_id("derivatives_futures_curve_deribit_obb")
            == "deribit_futures_curve_deribit_obb"
        )

    def test_resolve_keeps_the_shared_id_when_the_owner_is_present(self, monkeypatch):
        """A shared identifier stays put when its extension is installed."""
        monkeypatch.setitem(
            deribit_router._STANDALONE_WIDGET_IDS,
            "derivatives_futures_curve_deribit_obb",
            ("deribit_futures_curve_deribit_obb", True),
        )

        assert (
            deribit_router._resolve_widget_id("derivatives_futures_curve_deribit_obb")
            == "derivatives_futures_curve_deribit_obb"
        )


class TestApps:
    """The bundled dashboard is served with its identifiers resolved."""

    @pytest.mark.asyncio
    async def test_served_ids_resolve(self):
        """Every widget the dashboard names is one this install serves."""
        served = _widget_ids(deribit_router.router)
        apps = await deribit_router.deribit_apps()

        for app in apps:
            for tab in app["tabs"].values():
                for widget in tab["layout"]:
                    assert widget["i"] in served

    @pytest.mark.asyncio
    async def test_tabs(self):
        """The dashboard covers each area of the surface."""
        apps = await deribit_router.deribit_apps()

        assert set(apps[0]["tabs"]) == {
            "markets",
            "futures",
            "options",
            "analysis",
            "volatility",
            "reference",
        }

    @pytest.mark.asyncio
    async def test_the_file_is_not_rewritten(self):
        """Resolving the identifiers does not touch what is on disk."""
        before = APPS_JSON.read_text(encoding="utf-8")
        await deribit_router.deribit_apps()

        assert APPS_JSON.read_text(encoding="utf-8") == before

    def test_layout_is_well_formed(self):
        """Every widget names a position and a size within the grid."""
        apps = json.loads(APPS_JSON.read_text(encoding="utf-8"))

        for app in apps:
            for tab in app["tabs"].values():
                for widget in tab["layout"]:
                    assert set(widget) >= {"i", "x", "y", "w", "h"}
                    assert widget["x"] + widget["w"] <= 40
                    assert widget["h"] > 0
