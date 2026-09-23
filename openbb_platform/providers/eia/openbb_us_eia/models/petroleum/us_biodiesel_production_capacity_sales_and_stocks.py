"""US Biodiesel Production, Capacity, Sales, and Stocks - discontinued model."""

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


class EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksQueryParams(
    EiaApiQueryParams
):
    """US Biodiesel Production, Capacity, Sales, and Stocks - discontinued. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/sum/b100
    """

    __group__ = "petroleum"
    __dataset__ = "us_biodiesel_production_capacity_sales_and_stocks"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "biodiesel_production",
                "biodiesel_production_capacity",
                "ending_stocks",
                "number_of_producers_for_biodiesel_production",
                "sales_of_b100_included_biodiesel_blends",
                "sales_of_biodiesel_b100",
                "stock_change",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "florida",
                "massachusetts",
                "minnesota",
                "new_york",
                "ohio",
                "padd_1",
                "padd_2",
                "padd_3",
                "padd_4",
                "padd_5",
                "texas",
                "us",
                "usa_ak",
                "usa_al",
                "usa_ar",
                "usa_az",
                "usa_ct",
                "usa_ga",
                "usa_hi",
                "usa_ia",
                "usa_id",
                "usa_il",
                "usa_in",
                "usa_ks",
                "usa_ky",
                "usa_la",
                "usa_md",
                "usa_me",
                "usa_mi",
                "usa_mo",
                "usa_ms",
                "usa_mt",
                "usa_nc",
                "usa_nd",
                "usa_ne",
                "usa_nh",
                "usa_nj",
                "usa_nm",
                "usa_nv",
                "usa_ok",
                "usa_or",
                "usa_pa",
                "usa_ri",
                "usa_sc",
                "usa_sd",
                "usa_tn",
                "usa_ut",
                "usa_va",
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
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. There are 104 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksData(EiaApiData):
    """US Biodiesel Production, Capacity, Sales, and Stocks - discontinued. EIA petroleum gas survey data"""

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


class EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksFetcher(
    Fetcher[
        EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksQueryParams,
        list[EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksData],
    ]
):
    """US Biodiesel Production, Capacity, Sales, and Stocks - discontinued fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumUsBiodieselProductionCapacitySalesAndStocksData, query, data
        )
