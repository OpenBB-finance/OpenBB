"""Plant State Aggregates model."""

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


class EiaCoalPlantStateAggregatesQueryParams(EiaApiQueryParams):
    """Plant State Aggregates. Coal reciepts aggregated at state-level data, including price, quantity, quality, and rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/shipments/plant-state-aggregates
    """

    __group__ = "coal"
    __dataset__ = "plant_state_aggregates"
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
        "plant_state": {
            "multiple_items_allowed": True,
            "choices": [
                "alabama",
                "alaska",
                "arizona",
                "arkansas",
                "california",
                "colorado",
                "connecticut",
                "delaware",
                "east_north_central",
                "east_south_central",
                "florida",
                "georgia",
                "hawaii",
                "illinois",
                "indiana",
                "iowa",
                "kansas",
                "kentucky",
                "louisiana",
                "maine",
                "maryland",
                "massachusetts",
                "michigan",
                "middle_atlantic",
                "minnesota",
                "mississippi",
                "missouri",
                "montana",
                "mountain",
                "nebraska",
                "nevada",
                "new_england",
                "new_hampshire",
                "new_jersey",
                "new_mexico",
                "new_york",
                "north_carolina",
                "north_dakota",
                "ohio",
                "oklahoma",
                "oregon",
                "pacific_contiguous",
                "pacific_noncontiguous",
                "pennsylvania",
                "rhode_island",
                "south_atlantic",
                "south_carolina",
                "south_dakota",
                "tennessee",
                "texas",
                "us_total",
                "utah",
                "virginia",
                "washington",
                "west_north_central",
                "west_south_central",
                "west_virginia",
                "wisconsin",
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
    plant_state: str | None = Field(
        default=None,
        description="Plant State\\Region filter. Accepts a comma-separated list of values.",
    )


class EiaCoalPlantStateAggregatesData(EiaApiData):
    """Plant State Aggregates. Coal reciepts aggregated at state-level data, including price, quantity, quality, and rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank code.",
    )
    coal_rank_name: str | None = Field(
        default=None,
        description="Coal Rank name.",
    )
    plant_state: str | None = Field(
        default=None,
        description="Plant State\\Region code.",
    )
    plant_state_name: str | None = Field(
        default=None,
        description="Plant State\\Region name.",
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


class EiaCoalPlantStateAggregatesFetcher(
    Fetcher[
        EiaCoalPlantStateAggregatesQueryParams, list[EiaCoalPlantStateAggregatesData]
    ]
):
    """Plant State Aggregates fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaCoalPlantStateAggregatesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalPlantStateAggregatesQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalPlantStateAggregatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalPlantStateAggregatesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalPlantStateAggregatesData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalPlantStateAggregatesData, query, data)
