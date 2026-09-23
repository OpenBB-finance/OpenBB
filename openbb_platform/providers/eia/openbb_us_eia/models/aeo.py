"""Annual Energy Outlook model."""

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


class EiaAeoQueryParams(EiaApiQueryParams):
    """Annual Energy Outlook. Long-term energy projections by release year and scenario. Select the report vintage with the `release` parameter.

    Source: https://www.eia.gov/opendata/browser/aeo
    """

    __group__ = "aeo"
    __json_schema_extra__ = {
        "history": {
            "multiple_items_allowed": True,
            "choices": ["historic", "projection"],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "east_north_central",
                "east_south_central",
                "florida_reliability_coordinating_council",
                "midcontinent_central",
                "midcontinent_east",
                "midcontinent_south",
                "midcontinent_west",
                "middle_atlantic",
                "midwest_reliability_council_east",
                "midwest_reliability_council_west",
                "mountain",
                "new_england",
                "no_regional_tables",
                "northeast_power_coordinating_council_long_island",
                "northeast_power_coordinating_council_nyc_westchester",
                "northeast_power_coordinating_council_new_england",
                "northeast_power_coordinating_council_new_york_city_and_long",
                "northeast_power_coordinating_council_northeast",
                "northeast_power_coordinating_council_upstate_new_york",
                "pjm_commonwealth_edison",
                "pjm_dominion",
                "pjm_east",
                "pjm_west",
                "pacific",
                "reliability_first_corporation_east",
                "reliability_first_corporation_michigan",
                "reliability_first_corporation_west",
                "serc_reliability_corporation_central",
                "serc_reliability_corporation_delta",
                "serc_reliability_corporation_east",
                "serc_reliability_corporation_gateway",
                "serc_reliability_corporation_southeastern",
                "serc_reliability_corporation_virginia_carolina",
                "south_atlantic",
                "southwest_power_pool_central",
                "southwest_power_pool_north",
                "southwest_power_pool_south",
                "texas_regional_entity",
                "texas_reliability_entity",
                "united_states",
                "west_north_central",
                "west_south_central",
                "western_electricity_coordinating_council_basin",
                "western_electricity_coordinating_council_california",
                "western_electricity_coordinating_council_california_north",
                "western_electricity_coordinating_council_california_south",
                "western_electricity_coordinating_council_northwest_power",
                "western_electricity_coordinating_council_rockies",
                "western_electricity_coordinating_council_southwest",
            ],
        },
        "scenario": {"multiple_items_allowed": True},
        "series": {"multiple_items_allowed": True},
        "table": {
            "multiple_items_allowed": True,
            "choices": [
                "air_travel_energy_use",
                "aircraft_stock",
                "aluminum_industry_energy_consumption",
                "bulk_chemical_industry_energy_consumption",
                "cement_and_lime_industry_energy_consumption",
                "coal_minemouth_prices_by_region_and_type",
                "coal_production_and_minemouth_prices_by_region",
                "coal_production_by_region_and_type",
                "coal_supply_disposition_and_prices",
                "commercial_sector_energy_consumption_floorspace_and",
                "commercial_sector_key_indicators_and_consumption",
                "components_of_selected_petroleum_product_prices",
                "conversion_factors",
                "electric_power_projections_by_electricity_market_module",
                "electricity_generating_capacity",
                "electricity_generation_capacity_by_electricity_market",
                "electricity_generation_by_electricity_market_module_region",
                "electricity_supply_disposition_prices_and_emissions",
                "electricity_trade",
                "employment_and_shipments_by_industry_and_income_and",
                "energy_consumption_by_sector_and_source",
                "energy_prices_by_sector_and_source",
                "energy_related_carbon_dioxide_emissions_by_end_use",
                "energy_related_carbon_dioxide_emissions_by_sector_and_source",
                "food_industry_energy_consumption",
                "freight_transportation_energy_use",
                "glass_industry_energy_consumption",
                "imported_liquids_by_source",
                "industrial_sector_key_indicators_and_consumption",
                "industrial_sector_macroeconomic_indicators",
                "international_petroleum_and_other_liquids_supply",
                "iron_and_steel_industry_energy_consumption",
                "light_duty_vehicle_energy_consumption_by_technology_type",
                "light_duty_vehicle_miles_traveled_by_technology_type",
                "light_duty_vehicle_miles_per_gallon_by_technology_type",
                "light_duty_vehicle_sales_by_technology_type",
                "light_duty_vehicle_stock_by_technology_type",
                "lower_48_crude_oil_production_and_wellhead_prices_by_supply",
                "lower_48_natural_gas_production_and_supply_prices_by_supply",
                "macroeconomic_indicators",
                "metal_based_durables_industry_energy_consumption",
                "natural_gas_consumption_by_end_use_sector_and_census",
                "natural_gas_delivered_prices_by_end_use_sector_and_census",
                "natural_gas_imports_and_exports",
                "natural_gas_supply_disposition_and_prices",
                "new_light_duty_vehicle_fuel_economy",
                "new_light_duty_vehicle_prices",
                "new_light_duty_vehicle_range",
                "nonmanufacturing_sector_energy_consumption",
                "oil_and_gas_end_of_year_reserves_and_annual_reserve",
                "oil_and_gas_supply",
                "other_manufacturing_industry_energy_consumption",
                "paper_industry_energy_consumption",
                "petroleum_and_other_liquids_prices",
                "petroleum_and_other_liquids_supply_and_disposition",
                "primary_natural_gas_flows_entering_ngtdm_region_from",
                "refining_industry_energy_consumption",
                "renewable_energy_consumption_by_sector_and_source",
                "renewable_energy_generating_capacity_and_generation",
                "renewable_energy_generation_by_fuel",
                "residential_sector_equipment_stock_and_efficiency",
                "residential_sector_key_indicators_and_consumption",
                "summary_of_new_light_duty_vehicle_size_class_attributes",
                "hydrogen_supply_disposition_and_prices",
                "overnight_capital_costs_for_new_electricity_generating",
                "shale_gas_and_tight_oil_production_by_play_1",
                "carbon_dioxide_emissions_by_category_and_sector",
                "capacity_with_carbon_capture_and_carbon_flows",
                "technology_market_penetration_in_light_duty_vehicles",
                "total_energy_supply_disposition_and_price_summary",
                "transportation_fleet_car_and_truck_fuel_consumption_by_type",
                "transportation_fleet_car_and_truck_sales_by_type_and",
                "transportation_fleet_car_and_truck_stock_by_type_and",
                "transportation_fleet_car_and_truck_vehicle_miles_traveled",
                "transportation_sector_energy_use_by_fuel_type_within_a_mode",
                "transportation_sector_energy_use_by_mode_and_type",
                "transportation_sector_key_indicators_and_delivered_energy",
                "world_metallurgical_coal_flows_by_importing_regions_and",
                "world_steam_coal_flows_by_importing_regions_and_exporting",
                "world_total_coal_flows_by_importing_regions_and_exporting",
            ],
        },
    }

    release: Literal[
        "2014",
        "2014-er",
        "2015",
        "2016",
        "2017",
        "2018",
        "2019",
        "2020",
        "2021",
        "2022",
        "2023",
        "2025",
        "2026",
    ] = Field(
        default="2026",
        description="The Annual Energy Outlook release."
        " Facet values vary by release; use the `facet_options` endpoint to list them.",
    )
    history: Literal["historic", "projection"] | None = Field(
        default=None,
        description="History filter.",
    )
    region: str | None = Field(
        default=None,
        description="Region filter. Accepts a comma-separated list of values.",
    )
    scenario: str | None = Field(
        default=None,
        description="Scenario filter. Accepts a comma-separated list of values. There are 149 valid values - use the `facet_options` endpoint to list them.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    table: str | None = Field(
        default=None,
        description="Table filter. Accepts a comma-separated list of values.",
    )


