"""Costs and Savings from Energy Efficiency Programs model."""

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


class EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsQueryParams(
    EiaApiQueryParams
):
    """Costs and Savings from Energy Efficiency Programs. Costs and savings from energy efficiency programs by state and sector Source: Form EIA-861 Product: State Electricity Profiles, Table 13

    Source: https://www.eia.gov/opendata/browser/electricity/state-electricity-profiles/energy-efficiency
    """

    __group__ = "state_electricity_profiles"
    __dataset__ = "costs_and_savings_from_energy_efficiency_programs"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "all_other_costs",
                "customer_incentive",
                "energy_savings",
                "potential_peak_savings",
            ],
        },
        "sector": {
            "multiple_items_allowed": True,
            "choices": [
                "all_sectors",
                "commercial",
                "industrial",
                "residential",
                "transportation",
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
        "time_period": {
            "multiple_items_allowed": True,
            "choices": ["expected_life_cycle_of_programs", "reporting_year"],
        },
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: all_other_costs (thousand dollars); customer_incentive = Cost of Customer Incentives (thousand dollars); energy_savings = Annual Energy Savings (megawatthours); potential_peak_savings = Peak Demand Savings (megawatts).",
    )
    sector: str | None = Field(
        default=None,
        description="Sector filter. Accepts a comma-separated list of values.",
    )
    state: str | None = Field(
        default=None,
        description="State filter. Accepts a comma-separated list of values.",
    )
    time_period: Literal["expected_life_cycle_of_programs", "reporting_year"] | None = (
        Field(
            default=None,
            description="Time Period Included in Costs and Savings filter.",
        )
    )


class EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsData(
    EiaApiData
):
    """Costs and Savings from Energy Efficiency Programs. Costs and savings from energy efficiency programs by state and sector Source: Form EIA-861 Product: State Electricity Profiles, Table 13"""

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
    time_period: str | None = Field(
        default=None,
        description="Time Period Included in Costs and Savings code.",
    )
    time_period_name: str | None = Field(
        default=None,
        description="Time Period Included in Costs and Savings name.",
    )
    all_other_costs: float | None = Field(
        default=None,
        description="All Other Costs (thousand dollars). Withheld or unavailable values return as null.",
    )
    customer_incentive: float | None = Field(
        default=None,
        description="Cost of Customer Incentives (thousand dollars). Withheld or unavailable values return as null.",
    )
    energy_savings: float | None = Field(
        default=None,
        description="Annual Energy Savings (megawatthours). Withheld or unavailable values return as null.",
    )
    potential_peak_savings: float | None = Field(
        default=None,
        description="Peak Demand Savings (megawatts). Withheld or unavailable values return as null.",
    )


class EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsFetcher(
    Fetcher[
        EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsQueryParams,
        list[
            EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsData
        ],
    ]
):
    """Costs and Savings from Energy Efficiency Programs fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[
        EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsData
    ]:
        """Transform the data."""
        return transform_dataset_data(
            EiaStateElectricityProfilesCostsAndSavingsFromEnergyEfficiencyProgramsData,
            query,
            data,
        )
