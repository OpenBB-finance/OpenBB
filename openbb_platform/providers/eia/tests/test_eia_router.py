"""Tests for the EIA provider router."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_us_eia import eia_provider
from openbb_us_eia.eia_router import datasets, facet_options, router
from openbb_us_eia.utils import catalog
from openbb_us_eia.utils.catalog import DATASET_GROUPS, model_name

FLAT_MODEL_COMMANDS = {
    "/aeo": "EiaAeo",
    "/crude_oil_imports": "EiaCrudeOilImports",
    "/data_browser": "EiaDataBrowser",
    "/ieo": "EiaIeo",
    "/international": "EiaInternational",
    "/seds": "EiaSeds",
    "/total_energy": "EiaTotalEnergy",
}

GROUP_PREFIXES = {
    "coal": "/coal",
    "petroleum": "/petroleum",
    "natural_gas": "/natural_gas",
    "electricity": "/electricity",
    "electricity_grid": "/electricity_grid",
    "state_electricity_profiles": "/state_electricity_profiles",
    "densified_biomass": "/densified_biomass",
    "nuclear_outages": "/nuclear_outages",
}

CATEGORIZED_GROUPS = {"petroleum", "natural_gas"}


def _dataset_path(group: str, dataset: str, spec: dict) -> str:
    prefix = GROUP_PREFIXES[group]
    if group in CATEGORIZED_GROUPS:
        return f"{prefix}/{spec['category_slug']}/{dataset}"
    return f"{prefix}/{dataset}"


def _routes_by_path():
    """Map every registered path to its route.

    ``include_router`` is lazy in newer FastAPI, so the group sub-routers show
    up as ``_IncludedRouter`` placeholders rather than ``APIRoute``. Core's
    ``iter_api_routes`` resolves them to prefixed route descriptors.
    """
    from openbb_core.app.route_iter import iter_api_routes

    return {route.path: route for route in iter_api_routes(router.api_router)}


class TestRouterRegistration:
    """Every dataset and flat command is registered at its expected path."""

    def test_flat_model_commands_registered(self):
        routes = _routes_by_path()
        for path, model in FLAT_MODEL_COMMANDS.items():
            assert path in routes
            assert routes[path].openapi_extra["model"] == model
            assert model in eia_provider.fetcher_dict

    def test_every_dataset_command_registered(self):
        routes = _routes_by_path()
        for group in DATASET_GROUPS:
            for dataset, spec in catalog.get_group(group)["datasets"].items():
                path = _dataset_path(group, dataset, spec)
                assert path in routes, path
                assert routes[path].openapi_extra["model"] == model_name(group, dataset)

    def test_dataset_summaries_have_clean_first_sentence(self):
        routes = _routes_by_path()
        for group in DATASET_GROUPS:
            for dataset, spec in catalog.get_group(group)["datasets"].items():
                description = routes[_dataset_path(group, dataset, spec)].description
                first = description.split(".")[0]
                assert len(first) > 3, description

    def test_discovery_commands_registered(self):
        routes = _routes_by_path()
        assert "/datasets" in routes
        assert "/facet_options" in routes

    def test_report_commands_registered_without_commodity(self):
        import openbb_us_eia

        routes = _routes_by_path()
        expected = not openbb_us_eia.COMMODITY_INSTALLED
        assert ("/petroleum_status_report" in routes) is expected
        assert ("/short_term_energy_outlook" in routes) is expected


class TestDatasetsCommand:
    """The dataset catalog command."""

    @pytest.mark.asyncio
    async def test_all_groups(self):
        result = await datasets()
        assert len(result.results) == 218

    @pytest.mark.asyncio
    async def test_filtered_group(self):
        result = await datasets(group="coal")
        assert len(result.results) == 13
        record = next(
            row
            for row in result.results
            if row["dataset"] == "exports_imports_quantity_price"
        )
        assert record["route"] == "coal/exports-imports-quantity-price"
        assert "coal_rank" in record["filters"]
        assert "quantity" in record["data_columns"]


class TestFacetOptionsCommand:
    """The live facet options command."""

    @pytest.mark.asyncio
    async def test_unknown_facet_raises(self):
        with pytest.raises(OpenBBError, match="not a filter"):
            await facet_options(group="coal", facet="balancing_authority")

    @pytest.mark.asyncio
    async def test_catalogued_facet_served_with_param_slugs(self):
        result = await facet_options(
            group="coal", facet="coal_rank", dataset="exports_imports_quantity_price"
        )
        record = next(item for item in result.results if item["code"] == "MET")
        assert record == {
            "value": "metallurgical",
            "label": "Metallurgical",
            "code": "MET",
        }

    @pytest.mark.asyncio
    async def test_uncatalogued_facet_fetched_live(self, monkeypatch):
        from openbb_core.provider.utils import helpers as core_helpers

        captured: dict = {}

        async def fake_amake_request(url, response_callback=None, **kwargs):
            captured["url"] = url
            return {
                "response": {
                    "facets": [
                        {"id": "NUS", "name": "U.S."},
                        {"id": "SCA", "name": "California"},
                    ]
                }
            }

        monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
        result = await facet_options(
            group="petroleum",
            facet="series",
            dataset="pad_district_exports_by_destination",
        )
        assert "/petroleum/move/expcp/facet/series" in captured["url"]
        assert result.results == [
            {"value": "SCA", "label": "California", "code": "SCA"},
            {"value": "NUS", "label": "U.S.", "code": "NUS"},
        ]

    @pytest.mark.asyncio
    async def test_default_dataset_is_first_of_group(self, monkeypatch):
        from openbb_core.provider.utils import helpers as core_helpers

        captured: dict = {}

        async def fake_amake_request(url, response_callback=None, **kwargs):
            captured["url"] = url
            return {"response": {"facets": []}}

        monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
        await facet_options(group="petroleum", facet="series")
        first = catalog.dataset_choices("petroleum")[0]
        assert catalog.get_dataset("petroleum", first)["path"] in captured["url"]


class TestModelCommandBodies:
    """Model command bodies delegate to ``OBBject.from_query``."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "path",
        sorted(
            path
            for path, route in _routes_by_path().items()
            if (route.openapi_extra or {}).get("model")
        ),
    )
    async def test_body_calls_from_query(self, path):
        endpoint = _routes_by_path()[path].endpoint
        with (
            patch("openbb_us_eia.eia_router.OBBQuery", new=MagicMock()),
            patch(
                "openbb_us_eia.eia_router.OBBject.from_query",
                new=AsyncMock(return_value="OBBJECT"),
            ) as mock_from_query,
        ):
            result = await endpoint(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert result == "OBBJECT"
        mock_from_query.assert_awaited_once()


class TestAppsJson:
    """The Workspace app definition endpoint."""

    @pytest.mark.asyncio
    async def test_serves_app_definition(self):
        from openbb_us_eia.eia_router import get_eia_apps_json

        apps = await get_eia_apps_json()
        assert isinstance(apps, list)
        assert apps

    @pytest.mark.asyncio
    async def test_unreadable_file_returns_empty(self, monkeypatch):
        import json

        from openbb_us_eia.eia_router import get_eia_apps_json

        def broken(_file):
            raise ValueError("bad json")

        monkeypatch.setattr(json, "load", broken)
        assert await get_eia_apps_json() == []
