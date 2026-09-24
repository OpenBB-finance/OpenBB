"""Tests for the EIA APIv2 dataset models and their shared fetcher pipeline."""

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pydantic import ValidationError

from openbb_us_eia import eia_provider
from openbb_us_eia.models.registry import DATASET_FETCHERS
from openbb_us_eia.utils import catalog
from openbb_us_eia.utils.api_query import EiaApiQueryParams
from openbb_us_eia.utils.catalog import DATASET_GROUPS, STANDARD_FIELDS, model_name

API_MODELS = {
    name: fetcher
    for name, fetcher in eia_provider.fetcher_dict.items()
    if isinstance(fetcher, type)
    and issubclass(fetcher.query_params_type, EiaApiQueryParams)
    and name.startswith("Eia")
}

COAL_EXPORTS = DATASET_FETCHERS["EiaCoalExportsImportsQuantityPrice"]
COAL_PRICE_BY_RANK = DATASET_FETCHERS["EiaCoalPriceByRank"]
GRID_DEMAND = DATASET_FETCHERS["EiaElectricityGridDemand"]
COALBED_PRODUCTION = DATASET_FETCHERS["EiaNaturalGasCoalbedMethaneProduction"]


def dataset_facets(query_type) -> dict:
    """Return the facets that apply to a model, merged for whole-group models."""
    group = query_type.__group__
    if query_type.__dataset__:
        return catalog.get_dataset(group, query_type.__dataset__)["facets"]
    merged: dict = {}
    for spec in catalog.get_group(group)["datasets"].values():
        for facet, detail in spec["facets"].items():
            merged.setdefault(facet, detail)
    return merged


def split_facets(facets: dict) -> tuple[set, set]:
    """Split facets into real filters and fixed single-value facets."""
    filterable = {
        facet: detail
        for facet, detail in facets.items()
        if detail.get("filterable", True)
    }
    fixed = {
        facet
        for facet, detail in filterable.items()
        if len(detail.get("choices") or []) == 1
    }
    return set(filterable) - fixed, fixed


class TestModelRegistration:
    """Every catalog dataset and group is served by a registered, wired model."""

    def test_every_dataset_has_a_fetcher(self):
        for group in DATASET_GROUPS:
            for dataset in catalog.dataset_choices(group):
                name = model_name(group, dataset)
                assert name in eia_provider.fetcher_dict
                assert DATASET_FETCHERS[name] is eia_provider.fetcher_dict[name]

    def test_all_groups_covered(self):
        groups = {
            fetcher.query_params_type.__group__ for fetcher in API_MODELS.values()
        }
        assert groups == set(catalog.load_catalog())

    @pytest.mark.parametrize("name", sorted(API_MODELS))
    def test_generics_resolve(self, name):
        fetcher = API_MODELS[name]
        assert issubclass(fetcher.query_params_type, EiaApiQueryParams)
        assert fetcher.data_type.__name__ == f"{name}Data"

    @pytest.mark.parametrize("name", sorted(API_MODELS))
    def test_facet_fields_match_catalog(self, name):
        query_type = API_MODELS[name].query_params_type
        declared = set(query_type.model_fields) - STANDARD_FIELDS
        filters, fixed = split_facets(dataset_facets(query_type))
        assert declared == filters
        assert not declared & fixed

    @pytest.mark.parametrize("name", sorted(API_MODELS))
    def test_default_query_validates(self, name):
        fetcher = API_MODELS[name]
        query = fetcher.transform_query({})
        assert query.dataset_key in catalog.dataset_choices(query.__group__)


