"""Fuel Consumed at Biofuels Plants model."""

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


class EiaPetroleumFuelConsumedAtBiofuelsPlantsQueryParams(EiaApiQueryParams):
    """Fuel Consumed at Biofuels Plants. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/bioplfuel
    """

    __group__ = "petroleum"
    __dataset__ = "fuel_consumed_at_biofuels_plants"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "biogas_consumed_at_biofuels_plants",
                "coal_consumed_at_biofuels_plants",
                "liquefied_petroleum_gases_consumed_at_biofuels_plants",
                "natural_gas_consumed_at_biofuels_plants",
                "natural_gas_for_hydrogen_feedstock_at_biofuels_plants",
                "other_fuels_including_renewable_fuels_at_biofuels_plants",
                "purchased_electricity_consumed_at_biofuels_plants",
                "purchased_hydrogen_at_biofuels_plants",
                "purchased_steam_consumed_at_biofuels_plants",
            ],
        },
        "product": {"multiple_items_allowed": True},
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_biogas_consumed_at_biofuels_plants",
                "us_coal_consumed_at_biofuels_plants",
                "us_liquefied_petroleum_gases_consumed_at_biofuels_plants",
                "us_natural_gas_consumed_at_biofuels_plants",
                "us_natural_gas_for_hydrogen_feedstock_at_biofuels_plants",
                "us_other_fuels_including_renewable_fuels_at_biofuels_plants",
                "us_purchased_electricity_consumed_at_biofuels_plants",
                "us_purchased_hydrogen_at_biofuels_plants",
                "us_purchased_steam_consumed_at_biofuels_plants",
            ],
        },
    }

    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumFuelConsumedAtBiofuelsPlantsData(EiaApiData):
    """Fuel Consumed at Biofuels Plants. EIA petroleum gas survey data"""

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


class EiaPetroleumFuelConsumedAtBiofuelsPlantsFetcher(
    Fetcher[
        EiaPetroleumFuelConsumedAtBiofuelsPlantsQueryParams,
        list[EiaPetroleumFuelConsumedAtBiofuelsPlantsData],
    ]
):
    """Fuel Consumed at Biofuels Plants fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumFuelConsumedAtBiofuelsPlantsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumFuelConsumedAtBiofuelsPlantsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumFuelConsumedAtBiofuelsPlantsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumFuelConsumedAtBiofuelsPlantsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumFuelConsumedAtBiofuelsPlantsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumFuelConsumedAtBiofuelsPlantsData, query, data
        )
