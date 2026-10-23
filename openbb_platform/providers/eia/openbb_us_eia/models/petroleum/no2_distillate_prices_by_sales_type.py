"""No 2 Distillate Prices by Sales Type model."""

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


class EiaPetroleumNo2DistillatePricesBySalesTypeQueryParams(EiaApiQueryParams):
    """No 2 Distillate Prices by Sales Type. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/dist
    """

    __group__ = "petroleum"
    __dataset__ = "no2_distillate_prices_by_sales_type"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "industrial_price",
                "other_end_users_by_all_sellers",
                "price_delivered_to_commercial_sectors",
                "residential_price_by_all_sellers",
                "retail_sales_by_all_sellers",
                "through_company_outlets_price",
                "wholesale_resale_price_by_all_sellers",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "no_2_diesel",
                "no_2_diesel_high_sulfur",
                "no_2_diesel_low_sulfur_0_15_ppm",
                "no_2_diesel_low_sulfur_15_500_ppm",
                "no_2_distillate",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "massachusetts",
                "minnesota",
                "new_york",
                "ohio",
                "padd_1",
                "padd_1a",
                "padd_1b",
                "padd_1c",
                "padd_2",
                "padd_3",
                "padd_4",
                "padd_5",
                "us",
                "usa_ak",
                "usa_ct",
                "usa_dc",
                "usa_de",
                "usa_id",
                "usa_il",
                "usa_in",
                "usa_md",
                "usa_me",
                "usa_mi",
                "usa_nh",
                "usa_nj",
                "usa_or",
                "usa_pa",
                "usa_ri",
                "usa_va",
                "usa_vt",
                "usa_wi",
                "usa_wv",
                "washington",
            ],
        },
        "series": {"multiple_items_allowed": True},
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
        description="Series filter. Accepts a comma-separated list of values. There are 582 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumNo2DistillatePricesBySalesTypeData(EiaApiData):
    """No 2 Distillate Prices by Sales Type. EIA petroleum gas survey data"""

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


class EiaPetroleumNo2DistillatePricesBySalesTypeFetcher(
    Fetcher[
        EiaPetroleumNo2DistillatePricesBySalesTypeQueryParams,
        list[EiaPetroleumNo2DistillatePricesBySalesTypeData],
    ]
):
    """No 2 Distillate Prices by Sales Type fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumNo2DistillatePricesBySalesTypeQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumNo2DistillatePricesBySalesTypeQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumNo2DistillatePricesBySalesTypeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumNo2DistillatePricesBySalesTypeQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumNo2DistillatePricesBySalesTypeData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumNo2DistillatePricesBySalesTypeData, query, data
        )
