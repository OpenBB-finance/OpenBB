"""Hourly Demand by Subregion model."""

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


class EiaElectricityGridDemandBySubregionQueryParams(EiaApiQueryParams):
    """Hourly Demand by Subregion. Hourly demand by balancing authority subregion. Source: Form EIA-930 Product: Hourly Electric Grid Monitor

    Source: https://www.eia.gov/opendata/browser/electricity/rto/region-sub-ba-data
    """

    __group__ = "electricity_grid"
    __dataset__ = "demand_by_subregion"
    __json_schema_extra__ = {
        "parent": {
            "multiple_items_allowed": True,
            "choices": [
                "california_independent_system_operator",
                "electric_reliability_council_of_texas",
                "iso_new_england",
                "midcontinent_independent_system_operator",
                "new_york_independent_system_operator",
                "pjm_interconnection",
                "public_service_company_of_new_mexico",
                "southwest_power_pool",
            ],
        },
        "subregion": {
            "multiple_items_allowed": True,
            "choices": [
                "aepw_american_electric_power_west",
                "allegheny_power_zone_pjm",
                "american_electric_power_zone",
                "american_transmission_systems_zone_pjm",
                "atlantic_electric_zone",
                "baltimore_gas_null_zone_pjm",
                "capital_nyis",
                "central_nyis",
                "city_of_acoma_pueblo_pnm",
                "city_of_gallup",
                "city_of_springfield",
                "commonwealth_edison_zone",
                "connecticut",
                "dayton_power_null_zone_pjm",
                "delmarva_power_null_zone_pjm",
                "dominion_virginia_power_zone",
                "duke_energy_ohio_kentucky_zone_pjm",
                "dunwoodie_nyis",
                "duquesne_lighting_company_zone",
                "erco_coast",
                "erco_far_west",
                "erco_north_central",
                "erco_south_central",
                "east",
                "east_kentucky_power_cooperative_zone_pjm",
                "empire_district_electric_company",
                "freeport",
                "genesee_nyis",
                "grand_river_dam_authority_swpp",
                "hudson_valley",
                "isne_northeast_mass",
                "isne_vermont",
                "independence_power_null_swpp",
                "jersey_central_power_null_zone_pjm",
                "jicarilla_apache_nation",
                "kafb_pnm",
                "kcec_pnm",
                "kcp_and_l_greater_missouri_operations_swpp",
                "kansas_city_board_of_public_utilities_swpp",
                "kansas_city_power_and_light",
                "lincoln_electric_system",
                "long_island_nyis",
                "los_alamos_county",
                "maine",
                "metropolitan_edison_zone_pjm",
                "millwood_nyis",
                "mohawk_valley_nyis",
                "navajo_tribal_utility_authority_pnm",
                "nebraska_public_power_district",
                "new_hampshire",
                "new_york_city_nyis",
                "north",
                "north_nyis",
                "oklahoma_gas_and_electric_co_swpp",
                "omaha_public_power_district_swpp",
                "peco_energy_zone_pjm",
                "pnm_system_firm_load",
                "pacific_gas_and_electric",
                "pennsylvania_electric_zone_pjm",
                "pennsylvania_power_and_light_zone",
                "potomac_electric_power_zone",
                "public_service_electric_and_gas_of_new_jersey_zone_pjm",
                "rhode_island",
                "rockland_electric_zone_pjm",
                "san_diego_gas_and_electric",
                "south",
                "southeast_mass",
                "southern_california_edison",
                "southwestern_public_service_company_swpp",
                "sunflower_electric",
                "tri_state_generation_and_transmission",
                "valley_electric_association_ciso",
                "west",
                "west_nyis",
                "westar_energy",
                "western_area_power_upper_great_plains_east",
                "western_farmers_electric_cooperative",
                "western_central_mass",
                "zone_1",
                "zone_4_miso",
                "zone_6_miso",
                "zones_2_and_7",
                "zones_3_and_5",
                "zones_8_9_and_10_miso",
            ],
        },
        "timezone": {
            "multiple_items_allowed": True,
            "choices": ["arizona", "central", "eastern", "mountain", "pacific"],
        },
    }

    frequency: Literal["daily", "hourly", "local-hourly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'hourly'.",
    )
    parent: str | None = Field(
        default=None,
        description="Balancing Authority filter. Accepts a comma-separated list of values.",
    )
    subregion: str | None = Field(
        default=None,
        description="Subregion filter. Accepts a comma-separated list of values.",
    )
    timezone: Literal["arizona", "central", "eastern", "mountain", "pacific"] | None = (
        Field(
            default=None,
            description="Time Zone for Determining Date filter. Only applies to frequency: daily.",
        )
    )


class EiaElectricityGridDemandBySubregionData(EiaApiData):
    """Hourly Demand by Subregion. Hourly demand by balancing authority subregion. Source: Form EIA-930 Product: Hourly Electric Grid Monitor"""

    parent: str | None = Field(
        default=None,
        description="Balancing Authority code.",
    )
    parent_name: str | None = Field(
        default=None,
        description="Balancing Authority name.",
    )
    subregion: str | None = Field(
        default=None,
        description="Subregion code.",
    )
    subregion_name: str | None = Field(
        default=None,
        description="Subregion name.",
    )
    timezone: str | None = Field(
        default=None,
        description="Time Zone for Determining Date code.",
    )
    timezone_name: str | None = Field(
        default=None,
        description="Time Zone for Determining Date name.",
    )
    value: float | None = Field(
        default=None,
        description="Demand (megawatthours). Withheld or unavailable values return as null.",
    )


class EiaElectricityGridDemandBySubregionFetcher(
    Fetcher[
        EiaElectricityGridDemandBySubregionQueryParams,
        list[EiaElectricityGridDemandBySubregionData],
    ]
):
    """Hourly Demand by Subregion fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaElectricityGridDemandBySubregionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaElectricityGridDemandBySubregionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaElectricityGridDemandBySubregionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaElectricityGridDemandBySubregionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaElectricityGridDemandBySubregionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaElectricityGridDemandBySubregionData, query, data
        )
