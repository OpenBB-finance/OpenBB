"""Stocks of Motor Gasoline, Distillate Fuel Oil, Residual Fuel Oil, Propane and Propylene model."""

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


class EiaPetroleumStocksOfSelectedProductsQueryParams(EiaApiQueryParams):
    """Stocks of Motor Gasoline, Distillate Fuel Oil, Residual Fuel Oil, Propane and Propylene. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/stoc/ts
    """

    __group__ = "petroleum"
    __dataset__ = "stocks_of_selected_products"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "distillate_fuel_oil",
                "distillate_fuel_oil_0_to_15_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
                "propane_and_propylene",
                "residual_fuel_oil",
                "total_gasoline",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "padd_1",
                "padd_1a",
                "padd_1b",
                "padd_1c",
                "padd_2",
                "padd_3",
                "padd_4",
                "padd_5",
                "us",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "central_atlantic_padd_1b_ending_stocks_of_distillate_fuel_oil_thousand_barrels",
                "central_atlantic_ending_stocks_of_distillate_fuel_oil_0_to",
                "central_atlantic_padd_1b_ending_stocks_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels",
                "central_atlantic_padd_1b_ending_stocks_of_distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur_thousand_barrels",
                "central_atlantic_ending_stocks_of_propane_and_propylene",
                "central_atlantic_ending_stocks_of_residual_fuel_oil",
                "central_atlantic_ending_stocks_of_total_gasoline",
                "east_coast_ending_stocks_of_distillate_fuel_oil",
                "east_coast_ending_stocks_of_distillate_fuel_oil_0_to_15_ppm",
                "east_coast_padd_1_ending_stocks_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels",
                "east_coast_padd_1_ending_stocks_of_distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur_thousand_barrels",
                "east_coast_ending_stocks_of_propane_and_propylene",
                "east_coast_ending_stocks_of_residual_fuel_oil",
                "east_coast_ending_stocks_of_total_gasoline",
                "gulf_coast_ending_stocks_of_distillate_fuel_oil",
                "gulf_coast_ending_stocks_of_distillate_fuel_oil_0_to_15_ppm",
                "gulf_coast_padd_3_ending_stocks_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels",
                "gulf_coast_padd_3_ending_stocks_of_distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur_thousand_barrels",
                "gulf_coast_ending_stocks_of_propane_and_propylene",
                "gulf_coast_ending_stocks_of_residual_fuel_oil",
                "gulf_coast_ending_stocks_of_total_gasoline",
                "lower_atlantic_ending_stocks_of_distillate_fuel_oil",
                "lower_atlantic_ending_stocks_of_distillate_fuel_oil_0_to_15",
                "lower_atlantic_padd_1c_ending_stocks_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels",
                "lower_atlantic_padd_1c_ending_stocks_of_distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur_thousand_barrels",
                "lower_atlantic_ending_stocks_of_propane_and_propylene",
                "lower_atlantic_ending_stocks_of_residual_fuel_oil",
                "lower_atlantic_ending_stocks_of_total_gasoline",
                "midwest_ending_stocks_of_distillate_fuel_oil",
                "midwest_ending_stocks_of_distillate_fuel_oil_0_to_15_ppm",
                "midwest_padd_2_ending_stocks_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels",
                "midwest_padd_2_ending_stocks_of_distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur_thousand_barrels",
                "midwest_ending_stocks_of_propane_and_propylene",
                "midwest_ending_stocks_of_residual_fuel_oil",
                "midwest_ending_stocks_of_total_gasoline",
                "new_england_ending_stocks_of_distillate_fuel_oil_0_to_15",
                "new_england_padd_1a_ending_stocks_of_distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur_thousand_barrels",
                "new_england_ending_stocks_of_distillate_fuel_oil",
                "new_england_padd_1a_ending_stocks_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels",
                "new_england_ending_stocks_of_propane_and_propylene",
                "new_england_ending_stocks_of_residual_fuel_oil",
                "new_england_ending_stocks_of_total_gasoline",
                "rocky_mountain_ending_stocks_of_distillate_fuel_oil",
                "rocky_mountain_ending_stocks_of_distillate_fuel_oil_0_to_15",
                "rocky_mountain_padd_4_ending_stocks_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels",
                "rocky_mountain_padd_4_ending_stocks_of_distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur_thousand_barrels",
                "rocky_mountain_ending_stocks_of_propane_and_propylene",
                "rocky_mountain_ending_stocks_of_residual_fuel_oil",
                "rocky_mountain_ending_stocks_of_total_gasoline",
                "us_ending_stocks_of_distillate_fuel_oil",
                "us_ending_stocks_of_distillate_fuel_oil_0_to_15_ppm_sulfur",
                "us_ending_stocks_of_distillate_fuel_oil_greater_than_500",
                "us_ending_stocks_of_distillate_fuel_oil_greater_than_15_to",
                "us_ending_stocks_of_propane_and_propylene",
                "us_ending_stocks_of_residual_fuel_oil",
                "us_ending_stocks_of_total_gasoline",
                "west_coast_ending_stocks_of_distillate_fuel_oil",
                "west_coast_ending_stocks_of_distillate_fuel_oil_0_to_15_ppm",
                "west_coast_padd_5_ending_stocks_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels",
                "west_coast_padd_5_ending_stocks_of_distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur_thousand_barrels",
                "west_coast_ending_stocks_of_propane_and_propylene",
                "west_coast_ending_stocks_of_residual_fuel_oil",
                "west_coast_ending_stocks_of_total_gasoline",
            ],
        },
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumStocksOfSelectedProductsData(EiaApiData):
    """Stocks of Motor Gasoline, Distillate Fuel Oil, Residual Fuel Oil, Propane and Propylene. EIA petroleum gas survey data"""

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


class EiaPetroleumStocksOfSelectedProductsFetcher(
    Fetcher[
        EiaPetroleumStocksOfSelectedProductsQueryParams,
        list[EiaPetroleumStocksOfSelectedProductsData],
    ]
):
    """Stocks of Motor Gasoline, Distillate Fuel Oil, Residual Fuel Oil, Propane and Propylene fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumStocksOfSelectedProductsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumStocksOfSelectedProductsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumStocksOfSelectedProductsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumStocksOfSelectedProductsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumStocksOfSelectedProductsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumStocksOfSelectedProductsData, query, data
        )
