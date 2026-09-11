"""Tests for the USDA router commands and endpoints."""

import asyncio
from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.router import Router

from openbb_government_us.usda import COMMODITY_INSTALLED, usda_router

COMMODITY_MODEL_COMMANDS = [] if COMMODITY_INSTALLED else [usda_router.psd_data]

COMMODITY_RESULTS_COMMANDS = (
    []
    if COMMODITY_INSTALLED
    else [
        usda_router.psd_report,
        usda_router.weather_bulletins,
        usda_router.weather_bulletins_download,
    ]
)

MODEL_BACKED_COMMANDS = [
    usda_router.price_spreads,
    usda_router.publications,
    usda_router.report_calendar,
    usda_router.dairy_data,
    usda_router.milk_cost_of_production,
    usda_router.major_land_uses,
    usda_router.agricultural_trade,
    usda_router.meat_price_spreads,
    usda_router.wheat_data,
    usda_router.commodity_costs_and_returns,
    usda_router.rice_yearbook,
    usda_router.sugar_sweeteners_yearbook,
    usda_router.oil_crops_yearbook,
    usda_router.feed_grains_database,
    usda_router.fruit_and_tree_nuts_data,
    usda_router.vegetables_and_pulses,
    usda_router.cotton_wool_and_textile_data,
    usda_router.fertilizer_use_and_price,
    usda_router.food_price_outlook,
    usda_router.fruit_and_vegetable_prices,
    usda_router.livestock_and_meat_domestic_data,
    usda_router.season_average_price_forecasts,
    usda_router.farm_household_income_and_characteristics,
    usda_router.farm_income_and_wealth_statistics,
    usda_router.food_dollar_series,
    usda_router.food_expenditure_series,
    usda_router.us_food_imports,
    usda_router.us_bioenergy_statistics,
    usda_router.agricultural_exchange_rates,
    usda_router.agricultural_productivity,
    usda_router.international_agricultural_productivity,
    usda_router.international_macroeconomic_data_set,
    usda_router.livestock_and_meat_international_trade_data,
    usda_router.state_agricultural_trade,
    usda_router.normalized_prices,
    usda_router.agricultural_trade_multipliers,
    usda_router.agricultural_and_food_rd_expenditures,
    usda_router.adoption_of_genetically_engineered_crops,
    usda_router.food_security_in_the_united_states,
    usda_router.food_availability_per_capita,
    usda_router.food_at_home_monthly_area_prices,
    usda_router.rural_urban_continuum_codes,
    usda_router.urban_influence_codes,
    usda_router.county_typology_codes,
    usda_router.rural_urban_commuting_area_codes,
    usda_router.frontier_and_remote_area_codes,
    usda_router.commuting_zones_and_labor_market_areas,
    usda_router.natural_amenities_scale,
    usda_router.poverty_area_measures,
    usda_router.area_and_road_ruggedness_scales,
    usda_router.cost_estimates_of_foodborne_illnesses,
    usda_router.snap_policy_data_sets,
    usda_router.international_baseline_data,
    usda_router.eating_and_health_module_atus,
    usda_router.food_consumption_nutrient_intakes_and_diet_quality,
    usda_router.resource_requirements_of_food_demand,
    usda_router.purchase_to_plate,
    usda_router.global_food_assessment,
] + COMMODITY_MODEL_COMMANDS

RESULTS_ONLY_COMMANDS = [
    usda_router.bell_report,
    usda_router.publication_documents,
] + COMMODITY_RESULTS_COMMANDS

COMMODITIES = [
    {"id": 1, "commodity_code": 101, "commodity_name": "WHEAT - HARD RED WINTER"},
    {"id": 12, "commodity_code": 401, "commodity_name": "CORN"},
]
WEEKS = [
    {"week_ending": date(2026, 7, 9), "released_at": datetime(2026, 7, 16, 8, 30)},
    {"week_ending": date(2026, 7, 2), "released_at": datetime(2026, 7, 9, 8, 30)},
]


class TestUsdaRouter:
    """Tests for the USDA Router registration and command delegation."""

    def test_router_is_openbb_router(self):
        """The exported router is an openbb_core Router instance."""
        assert isinstance(usda_router.router, Router)

    def test_commodity_commands_registered_without_commodity(self):
        """The commodity-model commands register only when openbb-commodity is absent."""
        paths = {route.path for route in usda_router.router.api_router.routes}
        expected = not COMMODITY_INSTALLED
        assert ("/psd_data" in paths) is expected
        assert ("/psd_report" in paths) is expected
        assert ("/weather_bulletins" in paths) is expected
        assert ("/weather_bulletins_download" in paths) is expected

    def test_ers_endpoints_always_registered(self):
        """The ERS endpoints register regardless of installed extensions."""
        paths = {route.path for route in usda_router.router.api_router.routes}
        assert "/ers_chart" in paths
        assert "/ers_viz_catalog" in paths
        assert "/price_spreads" in paths


class TestBellReportOptions:
    """Tests for the endpoints backing the Bell Report widget's pickers."""

    @staticmethod
    def _patch(monkeypatch):
        async def fake_commodities():
            return COMMODITIES

        async def fake_weeks():
            return WEEKS

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.fas_bell_report.get_commodities",
            fake_commodities,
        )
        monkeypatch.setattr(
            "openbb_government_us.usda.utils.fas_bell_report.get_published_weeks",
            fake_weeks,
        )

    def test_commodities_labelled_for_the_workspace(self, monkeypatch):
        """The Workspace picker labels each commodity with its code."""
        self._patch(monkeypatch)
        options = asyncio.run(usda_router.bell_report_commodities(is_workspace=True))
        assert options[0] == {
            "label": "WHEAT - HARD RED WINTER (101)",
            "value": "101",
        }

    def test_commodities_raw_for_python(self, monkeypatch):
        """The Python interface gets the unlabelled records."""
        self._patch(monkeypatch)
        assert asyncio.run(usda_router.bell_report_commodities()) == COMMODITIES

    def test_weeks_labelled_for_the_workspace(self, monkeypatch):
        """The Workspace picker lists published weeks newest first."""
        self._patch(monkeypatch)
        options = asyncio.run(usda_router.bell_report_weeks(is_workspace=True))
        assert options == [
            {"label": "2026-07-09", "value": "2026-07-09"},
            {"label": "2026-07-02", "value": "2026-07-02"},
        ]

    def test_weeks_raw_for_python_and_limited(self, monkeypatch):
        """The Python interface gets the release timestamps, honouring the limit."""
        self._patch(monkeypatch)
        rows = asyncio.run(usda_router.bell_report_weeks(limit=1))
        assert rows == [
            {
                "week_ending": date(2026, 7, 9),
                "released_at": datetime(2026, 7, 16, 8, 30),
            }
        ]

    def test_urls_offer_every_marketing_year(self, monkeypatch):
        """The file selector lists one report per marketing year."""
        self._patch(monkeypatch)
        options = asyncio.run(usda_router.bell_report_urls())
        assert [option["label"] for option in options] == [
            "Bell Report MY1 - WHEAT - HARD RED WINTER - 2026-07-09",
            "Bell Report MY2 - WHEAT - HARD RED WINTER - 2026-07-09",
            "Bell Report MY3 - WHEAT - HARD RED WINTER - 2026-07-09",
        ]

    def test_urls_default_to_the_latest_published_week(self, monkeypatch):
        """Omitting the week addresses the most recently published one."""
        self._patch(monkeypatch)
        url = asyncio.run(usda_router.bell_report_urls())[0]["value"]
        assert "wed=07%2F09%2F2026" in url
        assert "RD=07%2F16%2F2026" in url

    def test_urls_translate_codes_to_report_ids(self, monkeypatch):
        """The published code is translated to the report viewer's id."""
        self._patch(monkeypatch)
        options = asyncio.run(usda_router.bell_report_urls(commodity_code="101,401"))
        assert "CID=1%2C12%2C" in options[0]["value"]
        assert options[0]["label"].endswith(
            "WHEAT - HARD RED WINTER, CORN - 2026-07-09"
        )

    def test_urls_for_an_explicit_published_week(self, monkeypatch):
        """An explicitly requested published week is used."""
        self._patch(monkeypatch)
        url = asyncio.run(usda_router.bell_report_urls(week_ending="2026-07-02"))[0][
            "value"
        ]
        assert "wed=07%2F02%2F2026" in url
        assert "RD=07%2F09%2F2026" in url

    def test_urls_unknown_code_raises(self, monkeypatch):
        """An unknown commodity code raises rather than returning nothing."""
        self._patch(monkeypatch)
        with pytest.raises(OpenBBError, match="Unknown commodity code"):
            asyncio.run(usda_router.bell_report_urls(commodity_code="999"))

    def test_urls_unpublished_week_raises(self, monkeypatch):
        """An embargoed week is never addressable."""
        self._patch(monkeypatch)
        with pytest.raises(OpenBBError, match="No published Bell Report"):
            asyncio.run(usda_router.bell_report_urls(week_ending="2026-07-16"))


