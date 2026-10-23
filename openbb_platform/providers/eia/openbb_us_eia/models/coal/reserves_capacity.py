"""Reserves Capacity model."""

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


class EiaCoalReservesCapacityQueryParams(EiaApiQueryParams):
    """Reserves Capacity. Coal capacity data, including productive capacity, stocks, and recoverable reserves by state, region and mine type. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/reserves-capacity
    """

    __group__ = "coal"
    __dataset__ = "reserves_capacity"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "producer_distributor_stocks",
                "productive_capacity",
                "recoverable_reserves",
            ],
        },
        "mine_type": {
            "multiple_items_allowed": True,
            "choices": ["surface", "total", "underground"],
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
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: producer_distributor_stocks (short tons); productive_capacity (short tons); recoverable_reserves (short tons).",
    )
    mine_type: Literal["surface", "total", "underground"] | None = Field(
        default=None,
        description="Mine Type filter.",
    )
    state_region: str | None = Field(
        default=None,
        description="State\\Region filter. Accepts a comma-separated list of values.",
    )


class EiaCoalReservesCapacityData(EiaApiData):
    """Reserves Capacity. Coal capacity data, including productive capacity, stocks, and recoverable reserves by state, region and mine type. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    mine_type: str | None = Field(
        default=None,
        description="Mine Type code.",
    )
    mine_type_name: str | None = Field(
        default=None,
        description="Mine Type name.",
    )
    state_region: str | None = Field(
        default=None,
        description="State\\Region code.",
    )
    state_region_name: str | None = Field(
        default=None,
        description="State\\Region name.",
    )
    producer_distributor_stocks: float | None = Field(
        default=None,
        description="Producer distributor stocks (short tons). Withheld or unavailable values return as null.",
    )
    productive_capacity: float | None = Field(
        default=None,
        description="Productive capacity (short tons). Withheld or unavailable values return as null.",
    )
    recoverable_reserves: float | None = Field(
        default=None,
        description="Recoverable reserves (short tons). Withheld or unavailable values return as null.",
    )


class EiaCoalReservesCapacityFetcher(
    Fetcher[EiaCoalReservesCapacityQueryParams, list[EiaCoalReservesCapacityData]]
):
    """Reserves Capacity fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaCoalReservesCapacityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalReservesCapacityQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalReservesCapacityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalReservesCapacityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalReservesCapacityData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalReservesCapacityData, query, data)
