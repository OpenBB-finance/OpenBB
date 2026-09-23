"""Electric Power Operations (Annual and Monthly) model."""

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


class EiaElectricityElectricPowerOperationsQueryParams(EiaApiQueryParams):
    """Electric Power Operations (Annual and Monthly). Monthly and annual electric power operations by state, sector, and energy source. Source: Form EIA-923

    Source: https://www.eia.gov/opendata/browser/electricity/electric-power-operational-data
    """

    __group__ = "electricity"
    __dataset__ = "electric_power_operations"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "ash_content",
                "consumption_for_eg",
                "consumption_for_eg_btu",
                "consumption_uto",
                "consumption_uto_btu",
                "cost",
                "cost_per_btu",
                "generation",
                "heat_content",
                "receipts",
                "receipts_btu",
                "stocks",
                "sulfur_content",
                "total_consumption",
                "total_consumption_btu",
            ],
        },
        "fuel": {
            "multiple_items_allowed": True,
            "choices": [
                "all_coal_products",
                "all_fuels",
                "all_renewables",
                "anthracite_coal",
                "biogenic_municipal_solid_waste",
                "biomass",
                "bituminous_coal",
                "bituminous_coal_and_synthetic_coal",
                "coal_excluding_waste_coal",
                "conventional_hydroelectric",
                "distillate_fuel_oil",
                "estimated_small_scale_solar_photovoltaic",
                "estimated_total_solar",
                "estimated_total_solar_photovoltaic",
                "fossil_fuels",
                "geothermal",
                "hydro_electric_pumped_storage",
                "landfill_gas",
                "lignite_coal",
                "municiapl_landfill_gas",
                "natural_gas",
                "natural_gas_and_other_gases",
                "nuclear",
                "offshore_wind_turbine",
                "onshore_wind_turbine",
                "other",
                "other_gases",
                "other_renewables",
                "petroleum",
                "petroleum_coke",
                "petroleum_liquids",
                "refined_coal",
                "renewable",
                "renewable_waste_products",
                "residual_fuel_oil",
                "solar",
                "solar_photovoltaic",
                "solar_thermal",
                "subbituminous_coal",
                "waste_coal",
                "waste_oil_and_other_oils",
                "wind",
                "wood_and_wood_wastes",
            ],
        },
        "sector": {
            "multiple_items_allowed": True,
            "choices": [
                "all_commercial",
                "all_industrial",
                "all_sectors",
                "coal_consumption",
                "commercial_chp",
                "commercial_non_chp",
                "electric_power",
                "electric_power_sector_non_chp",
                "electric_utility",
                "ipp_chp",
                "ipp_non_chp",
                "independent_power_producers",
                "industrial_chp",
                "industrial_non_chp",
                "residential",
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
                "east_north_central",
                "east_south_central",
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
                "middle_atlantic",
                "minnesota",
                "mississippi",
                "missouri",
                "montana",
                "mountain",
                "nebraska",
                "nevada",
                "new_england",
                "new_hampshire",
                "new_jersey",
                "new_mexico",
                "new_york",
                "north_carolina",
                "north_dakota",
                "ohio",
                "oklahoma",
                "oregon",
                "pacific",
                "pacific_contiguous",
                "pacific_noncontiguous",
                "pennsylvania",
                "puerto_rico",
                "rhode_island",
                "south_atlantic",
                "south_carolina",
                "south_dakota",
                "tennessee",
                "texas",
                "us_total",
                "utah",
                "vermont",
                "virginia",
                "washington",
                "west_north_central",
                "west_south_central",
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
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: ash_content = Average Ash Content of Consumed Fuel; consumption_for_eg = Consumption of Fuels for Electricity Generation (Physical Units); consumption_for_eg_btu = Consumption of Fuels for Electricity Generation (BTUs); consumption_uto = Consumption of Fuels for Useful Thermal Output (Physical Units); consumption_uto_btu = Consumption of Fuels for Useful Thermal Output (BTUs); cost = Average Cost of Fuels (per Physical Unit); cost_per_btu = Average Cost of Fuels (per BTU); generation = Utility Scale Electricity Net Generation; heat_content = Average Heat Content of Consumed Fuels; receipts = Receipts of Fuel (Physical Units); receipts_btu = Receipts of Fuel (BTUs); stocks = Stocks of Fuel (Physical Units); sulfur_content = Average Sulfur Content of Consumed Fuel; total_consumption = Consumption of Fuels for Electricity Generation and Useful Thermal Output (Physical Units); total_consumption_btu = Consumption of Fuels for Electricity Generation and Useful Thermal Output (BTUs).",
    )
    fuel: str | None = Field(
        default=None,
        description="Energy Source filter. Accepts a comma-separated list of values.",
    )
    sector: str | None = Field(
        default=None,
        description="Sector filter. Accepts a comma-separated list of values.",
    )
    state: str | None = Field(
        default=None,
        description="State / Census Region filter. Accepts a comma-separated list of values.",
    )


class EiaElectricityElectricPowerOperationsData(EiaApiData):
    """Electric Power Operations (Annual and Monthly). Monthly and annual electric power operations by state, sector, and energy source. Source: Form EIA-923"""

    fuel: str | None = Field(
        default=None,
        description="Energy Source code.",
    )
    fuel_name: str | None = Field(
        default=None,
        description="Energy Source name.",
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
        description="State / Census Region code.",
    )
    state_name: str | None = Field(
        default=None,
        description="State / Census Region name.",
    )
    ash_content: float | None = Field(
        default=None,
        description="Average Ash Content of Consumed Fuel. Withheld or unavailable values return as null.",
    )
    consumption_for_eg: float | None = Field(
        default=None,
        description="Consumption of Fuels for Electricity Generation (Physical Units). Withheld or unavailable values return as null.",
    )
    consumption_for_eg_btu: float | None = Field(
        default=None,
        description="Consumption of Fuels for Electricity Generation (BTUs). Withheld or unavailable values return as null.",
    )
    consumption_uto: float | None = Field(
        default=None,
        description="Consumption of Fuels for Useful Thermal Output (Physical Units). Withheld or unavailable values return as null.",
    )
    consumption_uto_btu: float | None = Field(
        default=None,
        description="Consumption of Fuels for Useful Thermal Output (BTUs). Withheld or unavailable values return as null.",
    )
    cost: float | None = Field(
        default=None,
        description="Average Cost of Fuels (per Physical Unit). Withheld or unavailable values return as null.",
    )
    cost_per_btu: float | None = Field(
        default=None,
        description="Average Cost of Fuels (per BTU). Withheld or unavailable values return as null.",
    )
    generation: float | None = Field(
        default=None,
        description="Utility Scale Electricity Net Generation. Withheld or unavailable values return as null.",
    )
    heat_content: float | None = Field(
        default=None,
        description="Average Heat Content of Consumed Fuels. Withheld or unavailable values return as null.",
    )
    receipts: float | None = Field(
        default=None,
        description="Receipts of Fuel (Physical Units). Withheld or unavailable values return as null.",
    )
    receipts_btu: float | None = Field(
        default=None,
        description="Receipts of Fuel (BTUs). Withheld or unavailable values return as null.",
    )
    stocks: float | None = Field(
        default=None,
        description="Stocks of Fuel (Physical Units). Withheld or unavailable values return as null.",
    )
    sulfur_content: float | None = Field(
        default=None,
        description="Average Sulfur Content of Consumed Fuel. Withheld or unavailable values return as null.",
    )
    total_consumption: float | None = Field(
        default=None,
        description="Consumption of Fuels for Electricity Generation and Useful Thermal Output (Physical Units). Withheld or unavailable values return as null.",
    )
    total_consumption_btu: float | None = Field(
        default=None,
        description="Consumption of Fuels for Electricity Generation and Useful Thermal Output (BTUs). Withheld or unavailable values return as null.",
    )


class EiaElectricityElectricPowerOperationsFetcher(
    Fetcher[
        EiaElectricityElectricPowerOperationsQueryParams,
        list[EiaElectricityElectricPowerOperationsData],
    ]
):
    """Electric Power Operations (Annual and Monthly) fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaElectricityElectricPowerOperationsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaElectricityElectricPowerOperationsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaElectricityElectricPowerOperationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaElectricityElectricPowerOperationsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaElectricityElectricPowerOperationsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaElectricityElectricPowerOperationsData, query, data
        )