class TestErsChart:
    """Tests for the ERS Tableau visualization widget endpoint."""

    @staticmethod
    def _payload(body: str) -> dict:
        """Extract the JSON payload the page bootstraps from."""
        import json
        import re

        match = re.search(
            r'<script id="ers-chart-data" type="application/json">(.*?)</script>',
            body,
            re.S,
        )
        assert match
        return json.loads(match.group(1))

    def test_renders_default_viz(self):
        """The default visualization is injected as the page's bootstrap payload."""
        response = asyncio.run(usda_router.ers_chart())
        payload = self._payload(response.body.decode())
        assert payload["viz"] == "Marketbaskets/Marketbaskets"
        assert payload["title"] == "Market Baskets"
        assert payload["theme"] == "dark"

    def test_light_theme(self):
        """The light theme is carried into the payload."""
        response = asyncio.run(usda_router.ers_chart(theme="light"))
        assert self._payload(response.body.decode())["theme"] == "light"

    def test_implements_the_iframe_protocol(self):
        """The page announces itself and answers the Workspace protocol messages."""
        body = asyncio.run(usda_router.ers_chart()).body.decode()
        for message in (
            "openbb-connect",
            "openbb-request",
            "openbb-data",
            "openbb-params-update",
            "openbb-auth",
        ):
            assert message in body
        assert "usda_ers_viz_catalog" in body
        assert "usda_ers_viz_about" in body

    def test_widget_is_an_iframe(self):
        """The widget is served to the Workspace as an iframe."""
        route = next(
            route
            for route in usda_router.router.api_router.routes
            if route.path == "/ers_chart"
        )
        config = route.openapi_extra["widget_config"]
        assert config["type"] == "iframe"
        assert config["widgetId"] == "usda_ers_chart_usda_obb"

    def test_unknown_viz_raises_404(self):
        """An unknown visualization path raises a 404."""
        from fastapi.exceptions import HTTPException

        with pytest.raises(HTTPException) as error:
            asyncio.run(usda_router.ers_chart(viz="Nope/Nope"))
        assert error.value.status_code == 404

    def test_every_catalog_entry_renders(self):
        """Every catalog entry produces a payload the page can embed."""
        from openbb_government_us.usda.utils.ers_catalog import load_catalog, viz_paths

        catalog = load_catalog()
        assert len(catalog) == len(viz_paths())
        for entry in catalog:
            path = f"{entry['workbook']}/{entry['default_view']}"
            body = asyncio.run(usda_router.ers_chart(viz=path)).body.decode()
            assert self._payload(body)["viz"] == path


class TestErsVizCatalog:
    """Tests for the catalog endpoint the iframe fetches its sub-widget data from."""

    def test_registered_and_excluded_from_widgets(self):
        """The catalog is served but never becomes a widget of its own."""
        route = next(
            route
            for route in usda_router.router.api_router.routes
            if route.path == "/ers_viz_catalog"
        )
        assert route.openapi_extra["widget_config"] == {"exclude": True}

    def test_lists_every_visualization(self):
        """Every catalog entry is returned with its embed path and public URL."""
        from openbb_government_us.usda.utils.ers_catalog import load_catalog

        rows = asyncio.run(usda_router.ers_viz_catalog())
        assert len(rows) == len(load_catalog())
        for row in rows:
            assert set(row) == {
                "viz",
                "title",
                "description",
                "last_updated",
                "url",
            }
            assert row["url"] == f"https://public.tableau.com/views/{row['viz']}"


class TestErsCatalog:
    """Tests for the ERS catalog utilities."""

    def test_load_catalog_shape(self):
        """The packaged catalog parses with the expected keys."""
        from openbb_government_us.usda.utils.ers_catalog import load_catalog

        catalog = load_catalog()
        assert len(catalog) > 0
        for entry in catalog:
            assert {"title", "workbook", "default_view"} <= set(entry)

    def test_fetch_catalog_pages_and_normalizes(self, monkeypatch):
        """fetch_catalog pages the profile API and normalizes entries."""
        from openbb_government_us.usda.utils import ers_catalog

        pages = {
            0: {
                "contents": [
                    {
                        "title": "B Title",
                        "workbookRepoUrl": "BBook",
                        "defaultViewRepoUrl": "BBook/sheets/BView",
                        "description": "B desc",
                        "lastUpdateDate": 1739750400000,
                    },
                    {
                        "title": "Skip Me",
                        "workbookRepoUrl": "",
                        "defaultViewRepoUrl": "",
                    },
                ],
                "nextIndex": 50,
            },
            50: {
                "contents": [
                    {
                        "title": "A Title",
                        "workbookRepoUrl": "ABook",
                        "defaultViewRepoUrl": "ABook/sheets/AView",
                        "lastPublishDate": None,
                    }
                ],
                "nextIndex": -1,
            },
        }

        async def fake_request(url, **kwargs):
            start = int(url.split("start=")[1].split("&")[0])
            return pages[start]

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.amake_request", fake_request
        )
        entries = asyncio.run(ers_catalog.fetch_catalog())
        assert [entry["workbook"] for entry in entries] == ["ABook", "BBook"]
        assert entries[1]["last_updated"] == "2025-02-17"
        assert entries[0]["last_updated"] is None
        assert entries[0]["description"] == "A Title"

    def test_main_writes_asset(self, monkeypatch, tmp_path):
        """The console script writes the regenerated catalog asset."""
        from openbb_government_us.usda.utils import ers_catalog

        async def fake_fetch():
            return [{"title": "T", "workbook": "W", "default_view": "V"}]

        target = tmp_path / "catalog.json"
        monkeypatch.setattr(ers_catalog, "fetch_catalog", fake_fetch)
        monkeypatch.setattr(ers_catalog, "CATALOG_FILE", target)
        ers_catalog.main()
        assert target.exists()
        assert '"workbook": "W"' in target.read_text()


