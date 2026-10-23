"""Test the JODI model validators, views, and error branches."""

import asyncio
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_jodi.models.gas_balance import JodiGasBalanceFetcher
from openbb_jodi.models.gas_demand import JodiGasDemandFetcher, JodiGasDemandQueryParams
from openbb_jodi.models.gas_imports import JodiGasImportsFetcher
from openbb_jodi.models.oil_balance import (
    JodiOilBalanceFetcher,
    JodiOilBalanceQueryParams,
)
from openbb_jodi.models.oil_demand_by_product import JodiOilDemandByProductFetcher
from openbb_jodi.models.oil_production import (
    JodiOilProductionFetcher,
    JodiOilProductionQueryParams,
)

DATES = {"start_date": date(2024, 1, 1), "end_date": date(2024, 3, 31)}


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, "united_states"),
        ("", "united_states"),
        ("SA", "saudi_arabia"),
        ("Saudi Arabia", "saudi_arabia"),
    ],
)
def test_single_country_validator(value, expected):
    assert JodiOilBalanceQueryParams(country=value).country == expected


def test_single_country_validator_rejects_multiple():
    with pytest.raises(OpenBBError, match="Only one country"):
        JodiOilBalanceQueryParams(country="united_states,saudi_arabia")


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, None),
        ("", None),
        ("US", "united_states"),
        (["US", "Saudi Arabia"], "united_states,saudi_arabia"),
        ("united_states,us", "united_states"),
    ],
)
def test_multi_country_validator(value, expected):
    assert JodiOilProductionQueryParams(country=value).country == expected


def test_country_validator_invalid():
    with pytest.raises(OpenBBError, match="Invalid country: 'atlantis'"):
        JodiOilProductionQueryParams(country="atlantis")


def test_token_normalization():
    params = JodiOilBalanceQueryParams(product="Crude Oil", unit="KBD")
    assert params.product == "crude_oil"
    assert params.unit == "kbd"
    params = JodiGasDemandQueryParams(measure=None, unit=None)
    assert params.measure == "observed"
    assert params.unit == "m3"


def test_token_invalid():
    with pytest.raises(ValidationError):
        JodiOilBalanceQueryParams(unit="furlongs")
    with pytest.raises(ValidationError):
        JodiOilProductionQueryParams(product="gasoline")  # secondary-only product


def _fetch(fetcher, params: dict):
    return asyncio.run(fetcher.fetch_data(params, {}))


def test_start_after_end():
    with pytest.raises(OpenBBError, match="start_date must be"):
        _fetch(
            JodiOilBalanceFetcher,
            {"start_date": date(2024, 2, 1), "end_date": date(2024, 1, 1)},
        )


def test_oil_dates_before_data():
    with pytest.raises(OpenBBError, match="The data starts in 2002"):
        _fetch(
            JodiOilProductionFetcher,
            {"start_date": date(2000, 1, 1), "end_date": date(2001, 12, 31)},
        )


def test_gas_dates_before_data():
    with pytest.raises(OpenBBError, match="The data starts in 2009"):
        _fetch(
            JodiGasBalanceFetcher,
            {"start_date": date(2007, 1, 1), "end_date": date(2008, 12, 31)},
        )


@pytest.mark.usefixtures("mock_download")
def test_empty_result():
    with pytest.raises(EmptyDataError):
        _fetch(
            JodiOilProductionFetcher,
            {"start_date": date(2024, 4, 1), "end_date": date(2024, 12, 31)},
        )


@pytest.mark.usefixtures("mock_download")
def test_oil_balance_view():
    result = _fetch(
        JodiOilBalanceFetcher,
        {"country": "united_states", "product": "crude_oil", "unit": "kbbl", **DATES},
    )
    assert len(result.result) == 3
    row = result.result[0]
    assert row.production is not None
    assert row.closing_stocks is not None
    assert row.refinery_output is None  # secondary-only flow
    assert result.metadata["country"] == "United States"
    assert result.metadata["product"] == "Crude oil"
    assert result.metadata["unit"] == "Thousand barrels"
    assert result.metadata["assessments"]["production"] is not None


@pytest.mark.usefixtures("mock_download")
def test_oil_balance_secondary_product():
    result = _fetch(
        JodiOilBalanceFetcher,
        {"country": "united_states", "product": "gasoline", "unit": "kbd", **DATES},
    )
    row = result.result[0]
    assert row.refinery_output is not None
    assert row.demand is not None
    assert row.refinery_intake is None  # primary-only flow


@pytest.mark.usefixtures("mock_download")
def test_oil_production_comparison_view():
    result = _fetch(JodiOilProductionFetcher, {**DATES})
    row = result.result[0].model_dump(exclude_none=True)
    # Columns are countries, alphabetical, after the date.
    # Russia is in the sample but reports no kb/d production values.
    assert list(row) == ["date", "saudi_arabia", "united_states"]
    assert result.metadata["flow"] == "Production"
    assert result.metadata["assessments"]["saudi_arabia"] is not None


@pytest.mark.usefixtures("mock_download")
def test_gas_empty_result():
    with pytest.raises(EmptyDataError):
        _fetch(
            JodiGasBalanceFetcher,
            {
                "country": "norway",
                "start_date": date(2024, 4, 1),
                "end_date": date(2024, 12, 31),
            },
        )


@pytest.mark.usefixtures("mock_download")
def test_oil_demand_by_product_view():
    result = _fetch(
        JodiOilDemandByProductFetcher, {"country": "united_states", **DATES}
    )
    row = result.result[0]
    assert row.gasoline is not None
    assert row.total_products is not None
    assert result.metadata["flow"] == "Demand"


@pytest.mark.usefixtures("mock_download")
def test_gas_balance_view():
    result = _fetch(JodiGasBalanceFetcher, {"country": "norway", **DATES})
    row = result.result[0]
    assert row.production is not None
    assert row.pipeline_exports is not None
    assert result.metadata["product"] == "Natural gas"


@pytest.mark.usefixtures("mock_download")
def test_gas_demand_measures_differ():
    observed = _fetch(
        JodiGasDemandFetcher,
        {"country": "united_states", "measure": "observed", **DATES},
    )
    calculated = _fetch(
        JodiGasDemandFetcher,
        {"country": "united_states", "measure": "calculated", **DATES},
    )
    assert observed.metadata["flow"] == "Gross inland deliveries (observed)"
    assert calculated.metadata["flow"] == "Gross inland deliveries (calculated)"
    obs = observed.result[0].model_dump(exclude_none=True)["united_states"]
    calc = calculated.result[0].model_dump(exclude_none=True)["united_states"]
    assert obs != calc


@pytest.mark.usefixtures("mock_download")
def test_gas_imports_flow_selection():
    total = _fetch(JodiGasImportsFetcher, {"country": "united_states", **DATES})
    pipeline = _fetch(
        JodiGasImportsFetcher,
        {"country": "united_states", "flow": "pipeline", **DATES},
    )
    assert total.metadata["flow"] == "Imports"
    assert pipeline.metadata["flow"] == "Pipeline imports"
    total_value = total.result[0].model_dump(exclude_none=True)["united_states"]
    pipeline_value = pipeline.result[0].model_dump(exclude_none=True)["united_states"]
    assert pipeline_value <= total_value