class TestSingleValueParametersAreNotParameters:
    """A dimension with exactly one possible value is applied, never exposed."""

    def test_single_frequency_dataset_has_no_frequency_field(self):
        spec = catalog.get_dataset("coal", "price_by_rank")
        assert list(spec["frequencies"]) == ["annual"]
        assert "frequency" not in COAL_PRICE_BY_RANK.query_params_type.model_fields

    def test_single_column_dataset_has_no_data_type_field(self):
        spec = catalog.get_dataset("coal", "price_by_rank")
        assert list(spec["data_columns"]) == ["price"]
        assert "data_type" not in COAL_PRICE_BY_RANK.query_params_type.__annotations__

    def test_fixed_facet_is_not_a_query_parameter(self):
        query_type = COALBED_PRODUCTION.query_params_type
        _, fixed = split_facets(dataset_facets(query_type))
        assert fixed == {"process", "product"}
        assert not fixed & set(query_type.model_fields)

    def test_fixed_facet_is_rejected_as_an_unknown_parameter(self):
        with pytest.raises(OpenBBError, match="Unknown parameter"):
            COALBED_PRODUCTION.transform_query({"product": "EPG0"})

    @pytest.mark.asyncio
    async def test_fixed_facet_still_filters_the_request(self, monkeypatch):
        from openbb_core.provider.utils import helpers as core_helpers

        captured: dict = {}

        async def fake_amake_request(url, response_callback=None, **kwargs):
            captured["url"] = url
            return {
                "response": {
                    "total": "1",
                    "dateFormat": "YYYY",
                    "data": [{"period": "2023", "value": "7"}],
                }
            }

        monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
        rows = await COALBED_PRODUCTION.fetch_data({}, {"eia_api_key": "MOCK_KEY"})
        assert "facets%5Bprocess%5D%5B%5D=R52" in captured["url"]
        assert "facets%5Bproduct%5D%5B%5D=EPG0" in captured["url"]
        assert rows[0].model_dump()["value"] == 7.0

    def test_single_frequency_still_selects_the_dataset_default(self):
        spec = catalog.get_dataset("coal", "price_by_rank")
        frequency, detail = catalog.resolve_frequency(spec, None)
        assert frequency == "annual"
        assert detail["format"] == "YYYY"

    def test_single_column_still_requests_that_column(self):
        spec = catalog.get_dataset("coal", "price_by_rank")
        assert catalog.resolve_data_columns(spec, None) == [
            spec["data_columns"]["price"]["id"]
        ]


class TestTransformQueryValidation:
    """The catalog validation surfaces clear errors at query time."""

    def test_invalid_frequency_rejected_by_literal(self):
        with pytest.raises(ValidationError, match="frequency"):
            COAL_EXPORTS.transform_query({"frequency": "hourly"})

    def test_invalid_data_type_raises(self):
        with pytest.raises(OpenBBError, match="Invalid data_type"):
            COAL_EXPORTS.transform_query({"data_type": "capacity"})

    def test_frequency_restricted_facet_raises(self):
        with pytest.raises(OpenBBError, match="only applies"):
            GRID_DEMAND.transform_query({"timezone": "eastern"})

    def test_invalid_facet_value_lists_choices(self):
        with pytest.raises(OpenBBError, match="metallurgical") as excinfo:
            COAL_EXPORTS.transform_query({"coal_rank": "ANTHRACITE"})
        assert "Invalid coal_rank value(s): ANTHRACITE" in str(excinfo.value)

    def test_facet_value_casing_corrected(self):
        query = COAL_EXPORTS.transform_query({"coal_rank": "met"})
        assert query.coal_rank == "met"

    def test_unknown_parameter_lists_valid_filters(self):
        with pytest.raises(OpenBBError, match="Unknown parameter") as excinfo:
            GRID_DEMAND.transform_query({"region": "united_states_lower_48"})
        assert "respondent" in str(excinfo.value)


class TestSchemaIsolation:
    """Per-model schema extras must not leak through the shared base class.

    The registry map walks the class family and lets a base-class field
    overwrite the child's, so ``data_type`` must be declared on every concrete
    model rather than on ``EiaApiQueryParams``.
    """

    def test_base_class_does_not_declare_data_type(self):
        assert "data_type" not in EiaApiQueryParams.model_fields

    @pytest.mark.parametrize("name", sorted(API_MODELS))
    def test_data_type_declared_only_when_the_dataset_has_a_choice(self, name):
        query_type = API_MODELS[name].query_params_type
        dataset = (
            query_type.__dataset__ or catalog.dataset_choices(query_type.__group__)[-1]
        )
        columns = catalog.get_dataset(query_type.__group__, dataset)["data_columns"]
        declared = "data_type" in query_type.__annotations__
        if query_type.__dataset__:
            assert declared is (len(columns) > 1)

    def test_data_type_choices_are_model_specific(self):
        nuclear = DATASET_FETCHERS["EiaNuclearOutagesUsNuclearOutages"]
        coal_choices = COAL_EXPORTS.query_params_type.__json_schema_extra__[
            "data_type"
        ]["choices"]
        nuclear_choices = nuclear.query_params_type.__json_schema_extra__["data_type"][
            "choices"
        ]
        assert coal_choices == ["price", "quantity"]
        assert nuclear_choices == ["capacity", "outage", "percent_outage"]


SAMPLE_PERIODS = {
    "YYYY": "2024",
    "YYYY-MM": "2024-01",
    'YYYY-"Q"Q': "2024-Q1",
    "YYYY-MM-DD": "2024-01-05",
    'YYYY-MM-DD"T"HH24': "2024-01-05T00",
    'YYYY-MM-DD"T"HH24TZH': "2024-01-05T00-05",
}


