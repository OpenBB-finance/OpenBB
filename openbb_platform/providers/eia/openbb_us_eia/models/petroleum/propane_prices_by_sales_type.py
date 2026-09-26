"""Propane (Consumer Grade) Prices by Sales Type model."""

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


class EiaPetroleumPropanePricesBySalesTypeQueryParams(EiaApiQueryParams):
    """Propane (Consumer Grade) Prices by Sales Type. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/prop
    """

    __group__ = "petroleum"
    __dataset__ = "propane_prices_by_sales_type"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "industrial_price",
                "other_end_users_by_all_sellers",
                "price_delivered_to_commercial_sectors",
                "residential_price_by_all_sellers",
                "retail_sales_by_all_sellers",
                "sales_to_petrochemical_plants_price",
                "through_company_outlets_price",
                "wholesale_resale_price_by_all_sellers",
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
                "central_atlantic_propane_commercial_price_by_all_sellers",
                "central_atlantic_propane_industrial_price_by_all_sellers",
                "central_atlantic_propane_other_end_users_price_by_all",
                "central_atlantic_propane_residential_price_by_all_sellers",
                "central_atlantic_propane_retail_sales_by_all_sellers",
                "central_atlantic_propane_sales_to_petrochemical_plants",
                "central_atlantic_propane_through_company_outlets_price_by",
                "central_atlantic_propane_wholesale_resale_price_by_all",
                "east_coast_propane_commercial_price_by_all_sellers",
                "east_coast_propane_industrial_price_by_all_sellers",
                "east_coast_propane_other_end_users_price_by_all_sellers",
                "east_coast_propane_residential_price_by_all_sellers",
                "east_coast_propane_retail_sales_by_all_sellers",
                "east_coast_propane_sales_to_petrochemical_plants_price_by",
                "east_coast_propane_through_company_outlets_price_by_all",
                "east_coast_propane_wholesale_resale_price_by_all_sellers",
                "gulf_coast_propane_commercial_price_by_all_sellers",
                "gulf_coast_propane_industrial_price_by_all_sellers",
                "gulf_coast_propane_other_end_users_price_by_all_sellers",
                "gulf_coast_propane_residential_price_by_all_sellers",
                "gulf_coast_propane_retail_sales_by_all_sellers",
                "gulf_coast_propane_sales_to_petrochemical_plants_price_by",
                "gulf_coast_propane_through_company_outlets_price_by_all",
                "gulf_coast_propane_wholesale_resale_price_by_all_sellers",
                "lower_atlantic_propane_commercial_price_by_all_sellers",
                "lower_atlantic_propane_industrial_price_by_all_sellers",
                "lower_atlantic_propane_other_end_users_price_by_all_sellers",
                "lower_atlantic_propane_residential_price_by_all_sellers",
                "lower_atlantic_propane_retail_sales_by_all_sellers",
                "lower_atlantic_propane_sales_to_petrochemical_plants_price",
                "lower_atlantic_propane_through_company_outlets_price_by_all",
                "lower_atlantic_propane_wholesale_resale_price_by_all_sellers",
                "midwest_propane_commercial_price_by_all_sellers",
                "midwest_propane_industrial_price_by_all_sellers",
                "midwest_propane_other_end_users_price_by_all_sellers",
                "midwest_propane_residential_price_by_all_sellers",
                "midwest_propane_retail_sales_by_all_sellers",
                "midwest_propane_sales_to_petrochemical_plants_price_by_all",
                "midwest_propane_through_company_outlets_price_by_all_sellers",
                "midwest_propane_wholesale_resale_price_by_all_sellers",
                "new_england_propane_commercial_price_by_all_sellers",
                "new_england_propane_industrial_price_by_all_sellers",
                "new_england_propane_other_end_users_price_by_all_sellers",
                "new_england_propane_residential_price_by_all_sellers",
                "new_england_propane_retail_sales_by_all_sellers",
                "new_england_propane_sales_to_petrochemical_plants_price_by",
                "new_england_propane_through_company_outlets_price_by_all",
                "new_england_propane_wholesale_resale_price_by_all_sellers",
                "rocky_mountain_propane_commercial_price_by_all_sellers",
                "rocky_mountain_propane_industrial_price_by_all_sellers",
                "rocky_mountain_propane_other_end_users_price_by_all_sellers",
                "rocky_mountain_propane_residential_price_by_all_sellers",
                "rocky_mountain_propane_retail_sales_by_all_sellers",
                "rocky_mountain_propane_sales_to_petrochemical_plants_price",
                "rocky_mountain_propane_through_company_outlets_price_by_all",
                "rocky_mountain_propane_wholesale_resale_price_by_all_sellers",
                "us_propane_commercial_price_by_all_sellers",
                "us_propane_industrial_price_by_all_sellers",
                "us_propane_other_end_users_price_by_all_sellers",
                "us_propane_residential_price_by_all_sellers",
                "us_propane_retail_sales_by_all_sellers",
                "us_propane_sales_to_petrochemical_plants_price_by_all",
                "us_propane_through_company_outlets_price_by_all_sellers",
                "us_propane_wholesale_resale_price_by_all_sellers",
                "west_coast_propane_commercial_price_by_all_sellers",
                "west_coast_propane_industrial_price_by_all_sellers",
                "west_coast_propane_other_end_users_price_by_all_sellers",
                "west_coast_propane_residential_price_by_all_sellers",
                "west_coast_propane_retail_sales_by_all_sellers",
                "west_coast_propane_sales_to_petrochemical_plants_price_by",
                "west_coast_propane_through_company_outlets_price_by_all",
                "west_coast_propane_wholesale_resale_price_by_all_sellers",
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
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumPropanePricesBySalesTypeData(EiaApiData):
    """Propane (Consumer Grade) Prices by Sales Type. EIA petroleum gas survey data"""

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


class EiaPetroleumPropanePricesBySalesTypeFetcher(
    Fetcher[
        EiaPetroleumPropanePricesBySalesTypeQueryParams,
        list[EiaPetroleumPropanePricesBySalesTypeData],
    ]
):
    """Propane (Consumer Grade) Prices by Sales Type fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumPropanePricesBySalesTypeQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumPropanePricesBySalesTypeQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumPropanePricesBySalesTypeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumPropanePricesBySalesTypeQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumPropanePricesBySalesTypeData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumPropanePricesBySalesTypeData, query, data
        )
