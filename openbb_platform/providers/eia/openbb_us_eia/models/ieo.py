"""International Energy Outlook model."""

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


class EiaIeoQueryParams(EiaApiQueryParams):
    """International Energy Outlook. Long-term energy projections by release year and scenario. Select the report vintage with the `release` parameter.

    Source: https://www.eia.gov/opendata/browser/ieo
    """

    __group__ = "ieo"
    __json_schema_extra__ = {
        "history": {
            "multiple_items_allowed": True,
            "choices": ["historic", "projection"],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "africa",
                "africa_and_middle_east",
                "americas",
                "asia_pacific",
                "australia_and_new_zealand",
                "australia_new_zealand",
                "brazil",
                "canada",
                "china",
                "eastern_europe_and_eurasia",
                "europe_and_eurasia",
                "india",
                "japan",
                "mexico",
                "mexico_and_other_oecd_americas",
                "middle_east",
                "no_regional_tables",
                "oecd_europe",
                "other_americas",
                "other_asia_pacific",
                "other_non_oecd_americas",
                "other_non_oecd_asia",
                "other_non_oecd_europe_and_eurasia",
                "russia",
                "south_korea",
                "total_non_oecd",
                "total_oecd",
                "total_world",
                "united_states",
                "western_europe",
            ],
        },
        "scenario": {
            "multiple_items_allowed": True,
            "choices": [
                "high_economic_growth",
                "high_oil_price",
                "high_zero_carbon_technology_cost",
                "low_economic_growth",
                "low_oil_price",
                "low_zero_carbon_technology_cost",
                "reference",
            ],
        },
        "series": {"multiple_items_allowed": True},
        "table": {
            "multiple_items_allowed": True,
            "choices": [
                "aircraft_efficiency",
                "buildings_delivered_energy_consumption_by_end_use_sector",
                "delivered_energy_consumption_by_end_use_sector_and_fuel",
                "freight_air_transport",
                "industrial_energy_consumption_by_sector_for_selected_regions",
                "international_other_liquid_fuels_a_production_by_region_and",
                "light_duty_vehicle_stocks_by_technology",
                "new_light_duty_vehicle_sales_by_technology",
                "passenger_air_travel",
                "passenger_aircraft_capacity",
                "revenue_freight_air_transport",
                "revenue_passenger_air_travel",
                "total_commercial_jet_fuel_use_by_region",
                "transportation_sector_energy_consumption_by_region_and_fuel",
                "transportation_sector_freight_transport_energy_consumption",
                "transportation_sector_passenger_transport_energy",
                "world_carbon_dioxide_emissions_by_region",
                "world_carbon_dioxide_emissions_from_coal_use_by_region",
                "world_carbon_dioxide_emissions_from_liquids_use_by_region",
                "world_carbon_dioxide_emissions_from_natural_gas_use_by",
                "world_carbon_dioxide_intensity_of_energy_use_by_region",
                "world_coal_consumption_by_region",
                "world_coal_exports_by_region",
                "world_coal_imports_by_region",
                "world_coal_supply_by_region",
                "world_consumption_of_hydroelectricity_and_other_renewable",
                "world_crude_oil_a_production_by_region_and_country",
                "world_energy_intensity_by_region",
                "world_gross_domestic_product_by_region_expressed_in_market",
                "world_gross_domestic_product_by_region_expressed_in",
                "world_gross_domestic_product_per_capita_by_region_expressed",
                "world_installed_coal_fired_generating_capacity_by_region",
                "world_installed_geothermal_generating_capacity_by_region",
                "world_installed_hydroelectric_and_other_renewable",
                "world_installed_hydroelectric_generating_capacity_by_region",
                "world_installed_liquids_fired_generating_capacity_by_region",
                "world_installed_natural_gas_fired_generating_capacity_by",
                "world_installed_nuclear_generating_capacity_by_region_and",
                "world_installed_other_renewable_generating_capacity_by",
                "world_installed_solar_generating_capacity_by_region_and",
                "world_installed_wind_powered_generating_capacity_by_region",
                "world_liquids_consumption_by_region",
                "world_metallurgical_coal_consumptiom_by_region",
                "world_metallurgical_coal_consumption_by_region",
                "world_metallurgical_coal_exports_by_region",
                "world_metallurgical_coal_imports_by_region",
                "world_metallurgical_coal_net_trade_by_region",
                "world_metallurgical_coal_supply_by_region",
                "world_natural_gas_consumption_by_region",
                "world_net_coal_fired_electricity_generation_by_region_and",
                "world_net_geothermal_electricity_generation_by_region_and",
                "world_net_hydroelectric_and_other_renewable_electricity",
                "world_net_hydroelectric_electricity_generation_by_region",
                "world_net_liquids_fired_electricity_generation_by_region",
                "world_net_natural_gas_fired_electricity_generation_by",
                "world_net_nuclear_electricity_generation_by_region_and",
                "world_net_other_renewable_electricity_generation_by_region",
                "world_net_solar_electricity_generation_by_region_and_country",
                "world_net_trade_in_natural_gas_by_region",
                "world_net_wind_powered_electricity_generation_by_region_and",
                "world_nuclear_energy_consumption_by_region",
                "world_other_natural_gas_production_by_region",
                "world_petroleum_and_other_liquids_production_by_region_and",
                "world_population_by_region",
                "world_thermal_coal_consumptiom_by_region",
                "world_thermal_coal_exports_by_region",
                "world_thermal_coal_imports_by_region",
                "world_thermal_coal_net_trade_by_region",
                "world_thermal_coal_supply_by_region",
                "world_tight_gas_shale_gas_and_coalbed_methane_production_by",
                "world_total_coal_consumptiom_by_region",
                "world_total_coal_exports_by_region",
                "world_total_coal_imports_by_region",
                "world_total_coal_net_trade_by_region",
                "world_total_coal_supply_by_region",
                "world_total_energy_consumption_by_region_and_fuel",
                "world_total_installed_generating_capacity_by_region_and",
                "world_total_natural_gas_production_by_region",
                "world_total_net_electricity_generation_by_region_and_country",
                "world_total_primary_energy_consumption_by_region",
            ],
        },
    }

    release: Literal["2017", "2019", "2021", "2023"] = Field(
        default="2023",
        description="The International Energy Outlook release."
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
        description="Scenario filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    table: str | None = Field(
        default=None,
        description="Table filter. Accepts a comma-separated list of values.",
    )


class EiaIeoData(EiaApiData):
    """International Energy Outlook. Long-term energy projections by release year and scenario. Select the report vintage with the `release` parameter."""

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


class EiaIeoFetcher(Fetcher[EiaIeoQueryParams, list[EiaIeoData]]):
    """International Energy Outlook fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaIeoQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaIeoQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaIeoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaIeoQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaIeoData]:
        """Transform the data."""
        return transform_dataset_data(EiaIeoData, query, data)
