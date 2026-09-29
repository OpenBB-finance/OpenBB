"""Sales and Price by Region model."""

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


class EiaDensifiedBiomassSalesAndPriceByRegionQueryParams(EiaApiQueryParams):
    """Sales and Price by Region. Densified biomass sales and average price by region. Source: EIA-63C Report: www.eia.gov/biomass/

    Source: https://www.eia.gov/opendata/browser/densified-biomass/sales-and-price-by-region
    """

    __group__ = "densified_biomass"
    __dataset__ = "sales_and_price_by_region"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": ["average_price", "quantity"],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["east", "south", "us_total", "west"],
        },
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: average_price (USD per ton); quantity (tons).",
    )
    region: Literal["east", "south", "us_total", "west"] | None = Field(
        default=None,
        description="Region filter.",
    )


class EiaDensifiedBiomassSalesAndPriceByRegionData(EiaApiData):
    """Sales and Price by Region. Densified biomass sales and average price by region. Source: EIA-63C Report: www.eia.gov/biomass/"""

    region: str | None = Field(
        default=None,
        description="Region code.",
    )
    region_name: str | None = Field(
        default=None,
        description="Region name.",
    )
    average_price: float | None = Field(
        default=None,
        description="Average price (USD per ton). Withheld or unavailable values return as null.",
    )
    quantity: float | None = Field(
        default=None,
        description="Quantity (tons). Withheld or unavailable values return as null.",
    )


class EiaDensifiedBiomassSalesAndPriceByRegionFetcher(
    Fetcher[
        EiaDensifiedBiomassSalesAndPriceByRegionQueryParams,
        list[EiaDensifiedBiomassSalesAndPriceByRegionData],
    ]
):
    """Sales and Price by Region fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaDensifiedBiomassSalesAndPriceByRegionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaDensifiedBiomassSalesAndPriceByRegionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaDensifiedBiomassSalesAndPriceByRegionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaDensifiedBiomassSalesAndPriceByRegionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaDensifiedBiomassSalesAndPriceByRegionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaDensifiedBiomassSalesAndPriceByRegionData, query, data
        )