class _QueryResponse:
    """Stand-in for the response a command's provider query returns."""

    @staticmethod
    def model_dump() -> dict:
        """Return the serialized response envelope."""
        return {"results": ["sentinel"]}


class TestModelBackedCommands:
    """Tests for the USDA commands that return the provider response unchanged."""

    @pytest.mark.parametrize(
        "command", MODEL_BACKED_COMMANDS, ids=lambda command: command.__name__
    )
    def test_command_queries_with_its_arguments(self, command):
        """Each command builds the query from its four arguments and returns the response."""
        response = _QueryResponse()
        with (
            patch.object(usda_router, "OBBject") as mock_obbject,
            patch.object(usda_router, "OpenBBQuery") as mock_query,
        ):
            mock_obbject.from_query = AsyncMock(return_value=response)
            result = asyncio.run(
                command(
                    cc="CC",
                    provider_choices="PC",
                    standard_params="SP",
                    extra_params="EP",
                )
            )
        assert mock_query.call_args.kwargs == {
            "cc": "CC",
            "provider_choices": "PC",
            "standard_params": "SP",
            "extra_params": "EP",
        }
        mock_obbject.from_query.assert_awaited_once_with(mock_query.return_value)
        assert result is response


class TestResultsOnlyCommands:
    """Tests for the document commands that unwrap the results list."""

    @pytest.mark.parametrize(
        "command", RESULTS_ONLY_COMMANDS, ids=lambda command: command.__name__
    )
    def test_command_returns_only_the_results(self, command):
        """The document downloads drop the envelope and return only the results."""
        with (
            patch.object(usda_router, "OBBject") as mock_obbject,
            patch.object(usda_router, "OpenBBQuery"),
        ):
            mock_obbject.from_query = AsyncMock(return_value=_QueryResponse())
            result = asyncio.run(
                command(
                    cc=None,
                    provider_choices=None,
                    standard_params=None,
                    extra_params=None,
                )
            )
        assert result == ["sentinel"]


class TestAppsJson:
    """Tests for the packaged Workspace app definition endpoint."""

    def test_serves_the_packaged_definition(self):
        """The endpoint returns the USDA app read from the packaged asset."""
        apps = asyncio.run(usda_router.get_usda_apps_json())
        assert [app["name"] for app in apps] == ["US Department of Agriculture"]
        assert apps[0]["tabs"]

    def test_missing_asset_returns_an_empty_list(self, monkeypatch, tmp_path):
        """A missing asset file degrades to an empty app list."""
        monkeypatch.setattr(usda_router, "Path", lambda _: tmp_path / "usda_router.py")
        assert asyncio.run(usda_router.get_usda_apps_json()) == []


class TestPriceSpreadItems:
    """Tests for the price-spread item picker."""

    def test_lists_every_item_without_a_category(self):
        """With no category every catalogued item is offered."""
        options = asyncio.run(usda_router.price_spread_items())
        assert len(options) == 24
        assert {
            "label": "Milk and dairy basket",
            "value": "milk_and_dairy_basket",
        } in options

    def test_narrows_to_a_category(self):
        """A category narrows the list to that category's items."""
        options = asyncio.run(usda_router.price_spread_items(category="dairy"))
        assert [option["value"] for option in options] == [
            "milk_and_dairy_basket",
            "butter",
            "cheddar_cheese",
            "ice_cream",
            "whole_milk",
        ]

    def test_unknown_category_matches_nothing(self):
        """An unknown category matches no item."""
        assert asyncio.run(usda_router.price_spread_items(category="nope")) == []


class TestMilkCostItems:
    """Tests for the milk cost of production item picker."""

    ROWS = [
        {"category": "Operating costs", "item": "Purchased feed"},
        {"category": "Operating costs", "item": "Purchased feed"},
        {"category": "Operating costs", "item": "Repairs"},
        {"category": "Allocated overhead", "item": "Hired labor"},
        {"category": "Operating costs", "item": "Not a published item"},
    ]

    def _patch(self, monkeypatch) -> list:
        rows = self.ROWS

        async def fake_report(report, **kwargs):
            requested.append(report)
            return rows

        requested: list = []
        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_milk_cost_of_production.afetch_report",
            fake_report,
        )
        return requested

    def test_deduplicates_and_drops_unpublished_items(self, monkeypatch):
        """Repeated items collapse and items outside the catalog are dropped."""
        self._patch(monkeypatch)
        assert asyncio.run(usda_router.milk_cost_items()) == [
            {"label": "Purchased feed", "value": "purchased_feed"},
            {"label": "Repairs", "value": "repairs"},
            {"label": "Hired labor", "value": "hired_labor"},
        ]

    def test_narrows_to_a_cost_category(self, monkeypatch):
        """A category key is translated to its label and used to filter the rows."""
        self._patch(monkeypatch)
        options = asyncio.run(
            usda_router.milk_cost_items(category="allocated_overhead")
        )
        assert options == [{"label": "Hired labor", "value": "hired_labor"}]

    def test_unknown_report_falls_back_to_by_state(self, monkeypatch):
        """An unknown report key is replaced by the by-state report."""
        requested = self._patch(monkeypatch)
        asyncio.run(usda_router.milk_cost_items(report="by_planet"))
        assert requested == ["by_state"]


class TestErsPublicationOptions:
    """Tests for the ERS publications pickers."""

    def test_urls_are_newest_first_and_limited(self, monkeypatch):
        """Publications are ordered newest first and cut to the limit."""
        requested: list = []

        async def fake_fetch(series, **kwargs):
            requested.append(series)
            return [
                {"release_date": "2026-01-05", "title": "Older", "url": "u1"},
                {"release_date": "2026-03-05", "title": "Newer", "url": "u2"},
                {"release_date": None, "title": "Undated", "url": "u3"},
            ]

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_publications.fetch_publications",
            fake_fetch,
        )
        options = asyncio.run(usda_router.ers_publication_urls(series="LDPM", limit=2))
        assert requested == ["LDPM"]
        assert options == [
            {"label": "2026-03-05 - Newer", "value": "u2"},
            {"label": "2026-01-05 - Older", "value": "u1"},
        ]

    def test_series_lists_the_groups_before_the_codes(self, monkeypatch):
        """The series picker offers the three groups first, then every series code."""
        options = asyncio.run(usda_router.ers_publication_series())
        assert options[:3] == [
            {"label": "Outlook Reports", "value": "outlook-reports"},
            {"label": "Research Reports", "value": "research-reports"},
            {"label": "Discontinued Reports", "value": "discontinued-reports"},
        ]
        assert {
            "label": "AES: Outlook for U.S. Agricultural Trade",
            "value": "AES",
        } in options


