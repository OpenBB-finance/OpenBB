"""By Mine, By Plant model."""

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


class EiaCoalByMineByPlantQueryParams(EiaApiQueryParams):
    """By Mine, By Plant. Coal shipments from mine- to plant-level data, including price, quantity, quality, and rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/shipments/by-mine-by-plant
    """

    __group__ = "coal"
    __dataset__ = "by_mine_by_plant"
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
            "choices": [
                "all",
                "anthracite",
                "bituminous",
                "lignite",
                "subbituminous",
                "synfuel_coal",
                "waste_coal",
            ],
        },
        "coal_supplier": {"multiple_items_allowed": True},
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
        "plant": {"multiple_items_allowed": True},
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
                "minnesota",
                "mississippi",
                "missouri",
                "montana",
                "nebraska",
                "nevada",
                "new_hampshire",
                "new_jersey",
                "new_mexico",
                "new_york",
                "north_carolina",
                "north_dakota",
                "ohio",
                "oklahoma",
                "oregon",
                "pennsylvania",
                "south_carolina",
                "south_dakota",
                "tennessee",
                "texas",
                "utah",
                "virginia",
                "washington",
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
        description="Coal Type filter. Accepts a comma-separated list of values.",
    )
    coal_supplier: str | None = Field(
        default=None,
        description="Coal Supplier filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    mine: str | None = Field(
        default=None,
        description="Mine filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    mine_state: str | None = Field(
        default=None,
        description="Mine State\\Region filter. Accepts a comma-separated list of values.",
    )
    plant: str | None = Field(
        default=None,
        description="Plant filter. Accepts a comma-separated list of values. There are 475 valid values - use the `facet_options` endpoint to list them.",
    )
    plant_state: str | None = Field(
        default=None,
        description="Plant State\\Region filter. Accepts a comma-separated list of values.",
    )


class EiaCoalByMineByPlantData(EiaApiData):
    """By Mine, By Plant. Coal shipments from mine- to plant-level data, including price, quantity, quality, and rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    coal_rank: str | None = Field(
        default=None,
        description="Coal Type code.",
    )
    coal_rank_name: str | None = Field(
        default=None,
        description="Coal Type name.",
    )
    coal_supplier: str | None = Field(
        default=None,
        description="Coal Supplier code.",
    )
    coal_supplier_name: str | None = Field(
        default=None,
        description="Coal Supplier name.",
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
    plant: str | None = Field(
        default=None,
        description="Plant code.",
    )
    plant_name: str | None = Field(
        default=None,
        description="Plant name.",
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


class EiaCoalByMineByPlantFetcher(
    Fetcher[EiaCoalByMineByPlantQueryParams, list[EiaCoalByMineByPlantData]]
):
    """By Mine, By Plant fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaCoalByMineByPlantQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalByMineByPlantQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalByMineByPlantQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalByMineByPlantQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalByMineByPlantData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalByMineByPlantData, query, data)
