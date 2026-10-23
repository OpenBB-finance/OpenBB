"""Plant Aggregates model."""

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


class EiaCoalPlantAggregatesQueryParams(EiaApiQueryParams):
    """Plant Aggregates. Coal reciepts aggregated to plant-level data, including price, quantity, quality, and rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/shipments/plant-aggregates
    """

    __group__ = "coal"
    __dataset__ = "plant_aggregates"
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
        "plant": {"multiple_items_allowed": True},
        "state_region": {
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
                "overseas",
                "pennsylvania_anthracite",
                "pennsylvania_bituminous",
                "tennessee",
                "texas",
                "utah",
                "virginia",
                "washington",
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
    plant: str | None = Field(
        default=None,
        description="Plant filter. Accepts a comma-separated list of values. There are 530 valid values - use the `facet_options` endpoint to list them.",
    )
    state_region: str | None = Field(
        default=None,
        description="Plant State\\Region. filter. Accepts a comma-separated list of values.",
    )


class EiaCoalPlantAggregatesData(EiaApiData):
    """Plant Aggregates. Coal reciepts aggregated to plant-level data, including price, quantity, quality, and rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank code.",
    )
    coal_rank_name: str | None = Field(
        default=None,
        description="Coal Rank name.",
    )
    plant: str | None = Field(
        default=None,
        description="Plant code.",
    )
    plant_name: str | None = Field(
        default=None,
        description="Plant name.",
    )
    state_region: str | None = Field(
        default=None,
        description="Plant State\\Region. code.",
    )
    state_region_name: str | None = Field(
        default=None,
        description="Plant State\\Region. name.",
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


class EiaCoalPlantAggregatesFetcher(
    Fetcher[EiaCoalPlantAggregatesQueryParams, list[EiaCoalPlantAggregatesData]]
):
    """Plant Aggregates fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaCoalPlantAggregatesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalPlantAggregatesQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalPlantAggregatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalPlantAggregatesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalPlantAggregatesData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalPlantAggregatesData, query, data)