class TestPsdReportOptions:
    """Tests for the PSD circular pickers."""

    def test_commodities_are_title_cased(self):
        """Every circular commodity is offered with a display label."""
        options = asyncio.run(usda_router.psd_report_commodities())
        assert len(options) == 12
        assert options[0] == {"label": "Citrus", "value": "citrus"}
        assert {"label": "Stone Fruit", "value": "stone_fruit"} in options

    @staticmethod
    def _patch(monkeypatch) -> tuple[list, list]:
        latest_calls: list = []
        historical_calls: list = []

        async def fake_latest(commodity):
            latest_calls.append(commodity)
            return [
                {"year": 2026, "month": 1, "commodity": "stone_fruit", "url": "a.pdf"}
            ]

        async def fake_historical(commodity):
            historical_calls.append(commodity)
            return [
                {
                    "year": 2026,
                    "month": 3,
                    "commodity": commodity,
                    "url": f"{commodity}.pdf",
                }
            ]

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.psd_circulars.latest_circulars",
            fake_latest,
        )
        monkeypatch.setattr(
            "openbb_government_us.usda.utils.psd_circulars.historical_circulars",
            fake_historical,
        )
        return latest_calls, historical_calls

    def test_without_a_commodity_only_the_latest_circulars_are_listed(
        self, monkeypatch
    ):
        """No commodity asks for the latest circular of every commodity."""
        latest_calls, historical_calls = self._patch(monkeypatch)
        options = asyncio.run(usda_router.psd_report_urls())
        assert latest_calls == [None]
        assert historical_calls == []
        assert options == [{"label": "Stone Fruit - 2026-01", "value": "a.pdf"}]

    def test_each_named_commodity_gets_its_history(self, monkeypatch):
        """A comma-separated commodity list is expanded to one history lookup each."""
        latest_calls, historical_calls = self._patch(monkeypatch)
        options = asyncio.run(usda_router.psd_report_urls(commodity="citrus, sugar"))
        assert latest_calls == []
        assert historical_calls == ["citrus", "sugar"]
        assert options == [
            {"label": "Citrus - 2026-03", "value": "citrus.pdf"},
            {"label": "Sugar - 2026-03", "value": "sugar.pdf"},
        ]


class TestPsdDataOptions:
    """Tests for the PSD attribute and country pickers."""

    def test_attribute_label_expands_the_known_acronyms(self):
        """The label formatter restores the US, TY, and FSI acronyms."""
        assert usda_router._psd_attribute_label("us_ty_fsi_total") == "US TY FSI Total"

    def test_attributes_default_to_the_whole_sorted_catalog(self):
        """With no commodity every PSD attribute is offered, sorted."""
        from openbb_government_us.usda.utils.psd_codes import ATTRIBUTES

        options = asyncio.run(usda_router.psd_data_attributes())
        assert options[0] == {"label": "All Attributes", "value": None}
        assert [option["value"] for option in options[1:]] == sorted(ATTRIBUTES)

    def test_attributes_narrow_to_a_commodity(self, monkeypatch):
        """A known commodity is resolved to its PSD code and its attributes listed."""
        requested: list = []

        def fake_attributes(code):
            requested.append(code)
            return ["exports", "area_planted"]

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.psd_data_downloader"
            "._get_commodity_attributes",
            fake_attributes,
        )
        options = asyncio.run(usda_router.psd_data_attributes(commodity="corn"))
        assert requested == ["0440000"]
        assert options == [
            {"label": "All Attributes", "value": None},
            {"label": "Exports", "value": "exports"},
            {"label": "Area Planted", "value": "area_planted"},
        ]

    def test_attributes_unknown_commodity_skips_the_lookup(self, monkeypatch):
        """An unknown commodity never triggers the per-commodity lookup."""

        def fail(code):
            raise AssertionError("the commodity lookup must not run")

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.psd_data_downloader"
            "._get_commodity_attributes",
            fail,
        )
        options = asyncio.run(usda_router.psd_data_attributes(commodity="unobtainium"))
        assert len(options) == 133

    def test_countries_default_to_countries_and_regions(self):
        """With no commodity the picker merges the country and region catalogs."""
        options = asyncio.run(usda_router.psd_data_countries())
        assert options[0] == {"label": "All Countries", "value": None}
        assert {"label": "Afghanistan", "value": "AF"} in options
        assert {"label": "North America", "value": "R01"} in options
        assert {"label": "World", "value": "R00"} in options

    def test_countries_narrow_to_a_commodity(self, monkeypatch):
        """A known commodity lists only the countries that report it."""
        requested: list = []

        def fake_countries(code):
            requested.append(code)
            return {"Brazil": "BR"}

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.psd_data_downloader"
            "._get_commodity_countries",
            fake_countries,
        )
        options = asyncio.run(usda_router.psd_data_countries(commodity="corn"))
        assert requested == ["0440000"]
        assert options == [
            {"label": "All Countries", "value": None},
            {"label": "Brazil", "value": "BR"},
        ]


class TestAgriculturalTradeOptions:
    """Tests for the agricultural trade dependent pickers."""

    def test_measures_default_to_the_year_to_date_exports_table(self):
        """No table falls back to the year-to-date export measures."""
        assert asyncio.run(usda_router.agricultural_trade_measures()) == [
            {"label": "Value", "value": "value"},
            {"label": "Volume", "value": "volume"},
        ]

    def test_measures_follow_the_table(self):
        """The import table adds the CIF value measure."""
        options = asyncio.run(
            usda_router.agricultural_trade_measures(table="imports_ytd")
        )
        assert options[-1] == {"label": "CIF value", "value": "cif"}

    def test_measures_unknown_table_falls_back(self):
        """An unknown table falls back to the year-to-date export measures."""
        options = asyncio.run(usda_router.agricultural_trade_measures(table="nope"))
        assert [option["value"] for option in options] == ["value", "volume"]

    def test_commodities_pass_the_table_through(self, monkeypatch):
        """The commodity picker scopes the distinct lookup to the table."""
        requested: list = []

        async def fake_distinct(field, table=None):
            requested.append((field, table))
            return ["Corn", "Soybeans"]

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_fatus_trade.distinct_field",
            fake_distinct,
        )
        options = asyncio.run(
            usda_router.agricultural_trade_commodities(table="exports_ytd")
        )
        assert requested == [("commodity", "exports_ytd")]
        assert options == [
            {"label": "Corn", "value": "Corn"},
            {"label": "Soybeans", "value": "Soybeans"},
        ]

    def test_periods_unknown_table_falls_back(self, monkeypatch):
        """An unknown table is replaced by the year-to-date exports table."""
        requested: list = []

        async def fake_bases(table, **kwargs):
            requested.append(table)
            return ["Calendar year"]

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_fatus_trade.table_period_bases",
            fake_bases,
        )
        options = asyncio.run(usda_router.agricultural_trade_periods(table="nope"))
        assert requested == ["exports_ytd"]
        assert options == [{"label": "Calendar year", "value": "Calendar year"}]

    def test_periods_keep_a_known_table(self, monkeypatch):
        """A known table is passed through unchanged."""
        requested: list = []

        async def fake_bases(table, **kwargs):
            requested.append(table)
            return ["Fiscal year"]

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_fatus_trade.table_period_bases",
            fake_bases,
        )
        asyncio.run(usda_router.agricultural_trade_periods(table="top_export_markets"))
        assert requested == ["top_export_markets"]