class EiaAeoData(EiaApiData):
    """Annual Energy Outlook. Long-term energy projections by release year and scenario. Select the report vintage with the `release` parameter."""

    history: str | None = Field(
        default=None,
        description="History code.",
    )
    history_name: str | None = Field(
        default=None,
        description="History name.",
    )
    region: str | None = Field(
        default=None,
        description="Region code.",
    )
    region_name: str | None = Field(
        default=None,
        description="Region name.",
    )
    scenario: str | None = Field(
        default=None,
        description="Scenario code.",
    )
    scenario_name: str | None = Field(
        default=None,
        description="Scenario name.",
    )
    series: str | None = Field(
        default=None,
        description="Series code.",
    )
    series_name: str | None = Field(
        default=None,
        description="Series name.",
    )
    table: str | None = Field(
        default=None,
        description="Table code.",
    )
    table_name: str | None = Field(
        default=None,
        description="Table name.",
    )
    value: float | None = Field(
        default=None,
        description="Value. Withheld or unavailable values return as null.",
    )
    unit: str | None = Field(
        default=None,
        description="Unit of the value.",
    )


class EiaAeoFetcher(Fetcher[EiaAeoQueryParams, list[EiaAeoData]]):
    """Annual Energy Outlook fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaAeoQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaAeoQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaAeoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaAeoQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaAeoData]:
        """Transform the data."""
        return transform_dataset_data(EiaAeoData, query, data)
