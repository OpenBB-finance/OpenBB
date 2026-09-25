"""Inventory of Operable Generators model."""

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


class EiaElectricityInventoryOfOperableGeneratorsQueryParams(EiaApiQueryParams):
    """Inventory of Operable Generators. Inventory of operable generators in the U.S. Source: Forms EIA-860, EIA-860M

    Source: https://www.eia.gov/opendata/browser/electricity/operating-generator-capacity
    """

    __group__ = "electricity"
    __dataset__ = "inventory_of_operable_generators"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "county",
                "latitude",
                "longitude",
                "nameplate_capacity_mw",
                "net_summer_capacity_mw",
                "net_winter_capacity_mw",
                "operating_year_month",
                "planned_derate_summer_cap_mw",
                "planned_derate_year_month",
                "planned_retirement_year_month",
                "planned_uprate_summer_cap_mw",
                "planned_uprate_year_month",
            ],
        },
        "balancing_authority": {
            "multiple_items_allowed": True,
            "choices": [
                "alcoa_power_generating_yadkin_division",
                "american_electric_power_service_corp_as_agent_for_public",
                "arizona_public_service_company",
                "arlington_valley_avba",
                "associated_electric_cooperative",
                "avangrid_renewables",
                "avista_corporation",
                "balancing_authority_of_northern_california",
                "board_of_public_utilities",
                "bonneville_power_administration",
                "california_independent_system_operator",
                "chugach_electric_assn",
                "city_utilities_of_springfield_mo",
                "city_of_homestead",
                "city_of_tacoma_department_of_public_utilities_light_division",
                "city_of_tallahassee",
                "constellation_energy_control_and_dispatch",
                "dominion_energy_south_carolina",
                "duke_energy_carolinas",
                "duke_energy_progress_west",
                "el_paso_electric_company",
                "electric_energy",
                "electric_reliability_council_of_texas",
                "florida_municipal_power_pool",
                "florida_power_and_light_company",
                "gainesville_regional_utilities",
                "gila_river_power",
                "grand_river_dam_authority",
                "gridliance",
                "gridforce_energy_management",
                "gridforce_south",
                "griffith_energy",
                "hawaiian_electric_co",
                "iso_new_england",
                "idaho_power_company",
                "imperial_irrigation_district",
                "independence_power_and_light",
                "jea",
                "kcpl_greater_missouri_operations",
                "kansas_city_power_and_light_company",
                "lg_and_e_and_ku_services_company_as_agent_for_louisville",
                "lincoln_electric_system",
                "los_angeles_department_of_water_and_power",
                "midcontinent_independent_transmission_system_operator",
                "naturener_power_watch",
                "naturener_wind_watch",
                "nebraska_public_power_district",
                "nevada_power_company",
                "new_brunswick_system_operator",
                "new_harquahala_generating_company_hgba",
                "new_smyrna_beach_utilities_commission_of",
                "new_york_independent_system_operator",
                "no_ba",
                "northwestern_energy",
                "ohio_valley_electric_corporation",
                "oklahoma_gas_and_electric_co",
                "omaha_public_power_district",
                "pjm_interconnection",
                "pud_no_1_of_douglas_county",
                "pacificorp_east",
                "pacificorp_west",
                "portland_general_electric_company",
                "powersouth_energy_cooperative",
                "progress_energy_carolinas_east",
                "progress_energy_florida",
                "public_service_company_of_colorado",
                "public_service_company_of_new_mexico",
                "public_utility_district_no_1_of_chelan_county",
                "public_utility_district_no_2_of_grant_county_washington",
                "puget_sound_energy",
                "salt_river_project",
                "seattle_city_light",
                "seminole_electric_cooperative",
                "south_carolina_electric_and_amp_gas_company",
                "southeastern_power_administration",
                "southern_company_services_trans",
                "southwest_power_pool",
                "southwestern_power_administration",
                "southwestern_public_service_co",
                "sunflower_electric_power_corporation",
                "tampa_electric_company",
                "tennessee_valley_authority",
                "the_empire_district_electric_company",
                "tucson_electric_power_company",
                "turlock_irrigation_district",
                "westar_energy",
                "western_area_power_administration_desert_southwest_region",
                "western_area_power_administration_rocky_mountain_region",
                "western_area_power_administration_upper_great_plains_east",
                "western_area_power_administration_ugp_west",
                "western_farmers_electric_cooperative",
            ],
        },
        "energy_source": {
            "multiple_items_allowed": True,
            "choices": [
                "value",
                "agriculture_byproducts",
                "bituminous_coal",
                "black_liquor",
                "blast_furnace_gas",
                "coal_derived_synthesis_gas",
                "disillate_fuel_oil",
                "electricity_used_for_energy_storage",
                "gaseous_propane",
                "geothermal",
                "jet_fuel",
                "kerosene",
                "landfill_gas",
                "lignite",
                "municipal_solid_waste",
                "natural_gas",
                "nuclear",
                "other",
                "other_biomass_gases",
                "other_biomass_liquids",
                "other_biomass_solids",
                "other_gas",
                "petroleum_coke",
                "purchased_steam",
                "refined_coal",
                "residual_fuel_oil",
                "sludge_waste",
                "solar",
                "subbituminous_coal",
                "synthesis_gas_from_petroleum_coke",
                "tire_derived_fuel",
                "waste_coal",
                "waste_heat",
                "waste_oil",
                "water",
                "wind",
                "wood_waste_liquids",
                "wood_waste_solids",
            ],
        },
        "entity": {"multiple_items_allowed": True},
        "generator": {"multiple_items_allowed": True},
        "plant": {"multiple_items_allowed": True},
        "prime_mover": {
            "multiple_items_allowed": True,
            "choices": [
                "ba",
                "bt",
                "ca",
                "ce",
                "cp",
                "cs",
                "ct",
                "fc",
                "fw",
                "gt",
                "hy",
                "ic",
                "ot",
                "ps",
                "pv",
                "st",
                "ws",
                "wt",
            ],
        },
        "sector": {
            "multiple_items_allowed": True,
            "choices": [
                "commercial_chp",
                "commercial_non_chp",
                "electric_utility",
                "ipp_chp",
                "ipp_non_chp",
                "industrial_chp",
                "industrial_non_chp",
            ],
        },
        "state": {
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
                "district_of_columbia",
                "florida",
                "georgia",
                "hawaii",
                "idaho",
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
                "rhode_island",
                "south_carolina",
                "south_dakota",
                "tennessee",
                "texas",
                "utah",
                "vermont",
                "virginia",
                "washington",
                "west_virginia",
                "wisconsin",
                "wyoming",
            ],
        },
        "status": {
            "multiple_items_allowed": True,
            "choices": [
                "operating",
                "out_of_service_and_not_expected_to_return_to_service_in",
                "out_of_service_but_expected_to_return_to_service_in_next",
                "standby_backup_available_for_service_but_not_normally_used",
            ],
        },
        "technology": {
            "multiple_items_allowed": True,
            "choices": [
                "all_other",
                "batteries",
                "coal_integrated_gasification_combined_cycle",
                "conventional_hydroelectric",
                "conventional_steam_coal",
                "flywheels",
                "geothermal",
                "hydroelectric_pumped_storage",
                "landfill_gas",
                "municipal_solid_waste",
                "natural_gas_fired_combined_cycle",
                "natural_gas_fired_combustion_turbine",
                "natural_gas_internal_combustion_engine",
                "natural_gas_steam_turbine",
                "natural_gas_with_compressed_air_storage",
                "nuclear",
                "offshore_wind_turbine",
                "onshore_wind_turbine",
                "other_gases",
                "other_natural_gas",
                "other_waste_biomass",
                "petroleum_coke",
                "petroleum_liquids",
                "solar_photovoltaic",
                "solar_thermal_with_energy_storage",
                "solar_thermal_without_energy_storage",
                "wood_wood_waste_biomass",
            ],
        },
        "unit": {"multiple_items_allowed": True},
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: county; latitude; longitude; nameplate_capacity_mw = Nameplate Capacity (MW); net_summer_capacity_mw = Net Summer Capacity (MW); net_winter_capacity_mw = Net Winter Capacity (MW); operating_year_month = Operating Date (Year and Month); planned_derate_summer_cap_mw = Magnitude of Planned Derate (Summer Capacity) (MW); planned_derate_year_month = Planned Derate Date (Year and Month); planned_retirement_year_month = Planned Retirement Date (Year and Month); planned_uprate_summer_cap_mw = Magnitude of Planned Uprate (Summer Capacity) (MW); planned_uprate_year_month = Planned Uprate Date (Year and Month).",
    )
    balancing_authority: str | None = Field(
        default=None,
        description="Balancing Authority filter. Accepts a comma-separated list of values.",
    )
    energy_source: str | None = Field(
        default=None,
        description="Primary Energy Source filter. Accepts a comma-separated list of values.",
    )
    entity: str | None = Field(
        default=None,
        description="Entity ID and Name filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    generator: str | None = Field(
        default=None,
        description="Generator ID filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    plant: str | None = Field(
        default=None,
        description="Plant ID and Name filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    prime_mover: str | None = Field(
        default=None,
        description="Prime Mover Code filter. Accepts a comma-separated list of values.",
    )
    sector: str | None = Field(
        default=None,
        description="Sector filter. Accepts a comma-separated list of values.",
    )
    state: str | None = Field(
        default=None,
        description="State filter. Accepts a comma-separated list of values.",
    )
    status: (
        Literal[
            "operating",
            "out_of_service_and_not_expected_to_return_to_service_in",
            "out_of_service_but_expected_to_return_to_service_in_next",
            "standby_backup_available_for_service_but_not_normally_used",
        ]
        | None
    ) = Field(
        default=None,
        description="Operating Status Code filter.",
    )
    technology: str | None = Field(
        default=None,
        description="Technology filter. Accepts a comma-separated list of values.",
    )
    unit: str | None = Field(
        default=None,
        description="Unit Code filter. Accepts a comma-separated list of values. There are 385 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaElectricityInventoryOfOperableGeneratorsData(EiaApiData):
    """Inventory of Operable Generators. Inventory of operable generators in the U.S. Source: Forms EIA-860, EIA-860M"""

    balancing_authority: str | None = Field(
        default=None,
        description="Balancing Authority code.",
    )
    balancing_authority_name: str | None = Field(
        default=None,
        description="Balancing Authority name.",
    )
    energy_source: str | None = Field(
        default=None,
        description="Primary Energy Source code.",
    )
    energy_source_name: str | None = Field(
        default=None,
        description="Primary Energy Source name.",
    )
    entity: str | None = Field(
        default=None,
        description="Entity ID and Name code.",
    )
    entity_name: str | None = Field(
        default=None,
        description="Entity ID and Name name.",
    )
    generator: str | None = Field(
        default=None,
        description="Generator ID code.",
    )
    generator_name: str | None = Field(
        default=None,
        description="Generator ID name.",
    )
    plant: str | None = Field(
        default=None,
        description="Plant ID and Name code.",
    )
    plant_name: str | None = Field(
        default=None,
        description="Plant ID and Name name.",
    )
    prime_mover: str | None = Field(
        default=None,
        description="Prime Mover Code code.",
    )
    prime_mover_name: str | None = Field(
        default=None,
        description="Prime Mover Code name.",
    )
    sector: str | None = Field(
        default=None,
        description="Sector code.",
    )
    sector_name: str | None = Field(
        default=None,
        description="Sector name.",
    )
    state: str | None = Field(
        default=None,
        description="State code.",
    )
    state_name: str | None = Field(
        default=None,
        description="State name.",
    )
    status: str | None = Field(
        default=None,
        description="Operating Status Code code.",
    )
    status_name: str | None = Field(
        default=None,
        description="Operating Status Code name.",
    )
    technology: str | None = Field(
        default=None,
        description="Technology code.",
    )
    technology_name: str | None = Field(
        default=None,
        description="Technology name.",
    )
    unit: str | None = Field(
        default=None,
        description="Unit Code code.",
    )
    unit_name: str | None = Field(
        default=None,
        description="Unit Code name.",
    )
    county: str | None = Field(
        default=None,
        description="County",
    )
    latitude: float | None = Field(
        default=None,
        description="Latitude. Withheld or unavailable values return as null.",
    )
    longitude: float | None = Field(
        default=None,
        description="Longitude. Withheld or unavailable values return as null.",
    )
    nameplate_capacity_mw: float | None = Field(
        default=None,
        description="Nameplate Capacity (MW). Withheld or unavailable values return as null.",
    )
    net_summer_capacity_mw: float | None = Field(
        default=None,
        description="Net Summer Capacity (MW). Withheld or unavailable values return as null.",
    )
    net_winter_capacity_mw: float | None = Field(
        default=None,
        description="Net Winter Capacity (MW). Withheld or unavailable values return as null.",
    )
    operating_year_month: str | None = Field(
        default=None,
        description="Operating Date (Year and Month)",
    )
    planned_derate_summer_cap_mw: float | None = Field(
        default=None,
        description="Magnitude of Planned Derate (Summer Capacity) (MW). Withheld or unavailable values return as null.",
    )
    planned_derate_year_month: str | None = Field(
        default=None,
        description="Planned Derate Date (Year and Month)",
    )
    planned_retirement_year_month: str | None = Field(
        default=None,
        description="Planned Retirement Date (Year and Month)",
    )
    planned_uprate_summer_cap_mw: float | None = Field(
        default=None,
        description="Magnitude of Planned Uprate (Summer Capacity) (MW). Withheld or unavailable values return as null.",
    )
    planned_uprate_year_month: str | None = Field(
        default=None,
        description="Planned Uprate Date (Year and Month)",
    )


class EiaElectricityInventoryOfOperableGeneratorsFetcher(
    Fetcher[
        EiaElectricityInventoryOfOperableGeneratorsQueryParams,
        list[EiaElectricityInventoryOfOperableGeneratorsData],
    ]
):
    """Inventory of Operable Generators fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaElectricityInventoryOfOperableGeneratorsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaElectricityInventoryOfOperableGeneratorsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaElectricityInventoryOfOperableGeneratorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaElectricityInventoryOfOperableGeneratorsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaElectricityInventoryOfOperableGeneratorsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaElectricityInventoryOfOperableGeneratorsData, query, data
        )