class TestEveryModelPipeline:
    """Every generated model runs its full TET pipeline over a stubbed page."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name", sorted(API_MODELS))
    async def test_fetch_data_round_trip(self, name, monkeypatch):
        from openbb_core.provider.utils import helpers as core_helpers

        fetcher = API_MODELS[name]
        query_type = fetcher.query_params_type
        group = query_type.__group__
        dataset = query_type.__dataset__ or catalog.dataset_choices(group)[-1]
        spec = catalog.get_dataset(group, dataset)
        _, freq_spec = catalog.resolve_frequency(spec, None)
        period = SAMPLE_PERIODS[freq_spec["format"]]
        row: dict = {"period": period}
        for detail in spec["facets"].values():
            row[detail["id"]] = "X"
        for detail in spec["data_columns"].values():
            row[detail["id"]] = "1.5" if detail.get("numeric", True) else "text"

        async def fake_amake_request(url, response_callback=None, **kwargs):
            return {
                "response": {
                    "total": "1",
                    "dateFormat": freq_spec["format"],
                    "data": [row],
                }
            }

        monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
        rows = await fetcher.fetch_data({}, {"eia_api_key": "MOCK_KEY"})
        assert len(rows) == 1
        record = rows[0].model_dump(exclude_none=True)
        for column, detail in spec["data_columns"].items():
            assert record[column] == (1.5 if detail.get("numeric", True) else "text")


class TestFetcherPipeline:
    """The shared fetcher pipeline over stubbed HTTP responses."""

    @pytest.mark.asyncio
    async def test_fetch_data_end_to_end(self, monkeypatch):
        from openbb_core.provider.utils import helpers as core_helpers

        captured: dict = {}

        async def fake_amake_request(url, response_callback=None, **kwargs):
            captured["url"] = url
            return {
                "response": {
                    "total": "2",
                    "dateFormat": 'YYYY-"Q"Q',
                    "data": [
                        {
                            "period": "2023-Q2",
                            "coalRankId": "MET",
                            "quantity": "10",
                            "price": "1.5",
                        },
                        {
                            "period": "2023-Q1",
                            "coalRankId": "MET",
                            "quantity": "20",
                            "price": "2.5",
                        },
                    ],
                }
            }

        monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
        rows = await COAL_EXPORTS.fetch_data(
            {
                "frequency": "quarterly",
                "coal_rank": "MET",
                "start_date": date(2023, 1, 1),
                "end_date": date(2023, 6, 30),
            },
            {"eia_api_key": "MOCK_KEY"},
        )
        assert "facets%5BcoalRankId%5D%5B%5D=MET" in captured["url"]
        assert "start=2023-Q1" in captured["url"]
        assert "end=2023-Q2" in captured["url"]
        assert [row.date for row in rows] == [date(2023, 1, 1), date(2023, 4, 1)]
        assert rows[0].model_dump()["quantity"] == 20.0

    @pytest.mark.asyncio
    async def test_grid_daily_frequency_routes_to_daily_path(self, monkeypatch):
        from openbb_core.provider.utils import helpers as core_helpers

        captured: dict = {}

        async def fake_amake_request(url, response_callback=None, **kwargs):
            captured["url"] = url
            return {
                "response": {
                    "total": "1",
                    "dateFormat": "YYYY-MM-DD",
                    "data": [{"period": "2025-06-01", "value": "42"}],
                }
            }

        monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
        rows = await GRID_DEMAND.fetch_data(
            {"frequency": "daily", "timezone": "eastern"},
            {"eia_api_key": "MOCK_KEY"},
        )
        assert "/electricity/rto/daily-region-data/data/" in captured["url"]
        assert rows[0].model_dump()["value"] == 42.0

    @pytest.mark.asyncio
    async def test_desc_sort_and_limit_applied(self, monkeypatch):
        from openbb_core.provider.utils import helpers as core_helpers

        async def fake_amake_request(url, response_callback=None, **kwargs):
            return {
                "response": {
                    "total": "3",
                    "dateFormat": "YYYY",
                    "data": [
                        {"period": "2022", "price": "3"},
                        {"period": "2021", "price": "2"},
                        {"period": "2020", "price": "1"},
                    ],
                }
            }

        monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
        rows = await COAL_PRICE_BY_RANK.fetch_data(
            {"sort": "desc", "limit": 2},
            {"eia_api_key": "MOCK_KEY"},
        )
        assert [row.date.year for row in rows] == [2022, 2021]
