"""Costs of Crude Oil and Natural Gas Wells Drilled model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_us_eia.utils.api_query import (
    EiaApiData,
    EiaApiQueryParams,
    extract_dataset_data,
    transform_dataset_data,
    transform_dataset_query,
)


class EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledQueryParams(
    EiaApiQueryParams
):
    """Costs of Crude Oil and Natural Gas Wells Drilled. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/crd/wellcost
    """

    __group__ = "petroleum"
    __dataset__ = "costs_of_crude_oil_and_natural_gas_wells_drilled"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "nominal_cost_per_foot_of_dry_wells_drilled",
                "nominal_cost_per_well_drilled",
                "real_cost",
                "real_cost_per_foot",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": ["wells_dry", "wells_gas", "wells_oil", "wells_total"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_nominal_cost_per_crude_oil_well_drilled",
                "us_nominal_cost_per_crude_oil_natural_gas_and_dry_well",
                "us_nominal_cost_per_dry_well_drilled",
                "us_nominal_cost_per_foot_of_crude_oil_wells_drilled",
                "us_nominal_cost_per_foot_of_crude_oil_natural_gas_and_dry",
                "us_nominal_cost_per_foot_of_dry_wells_drilled",
                "us_nominal_cost_per_foot_of_natural_gas_wells_drilled",
                "us_nominal_cost_per_natural_gas_well_drilled",
                "us_real_cost_per_crude_oil_natural_gas_and_dry_well_drilled",
                "us_real_cost_per_foot_of_crude_oil_natural_gas_and_dry",
            ],
        },
    }

    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledData(EiaApiData):
    """Costs of Crude Oil and Natural Gas Wells Drilled. EIA petroleum gas survey data"""

    process: str | None = Field(
        default=None,
        description="Process code.",
    )
    process_name: str | None = Field(
        default=None,
        description="Process name.",
    )
    product: str | None = Field(
        default=None,
        description="Product code.",
    )
    product_name: str | None = Field(
        default=None,
        description="Product name.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea code.",
    )
    region_name: str | None = Field(
        default=None,
        description="DuoArea name.",
    )
    series: str | None = Field(
        default=None,
        description="Series code.",
    )
    series_name: str | None = Field(
        default=None,
        description="Series name.",
    )
    value: float | None = Field(
        default=None,
        description="Value. Withheld or unavailable values return as null.",
    )
    units: str | None = Field(
        default=None,
        description="Unit of the value.",
    )


class EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledFetcher(
    Fetcher[
        EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledQueryParams,
        list[EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledData],
    ]
):
    """Costs of Crude Oil and Natural Gas Wells Drilled fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumCostsOfCrudeOilAndNaturalGasWellsDrilledData, query, data
        )
