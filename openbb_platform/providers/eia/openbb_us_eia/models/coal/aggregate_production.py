"""Aggregate Production model."""

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


class EiaCoalAggregateProductionQueryParams(EiaApiQueryParams):
    """Aggregate Production. Coal state aggregated data by mine type, includes production, productivity, labor hours, employees, and coal rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/aggregate-production
    """

    __group__ = "coal"
    __dataset__ = "aggregate_production"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "average_employees",
                "labor_hours",
                "number_of_mines",
                "production",
                "productivity",
            ],
        },
        "coal_rank": {
            "multiple_items_allowed": True,
            "choices": ["all", "anthracite", "bituminous", "lignite", "subbituminous"],
        },
        "mine_type": {
            "multiple_items_allowed": True,
            "choices": ["all", "refuse", "surface", "underground"],
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
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: average_employees (number of employees); labor_hours (hours); number_of_mines (number of mines); production (short tons); productivity (short tons per labor hour).",
    )
    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank filter. Accepts a comma-separated list of values.",
    )
    mine_type: Literal["all", "refuse", "surface", "underground"] | None = Field(
        default=None,
        description="Mine Type filter.",
    )
    state_region: str | None = Field(
        default=None,
        description="State\\Region filter. Accepts a comma-separated list of values.",
    )


class EiaCoalAggregateProductionData(EiaApiData):
    """Aggregate Production. Coal state aggregated data by mine type, includes production, productivity, labor hours, employees, and coal rank. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank code.",
    )
    coal_rank_name: str | None = Field(
        default=None,
        description="Coal Rank name.",
    )
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
    average_employees: float | None = Field(
        default=None,
        description="Average employees (number of employees). Withheld or unavailable values return as null.",
    )
    labor_hours: float | None = Field(
        default=None,
        description="Labor hours (hours). Withheld or unavailable values return as null.",
    )
    number_of_mines: float | None = Field(
        default=None,
        description="Number of mines (number of mines). Withheld or unavailable values return as null.",
    )
    production: float | None = Field(
        default=None,
        description="Production (short tons). Withheld or unavailable values return as null.",
    )
    productivity: float | None = Field(
        default=None,
        description="Productivity (short tons per labor hour). Withheld or unavailable values return as null.",
    )


class EiaCoalAggregateProductionFetcher(
    Fetcher[EiaCoalAggregateProductionQueryParams, list[EiaCoalAggregateProductionData]]
):
    """Aggregate Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaCoalAggregateProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalAggregateProductionQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalAggregateProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalAggregateProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalAggregateProductionData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalAggregateProductionData, query, data)