class TestYearbookFrequencyOptions:
    """Tests for the yearbook frequency and region pickers."""

    @staticmethod
    def _patch_frequencies(monkeypatch, module: str) -> list:
        requested: list = []

        async def fake_frequencies(table, **kwargs):
            requested.append(table)
            return ["Annual", "Monthly"]

        monkeypatch.setattr(
            f"openbb_government_us.usda.utils.{module}.table_frequencies",
            fake_frequencies,
        )
        return requested

    def test_rice_unknown_table_falls_back(self, monkeypatch):
        """An unknown rice table is replaced by the supply and disappearance table."""
        requested = self._patch_frequencies(monkeypatch, "ers_rice_yearbook")
        options = asyncio.run(usda_router.rice_frequencies(table="nope"))
        assert requested == ["us_supply_disappearance_price"]
        assert options == [
            {"label": "Annual", "value": "Annual"},
            {"label": "Monthly", "value": "Monthly"},
        ]

    def test_rice_known_table_is_kept(self, monkeypatch):
        """A known rice table reaches the frequency lookup unchanged."""
        requested = self._patch_frequencies(monkeypatch, "ers_rice_yearbook")
        asyncio.run(usda_router.rice_frequencies(table="us_state_yields"))
        assert requested == ["us_state_yields"]

    def test_sugar_unknown_table_falls_back(self, monkeypatch):
        """An unknown sugar table is replaced by table 24a."""
        requested = self._patch_frequencies(
            monkeypatch, "ers_sugar_sweeteners_yearbook"
        )
        options = asyncio.run(usda_router.sugar_frequencies(table="nope"))
        assert requested == ["table_24a"]
        assert options[0] == {"label": "Annual", "value": "Annual"}

    def test_sugar_known_table_is_kept(self, monkeypatch):
        """A known sugar table reaches the frequency lookup unchanged."""
        requested = self._patch_frequencies(
            monkeypatch, "ers_sugar_sweeteners_yearbook"
        )
        asyncio.run(usda_router.sugar_frequencies(table="table_2"))
        assert requested == ["table_2"]

    def test_cotton_unknown_table_falls_back(self, monkeypatch):
        """An unknown cotton table is replaced by cotton supply and use."""
        requested = self._patch_frequencies(
            monkeypatch, "ers_cotton_wool_and_textile_data"
        )
        options = asyncio.run(usda_router.cotton_frequencies(table="nope"))
        assert requested == ["cotton_supply_and_use"]
        assert options[1] == {"label": "Monthly", "value": "Monthly"}

    def test_cotton_known_table_is_kept(self, monkeypatch):
        """A known cotton table reaches the frequency lookup unchanged."""
        requested = self._patch_frequencies(
            monkeypatch, "ers_cotton_wool_and_textile_data"
        )
        asyncio.run(
            usda_router.cotton_frequencies(table="upland_cotton_supply_and_use")
        )
        assert requested == ["upland_cotton_supply_and_use"]

    def test_oil_crops_default_table_is_annual(self):
        """The default oil crops table publishes only annual observations."""
        assert asyncio.run(usda_router.oil_crops_frequencies()) == [
            {"label": "Annual", "value": "annual"}
        ]

    def test_oil_crops_quarterly_stocks_table(self):
        """The soybean stocks table publishes point-in-time observations."""
        options = asyncio.run(
            usda_router.oil_crops_frequencies(table="soybean_stocks_quarterly")
        )
        assert options == [{"label": "Point-in-time", "value": "point_in_time"}]

    def test_oil_crops_unknown_table_falls_back(self):
        """An unknown oil crops table falls back to the soybean default."""
        assert asyncio.run(usda_router.oil_crops_frequencies(table="nope")) == [
            {"label": "Annual", "value": "annual"}
        ]

    def test_fruit_yearbook_tables_narrow_to_a_category(self):
        """A letter category narrows the yearbook tables to that letter."""
        options = asyncio.run(usda_router.fruit_yearbook_tables(category="A"))
        assert all(option["value"].startswith("A-") for option in options)
        assert options[0]["label"].startswith("A-1 - Fruit and tree nuts")

    def test_fruit_yearbook_tables_default_to_everything(self):
        """With no category every yearbook table is offered."""
        assert len(asyncio.run(usda_router.fruit_yearbook_tables())) == 152

    def test_commodity_cost_regions_default_to_corn(self):
        """The default commodity is corn and its regions lead with the U.S. total."""
        options = asyncio.run(usda_router.commodity_cost_regions())
        assert options[0] == {"label": "U.S. total", "value": "U.S. total"}
        assert {"label": "Heartland", "value": "Heartland"} in options

    def test_commodity_cost_regions_follow_the_commodity(self):
        """Wheat's budget is published for its own region set."""
        options = asyncio.run(usda_router.commodity_cost_regions(commodity="wheat"))
        assert {"label": "Basin and Range", "value": "Basin and Range"} in options

    def test_commodity_cost_regions_unknown_commodity_falls_back(self):
        """An unknown commodity falls back to corn's regions."""
        assert asyncio.run(
            usda_router.commodity_cost_regions(commodity="nope")
        ) == asyncio.run(usda_router.commodity_cost_regions(commodity="corn"))


class TestFoodPriceOutlookItems:
    """Tests for the Food Price Outlook item picker."""

    @staticmethod
    def _patch(monkeypatch) -> list:
        requested: list = []

        async def fake_table(table, **kwargs):
            requested.append(table)
            return [
                {"item": "All food"},
                {"item": "Beef and veal"},
                {"item": "All food"},
                {"item": None},
            ]

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_food_price_outlook.afetch_table",
            fake_table,
        )
        return requested

    def test_items_are_deduplicated_in_first_seen_order(self, monkeypatch):
        """Repeated items collapse and blank items are dropped."""
        self._patch(monkeypatch)
        assert asyncio.run(usda_router.food_price_outlook_items()) == [
            {"label": "All food", "value": "All food"},
            {"label": "Beef and veal", "value": "Beef and veal"},
        ]

    def test_unknown_table_falls_back_to_the_cpi_forecast(self, monkeypatch):
        """An unknown table key is replaced by the CPI forecast table."""
        requested = self._patch(monkeypatch)
        asyncio.run(usda_router.food_price_outlook_items(table="nope"))
        assert requested == ["cpi_forecast"]

    def test_known_table_is_kept(self, monkeypatch):
        """A known table key reaches the fetch unchanged."""
        requested = self._patch(monkeypatch)
        asyncio.run(usda_router.food_price_outlook_items(table="cpi_annual"))
        assert requested == ["cpi_annual"]


