"""Tests for the Nasdaq router assembly and its non-model endpoints."""

import asyncio
import json
from datetime import datetime
from unittest.mock import patch

import pytest

from openbb_nasdaq import nasdaq_router
from openbb_nasdaq.routers import equity, etf, index, markets, nordic


class TestRouterAssembly:
    """Cover the sub-router assembly."""

    def test_every_namespace_is_mounted(self):
        """Each sub-router contributes its namespace."""
        paths = {route.path for route in nasdaq_router.router.api_router.routes}
        prefixes = {path.split("/")[1] for path in paths if path.count("/") > 1}

        assert {
            "equity",
            "etf",
            "index",
            "markets",
            "nordic",
            "options",
        } <= prefixes

    def test_apps_json_is_served(self):
        """The dashboard template is exposed on the router."""
        assert "/apps.json" in {
            route.path for route in nasdaq_router.router.api_router.routes
        }

    def test_no_duplicate_routes(self):
        """No path is registered twice."""
        paths = [route.path for route in nasdaq_router.router.api_router.routes]

        assert len(paths) == len(set(paths))


class TestWidgetIdResolution:
    """Cover the standalone widget-ID swap."""

    def test_absent_extension_swaps_the_id(self):
        """A namespace served by Nasdaq alone uses the standalone ID."""
        with patch.dict(
            nasdaq_router._STANDALONE_WIDGET_IDS,
            {"etf_holdings_nasdaq_obb": ("nasdaq_etf_holdings_nasdaq_obb", False)},
        ):
            assert (
                nasdaq_router._resolve_widget_id("etf_holdings_nasdaq_obb")
                == "nasdaq_etf_holdings_nasdaq_obb"
            )

    def test_installed_extension_keeps_the_id(self):
        """An installed namespace keeps its standard widget ID."""
        with patch.dict(
            nasdaq_router._STANDALONE_WIDGET_IDS,
            {"etf_holdings_nasdaq_obb": ("nasdaq_etf_holdings_nasdaq_obb", True)},
        ):
            assert (
                nasdaq_router._resolve_widget_id("etf_holdings_nasdaq_obb")
                == "etf_holdings_nasdaq_obb"
            )

    def test_unknown_id_passes_through(self):
        """An ID outside the map is returned unchanged."""
        assert nasdaq_router._resolve_widget_id("something_else") == "something_else"


class TestAppsJson:
    """Cover the served dashboard template."""

    @pytest.fixture(scope="class")
    def apps(self):
        """The resolved apps.json payload."""
        return asyncio.run(nasdaq_router.nasdaq_apps())

    def test_is_a_list_of_apps(self, apps):
        """The template is a list carrying at least one app."""
        assert isinstance(apps, list)
        assert apps[0]["name"] == "Nasdaq Market Data"

    def test_every_tab_has_a_layout(self, apps):
        """No tab is served empty."""
        for name, tab in apps[0]["tabs"].items():
            assert tab["layout"], name

    def test_widget_ids_are_resolved(self, apps):
        """Stored IDs are swapped for the ones the install exposes."""
        stored = json.loads(nasdaq_router._APPS_JSON.read_text(encoding="utf-8"))
        served = {w["i"] for tab in apps[0]["tabs"].values() for w in tab["layout"]}
        raw = {w["i"] for tab in stored[0]["tabs"].values() for w in tab["layout"]}

        assert served == {nasdaq_router._resolve_widget_id(i) for i in raw}

    def test_group_ids_are_resolved(self, apps):
        """Group membership is resolved alongside the layouts."""
        for group in apps[0]["groups"]:
            for widget_id in group["widgetIds"]:
                assert widget_id == nasdaq_router._resolve_widget_id(widget_id)

    def test_groups_carry_a_param(self, apps):
        """Every group binds a real parameter across a non-empty widget set."""
        for group in apps[0]["groups"]:
            assert group["paramName"]
            assert group["widgetIds"]


class TestEquityEndpoints:
    """Cover the non-model equity endpoints."""

    def test_symbol_choices(self, monkeypatch):
        """The picker delegates to the directory helper."""

        async def _choices():
            return [{"label": "AAPL", "value": "AAPL"}]

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_symbol_choices", _choices)

        assert asyncio.run(equity.symbol_choices()) == [
            {"label": "AAPL", "value": "AAPL"}
        ]

    def test_document_choices(self, monkeypatch):
        """The filing picker passes its filters through."""
        seen: list[tuple] = []

        async def _choices(symbol, year, form_group):
            seen.append((symbol, year, form_group))

            return []

        monkeypatch.setattr(
            "openbb_nasdaq.utils.helpers.get_document_choices", _choices
        )
        asyncio.run(equity.document_choices("AAPL", 2026, "annual"))

        assert seen == [("AAPL", 2026, "annual")]

    def test_filing_years(self):
        """The year picker runs from the current year back to 1994."""
        years = asyncio.run(equity.filing_years())

        assert years[0]["value"] == datetime.now().year
        assert years[-1]["value"] == 1994

    def test_filings_viewer_opens_each_document(self, monkeypatch):
        """Only fully-qualified URLs are opened."""
        opened: list[str] = []

        async def _open(url):
            opened.append(url)

            return {"content": "QUJD"}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.open_filing_document", _open)
        documents = asyncio.run(
            equity.filings_viewer(
                {"document_url": ["https://x/a.pdf", "not-a-url", 42]}
            )
        )

        assert opened == ["https://x/a.pdf"]
        assert len(documents) == 1

    def test_filings_viewer_without_a_selection(self):
        """No selection yields no documents."""
        assert asyncio.run(equity.filings_viewer({})) == []

    def test_filings_viewer_skips_empty_documents(self, monkeypatch):
        """A document that opens empty is not returned."""

        async def _open(url):
            return {}

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.open_filing_document", _open)

        assert (
            asyncio.run(equity.filings_viewer({"document_url": ["https://x/a.pdf"]}))
            == []
        )


