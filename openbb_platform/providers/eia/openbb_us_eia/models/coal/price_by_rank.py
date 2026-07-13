"""Price by Rank model."""

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


class EiaCoalPriceByRankQueryParams(EiaApiQueryParams):
    """Price by Rank. Coal prices by rank data for region and state. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/price-by-rank
    """

    __group__ = "coal"
    __dataset__ = "price_by_rank"
    __json_schema_extra__ = {
        "coal_rank": {
            "multiple_items_allowed": True,
            "choices": ["all", "anthracite", "bituminous", "lignite", "subbituminous"],
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

    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank filter. Accepts a comma-separated list of values.",
    )
    state_region: str | None = Field(
        default=None,
        description="State\\Region filter. Accepts a comma-separated list of values.",
    )


class EiaCoalPriceByRankData(EiaApiData):
    """Price by Rank. Coal prices by rank data for region and state. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank code.",
    )
    coal_rank_name: str | None = Field(
        default=None,
        description="Coal Rank name.",
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


class EiaCoalPriceByRankFetcher(
    Fetcher[EiaCoalPriceByRankQueryParams, list[EiaCoalPriceByRankData]]
):
    """Price by Rank fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaCoalPriceByRankQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalPriceByRankQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalPriceByRankQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalPriceByRankQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalPriceByRankData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalPriceByRankData, query, data)
