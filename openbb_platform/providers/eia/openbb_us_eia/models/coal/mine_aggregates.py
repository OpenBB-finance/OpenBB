"""Mine Aggregates model."""

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


class EiaCoalMineAggregatesQueryParams(EiaApiQueryParams):
    """Mine Aggregates. Coal shipments aggregated at mine-level data, including price, quantity, quality, and rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/shipments/mine-aggregates
    """

    __group__ = "coal"
    __dataset__ = "mine_aggregates"
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
        "mine": {"multiple_items_allowed": True},
        "mine_state": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama",
                "alaska",
                "arizona",
                "arkansas",
                "colorado",
                "illinois",
                "indiana",
                "kansas",
                "kentucky_east",
                "kentucky_west",
                "louisiana",
                "maryland",
                "mississippi",
                "missouri",
                "montana",
                "new_mexico",
                "north_dakota",
                "ohio",
                "oklahoma",
                "pennsylvania_anthracite",
                "pennsylvania_bituminous",
                "tennessee",
                "texas",
                "utah",
                "virginia",
                "west_virginia_northern",
                "west_virginia_southern",
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
    mine: str | None = Field(
        default=None,
        description="Mine filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    mine_state: str | None = Field(
        default=None,
        description="Mine State\\Region filter. Accepts a comma-separated list of values.",
    )


class EiaCoalMineAggregatesData(EiaApiData):
    """Mine Aggregates. Coal shipments aggregated at mine-level data, including price, quantity, quality, and rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank code.",
    )
    coal_rank_name: str | None = Field(
        default=None,
        description="Coal Rank name.",
    )
    mine: str | None = Field(
        default=None,
        description="Mine code.",
    )
    mine_name: str | None = Field(
        default=None,
        description="Mine name.",
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


class EiaCoalMineAggregatesFetcher(
    Fetcher[EiaCoalMineAggregatesQueryParams, list[EiaCoalMineAggregatesData]]
):
    """Mine Aggregates fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaCoalMineAggregatesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalMineAggregatesQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalMineAggregatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalMineAggregatesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalMineAggregatesData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalMineAggregatesData, query, data)