class TestMarketsEndpoints:
    """Cover the non-model markets endpoints."""

    def test_upcoming_summarizes_each_block(self, monkeypatch):
        """Each calendar block becomes a count with a preview."""

        async def _data(path, **kwargs):
            assert path == "calendar/upcoming?date=2026-07-27"

            return [
                {
                    "name": "Earnings",
                    "eventCount": 71,
                    "earningsList": [{"companyName": "AstraZeneca PLC"}],
                },
                {"name": "IPOs", "eventCount": 0, "iposList": []},
            ]

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        rows = asyncio.run(markets.upcoming("2026-07-27"))

        assert rows[0] == {
            "event": "Earnings",
            "count": 71,
            "preview": [{"companyName": "AstraZeneca PLC"}],
        }
        assert rows[1]["preview"] == []

    def test_upcoming_without_a_date(self, monkeypatch):
        """Omitting the date requests the default window."""
        seen: list[str] = []

        async def _data(path, **kwargs):
            seen.append(path)

            return []

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        asyncio.run(markets.upcoming())

        assert seen == ["calendar/upcoming"]

    def test_upcoming_handles_an_unknown_block(self, monkeypatch):
        """A block the constant table does not name still reports its count."""

        async def _data(path, **kwargs):
            return [{"name": "Something New", "eventCount": 3}]

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)

        assert asyncio.run(markets.upcoming())[0]["preview"] == []


class TestNordicEndpoints:
    """Cover the non-model Nordic endpoints."""

    def test_derivatives_volume(self, monkeypatch):
        """Each market's session volume is returned as a number."""

        async def _data(path, **kwargs):
            return {
                "volumeSummary": {
                    "rows": [
                        {"name": "Swedish Equity Derivatives", "volume": "137,339"},
                        {"name": "Danish Equity Derivatives", "volume": ""},
                    ]
                }
            }

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)
        rows = asyncio.run(nordic.derivatives_volume())

        assert rows[0] == {"market": "Swedish Equity Derivatives", "volume": 137339.0}
        assert rows[1]["volume"] is None

    def test_derivatives_volume_when_empty(self, monkeypatch):
        """No published volume yields no rows."""

        async def _data(path, **kwargs):
            return None

        monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)

        assert asyncio.run(nordic.derivatives_volume()) == []


def _model_commands():
    """Yield every model-backed command function across the sub-routers."""
    import importlib
    import inspect

    names = (
        "calendar",
        "crypto",
        "derivatives",
        "economy",
        "equity",
        "estimates",
        "etf",
        "fundamentals",
        "index",
        "markets",
        "news",
        "nordic",
        "ownership",
    )

    for name in names:
        module = importlib.import_module(f"openbb_nasdaq.routers.{name}")

        for attribute, value in vars(module).items():
            if not inspect.iscoroutinefunction(value):
                continue

            signature = inspect.signature(value)

            if "provider_choices" in signature.parameters:
                yield f"{name}.{attribute}", module, value


class TestModelCommands:
    """Cover the model-backed command bodies."""

    @pytest.mark.parametrize(
        ("name", "module", "command"),
        list(_model_commands()),
        ids=[name for name, _, _ in _model_commands()],
    )
    def test_command_delegates_to_the_query(self, name, module, command, monkeypatch):
        """Each command hands its parameters to the standard query pipeline."""
        seen: list[dict] = []

        async def _from_query(query):
            seen.append(query)

            return "obbject"

        monkeypatch.setattr(module, "OBBQuery", dict)
        monkeypatch.setattr(
            "openbb_core.app.model.obbject.OBBject.from_query", _from_query
        )
        result = asyncio.run(command("cc", "providers", "standard", "extra"))

        assert result == "obbject"
        assert seen[0]["provider_choices"] == "providers"


class TestNordicSymbolChoicesEndpoint:
    """Cover the Nordic instrument picker endpoint."""

    def test_serves_the_directory(self, monkeypatch):
        """The picker delegates to the Nordic directory choices."""

        async def _choices():
            return [{"label": "ATCO A", "value": "ATCO A"}]

        monkeypatch.setattr(
            "openbb_nasdaq.utils.nordic.get_nordic_symbol_choices", _choices
        )

        assert asyncio.run(nordic.symbol_choices()) == [
            {"label": "ATCO A", "value": "ATCO A"}
        ]


class TestIndexSymbolChoicesEndpoint:
    """Cover the index picker endpoint."""

    def test_serves_the_directory(self, monkeypatch):
        """The picker delegates to the index directory choices."""

        async def _choices():
            return [{"label": "COMP", "value": "COMP"}]

        monkeypatch.setattr(
            "openbb_nasdaq.utils.helpers.get_index_symbol_choices", _choices
        )

        assert asyncio.run(index.symbol_choices()) == [
            {"label": "COMP", "value": "COMP"}
        ]


class TestEtfSymbolChoicesEndpoint:
    """Cover the fund picker endpoint."""

    def test_serves_the_directory(self, monkeypatch):
        """The picker delegates to the fund directory choices."""

        async def _choices():
            return [{"label": "QQQ", "value": "QQQ"}]

        monkeypatch.setattr(
            "openbb_nasdaq.utils.helpers.get_etf_symbol_choices", _choices
        )

        assert asyncio.run(etf.symbol_choices()) == [{"label": "QQQ", "value": "QQQ"}]
