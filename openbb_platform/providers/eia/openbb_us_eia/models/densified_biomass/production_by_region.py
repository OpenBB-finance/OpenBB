"""Production by Region model."""

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


class EiaDensifiedBiomassProductionByRegionQueryParams(EiaApiQueryParams):
    """Production by Region. Densified biomass production by region and fuel type. Source: EIA-63C Report: www.eia.gov/biomass/

    Source: https://www.eia.gov/opendata/browser/densified-biomass/production-by-region
    """

    __group__ = "densified_biomass"
    __dataset__ = "production_by_region"
    __json_schema_extra__ = {
        "fuel_type": {
            "multiple_items_allowed": True,
            "choices": [
                "compressed_bricks_log",
                "wood_pellets_premium_standard",
                "wood_pellets_utility",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["east", "south", "us_total", "west"],
        },
    }

    fuel_type: (
        Literal[
            "compressed_bricks_log",
            "wood_pellets_premium_standard",
            "wood_pellets_utility",
        ]
        | None
    ) = Field(
        default=None,
        description="Fuel Type filter.",
    )
    region: Literal["east", "south", "us_total", "west"] | None = Field(
        default=None,
        description="Region filter.",
    )


class EiaDensifiedBiomassProductionByRegionData(EiaApiData):
    """Production by Region. Densified biomass production by region and fuel type. Source: EIA-63C Report: www.eia.gov/biomass/"""

    fuel_type: str | None = Field(
        default=None,
        description="Fuel Type code.",
    )
    fuel_type_name: str | None = Field(
        default=None,
        description="Fuel Type name.",
    )
    region: str | None = Field(
        default=None,
        description="Region code.",
    )
    region_name: str | None = Field(
        default=None,
        description="Region name.",
    )
    production: float | None = Field(
        default=None,
        description="Production (tons). Withheld or unavailable values return as null.",
    )


class EiaDensifiedBiomassProductionByRegionFetcher(
    Fetcher[
        EiaDensifiedBiomassProductionByRegionQueryParams,
        list[EiaDensifiedBiomassProductionByRegionData],
    ]
):
    """Production by Region fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaDensifiedBiomassProductionByRegionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaDensifiedBiomassProductionByRegionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaDensifiedBiomassProductionByRegionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaDensifiedBiomassProductionByRegionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaDensifiedBiomassProductionByRegionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaDensifiedBiomassProductionByRegionData, query, data
        )
