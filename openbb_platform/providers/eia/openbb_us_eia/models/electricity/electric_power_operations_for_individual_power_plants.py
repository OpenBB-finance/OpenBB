"""Electric Power Operations for Individual Power Plants (Annual and Monthly) model."""

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


class EiaElectricityElectricPowerOperationsForIndividualPowerPlantsQueryParams(
    EiaApiQueryParams
):
    """Electric Power Operations for Individual Power Plants (Annual and Monthly). Annual and monthly electric power operations for individual power plants, by energy source and prime mover Source: Form EIA-923

    Source: https://www.eia.gov/opendata/browser/electricity/facility-fuel
    """

    __group__ = "electricity"
    __dataset__ = "electric_power_operations_for_individual_power_plants"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "average_heat_content",
                "consumption_for_eg",
                "consumption_for_eg_btu",
                "generation",
                "gross_generation",
                "total_consumption",
                "total_consumption_btu",
            ],
        },
        "fuel": {
            "multiple_items_allowed": True,
            "choices": [
                "agricultural_by_products",
                "anthracite_coal",
                "bituminous_coal",
                "black_liquor",
                "blast_furnace_gas",
                "coal_synfuel",
                "coal_derived_synthesis_gas",
                "distillate_fuel_oil",
                "electricity_used_for_energy_storage",
                "gaseous_propane",
                "geothermal",
                "hydrogen",
                "jet_fuel",
                "kerosene",
                "landfill_gas",
                "lignite_coal",
                "municipal_solid_waste",
                "municipal_solid_waste_biogenic",
                "municipal_solid_waste_non_biogenic",
                "natural_gas",
                "nuclear",
                "other",
                "other_biomass_gas",
                "other_biomass_liquids",
                "other_biomass_solids",
                "other_gas",
                "other_gases",
                "petroleum_coke",
                "purchased_steam",
                "refined_coal",
                "residual_fuel_oil",
                "sludge_waste",
                "solar",
                "subbituminous_coal",
                "synthesis_gas_from_petroleum_coke",
                "tire_derived_fuels",
                "total",
                "waste_coal",
                "waste_heat",
                "waste_oil",
                "water",
                "wind",
                "wood_waste_liquids",
                "wood_wood_waste",
            ],
        },
        "fuel_type": {
            "multiple_items_allowed": True,
            "choices": [
                "coal",
                "distillate_fuel_oil",
                "geothermal",
                "hydroelectric_conventional",
                "hydroelectric_pumped_storage",
                "municiapl_landfill_gas",
                "natural_gas",
                "nuclear",
                "other",
                "other_gases",
                "petroleum_coke",
                "residual_fuel_oil",
                "solar",
                "total",
                "waste_coal",
                "waste_oil_and_other_oils",
                "wind",
                "wood_waste_solids",
                "other_renewables",
            ],
        },
        "plant": {"multiple_items_allowed": True},
        "prime_mover": {
            "multiple_items_allowed": True,
            "choices": [
                "value",
                "all",
                "ba",
                "bt",
                "ca",
                "cc",
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
                "none",
                "north_carolina",
                "north_dakota",
                "ohio",
                "oklahoma",
                "oregon",
                "pennsylvania",
                "puerto_rico",
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
    }

    frequency: Literal["annual", "monthly", "quarterly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: average_heat_content = Average Heat Content of Consumed Fuels; consumption_for_eg = Consumption of Fuels for Electricity Generation (Physical Units); consumption_for_eg_btu = Consumption of Fuels for Electricity Generation (BTUs) (MMBtu); generation = Net Generation (megawatthours); gross_generation (megawatthours); total_consumption = Consumption of Fuels for Electricity Generation and Useful Thermal Output (Physical Units); total_consumption_btu = Consumption of Fuels for Electricity Generation and Useful Thermal Output (BTUs) (MMBtu).",
    )
    fuel: str | None = Field(
        default=None,
        description="2002 Fuel Source filter. Accepts a comma-separated list of values.",
    )
    fuel_type: str | None = Field(
        default=None,
        description="Fuel Source filter. Accepts a comma-separated list of values.",
    )
    plant: str | None = Field(
        default=None,
        description="Plant ID and Name filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    prime_mover: str | None = Field(
        default=None,
        description="Prime Mover filter. Accepts a comma-separated list of values.",
    )
    state: str | None = Field(
        default=None,
        description="State filter. Accepts a comma-separated list of values.",
    )


class EiaElectricityElectricPowerOperationsForIndividualPowerPlantsData(EiaApiData):
    """Electric Power Operations for Individual Power Plants (Annual and Monthly). Annual and monthly electric power operations for individual power plants, by energy source and prime mover Source: Form EIA-923"""

    fuel: str | None = Field(
        default=None,
        description="2002 Fuel Source code.",
    )
    fuel_name: str | None = Field(
        default=None,
        description="2002 Fuel Source name.",
    )
    fuel_type: str | None = Field(
        default=None,
        description="Fuel Source code.",
    )
    fuel_type_name: str | None = Field(
        default=None,
        description="Fuel Source name.",
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
        description="Prime Mover code.",
    )
    prime_mover_name: str | None = Field(
        default=None,
        description="Prime Mover name.",
    )
    state: str | None = Field(
        default=None,
        description="State code.",
    )
    state_name: str | None = Field(
        default=None,
        description="State name.",
    )
    average_heat_content: float | None = Field(
        default=None,
        description="Average Heat Content of Consumed Fuels. Withheld or unavailable values return as null.",
    )
    consumption_for_eg: float | None = Field(
        default=None,
        description="Consumption of Fuels for Electricity Generation (Physical Units). Withheld or unavailable values return as null.",
    )
    consumption_for_eg_btu: float | None = Field(
        default=None,
        description="Consumption of Fuels for Electricity Generation (BTUs) (MMBtu). Withheld or unavailable values return as null.",
    )
    generation: float | None = Field(
        default=None,
        description="Net Generation (megawatthours). Withheld or unavailable values return as null.",
    )
    gross_generation: float | None = Field(
        default=None,
        description="Gross Generation (megawatthours). Withheld or unavailable values return as null.",
    )
    total_consumption: float | None = Field(
        default=None,
        description="Consumption of Fuels for Electricity Generation and Useful Thermal Output (Physical Units). Withheld or unavailable values return as null.",
    )
    total_consumption_btu: float | None = Field(
        default=None,
        description="Consumption of Fuels for Electricity Generation and Useful Thermal Output (BTUs) (MMBtu). Withheld or unavailable values return as null.",
    )


class EiaElectricityElectricPowerOperationsForIndividualPowerPlantsFetcher(
    Fetcher[
        EiaElectricityElectricPowerOperationsForIndividualPowerPlantsQueryParams,
        list[EiaElectricityElectricPowerOperationsForIndividualPowerPlantsData],
    ]
):
    """Electric Power Operations for Individual Power Plants (Annual and Monthly) fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaElectricityElectricPowerOperationsForIndividualPowerPlantsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaElectricityElectricPowerOperationsForIndividualPowerPlantsQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaElectricityElectricPowerOperationsForIndividualPowerPlantsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaElectricityElectricPowerOperationsForIndividualPowerPlantsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaElectricityElectricPowerOperationsForIndividualPowerPlantsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaElectricityElectricPowerOperationsForIndividualPowerPlantsData,
            query,
            data,
        )
