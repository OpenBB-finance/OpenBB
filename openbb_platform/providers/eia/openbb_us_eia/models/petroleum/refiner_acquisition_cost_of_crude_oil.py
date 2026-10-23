"""Refiner Acquisition Cost of Crude Oil model."""

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_us_eia.utils.api_query import (
    EiaApiData,
    EiaApiQueryParams,
    extract_dataset_data,
    transform_dataset_data,
    transform_dataset_query,
)


class EiaPetroleumRefinerAcquisitionCostOfCrudeOilQueryParams(EiaApiQueryParams):
    """Refiner Acquisition Cost of Crude Oil. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/rac2
    """

    __group__ = "petroleum"
    __dataset__ = "refiner_acquisition_cost_of_crude_oil"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "composite_acquisition_cost",
                "domestic_acquisition_cost",
                "imported_acquisition_cost",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "east_coast_crude_oil_composite_acquisition_cost_by_refiners",
                "east_coast_crude_oil_domestic_acquisition_cost_by_refiners",
                "east_coast_crude_oil_imported_acquisition_cost_by_refiners",
                "gulf_coast_crude_oil_composite_acquisition_cost_by_refiners",
                "gulf_coast_crude_oil_domestic_acquisition_cost_by_refiners",
                "gulf_coast_crude_oil_imported_acquisition_cost_by_refiners",
                "midwest_crude_oil_composite_acquisition_cost_by_refiners",
                "midwest_crude_oil_domestic_acquisition_cost_by_refiners",
                "midwest_crude_oil_imported_acquisition_cost_by_refiners",
                "rocky_mountain_crude_oil_composite_acquisition_cost_by",
                "rocky_mountain_crude_oil_domestic_acquisition_cost_by",
                "rocky_mountain_crude_oil_imported_acquisition_cost_by",
                "us_crude_oil_composite_acquisition_cost_by_refiners",
                "us_crude_oil_domestic_acquisition_cost_by_refiners",
                "us_crude_oil_imported_acquisition_cost_by_refiners",
                "west_coast_crude_oil_composite_acquisition_cost_by_refiners",
                "west_coast_crude_oil_domestic_acquisition_cost_by_refiners",
                "west_coast_crude_oil_imported_acquisition_cost_by_refiners",
            ],
        },
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumRefinerAcquisitionCostOfCrudeOilData(EiaApiData):
    """Refiner Acquisition Cost of Crude Oil. EIA petroleum gas survey data"""

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


class EiaPetroleumRefinerAcquisitionCostOfCrudeOilFetcher(
    Fetcher[
        EiaPetroleumRefinerAcquisitionCostOfCrudeOilQueryParams,
        list[EiaPetroleumRefinerAcquisitionCostOfCrudeOilData],
    ]
):
    """Refiner Acquisition Cost of Crude Oil fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumRefinerAcquisitionCostOfCrudeOilQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumRefinerAcquisitionCostOfCrudeOilQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumRefinerAcquisitionCostOfCrudeOilQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumRefinerAcquisitionCostOfCrudeOilQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumRefinerAcquisitionCostOfCrudeOilData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumRefinerAcquisitionCostOfCrudeOilData, query, data
        )
