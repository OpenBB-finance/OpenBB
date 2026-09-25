"""Feedstocks and Costs model."""

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


class EiaDensifiedBiomassFeedstocksAndCostsQueryParams(EiaApiQueryParams):
    """Feedstocks and Costs. Densified biomass feedstocks and cost by type. Source: EIA-63C Report: www.eia.gov/biomass/

    Source: https://www.eia.gov/opendata/browser/densified-biomass/feedstocks-and-cost
    """

    __group__ = "densified_biomass"
    __dataset__ = "feedstocks_and_costs"
    __json_schema_extra__ = {
        "data_type": {"multiple_items_allowed": True, "choices": ["cost", "quantity"]},
        "fuel_type": {
            "multiple_items_allowed": True,
            "choices": [
                "other_residuals",
                "roundwood_pulpwood",
                "sawmill_residuals",
                "wood_product_manufacturing_residuals",
            ],
        },
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: cost (USD per ton); quantity (tons).",
    )
    fuel_type: (
        Literal[
            "other_residuals",
            "roundwood_pulpwood",
            "sawmill_residuals",
            "wood_product_manufacturing_residuals",
        ]
        | None
    ) = Field(
        default=None,
        description="Fuel Type filter.",
    )


class EiaDensifiedBiomassFeedstocksAndCostsData(EiaApiData):
    """Feedstocks and Costs. Densified biomass feedstocks and cost by type. Source: EIA-63C Report: www.eia.gov/biomass/"""

    fuel_type: str | None = Field(
        default=None,
        description="Fuel Type code.",
    )
    fuel_type_name: str | None = Field(
        default=None,
        description="Fuel Type name.",
    )
    cost: float | None = Field(
        default=None,
        description="Cost (USD per ton). Withheld or unavailable values return as null.",
    )
    quantity: float | None = Field(
        default=None,
        description="Quantity (tons). Withheld or unavailable values return as null.",
    )


class EiaDensifiedBiomassFeedstocksAndCostsFetcher(
    Fetcher[
        EiaDensifiedBiomassFeedstocksAndCostsQueryParams,
        list[EiaDensifiedBiomassFeedstocksAndCostsData],
    ]
):
    """Feedstocks and Costs fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaDensifiedBiomassFeedstocksAndCostsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaDensifiedBiomassFeedstocksAndCostsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaDensifiedBiomassFeedstocksAndCostsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaDensifiedBiomassFeedstocksAndCostsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaDensifiedBiomassFeedstocksAndCostsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaDensifiedBiomassFeedstocksAndCostsData, query, data
        )
