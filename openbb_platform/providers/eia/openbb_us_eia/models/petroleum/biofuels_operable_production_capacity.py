"""Biofuels Operable Production Capacity model."""

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


class EiaPetroleumBiofuelsOperableProductionCapacityQueryParams(EiaApiQueryParams):
    """Biofuels Operable Production Capacity. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/capbio
    """

    __group__ = "petroleum"
    __dataset__ = "biofuels_operable_production_capacity"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "biodiesel",
                "fuel_ethanol",
                "renewable_diesel_and_other_biofuels",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_biodiesel_production_capacity",
                "us_fuel_ethanol_production_capacity",
                "us_renewable_diesel_and_other_biofuels_production_capacity",
            ],
        },
    }

    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumBiofuelsOperableProductionCapacityData(EiaApiData):
    """Biofuels Operable Production Capacity. EIA petroleum gas survey data"""

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


class EiaPetroleumBiofuelsOperableProductionCapacityFetcher(
    Fetcher[
        EiaPetroleumBiofuelsOperableProductionCapacityQueryParams,
        list[EiaPetroleumBiofuelsOperableProductionCapacityData],
    ]
):
    """Biofuels Operable Production Capacity fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumBiofuelsOperableProductionCapacityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumBiofuelsOperableProductionCapacityQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumBiofuelsOperableProductionCapacityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumBiofuelsOperableProductionCapacityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumBiofuelsOperableProductionCapacityData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumBiofuelsOperableProductionCapacityData, query, data
        )
