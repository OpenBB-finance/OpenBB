"""Domestic Crude Oil First Purchase Prices by Area model."""

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


class EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaQueryParams(
    EiaApiQueryParams
):
    """Domestic Crude Oil First Purchase Prices by Area. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/dfp1
    """

    __group__ = "petroleum"
    __dataset__ = "domestic_crude_oil_first_purchase_prices_by_area"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": ["ans_crude_oil", "crude_oil"],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "na",
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
                "usa_il",
                "usa_in",
                "usa_ks",
                "usa_ky",
                "usa_la",
                "usa_mi",
                "usa_ms",
                "usa_mt",
                "usa_nd",
                "usa_ne",
                "usa_nm",
                "usa_ok",
                "usa_pa",
                "usa_sd",
                "usa_ut",
                "usa_wv",
                "usa_wy",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama_crude_oil_first_purchase_price",
                "alaska_north_slope_first_purchase_price",
                "alaska_other_crude_oil_first_purchase_price",
                "arkansas_crude_oil_first_purchase_price",
                "california_crude_oil_first_purchase_price",
                "colorado_crude_oil_first_purchase_price",
                "east_coast_crude_oil_first_purchase_price",
                "federal_offshore_california_crude_oil_first_purchase_price",
                "federal_offshore_us_gulf_coast_crude_oil_first_purchase",
                "gulf_coast_crude_oil_first_purchase_price",
                "illinois_crude_oil_first_purchase_price",
                "indiana_crude_oil_first_purchase_price",
                "kansas_crude_oil_first_purchase_price",
                "kentucky_crude_oil_first_purchase_price",
                "louisiana_crude_oil_first_purchase_price",
                "michigan_crude_oil_first_purchase_price",
                "midwest_crude_oil_first_purchase_price",
                "mississippi_crude_oil_first_purchase_price",
                "montana_crude_oil_first_purchase_price",
                "nebraska_crude_oil_first_purchase_price",
                "new_mexico_crude_oil_first_purchase_price",
                "new_york_crude_oil_first_purchase_price",
                "north_dakota_crude_oil_first_purchase_price",
                "ohio_crude_oil_first_purchase_price",
                "oklahoma_crude_oil_first_purchase_price",
                "pennsylvania_crude_oil_first_purchase_price",
                "rocky_mountain_crude_oil_first_purchase_price",
                "south_dakota_crude_oil_first_purchase_price",
                "texas_crude_oil_first_purchase_price",
                "us_crude_oil_first_purchase_price",
                "us_less_alaskan_north_slope_crude_oil_first_purchase_price",
                "utah_crude_oil_first_purchase_price",
                "west_coast_crude_oil_first_purchase_price",
                "west_virginia_crude_oil_first_purchase_price",
                "wyoming_crude_oil_first_purchase_price",
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


class EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaData(EiaApiData):
    """Domestic Crude Oil First Purchase Prices by Area. EIA petroleum gas survey data"""

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


class EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaFetcher(
    Fetcher[
        EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaQueryParams,
        list[EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaData],
    ]
):
    """Domestic Crude Oil First Purchase Prices by Area fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumDomesticCrudeOilFirstPurchasePricesByAreaData, query, data
        )
