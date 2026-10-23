"""Domestic Crude Oil First Purchase Prices for Selected Crude Streams model."""

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


class EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsQueryParams(EiaApiQueryParams):
    """Domestic Crude Oil First Purchase Prices for Selected Crude Streams. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/dfp2
    """

    __group__ = "petroleum"
    __dataset__ = "crude_first_purchase_prices_selected_streams"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "ans_crude_oil",
                "california_kern_river_crude_oil",
                "california_midwest_sunset_crude_oil",
                "louisiana_heavy_sweet_crude_oil",
                "louisiana_light_sweet_crude_oil",
                "mars_crude_oil",
                "wti_crude_oil",
                "west_texas_sour_crude_oil",
                "wyoming_sweet_crude_oil",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["california", "texas", "usa_ak", "usa_la", "usa_wy"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "alaska_north_slope_first_purchase_price",
                "california_kern_river_first_purchase_price",
                "california_midway_sunset_first_purchase_price",
                "heavy_louisiana_sweet_first_purchase_price",
                "light_louisiana_sweet_first_purchase_price",
                "mars_blend_first_purchase_price",
                "west_texas_intermediate_first_purchase_price",
                "west_texas_sour_first_purchase_price",
                "wyoming_sweet_first_purchase_price",
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


class EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsData(EiaApiData):
    """Domestic Crude Oil First Purchase Prices for Selected Crude Streams. EIA petroleum gas survey data"""

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


class EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsFetcher(
    Fetcher[
        EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsQueryParams,
        list[EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsData],
    ]
):
    """Domestic Crude Oil First Purchase Prices for Selected Crude Streams fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumCrudeFirstPurchasePricesSelectedStreamsData, query, data
        )
