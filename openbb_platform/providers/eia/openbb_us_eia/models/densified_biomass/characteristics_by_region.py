"""Characteristics by Region model."""

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


class EiaDensifiedBiomassCharacteristicsByRegionQueryParams(EiaApiQueryParams):
    """Characteristics by Region. Densified biomass characteristics includes fuel type, average ash, heat, and moisture content by region. Source: EIA-63C Report: www.eia.gov/biomass/

    Source: https://www.eia.gov/opendata/browser/densified-biomass/characteristics-by-region
    """

    __group__ = "densified_biomass"
    __dataset__ = "characteristics_by_region"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": ["average_ash", "average_heat", "average_moisture"],
        },
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
            "choices": ["east", "south", "west"],
        },
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: average_ash (percent by weight); average_heat (btu/lb); average_moisture (percent by weight).",
    )
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
    region: Literal["east", "south", "west"] | None = Field(
        default=None,
        description="Region filter.",
    )


class EiaDensifiedBiomassCharacteristicsByRegionData(EiaApiData):
    """Characteristics by Region. Densified biomass characteristics includes fuel type, average ash, heat, and moisture content by region. Source: EIA-63C Report: www.eia.gov/biomass/"""

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
    average_ash: float | None = Field(
        default=None,
        description="Average ash (percent by weight). Withheld or unavailable values return as null.",
    )
    average_heat: float | None = Field(
        default=None,
        description="Average heat (btu/lb). Withheld or unavailable values return as null.",
    )
    average_moisture: float | None = Field(
        default=None,
        description="Average moisture (percent by weight). Withheld or unavailable values return as null.",
    )


class EiaDensifiedBiomassCharacteristicsByRegionFetcher(
    Fetcher[
        EiaDensifiedBiomassCharacteristicsByRegionQueryParams,
        list[EiaDensifiedBiomassCharacteristicsByRegionData],
    ]
):
    """Characteristics by Region fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaDensifiedBiomassCharacteristicsByRegionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaDensifiedBiomassCharacteristicsByRegionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaDensifiedBiomassCharacteristicsByRegionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaDensifiedBiomassCharacteristicsByRegionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaDensifiedBiomassCharacteristicsByRegionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaDensifiedBiomassCharacteristicsByRegionData, query, data
        )
