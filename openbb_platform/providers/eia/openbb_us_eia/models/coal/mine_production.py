"""Mine Production model."""

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


class EiaCoalMineProductionQueryParams(EiaApiQueryParams):
    """Mine Production. Coal mine-level data, including production, region, state, county, rank, status, type, name and description. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/

    Source: https://www.eia.gov/opendata/browser/coal/mine-production
    """

    __group__ = "coal"
    __dataset__ = "mine_production"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "average_employees",
                "labor_hours",
                "latitude",
                "longitude",
                "operating_company",
                "operating_company_address",
                "production",
                "refuse_flag",
            ],
        },
        "census_region": {
            "multiple_items_allowed": True,
            "choices": [
                "east_north_central",
                "east_south_central",
                "middle_atlantic",
                "mountain",
                "pacific_contiguous",
                "pacific_noncontiguous",
                "south_atlantic",
                "west_north_central",
                "west_south_central",
            ],
        },
        "coal_rank": {
            "multiple_items_allowed": True,
            "choices": [
                "anthracite",
                "bituminous",
                "lignite",
                "preparation_plant",
                "subbituminous",
            ],
        },
        "mine": {"multiple_items_allowed": True},
        "mine_county": {"multiple_items_allowed": True},
        "mine_region": {
            "multiple_items_allowed": True,
            "choices": ["east", "midwest", "south", "west"],
        },
        "mine_status": {
            "multiple_items_allowed": True,
            "choices": [
                "active",
                "active_men_not_working_not_producing",
                "active_men_working_not_producing",
                "mine_closed_by_msha",
                "new_under_construction",
                "permanently_abandoned",
                "temporarily_closed",
            ],
        },
        "mine_type": {
            "multiple_items_allowed": True,
            "choices": ["refuse", "surface", "underground"],
        },
        "mississippi_region": {
            "multiple_items_allowed": True,
            "choices": ["east_of_mississippi_river", "west_of_mississippi_river"],
        },
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
        "supply_region": {
            "multiple_items_allowed": True,
            "choices": [
                "appalachia_central",
                "appalachia_northern",
                "appalachia_southern",
                "illinois_basin",
                "other_interior",
                "other_western",
                "powder_river_basin",
                "uinta_basin",
            ],
        },
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: average_employees (number of employees); labor_hours (hours); latitude; longitude; operating_company; operating_company_address; production (short tons); refuse_flag.",
    )
    census_region: (
        Literal[
            "east_north_central",
            "east_south_central",
            "middle_atlantic",
            "mountain",
            "pacific_contiguous",
            "pacific_noncontiguous",
            "south_atlantic",
            "west_north_central",
            "west_south_central",
        ]
        | None
    ) = Field(
        default=None,
        description="Census Region filter.",
    )
    coal_rank: str | None = Field(
        default=None,
        description="Coal Rank filter. Accepts a comma-separated list of values.",
    )
    mine: str | None = Field(
        default=None,
        description="Mine filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    mine_county: str | None = Field(
        default=None,
        description="Mine County filter. Accepts a comma-separated list of values. There are 107 valid values - use the `facet_options` endpoint to list them.",
    )
    mine_region: Literal["east", "midwest", "south", "west"] | None = Field(
        default=None,
        description="Region filter.",
    )
    mine_status: (
        Literal[
            "active",
            "active_men_not_working_not_producing",
            "active_men_working_not_producing",
            "mine_closed_by_msha",
            "new_under_construction",
            "permanently_abandoned",
            "temporarily_closed",
        ]
        | None
    ) = Field(
        default=None,
        description="Mine Status filter.",
    )
    mine_type: Literal["refuse", "surface", "underground"] | None = Field(
        default=None,
        description="Mine Type filter.",
    )
    mississippi_region: (
        Literal["east_of_mississippi_river", "west_of_mississippi_river"] | None
    ) = Field(
        default=None,
        description="Mississippi Region filter.",
    )
    state_region: str | None = Field(
        default=None,
        description="State filter. Accepts a comma-separated list of values.",
    )
    supply_region: (
        Literal[
            "appalachia_central",
            "appalachia_northern",
            "appalachia_southern",
            "illinois_basin",
            "other_interior",
            "other_western",
            "powder_river_basin",
            "uinta_basin",
        ]
        | None
    ) = Field(
        default=None,
        description="Supply Region filter.",
    )


class EiaCoalMineProductionData(EiaApiData):
    """Mine Production. Coal mine-level data, including production, region, state, county, rank, status, type, name and description. Source: EIA Form 7A and MSHA Form 7000-2. Interactive browser: https://www.eia.gov/coal/data/browser/"""

    census_region: str | None = Field(
        default=None,
        description="Census Region code.",
    )
    census_region_name: str | None = Field(
        default=None,
        description="Census Region name.",
    )
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
    mine_county: str | None = Field(
        default=None,
        description="Mine County code.",
    )
    mine_county_name: str | None = Field(
        default=None,
        description="Mine County name.",
    )
    mine_region: str | None = Field(
        default=None,
        description="Region code.",
    )
    mine_region_name: str | None = Field(
        default=None,
        description="Region name.",
    )
    mine_status: str | None = Field(
        default=None,
        description="Mine Status code.",
    )
    mine_status_name: str | None = Field(
        default=None,
        description="Mine Status name.",
    )
    mine_type: str | None = Field(
        default=None,
        description="Mine Type code.",
    )
    mine_type_name: str | None = Field(
        default=None,
        description="Mine Type name.",
    )
    mississippi_region: str | None = Field(
        default=None,
        description="Mississippi Region code.",
    )
    mississippi_region_name: str | None = Field(
        default=None,
        description="Mississippi Region name.",
    )
    state_region: str | None = Field(
        default=None,
        description="State code.",
    )
    state_region_name: str | None = Field(
        default=None,
        description="State name.",
    )
    supply_region: str | None = Field(
        default=None,
        description="Supply Region code.",
    )
    supply_region_name: str | None = Field(
        default=None,
        description="Supply Region name.",
    )
    average_employees: float | None = Field(
        default=None,
        description="Average employees (number of employees). Withheld or unavailable values return as null.",
    )
    labor_hours: float | None = Field(
        default=None,
        description="Labor hours (hours). Withheld or unavailable values return as null.",
    )
    latitude: float | None = Field(
        default=None,
        description="Latitude. Withheld or unavailable values return as null.",
    )
    longitude: float | None = Field(
        default=None,
        description="Longitude. Withheld or unavailable values return as null.",
    )
    operating_company: str | None = Field(
        default=None,
        description="Operating company",
    )
    operating_company_address: str | None = Field(
        default=None,
        description="Operating company address",
    )
    production: float | None = Field(
        default=None,
        description="Production (short tons). Withheld or unavailable values return as null.",
    )
    refuse_flag: str | None = Field(
        default=None,
        description="Refuse flag",
    )


class EiaCoalMineProductionFetcher(
    Fetcher[EiaCoalMineProductionQueryParams, list[EiaCoalMineProductionData]]
):
    """Mine Production fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaCoalMineProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaCoalMineProductionQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaCoalMineProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaCoalMineProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaCoalMineProductionData]:
        """Transform the data."""
        return transform_dataset_data(EiaCoalMineProductionData, query, data)
