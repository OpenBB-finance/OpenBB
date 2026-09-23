"""Market Sales Price model."""

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


class EiaCoalMarketSalesPriceQueryParams(EiaApiQueryParams):
    """Market Sales Price. Coal market sales prices and amounts by mine types for regions and states (unless withheld for pricing protections). Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/market-sales-price
    """

    __group__ = "coal"
    __dataset__ = "market_sales_price"
    __json_schema_extra__ = {
        "data_type": {"multiple_items_allowed": True, "choices": ["price", "sales"]},
        "market_type": {
            "multiple_items_allowed": True,
            "choices": ["captive", "open_market", "total"],
        },
        "state_region": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama",
                "alaska",
                "appalachia_central",
                "appalachia_northern",
                "appalachia_southern",
                "appalachia_total",
                "arizona",
                "arkansas",
                "colorado",
                "east_north_central",
                "east_south_central",
                "east_total",
                "east_of_mississippi_river",
                "illinois",
                "illinois_basin",
                "indiana",
                "interior_region_total",
                "kansas",
                "kentucky",
                "kentucky_east",
                "kentucky_west",
                "louisiana",
                "maryland",
                "middle_atlantic",
                "midwest_total",
                "mississippi",
                "missouri",
                "montana",
                "mountain",
                "new_mexico",
                "north_dakota",
                "ohio",
                "oklahoma",
                "other_interior",
                "other_western",
                "pacific_contiguous",
                "pacific_noncontiguous",
                "pennsylvania",
                "pennsylvania_anthracite",
                "pennsylvania_bituminous",
                "powder_river_basin",
                "south_atlantic",
                "south_total",
                "tennessee",
                "texas",
                "us_total",
                "uinta_basin",
                "utah",
                "virginia",
                "washington",
                "west_north_central",
                "west_south_central",
                "west_total",
                "west_virginia",
                "west_virginia_northern",
                "west_virginia_southern",
                "west_of_mississippi_river",
                "western_region_total",
                "wyoming",
            ],
        },
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: price (dollars per short ton); sales (short tons).",
    )
    market_type: Literal["captive", "open_market", "total"] | None = Field(
        default=None,
        description="Market Type filter.",
    )
    state_region: str | None = Field(
        default=None,
        description="State\\Region filter. Accepts a comma-separated list of values.",
    )


class EiaCoalMarketSalesPriceData(EiaApiData):
    """Market Sales Price. Coal market sales prices and amounts by mine types for regions and states (unless withheld for pricing protections). Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    market_type: str | None = Field(
        default=None,
        description="Market Type code.",
    )
    market_type_name: str | None = Field(
        default=None,
        description="Market Type name.",
    )
    state_region: str | None = Field(
        default=None,
        description="State\\Region code.",
    )
    state_region_name: str | None = Field(
        default=None,
        description="State\\Region name.",
    )
    price: float | None = Field(
        default=None,
        description="Price (dollars per short ton). Withheld or unavailable values return as null.",
    )
    sales: float | None = Field(
        default=None,
        description="Sales (short tons). Withheld or unavailable values return as null.",
    )


class EiaCoalMarketSalesPriceFetcher(
    Fetcher[EiaCoalMarketSalesPriceQueryParams, list[EiaCoalMarketSalesPriceData]]
):
    """Market Sales Price fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaCoalMarketSalesPriceQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalMarketSalesPriceQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalMarketSalesPriceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalMarketSalesPriceQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalMarketSalesPriceData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalMarketSalesPriceData, query, data)
