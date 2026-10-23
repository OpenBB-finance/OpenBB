"""Refiner Residual Fuel Oil and No 4 Fuel Sales Volumes model."""

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


class EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesQueryParams(
    EiaApiQueryParams
):
    """Refiner Residual Fuel Oil and No 4 Fuel Sales Volumes. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/cons/refres
    """

    __group__ = "petroleum"
    __dataset__ = "refiner_residual_fuel_oil_and_no4_fuel_sales_volumes"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "retail_sales_by_refiners_and_gas_plants",
                "wholesale_resale_volume_by_refiners_and_gas_plants",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "no_4_distillate",
                "residual_fuel_oil",
                "residual_fuel_oil_0_to_1_0_sulfur",
                "residual_fuel_oil_greater_than_1_sulfur",
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
                "central_atlantic_no_4_distillate_retail_sales_by_refiners",
                "central_atlantic_no_4_distillate_wholesale_resale_volume_by",
                "central_atlantic_residual_fuel_oil_retail_sales_by_refiners",
                "central_atlantic_padd_1b_residual_fuel_oil_sulfur_greater_than_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "central_atlantic_padd_1b_residual_fuel_oil_sulfur_greater_than_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "central_atlantic_padd_1b_residual_fuel_oil_sulfur_less_than_or_equal_to_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "central_atlantic_padd_1b_residual_fuel_oil_sulfur_less_than_or_equal_to_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "central_atlantic_residual_fuel_oil_wholesale_resale_volume",
                "east_coast_no_4_distillate_retail_sales_by_refiners",
                "east_coast_no_4_distillate_wholesale_resale_volume_by",
                "east_coast_residual_fuel_oil_retail_sales_by_refiners",
                "east_coast_residual_fuel_oil_sulfur_greater_than_1_retail",
                "east_coast_residual_fuel_oil_sulfur_greater_than_1",
                "east_coast_padd_1_residual_fuel_oil_sulfur_less_than_or_equal_to_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "east_coast_padd_1_residual_fuel_oil_sulfur_less_than_or_equal_to_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "east_coast_residual_fuel_oil_wholesale_resale_volume_by",
                "gulf_coast_no_4_distillate_retail_sales_by_refiners",
                "gulf_coast_no_4_distillate_wholesale_resale_volume_by",
                "gulf_coast_residual_fuel_oil_retail_sales_by_refiners",
                "gulf_coast_residual_fuel_oil_sulfur_greater_than_1_retail",
                "gulf_coast_residual_fuel_oil_sulfur_greater_than_1",
                "gulf_coast_padd_3_residual_fuel_oil_sulfur_less_than_or_equal_to_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "gulf_coast_padd_3_residual_fuel_oil_sulfur_less_than_or_equal_to_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "gulf_coast_residual_fuel_oil_wholesale_resale_volume_by",
                "lower_atlantic_no_4_distillate_retail_sales_by_refiners",
                "lower_atlantic_no_4_distillate_wholesale_resale_volume_by",
                "lower_atlantic_residual_fuel_oil_retail_sales_by_refiners",
                "lower_atlantic_padd_1c_residual_fuel_oil_sulfur_greater_than_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "lower_atlantic_padd_1c_residual_fuel_oil_sulfur_greater_than_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "lower_atlantic_padd_1c_residual_fuel_oil_sulfur_less_than_or_equal_to_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "lower_atlantic_padd_1c_residual_fuel_oil_sulfur_less_than_or_equal_to_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "lower_atlantic_residual_fuel_oil_wholesale_resale_volume_by",
                "midwest_no_4_distillate_retail_sales_by_refiners",
                "midwest_no_4_distillate_wholesale_resale_volume_by_refiners",
                "midwest_residual_fuel_oil_retail_sales_by_refiners",
                "midwest_residual_fuel_oil_sulfur_greater_than_1_retail",
                "midwest_residual_fuel_oil_sulfur_greater_than_1_wholesale",
                "midwest_padd_2_residual_fuel_oil_sulfur_less_than_or_equal_to_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "midwest_padd_2_residual_fuel_oil_sulfur_less_than_or_equal_to_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "midwest_residual_fuel_oil_wholesale_resale_volume_by",
                "new_england_no_4_distillate_retail_sales_by_refiners",
                "new_england_no_4_distillate_wholesale_resale_volume_by",
                "new_england_residual_fuel_oil_retail_sales_by_refiners",
                "new_england_residual_fuel_oil_sulfur_greater_than_1_retail",
                "new_england_residual_fuel_oil_sulfur_greater_than_1",
                "new_england_padd_1a_residual_fuel_oil_sulfur_less_than_or_equal_to_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "new_england_padd_1a_residual_fuel_oil_sulfur_less_than_or_equal_to_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "new_england_residual_fuel_oil_wholesale_resale_volume_by",
                "rocky_mountain_no_4_distillate_retail_sales_by_refiners",
                "rocky_mountain_no_4_distillate_wholesale_resale_volume_by",
                "rocky_mountain_residual_fuel_oil_retail_sales_by_refiners",
                "rocky_mountain_padd_4_residual_fuel_oil_sulfur_greater_than_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "rocky_mountain_padd_4_residual_fuel_oil_sulfur_greater_than_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "rocky_mountain_padd_4_residual_fuel_oil_sulfur_less_than_or_equal_to_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "rocky_mountain_padd_4_residual_fuel_oil_sulfur_less_than_or_equal_to_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "rocky_mountain_residual_fuel_oil_wholesale_resale_volume_by",
                "us_no_4_distillate_retail_sales_by_refiners",
                "us_no_4_distillate_wholesale_resale_volume_by_refiners",
                "us_residual_fuel_oil_retail_sales_by_refiners",
                "us_residual_fuel_oil_sulfur_greater_than_1_retail_sales_by",
                "us_residual_fuel_oil_sulfur_greater_than_1_wholesale_resale",
                "us_residual_fuel_oil_sulfur_less_than_or_equal_to_1_retail",
                "us_residual_fuel_oil_sulfur_less_than_or_equal_to_1",
                "us_residual_fuel_oil_wholesale_resale_volume_by_refiners",
                "west_coast_no_4_distillate_retail_sales_by_refiners",
                "west_coast_no_4_distillate_wholesale_resale_volume_by",
                "west_coast_residual_fuel_oil_retail_sales_by_refiners",
                "west_coast_residual_fuel_oil_sulfur_greater_than_1_retail",
                "west_coast_residual_fuel_oil_sulfur_greater_than_1",
                "west_coast_padd_5_residual_fuel_oil_sulfur_less_than_or_equal_to_1_retail_sales_by_refiners_thousand_gallons_per_day",
                "west_coast_padd_5_residual_fuel_oil_sulfur_less_than_or_equal_to_1_wholesale_resale_volume_by_refiners_thousand_gallons_per_day",
                "west_coast_residual_fuel_oil_wholesale_resale_volume_by",
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


class EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesData(EiaApiData):
    """Refiner Residual Fuel Oil and No 4 Fuel Sales Volumes. EIA petroleum gas survey data"""

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


class EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesFetcher(
    Fetcher[
        EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesQueryParams,
        list[EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesData],
    ]
):
    """Refiner Residual Fuel Oil and No 4 Fuel Sales Volumes fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumRefinerResidualFuelOilAndNo4FuelSalesVolumesData, query, data
        )