class TestFarmIncomeStates:
    """Tests for the farm income and wealth state picker."""

    def test_income_statement_lists_the_nation_and_the_states(self):
        """The income statement is published for the nation and every state."""
        options = asyncio.run(usda_router.farm_income_states())
        assert options[0] == {"label": "United States", "value": "US"}
        assert len(options) > 1

    def test_national_only_table_lists_the_nation(self):
        """The financial ratios table is published for the nation only."""
        assert asyncio.run(
            usda_router.farm_income_states(table="financial_ratios")
        ) == [{"label": "United States", "value": "US"}]

    def test_unknown_table_falls_back_to_the_income_statement(self):
        """An unknown table falls back to the income statement's states."""
        assert asyncio.run(usda_router.farm_income_states(table="nope")) == asyncio.run(
            usda_router.farm_income_states(table="income_statement")
        )


class TestFoodDollarOptions:
    """Tests for the food dollar series pickers."""

    def test_nominal_components(self):
        """The nominal series breaks the food dollar into five primary factors."""
        options = asyncio.run(usda_router.food_dollar_components())
        assert [option["value"] for option in options] == [
            "total",
            "salary_and_benefits",
            "property_income",
            "output_taxes",
            "imports",
        ]

    def test_real_components(self):
        """The real series collapses the factors into value added and imports."""
        assert asyncio.run(usda_router.food_dollar_components(series="real")) == [
            {"label": "Total", "value": "total"},
            {"label": "Value added", "value": "value_added"},
            {"label": "Imports", "value": "imports"},
        ]

    def test_unknown_series_components_fall_back_to_nominal(self):
        """An unknown series falls back to the nominal components."""
        assert asyncio.run(
            usda_router.food_dollar_components(series="nope")
        ) == asyncio.run(usda_router.food_dollar_components(series="nominal"))

    def test_nominal_tables(self):
        """The nominal series publishes all twenty-two tables."""
        options = asyncio.run(usda_router.food_dollar_tables())
        assert len(options) == 22
        assert options[0] == {"label": "1 - Food dollar", "value": 1}

    def test_real_tables(self):
        """The real series publishes only the first six tables."""
        options = asyncio.run(usda_router.food_dollar_tables(series="real"))
        assert [option["value"] for option in options] == [1, 2, 3, 4, 5, 6]

    def test_unknown_series_tables_fall_back_to_nominal(self):
        """An unknown series falls back to the nominal table list."""
        assert len(asyncio.run(usda_router.food_dollar_tables(series="nope"))) == 22


class TestFoodImportCommodities:
    """Tests for the U.S. food imports product-line picker."""

    RECORDS = [
        {"category": "Fruits", "commodity": "Total fruit", "row_number": 1},
        {"category": "Fruits", "commodity": "Fresh fruit", "row_number": 2},
        {"category": "Nuts", "commodity": "Total nuts", "row_number": 3},
    ]

    def _patch(self, monkeypatch) -> None:
        records = self.RECORDS

        async def fake_records():
            return records

        monkeypatch.setattr(
            "openbb_government_us.usda.utils.ers_us_food_imports.afetch_records",
            fake_records,
        )

    def test_lists_the_group_product_lines_in_rank_order(self, monkeypatch):
        """A food group's product lines are listed in their published row order."""
        self._patch(monkeypatch)
        assert asyncio.run(usda_router.food_import_commodities()) == [
            {"label": "Total fruit", "value": "Total fruit"},
            {"label": "Fresh fruit", "value": "Fresh fruit"},
        ]

    def test_follows_the_food_group(self, monkeypatch):
        """A different food group lists its own product lines."""
        self._patch(monkeypatch)
        assert asyncio.run(usda_router.food_import_commodities(food_group="Nuts")) == [
            {"label": "Total nuts", "value": "Total nuts"}
        ]

    def test_unknown_group_falls_back_to_fruits(self, monkeypatch):
        """An unknown food group falls back to fruits."""
        self._patch(monkeypatch)
        assert asyncio.run(usda_router.food_import_commodities(food_group="Nope")) == [
            {"label": "Total fruit", "value": "Total fruit"},
            {"label": "Fresh fruit", "value": "Fresh fruit"},
        ]


class TestProductivityOptions:
    """Tests for the agricultural productivity pickers."""

    def test_national_table_lists_the_nation(self):
        """The national indices table is published for the United States only."""
        assert asyncio.run(usda_router.agricultural_productivity_states()) == [
            {"label": "United States", "value": "US"}
        ]

    def test_state_table_lists_the_contiguous_states(self):
        """The relative levels table is published for the 48 contiguous states."""
        options = asyncio.run(
            usda_router.agricultural_productivity_states(table="state_relative_levels")
        )
        assert len(options) == 48
        assert options[0] == {"label": "Alabama", "value": "AL"}

    def test_unknown_table_falls_back_to_national(self):
        """An unknown productivity table falls back to the national table."""
        assert asyncio.run(
            usda_router.agricultural_productivity_states(table="nope")
        ) == [{"label": "United States", "value": "US"}]

    def test_grouping_lists_its_entities(self):
        """A regional grouping lists its member countries and the aggregate."""
        options = asyncio.run(
            usda_router.ag_productivity_countries(grouping="north_america")
        )
        assert options == [
            {"label": "Canada", "value": 178},
            {"label": "United States", "value": 179},
            {"label": "NORTH AMERICA", "value": 215},
        ]

    def test_unknown_grouping_falls_back_to_the_country_grouping(self):
        """An unknown grouping falls back to the nine country groupings."""
        assert len(asyncio.run(usda_router.ag_productivity_countries("nope"))) == 9


class TestLivestockTradeProducts:
    """Tests for the livestock and meat trade product picker."""

    @staticmethod
    def _patch(monkeypatch) -> list:
        requested: list = []

        async def fake_products(species, direction):
            requested.append((species, direction))
            return [{"label": "Fresh or chilled", "value": "Fresh or chilled"}]

        monkeypatch.setattr(
            "openbb_government_us.usda.utils"
            ".ers_livestock_and_meat_international_trade_data.afetch_products",
            fake_products,
        )
        return requested

    def test_defaults_to_beef_and_veal_imports(self, monkeypatch):
        """The picker defaults to beef and veal imports."""
        requested = self._patch(monkeypatch)
        options = asyncio.run(usda_router.livestock_trade_products())
        assert requested == [("beef_veal", "imports")]
        assert options == [{"label": "Fresh or chilled", "value": "Fresh or chilled"}]

    def test_passes_a_known_species_and_direction(self, monkeypatch):
        """A known species and direction reach the lookup unchanged."""
        requested = self._patch(monkeypatch)
        asyncio.run(
            usda_router.livestock_trade_products(table="pork", direction="exports")
        )
        assert requested == [("pork", "exports")]

    def test_unknown_species_and_direction_fall_back(self, monkeypatch):
        """Unknown species and directions fall back to beef and veal imports."""
        requested = self._patch(monkeypatch)
        asyncio.run(
            usda_router.livestock_trade_products(table="unicorn", direction="sideways")
        )
        assert requested == [("beef_veal", "imports")]


