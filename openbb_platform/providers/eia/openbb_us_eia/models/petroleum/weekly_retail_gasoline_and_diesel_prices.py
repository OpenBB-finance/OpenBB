"""Weekly Retail Gasoline and Diesel Prices model."""

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


class EiaPetroleumWeeklyRetailGasolineAndDieselPricesQueryParams(EiaApiQueryParams):
    """Weekly Retail Gasoline and Diesel Prices. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/gnd
    """

    __group__ = "petroleum"
    __dataset__ = "weekly_retail_gasoline_and_diesel_prices"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "conventional_gasoline",
                "conventional_premium_gasoline",
                "conventional_regular_gasoline",
                "gasoline_conventional_midgrade",
                "gasoline_reformulated_midgrade",
                "midgrade_gasoline",
                "no_2_diesel",
                "no_2_diesel_low_sulfur_0_15_ppm",
                "no_2_diesel_low_sulfur_15_500_ppm",
                "premium_gasoline",
                "reformulated_motor_gasoline",
                "reformulated_premium_gasoline",
                "reformulated_regular_gasoline",
                "regular_gasoline",
                "total_gasoline",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "boston",
                "california",
                "chicago",
                "cleveland",
                "colorado",
                "denver",
                "florida",
                "houston",
                "los_angeles",
                "massachusetts",
                "miami",
                "minnesota",
                "new_york",
                "new_york_city",
                "ohio",
                "padd_1",
                "padd_1a",
                "padd_1b",
                "padd_1c",
                "padd_2",
                "padd_3",
                "padd_4",
                "padd_5",
                "padd_5_except_california",
                "san_francisco",
                "seattle",
                "texas",
                "us",
                "washington",
            ],
        },
        "series": {"multiple_items_allowed": True},
    }

    frequency: Literal["annual", "monthly", "weekly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'weekly'.",
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
        description="Series filter. Accepts a comma-separated list of values. There are 311 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumWeeklyRetailGasolineAndDieselPricesData(EiaApiData):
    """Weekly Retail Gasoline and Diesel Prices. EIA petroleum gas survey data"""

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


class EiaPetroleumWeeklyRetailGasolineAndDieselPricesFetcher(
    Fetcher[
        EiaPetroleumWeeklyRetailGasolineAndDieselPricesQueryParams,
        list[EiaPetroleumWeeklyRetailGasolineAndDieselPricesData],
    ]
):
    """Weekly Retail Gasoline and Diesel Prices fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumWeeklyRetailGasolineAndDieselPricesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumWeeklyRetailGasolineAndDieselPricesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumWeeklyRetailGasolineAndDieselPricesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumWeeklyRetailGasolineAndDieselPricesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumWeeklyRetailGasolineAndDieselPricesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumWeeklyRetailGasolineAndDieselPricesData, query, data
        )
