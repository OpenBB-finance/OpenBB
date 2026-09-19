"""Domestic Crude Oil First Purchase Prices by API Gravity model."""

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


class EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityQueryParams(
    EiaApiQueryParams
):
    """Domestic Crude Oil First Purchase Prices by API Gravity. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/dfp3
    """

    __group__ = "petroleum"
    __dataset__ = "domestic_crude_oil_first_purchase_prices_by_api_gravity"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "crude_gravity_20_0_percent_or_less",
                "crude_gravity_20_1_to_25_0_percent",
                "crude_gravity_25_1_to_30_0_percent",
                "crude_gravity_30_1_to_35_0_percent",
                "crude_gravity_35_1_to_40_0_percent",
                "crude_gravity_40_1_percent_or_more",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_domestic_crude_oil_first_purchase_prices_with_api_gravity_20_0_degrees_or_less_dollars_per_barrel",
                "us_domestic_crude_oil_first_purchase_prices_with_api_gravity_20_1_to_25_0_degrees_dollars_per_barrel",
                "us_domestic_crude_oil_first_purchase_prices_with_api_gravity_25_1_to_30_0_degrees_dollars_per_barrel",
                "us_domestic_crude_oil_first_purchase_prices_with_api_gravity_30_1_to_35_0_degrees_dollars_per_barrel",
                "us_domestic_crude_oil_first_purchase_prices_with_api_gravity_35_1_to_40_0_degrees_dollars_per_barrel",
                "us_domestic_crude_oil_first_purchase_prices_with_api_gravity_40_1_degrees_or_more_dollars_per_barrel",
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
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityData(EiaApiData):
    """Domestic Crude Oil First Purchase Prices by API Gravity. EIA petroleum gas survey data"""

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


class EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityFetcher(
    Fetcher[
        EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityQueryParams,
        list[EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityData],
    ]
):
    """Domestic Crude Oil First Purchase Prices by API Gravity fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumDomesticCrudeOilFirstPurchasePricesByApiGravityData, query, data
        )