class TestStateAgTradeStates:
    """Tests for the state agricultural trade state picker."""

    def test_calendar_year_table_states(self):
        """The calendar-year table publishes 51 state options."""
        options = asyncio.run(usda_router.state_ag_trade_states())
        assert len(options) == 51
        assert options[0] == {"label": "United States", "value": "United States"}

    def test_fiscal_year_table_states(self):
        """The fiscal-year top-exports table publishes a wider state list."""
        assert (
            len(asyncio.run(usda_router.state_ag_trade_states(table="top_exports")))
            == 54
        )

    def test_unknown_table_falls_back_to_exports_by_commodity(self):
        """An unknown table falls back to the exports-by-commodity states."""
        assert len(asyncio.run(usda_router.state_ag_trade_states(table="nope"))) == 51


class TestGeCropStates:
    """Tests for the genetically engineered crop state picker."""

    def test_corn_states(self):
        """Corn adoption is published for the corn-belt states."""
        options = asyncio.run(usda_router.ge_crop_states())
        assert options[0] == {"label": "Illinois", "value": "Illinois"}

    def test_cotton_states(self):
        """Cotton adoption is published for the cotton-belt states."""
        options = asyncio.run(usda_router.ge_crop_states(crop="cotton"))
        assert options[0] == {"label": "Alabama", "value": "Alabama"}

    def test_unknown_crop_falls_back_to_corn(self):
        """An unknown crop falls back to corn's states."""
        assert asyncio.run(usda_router.ge_crop_states(crop="nope")) == asyncio.run(
            usda_router.ge_crop_states(crop="corn")
        )


class TestFoodSecurityCategories:
    """Tests for the food security category picker."""

    @staticmethod
    def _patch(monkeypatch) -> list:
        requested: list = []

        async def fake_categories(table):
            requested.append(table)
            return ["Race/ethnicity of households"]

        monkeypatch.setattr(
            "openbb_government_us.usda.utils"
            ".ers_food_security_in_the_united_states.afetch_categories",
            fake_categories,
        )
        return requested

    def test_defaults_to_the_by_characteristic_table(self, monkeypatch):
        """The picker defaults to the by-characteristic table's categories."""
        requested = self._patch(monkeypatch)
        options = asyncio.run(usda_router.food_security_categories())
        assert requested == ["by_characteristic"]
        assert options == [
            {
                "label": "Race/ethnicity of households",
                "value": "Race/ethnicity of households",
            }
        ]

    def test_known_table_is_kept(self, monkeypatch):
        """A known food security table reaches the lookup unchanged."""
        requested = self._patch(monkeypatch)
        asyncio.run(usda_router.food_security_categories(table="by_state"))
        assert requested == ["by_state"]

    def test_unknown_table_falls_back(self, monkeypatch):
        """An unknown table falls back to the by-characteristic table."""
        requested = self._patch(monkeypatch)
        asyncio.run(usda_router.food_security_categories(table="nope"))
        assert requested == ["by_characteristic"]


class TestFoodAvailabilityOptions:
    """Tests for the food availability data system pickers."""

    def test_groups_follow_the_data_system(self):
        """The nutrient system publishes its own two food-group files."""
        assert asyncio.run(
            usda_router.food_availability_groups(data_system="nutrient")
        ) == [
            {"label": "Totals", "value": "totals"},
            {"label": "By food group", "value": "food_group"},
        ]

    def test_unknown_data_system_falls_back(self):
        """An unknown data system falls back to per-capita food availability."""
        assert asyncio.run(
            usda_router.food_availability_groups(data_system="nope")
        ) == asyncio.run(usda_router.food_availability_groups())

    @staticmethod
    def _patch_blocks(monkeypatch) -> list:
        requested: list = []

        async def fake_blocks(system, group):
            requested.append((system, group))
            return ["Eggs: Per capita availability"]

        monkeypatch.setattr(
            "openbb_government_us.usda.utils"
            ".ers_food_availability_per_capita_data_system.afetch_blocks",
            fake_blocks,
        )
        return requested

    def test_commodities_pass_the_system_and_group(self, monkeypatch):
        """The commodity picker scopes the block lookup to the system and group."""
        requested = self._patch_blocks(monkeypatch)
        options = asyncio.run(usda_router.food_availability_commodities())
        assert requested == [("food_availability", "eggs")]
        assert options == [
            {
                "label": "Eggs: Per capita availability",
                "value": "Eggs: Per capita availability",
            }
        ]

    def test_commodities_unknown_group_falls_back_to_the_first_file(self, monkeypatch):
        """An unknown food group falls back to the system's first file."""
        requested = self._patch_blocks(monkeypatch)
        asyncio.run(
            usda_router.food_availability_commodities(
                data_system="nutrient", food_group="nope"
            )
        )
        assert requested == [("nutrient", "totals")]

    def test_commodities_unknown_system_falls_back(self, monkeypatch):
        """An unknown data system falls back to per-capita food availability."""
        requested = self._patch_blocks(monkeypatch)
        asyncio.run(
            usda_router.food_availability_commodities(
                data_system="nope", food_group="dairy_products"
            )
        )
        assert requested == [("food_availability", "dairy_products")]


class TestFmapOptions:
    """Tests for the Food-at-Home Monthly Area Prices pickers."""

    def test_items_follow_the_group(self):
        """The vegetables group publishes its own item list."""
        options = asyncio.run(usda_router.fmap_food_items(group="Vegetables"))
        assert len(options) == 23

    def test_items_unknown_group_falls_back_to_dairy(self):
        """An unknown food group falls back to the default dairy group."""
        options = asyncio.run(usda_router.fmap_food_items(group="Nope"))
        assert options[0] == {"label": "Whole milk", "value": "40000"}

    def test_measures_follow_the_table(self):
        """The supplemental table publishes a wider measure list."""
        options = asyncio.run(
            usda_router.fmap_measures(table="supplemental_price_indexes")
        )
        assert len(options) == 11

    def test_measures_unknown_table_falls_back(self):
        """An unknown table falls back to the monthly area prices measures."""
        options = asyncio.run(usda_router.fmap_measures(table="nope"))
        assert len(options) == 9
        assert options[-1] == {"label": "Number of stores", "value": "number_stores"}


