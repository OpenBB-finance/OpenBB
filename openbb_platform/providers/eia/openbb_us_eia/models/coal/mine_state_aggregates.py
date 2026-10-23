"""Mine State Aggregates model."""

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


class EiaCoalMineStateAggregatesQueryParams(EiaApiQueryParams):
    """Mine State Aggregates. Coal shipments aggregated at state-level data, including price, quantity, quality, and rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/shipments/mine-state-aggregates
    """

    __group__ = "coal"
    __dataset__ = "mine_state_aggregates"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "ash_content",
                "heat_content",
                "price",
                "quantity",
                "sulfur_content",
            ],
        },
        "coal_rank": {
            "multiple_items_allowed": True,
            "choices": ["all", "anthracite", "bituminous", "lignite", "subbituminous"],
        },
        "mine_state": {
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
                "overseas",
                "pacific_contiguous",
                "pacific_noncontiguous",
                "pennsylvania",
                "pennsylvania_anthracite",
                "pennsylvania_bituminous",
                "powder_river_basin",
                "south_atlantic",
                "tennessee",
                "texas",
                "us_total",
                "uinta_basin",
                "utah",
                "virginia",
                "washington",
                "west_north_central",
                "west_south_central",
                "west_virginia",
                "west_virginia_northern",
                "west_virginia_southern",
                "western_region_total",
                "wyoming",
            ],
        },
    }

    frequency: Literal["annual", "quarterly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'annual'.",
    )
    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: ash_content (percent by weight); heat_content (Btu per pound); price (average dollars per ton); quantity (tons); sulfur_content (percent by weight).",
    )
    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank filter. Accepts a comma-separated list of values.",
    )
    mine_state: str | None = Field(
        default=None,
        description="Mine State\\Region filter. Accepts a comma-separated list of values.",
    )


class EiaCoalMineStateAggregatesData(EiaApiData):
    """Mine State Aggregates. Coal shipments aggregated at state-level data, including price, quantity, quality, and rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank code.",
    )
    coal_rank_name: str | None = Field(
        default=None,
        description="Coal Rank name.",
    )
    mine_state: str | None = Field(
        default=None,
        description="Mine State\\Region code.",
    )
    mine_state_name: str | None = Field(
        default=None,
        description="Mine State\\Region name.",
    )
    ash_content: float | None = Field(
        default=None,
        description="Ash content (percent by weight). Withheld or unavailable values return as null.",
    )
    heat_content: float | None = Field(
        default=None,
        description="Heat content (Btu per pound). Withheld or unavailable values return as null.",
    )
    price: float | None = Field(
        default=None,
        description="Price (average dollars per ton). Withheld or unavailable values return as null.",
    )
    quantity: float | None = Field(
        default=None,
        description="Quantity (tons). Withheld or unavailable values return as null.",
    )
    sulfur_content: float | None = Field(
        default=None,
        description="Sulfur content (percent by weight). Withheld or unavailable values return as null.",
    )


class EiaCoalMineStateAggregatesFetcher(
    Fetcher[EiaCoalMineStateAggregatesQueryParams, list[EiaCoalMineStateAggregatesData]]
):
    """Mine State Aggregates fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaCoalMineStateAggregatesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalMineStateAggregatesQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalMineStateAggregatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalMineStateAggregatesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalMineStateAggregatesData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalMineStateAggregatesData, query, data)
