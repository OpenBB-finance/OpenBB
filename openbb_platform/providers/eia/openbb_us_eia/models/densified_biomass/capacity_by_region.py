"""Capacity by Region model."""

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


class EiaDensifiedBiomassCapacityByRegionQueryParams(EiaApiQueryParams):
    """Capacity by Region. Densified biomass capacity includes number of facilities and number of employees. Source: EIA-63C Report: www.eia.gov/biomass/

    Source: https://www.eia.gov/opendata/browser/densified-biomass/capacity-by-region
    """

    __group__ = "densified_biomass"
    __dataset__ = "capacity_by_region"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": ["capacity", "number_of_facilities", "number_of_fte_employees"],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["east", "south", "us_total", "west"],
        },
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: capacity (tons); number_of_facilities (number of facilities); number_of_fte_employees (number of fte employees).",
    )
    region: Literal["east", "south", "us_total", "west"] | None = Field(
        default=None,
        description="Region filter.",
    )


class EiaDensifiedBiomassCapacityByRegionData(EiaApiData):
    """Capacity by Region. Densified biomass capacity includes number of facilities and number of employees. Source: EIA-63C Report: www.eia.gov/biomass/"""

    region: str | None = Field(
        default=None,
        description="Region code.",
    )
    region_name: str | None = Field(
        default=None,
        description="Region name.",
    )
    capacity: float | None = Field(
        default=None,
        description="Capacity (tons). Withheld or unavailable values return as null.",
    )
    number_of_facilities: float | None = Field(
        default=None,
        description="Number of facilities (number of facilities). Withheld or unavailable values return as null.",
    )
    number_of_fte_employees: float | None = Field(
        default=None,
        description="Number of fte employees (number of fte employees). Withheld or unavailable values return as null.",
    )


class EiaDensifiedBiomassCapacityByRegionFetcher(
    Fetcher[
        EiaDensifiedBiomassCapacityByRegionQueryParams,
        list[EiaDensifiedBiomassCapacityByRegionData],
    ]
):
    """Capacity by Region fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaDensifiedBiomassCapacityByRegionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaDensifiedBiomassCapacityByRegionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaDensifiedBiomassCapacityByRegionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaDensifiedBiomassCapacityByRegionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaDensifiedBiomassCapacityByRegionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaDensifiedBiomassCapacityByRegionData, query, data
        )
