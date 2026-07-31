"""Fuel Consumed at Refineries model."""

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


class EiaPetroleumFuelConsumedAtRefineriesQueryParams(EiaApiQueryParams):
    """Fuel Consumed at Refineries. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/capfuel
    """

    __group__ = "petroleum"
    __dataset__ = "fuel_consumed_at_refineries"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "catalyst_petroleum_coke_consumed_at_refineries",
                "coal_consumed_at_refineries",
                "consumed_at_refineries",
                "crude_oil_consumed_at_refineries",
                "distillate_consumed_at_refineries",
                "lpg_s_consumed_at_refineries",
                "marketable_petroleum_coke_consumed_at_refineries",
                "other_products_consumed_at_refineries",
                "petroleum_coke_consumed_at_refineries",
                "purchased_electricity_consumed_at_refineries",
                "purchased_steam_consumed_at_refineries",
                "residual_fuel_oil_consumed_at_refineries",
                "still_gas_consumed_at_refineries",
            ],
        },
        "product": {"multiple_items_allowed": True},
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "east_coast_catalyst_petroleum_coke_consumed_at_refineries",
                "east_coast_coal_consumed_at_refineries",
                "east_coast_crude_oil_consumed_at_refineries",
                "east_coast_distillate_consumed_at_refineries",
                "east_coast_hgl_s_consumed_at_refineries",
                "east_coast_marketable_petroleum_coke_consumed_at_refineries",
                "east_coast_natural_gas_consumed_at_refineries",
                "east_coast_other_products_consumed_at_refineries",
                "east_coast_petroleum_coke_consumed_at_refineries",
                "east_coast_purchased_electricity_consumed_at_refineries",
                "east_coast_purchased_steam_consumed_at_refineries",
                "east_coast_residual_fuel_oil_consumed_at_refineries",
                "east_coast_still_gas_consumed_at_refineries",
                "gulf_coast_catalyst_petroleum_coke_consumed_at_refineries",
                "gulf_coast_coal_consumed_at_refineries",
                "gulf_coast_crude_oil_consumed_at_refineries",
                "gulf_coast_distillate_consumed_at_refineries",
                "gulf_coast_hgl_s_consumed_at_refineries",
                "gulf_coast_marketable_petroleum_coke_consumed_at_refineries",
                "gulf_coast_natural_gas_consumed_at_refineries",
                "gulf_coast_other_products_consumed_at_refineries",
                "gulf_coast_petroleum_coke_consumed_at_refineries",
                "gulf_coast_purchased_electricity_consumed_at_refineries",
                "gulf_coast_purchased_steam_consumed_at_refineries",
                "gulf_coast_residual_fuel_oil_consumed_at_refineries",
                "gulf_coast_still_gas_consumed_at_refineries",
                "midwest_catalyst_petroleum_coke_consumed_at_refineries",
                "midwest_coal_consumed_at_refineries",
                "midwest_crude_oil_consumed_at_refineries",
                "midwest_distillate_consumed_at_refineries",
                "midwest_hgl_s_consumed_at_refineries",
                "midwest_marketable_petroleum_coke_consumed_at_refineries",
                "midwest_natural_gas_consumed_at_refineries",
                "midwest_other_products_consumed_at_refineries",
                "midwest_petroleum_coke_consumed_at_refineries",
                "midwest_purchased_electricity_consumed_at_refineries",
                "midwest_purchased_steam_consumed_at_refineries",
                "midwest_residual_fuel_oil_consumed_at_refineries",
                "midwest_still_gas_consumed_at_refineries",
                "rocky_mountain_catalyst_petroleum_coke_consumed_at",
                "rocky_mountain_coal_consumed_at_refineries",
                "rocky_mountain_crude_oil_consumed_at_refineries",
                "rocky_mountain_distillate_consumed_at_refineries",
                "rocky_mountain_hgl_s_consumed_at_refineries",
                "rocky_mountain_marketable_petroleum_coke_consumed_at",
                "rocky_mountain_natural_gas_consumed_at_refineries",
                "rocky_mountain_other_products_consumed_at_refineries",
                "rocky_mountain_petroleum_coke_consumed_at_refineries",
                "rocky_mountain_purchased_electricity_consumed_at_refineries",
                "rocky_mountain_purchased_steam_consumed_at_refineries",
                "rocky_mountain_residual_fuel_oil_consumed_at_refineries",
                "rocky_mountain_still_gas_consumed_at_refineries",
                "us_catalyst_petroleum_coke_consumed_at_refineries",
                "us_coal_consumed_at_refineries",
                "us_crude_oil_consumed_at_refineries",
                "us_distillate_consumed_at_refineries",
                "us_hgl_s_consumed_at_refineries",
                "us_marketable_petroleum_coke_consumed_at_refineries",
                "us_natural_gas_consumed_at_refineries",
                "us_other_products_consumed_at_refineries",
                "us_petroleum_coke_consumed_at_refineries",
                "us_purchased_electricity_consumed_at_refineries",
                "us_purchased_steam_consumed_at_refineries",
                "us_residual_fuel_oil_consumed_at_refineries",
                "us_still_gas_consumed_at_refineries",
                "west_coast_catalyst_petroleum_coke_consumed_at_refineries",
                "west_coast_coal_consumed_at_refineries",
                "west_coast_crude_oil_consumed_at_refineries",
                "west_coast_distillate_consumed_at_refineries",
                "west_coast_hgl_s_consumed_at_refineries",
                "west_coast_marketable_petroleum_coke_consumed_at_refineries",
                "west_coast_natural_gas_consumed_at_refineries",
                "west_coast_other_products_consumed_at_refineries",
                "west_coast_petroleum_coke_consumed_at_refineries",
                "west_coast_purchased_electricity_consumed_at_refineries",
                "west_coast_purchased_steam_consumed_at_refineries",
                "west_coast_residual_fuel_oil_consumed_at_refineries",
                "west_coast_still_gas_consumed_at_refineries",
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
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumFuelConsumedAtRefineriesData(EiaApiData):
    """Fuel Consumed at Refineries. EIA petroleum gas survey data"""

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


class EiaPetroleumFuelConsumedAtRefineriesFetcher(
    Fetcher[
        EiaPetroleumFuelConsumedAtRefineriesQueryParams,
        list[EiaPetroleumFuelConsumedAtRefineriesData],
    ]
):
    """Fuel Consumed at Refineries fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumFuelConsumedAtRefineriesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumFuelConsumedAtRefineriesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumFuelConsumedAtRefineriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumFuelConsumedAtRefineriesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumFuelConsumedAtRefineriesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumFuelConsumedAtRefineriesData, query, data
        )