class TestGeographyCodeStates:
    """Tests for the county and tract classification state pickers."""

    @staticmethod
    def _patch_states(monkeypatch, module: str) -> list:
        requested: list = []

        async def fake_states(key):
            requested.append(key)
            return [{"label": "Mississippi", "value": "MS"}]

        monkeypatch.setattr(
            f"openbb_government_us.usda.utils.{module}.afetch_states",
            fake_states,
        )
        return requested

    def test_continuum_default_vintage(self, monkeypatch):
        """The rural-urban continuum picker defaults to the 2023 vintage."""
        requested = self._patch_states(monkeypatch, "ers_rural_urban_continuum_codes")
        options = asyncio.run(usda_router.rural_urban_continuum_states())
        assert requested == ["2023"]
        assert options == [{"label": "Mississippi", "value": "MS"}]

    def test_continuum_known_vintage_is_kept(self, monkeypatch):
        """A published continuum vintage reaches the lookup unchanged."""
        requested = self._patch_states(monkeypatch, "ers_rural_urban_continuum_codes")
        asyncio.run(usda_router.rural_urban_continuum_states(vintage="2003"))
        assert requested == ["2003"]

    def test_continuum_unknown_vintage_falls_back(self, monkeypatch):
        """An unknown continuum vintage falls back to 2023."""
        requested = self._patch_states(monkeypatch, "ers_rural_urban_continuum_codes")
        asyncio.run(usda_router.rural_urban_continuum_states(vintage="1899"))
        assert requested == ["2023"]

    def test_poverty_default_edition(self, monkeypatch):
        """The poverty area measures picker defaults to the 2025 edition."""
        requested = self._patch_states(monkeypatch, "ers_poverty_area_measures")
        options = asyncio.run(usda_router.poverty_area_measures_states())
        assert requested == ["2025"]
        assert options == [{"label": "Mississippi", "value": "MS"}]

    def test_poverty_unknown_edition_falls_back(self, monkeypatch):
        """An unknown poverty edition falls back to 2025."""
        requested = self._patch_states(monkeypatch, "ers_poverty_area_measures")
        asyncio.run(usda_router.poverty_area_measures_states(edition="1899"))
        assert requested == ["2025"]

    def test_urban_influence_vintages_differ(self):
        """Each Urban Influence Codes vintage publishes its own state list."""
        assert len(asyncio.run(usda_router.urban_influence_code_states())) == 56
        assert (
            len(asyncio.run(usda_router.urban_influence_code_states(vintage="1993")))
            == 51
        )

    def test_urban_influence_unknown_vintage_falls_back(self):
        """An unknown Urban Influence vintage falls back to 2024."""
        assert (
            len(asyncio.run(usda_router.urban_influence_code_states(vintage="1899")))
            == 56
        )

    def test_ruca_tables_differ(self):
        """Each RUCA table publishes its own state list."""
        assert len(asyncio.run(usda_router.ruca_states())) == 56
        assert len(asyncio.run(usda_router.ruca_states(table="tract_1990"))) == 51

    def test_ruca_unknown_table_falls_back(self):
        """An unknown RUCA table falls back to the 2020 census tracts."""
        assert len(asyncio.run(usda_router.ruca_states(table="nope"))) == 56

    def test_far_zip_vintages_differ(self):
        """Each frontier and remote vintage publishes its own state list."""
        assert len(asyncio.run(usda_router.far_zip_states())) == 51
        assert len(asyncio.run(usda_router.far_zip_states(year="2000"))) == 49

    def test_far_zip_unknown_vintage_falls_back(self):
        """An unknown frontier and remote vintage falls back to 2020."""
        assert len(asyncio.run(usda_router.far_zip_states(year="1899"))) == 51

    def test_ruggedness_default_vintage(self):
        """The ruggedness picker defaults to the 2020 vintage's states."""
        options = asyncio.run(usda_router.area_road_ruggedness_states())
        assert options[0] == {"label": "Alaska", "value": "AK"}
        assert len(options) == 51

    def test_ruggedness_known_vintage_is_kept(self):
        """A published ruggedness vintage is used as given."""
        assert len(asyncio.run(usda_router.area_road_ruggedness_states("2010"))) == 51

    def test_ruggedness_unknown_vintage_falls_back(self):
        """An unknown ruggedness vintage falls back to 2020."""
        assert asyncio.run(
            usda_router.area_road_ruggedness_states(vintage="1899")
        ) == asyncio.run(usda_router.area_road_ruggedness_states(vintage="2020"))


class TestIntlBaselineOptions:
    """Tests for the international baseline data pickers."""

    RECORDS = [
        {"commodity": "Wheat", "attribute": "Production", "country": "China"},
        {"commodity": "Wheat", "attribute": "Exports", "country": "China"},
        {"commodity": "Corn", "attribute": "Exports", "country": "Brazil"},
    ]

    def _patch(self, monkeypatch) -> None:
        records = self.RECORDS

        async def fake_records():
            return records

        monkeypatch.setattr(
            "openbb_government_us.usda.utils"
            ".ers_international_baseline_data.afetch_records",
            fake_records,
        )

    def test_attributes_default_to_wheat(self, monkeypatch):
        """The attribute picker defaults to wheat's measures, in source order."""
        self._patch(monkeypatch)
        assert asyncio.run(usda_router.intl_baseline_attributes()) == [
            {"label": "Production", "value": "Production"},
            {"label": "Exports", "value": "Exports"},
        ]

    def test_attributes_follow_the_commodity(self, monkeypatch):
        """A named commodity lists only its own measures."""
        self._patch(monkeypatch)
        assert asyncio.run(usda_router.intl_baseline_attributes(commodity="Corn")) == [
            {"label": "Exports", "value": "Exports"}
        ]

    def test_attributes_unknown_commodity_falls_back_to_wheat(self, monkeypatch):
        """An unknown commodity falls back to wheat's measures."""
        self._patch(monkeypatch)
        assert asyncio.run(
            usda_router.intl_baseline_attributes(commodity="Unobtainium")
        ) == [
            {"label": "Production", "value": "Production"},
            {"label": "Exports", "value": "Exports"},
        ]

    def test_countries_default_to_wheat(self, monkeypatch):
        """The country picker defaults to wheat's reporting areas."""
        self._patch(monkeypatch)
        assert asyncio.run(usda_router.intl_baseline_countries()) == [
            {"label": "China", "value": "China"}
        ]

    def test_countries_follow_the_commodity(self, monkeypatch):
        """A named commodity lists only its own reporting areas."""
        self._patch(monkeypatch)
        assert asyncio.run(usda_router.intl_baseline_countries(commodity="Corn")) == [
            {"label": "Brazil", "value": "Brazil"}
        ]

    def test_countries_unknown_commodity_falls_back_to_wheat(self, monkeypatch):
        """An unknown commodity falls back to wheat's reporting areas."""
        self._patch(monkeypatch)
        assert asyncio.run(
            usda_router.intl_baseline_countries(commodity="Unobtainium")
        ) == [{"label": "China", "value": "China"}]
