"""Supply and disposition of electricity model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from pydantic import Field

from openbb_us_eia.utils.api_query import (
    EiaApiData,
    EiaApiQueryParams,
    extract_dataset_data,
    transform_dataset_data,
    transform_dataset_query,
)


class EiaStateElectricityProfilesSupplyAndDispositionOfElectricityQueryParams(
    EiaApiQueryParams
):
    """Supply and disposition of electricity. Supply and disposition of electricity by state. Sources: Forms EIA-860, EIA-861, and EIA-923 Product: State Electricity Profiles, Table 10

    Source: https://www.eia.gov/opendata/browser/electricity/state-electricity-profiles/source-disposition
    """

    __group__ = "state_electricity_profiles"
    __dataset__ = "supply_and_disposition_of_electricity"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "combined_heat_and_pwr_comm",
                "combined_heat_and_pwr_elect",
                "combined_heat_and_pwr_indust",
                "direct_use",
                "elect_pwr_sector_gen_subtotal",
                "electric_utilities",
                "energy_only_providers",
                "estimated_losses",
                "facility_direct",
                "full_service_providers",
                "independent_power_producers",
                "indust_and_comm_gen_subtotal",
                "net_interstate_trade",
                "net_trade_index",
                "total_disposition",
                "total_elect_indust",
                "total_international_exports",
                "total_international_imports",
                "total_net_generation",
                "total_supply",
                "unaccounted",
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
                "united_states",
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

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: combined_heat_and_pwr_comm = Net Generation from Commercial Sector (megawatthours); combined_heat_and_pwr_elect = Net Generation from Independent Power Producers, Combined Heat and Power (megawatthours); combined_heat_and_pwr_indust = Net Generation from Industrial Sector (megawatthours); direct_use = Direct Use of Generation by Commercial and Industrial Facilities (megawatthours); elect_pwr_sector_gen_subtotal = Net Generation from Electric Power Sector (megawatthours); electric_utilities = Net Generation from Electric Utilities (megawatthours); energy_only_providers = Retail Sales of Electrcity by Energy-Only Providers (megawatthours); estimated_losses = Estimated Losses Incurred in Transmission and Distribution (megawatthours); facility_direct = Retail Sales of Electricity Sold Directly by Commercial and Industrial Facilities (megawatthours); full_service_providers = Retail Sales of Electricity by Full Service Providers (megawatthours); independent_power_producers = Net Generation from Independent Power Producers, Non-Combined Heat and Power (megawatthours); indust_and_comm_gen_subtotal = Net Generation from Industrial and Commercial Sectors (megawatthours); net_interstate_trade = Net Interstate Imports (megawatthours); net_trade_index = Net Trade Index Ratio (ratio); total_disposition (megawatthours); total_elect_indust = Retail Sales of Electricity, Total Electric Industry (megawatthours); total_international_exports (megawatthours); total_international_imports (megawatthours); total_net_generation = Net Generation from All Sectors (megawatthours); total_supply (megawatthours); unaccounted = Unaccounted Electricity (megawatthours).",
    )
    state: str | None = Field(
        default=None,
        description="State filter. Accepts a comma-separated list of values.",
    )


class EiaStateElectricityProfilesSupplyAndDispositionOfElectricityData(EiaApiData):
    """Supply and disposition of electricity. Supply and disposition of electricity by state. Sources: Forms EIA-860, EIA-861, and EIA-923 Product: State Electricity Profiles, Table 10"""

    state: str | None = Field(
        default=None,
        description="State code.",
    )
    state_name: str | None = Field(
        default=None,
        description="State name.",
    )
    combined_heat_and_pwr_comm: float | None = Field(
        default=None,
        description="Net Generation from Commercial Sector (megawatthours). Withheld or unavailable values return as null.",
    )
    combined_heat_and_pwr_elect: float | None = Field(
        default=None,
        description="Net Generation from Independent Power Producers, Combined Heat and Power (megawatthours). Withheld or unavailable values return as null.",
    )
    combined_heat_and_pwr_indust: float | None = Field(
        default=None,
        description="Net Generation from Industrial Sector (megawatthours). Withheld or unavailable values return as null.",
    )
    direct_use: float | None = Field(
        default=None,
        description="Direct Use of Generation by Commercial and Industrial Facilities (megawatthours). Withheld or unavailable values return as null.",
    )
    elect_pwr_sector_gen_subtotal: float | None = Field(
        default=None,
        description="Net Generation from Electric Power Sector (megawatthours). Withheld or unavailable values return as null.",
    )
    electric_utilities: float | None = Field(
        default=None,
        description="Net Generation from Electric Utilities (megawatthours). Withheld or unavailable values return as null.",
    )
    energy_only_providers: float | None = Field(
        default=None,
        description="Retail Sales of Electrcity by Energy-Only Providers (megawatthours). Withheld or unavailable values return as null.",
    )
    estimated_losses: float | None = Field(
        default=None,
        description="Estimated Losses Incurred in Transmission and Distribution (megawatthours). Withheld or unavailable values return as null.",
    )
    facility_direct: float | None = Field(
        default=None,
        description="Retail Sales of Electricity Sold Directly by Commercial and Industrial Facilities (megawatthours). Withheld or unavailable values return as null.",
    )
    full_service_providers: float | None = Field(
        default=None,
        description="Retail Sales of Electricity by Full Service Providers (megawatthours). Withheld or unavailable values return as null.",
    )
    independent_power_producers: float | None = Field(
        default=None,
        description="Net Generation from Independent Power Producers, Non-Combined Heat and Power (megawatthours). Withheld or unavailable values return as null.",
    )
    indust_and_comm_gen_subtotal: float | None = Field(
        default=None,
        description="Net Generation from Industrial and Commercial Sectors (megawatthours). Withheld or unavailable values return as null.",
    )
    net_interstate_trade: float | None = Field(
        default=None,
        description="Net Interstate Imports (megawatthours). Withheld or unavailable values return as null.",
    )
    net_trade_index: float | None = Field(
        default=None,
        description="Net Trade Index Ratio (ratio). Withheld or unavailable values return as null.",
    )
    total_disposition: float | None = Field(
        default=None,
        description="Total Disposition (megawatthours). Withheld or unavailable values return as null.",
    )
    total_elect_indust: float | None = Field(
        default=None,
        description="Retail Sales of Electricity, Total Electric Industry (megawatthours). Withheld or unavailable values return as null.",
    )
    total_international_exports: float | None = Field(
        default=None,
        description="Total International Exports (megawatthours). Withheld or unavailable values return as null.",
    )
    total_international_imports: float | None = Field(
        default=None,
        description="Total International Imports (megawatthours). Withheld or unavailable values return as null.",
    )
    total_net_generation: float | None = Field(
        default=None,
        description="Net Generation from All Sectors (megawatthours). Withheld or unavailable values return as null.",
    )
    total_supply: float | None = Field(
        default=None,
        description="Total Supply (megawatthours). Withheld or unavailable values return as null.",
    )
    unaccounted: float | None = Field(
        default=None,
        description="Unaccounted Electricity (megawatthours). Withheld or unavailable values return as null.",
    )


class EiaStateElectricityProfilesSupplyAndDispositionOfElectricityFetcher(
    Fetcher[
        EiaStateElectricityProfilesSupplyAndDispositionOfElectricityQueryParams,
        list[EiaStateElectricityProfilesSupplyAndDispositionOfElectricityData],
    ]
):
    """Supply and disposition of electricity fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaStateElectricityProfilesSupplyAndDispositionOfElectricityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaStateElectricityProfilesSupplyAndDispositionOfElectricityQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaStateElectricityProfilesSupplyAndDispositionOfElectricityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaStateElectricityProfilesSupplyAndDispositionOfElectricityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaStateElectricityProfilesSupplyAndDispositionOfElectricityData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaStateElectricityProfilesSupplyAndDispositionOfElectricityData,
            query,
            data,
        )
