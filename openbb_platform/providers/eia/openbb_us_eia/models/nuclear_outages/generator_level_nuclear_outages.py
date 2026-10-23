"""Generator Level Nuclear Outages model."""

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


class EiaNuclearOutagesGeneratorLevelNuclearOutagesQueryParams(EiaApiQueryParams):
    """Generator Level Nuclear Outages. Generator level nuclear outages with capacity, outages, and percent outage. Source: Nuclear Regulatory Commission's Power Reactor Status Report. Interactive data report: Daily Status of Nuclear Reactors.

    Source: https://www.eia.gov/opendata/browser/nuclear-outages/generator-nuclear-outages
    """

    __group__ = "nuclear_outages"
    __dataset__ = "generator_level_nuclear_outages"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": ["capacity", "outage", "percent_outage"],
        },
        "facility": {
            "multiple_items_allowed": True,
            "choices": [
                "arkansas_nuclear_one",
                "beaver_valley",
                "braidwood_generation_station",
                "browns_ferry",
                "brunswick",
                "byron_generating_station",
                "callaway",
                "calvert_cliffs_nuclear_power_plant",
                "catawba",
                "clinton_power_station",
                "columbia_generating_station",
                "comanche_peak",
                "cooper",
                "crystal_river",
                "davis_besse",
                "diablo_canyon",
                "donald_c_cook",
                "dresden_generating_station",
                "duane_arnold",
                "edwin_i_hatch",
                "fermi",
                "fort_calhoun",
                "grand_gulf",
                "h_b_robinson",
                "harris",
                "indian_point_2",
                "indian_point_3",
                "james_a_fitzpatrick",
                "joseph_m_farley",
                "kewaunee",
                "lasalle_generating_station",
                "limerick",
                "mcguire",
                "millstone",
                "monticello",
                "nine_mile_point_nuclear_station",
                "north_anna",
                "oconee",
                "oyster_creek",
                "ppl_susquehanna",
                "pseg_hope_creek_generating_station",
                "pseg_salem_generating_station",
                "palisades",
                "palo_verde",
                "peach_bottom",
                "perry",
                "pilgrim_nuclear_power_station",
                "point_beach",
                "prairie_island",
                "quad_cities_generating_station",
                "r_e_ginna_nuclear_power_plant",
                "river_bend_station",
                "san_onofre",
                "seabrook",
                "sequoyah",
                "south_texas_project",
                "st_lucie",
                "surry",
                "three_mile_island",
                "turkey_point",
                "v_c_summer",
                "vermont_yankee",
                "vogtle",
                "waterford_3",
                "watts_bar_nuclear_plant",
                "wolf_creek_generating_station",
            ],
        },
        "generator": {"multiple_items_allowed": True, "choices": ["1", "2", "3", "4"]},
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: capacity (megawatts); outage (megawatts); percent_outage (percent).",
    )
    facility: str | None = Field(
        default=None,
        description="Plant code filter. Accepts a comma-separated list of values.",
    )
    generator: Literal["1", "2", "3", "4"] | None = Field(
        default=None,
        description="Facility's generator ID number filter.",
    )


class EiaNuclearOutagesGeneratorLevelNuclearOutagesData(EiaApiData):
    """Generator Level Nuclear Outages. Generator level nuclear outages with capacity, outages, and percent outage. Source: Nuclear Regulatory Commission's Power Reactor Status Report. Interactive data report: Daily Status of Nuclear Reactors."""

    facility: str | None = Field(
        default=None,
        description="Plant code code.",
    )
    facility_name: str | None = Field(
        default=None,
        description="Plant code name.",
    )
    generator: str | None = Field(
        default=None,
        description="Facility's generator ID number code.",
    )
    generator_name: str | None = Field(
        default=None,
        description="Facility's generator ID number name.",
    )
    capacity: float | None = Field(
        default=None,
        description="Capacity (megawatts). Withheld or unavailable values return as null.",
    )
    outage: float | None = Field(
        default=None,
        description="Outage (megawatts). Withheld or unavailable values return as null.",
    )
    percent_outage: float | None = Field(
        default=None,
        description="Percent outage (percent). Withheld or unavailable values return as null.",
    )


class EiaNuclearOutagesGeneratorLevelNuclearOutagesFetcher(
    Fetcher[
        EiaNuclearOutagesGeneratorLevelNuclearOutagesQueryParams,
        list[EiaNuclearOutagesGeneratorLevelNuclearOutagesData],
    ]
):
    """Generator Level Nuclear Outages fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNuclearOutagesGeneratorLevelNuclearOutagesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNuclearOutagesGeneratorLevelNuclearOutagesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNuclearOutagesGeneratorLevelNuclearOutagesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNuclearOutagesGeneratorLevelNuclearOutagesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNuclearOutagesGeneratorLevelNuclearOutagesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNuclearOutagesGeneratorLevelNuclearOutagesData, query, data
        )
