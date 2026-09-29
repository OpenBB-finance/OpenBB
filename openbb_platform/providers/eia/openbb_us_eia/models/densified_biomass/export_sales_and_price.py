"""Export Sales and Price model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_us_eia.utils.api_query import (
    EiaApiData,
    EiaApiQueryParams,
    extract_dataset_data,
    transform_dataset_data,
    transform_dataset_query,
)


class EiaDensifiedBiomassExportSalesAndPriceQueryParams(EiaApiQueryParams):
    """Export Sales and Price. Densified biomass export prices and quantity. Source: EIA-63C Report: www.eia.gov/biomass/

    Source: https://www.eia.gov/opendata/browser/densified-biomass/export-sales-and-price
    """

    __group__ = "densified_biomass"
    __dataset__ = "export_sales_and_price"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": ["average_price", "quantity"],
        },
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: average_price (USD per ton); quantity (tons).",
    )


class EiaDensifiedBiomassExportSalesAndPriceData(EiaApiData):
    """Export Sales and Price. Densified biomass export prices and quantity. Source: EIA-63C Report: www.eia.gov/biomass/"""

    average_price: float | None = Field(
        default=None,
        description="Average price (USD per ton). Withheld or unavailable values return as null.",
    )
    quantity: float | None = Field(
        default=None,
        description="Quantity (tons). Withheld or unavailable values return as null.",
    )


class EiaDensifiedBiomassExportSalesAndPriceFetcher(
    Fetcher[
        EiaDensifiedBiomassExportSalesAndPriceQueryParams,
        list[EiaDensifiedBiomassExportSalesAndPriceData],
    ]
):
    """Export Sales and Price fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaDensifiedBiomassExportSalesAndPriceQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaDensifiedBiomassExportSalesAndPriceQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaDensifiedBiomassExportSalesAndPriceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaDensifiedBiomassExportSalesAndPriceQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaDensifiedBiomassExportSalesAndPriceData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaDensifiedBiomassExportSalesAndPriceData, query, data
        )
