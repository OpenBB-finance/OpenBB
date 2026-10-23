"""Weekly Ethanol Plant Production model."""

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


class EiaPetroleumWeeklyEthanolPlantProductionQueryParams(EiaApiQueryParams):
    """Weekly Ethanol Plant Production. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/wprode
    """

    __group__ = "petroleum"
    __dataset__ = "weekly_ethanol_plant_production"
    __json_schema_extra__ = {
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "east_coast_oxygenate_plant_production_of_fuel_ethanol",
                "gulf_coast_oxygenate_plant_production_of_fuel_ethanol",
                "midwest_oxygenate_plant_production_of_fuel_ethanol",
                "rocky_mountain_oxygenate_plant_production_of_fuel_ethanol",
                "us_oxygenate_plant_production_of_fuel_ethanol",
                "west_coast_oxygenate_plant_production_of_fuel_ethanol",
            ],
        },
    }

    frequency: Literal["four-week-average", "weekly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'weekly'.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumWeeklyEthanolPlantProductionData(EiaApiData):
    """Weekly Ethanol Plant Production. EIA petroleum gas survey data"""

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


class EiaPetroleumWeeklyEthanolPlantProductionFetcher(
    Fetcher[
        EiaPetroleumWeeklyEthanolPlantProductionQueryParams,
        list[EiaPetroleumWeeklyEthanolPlantProductionData],
    ]
):
    """Weekly Ethanol Plant Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumWeeklyEthanolPlantProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumWeeklyEthanolPlantProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumWeeklyEthanolPlantProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumWeeklyEthanolPlantProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumWeeklyEthanolPlantProductionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumWeeklyEthanolPlantProductionData, query, data
        )
