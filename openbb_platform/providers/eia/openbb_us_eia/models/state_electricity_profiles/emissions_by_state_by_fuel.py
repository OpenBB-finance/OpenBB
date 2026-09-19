"""Emissions from Energy Consumption at Conventional Power Plants and Combined-Heat-and-Power Plants model."""

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


class EiaStateElectricityProfilesEmissionsByStateByFuelQueryParams(EiaApiQueryParams):
    """Emissions from Energy Consumption at Conventional Power Plants and Combined-Heat-and-Power Plants. Emissions from electricity generation and the production of useful thermal output at conventional power plants and combined-heat-and-power plants. See Electric Power Annual, Technical Notes for a description of the sources and methodology used to develop the emissions estimates. Sources: Forms EIA-860, EIA-923, and calculations made by the Office of Energy Production, Conversion & Delivery (EPCD) Product: State Electricity Profiles, Table 7

    Source: https://www.eia.gov/opendata/browser/electricity/state-electricity-profiles/emissions-by-state-by-fuel
    """

    __group__ = "state_electricity_profiles"
    __dataset__ = "emissions_by_state_by_fuel"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": [
                "co2_rate_lbs_mwh",
                "co2_thousand_metric_tons",
                "nox_rate_lbs_mwh",
                "nox_short_tons",
                "so2_rate_lbs_mwh",
                "so2_short_tons",
            ],
        },
        "fuel": {
            "multiple_items_allowed": True,
            "choices": ["coal", "natural_gas", "other", "petroleum", "total"],
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
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: co2_rate_lbs_mwh = CO2 Emissions Rate per MWh (pounds per megawatthour); co2_thousand_metric_tons = CO2 Emissions (thousand metric tons); nox_rate_lbs_mwh = NOx Emissions Rate per MWh (pounds per megawatthour); nox_short_tons = NOx Emissions (short tons); so2_rate_lbs_mwh = SO2 Emissions Rate per MWh (pounds per megawatthour); so2_short_tons = SO2 Emissions (short tons).",
    )
    fuel: Literal["coal", "natural_gas", "other", "petroleum", "total"] | None = Field(
        default=None,
        description="Energy Source filter.",
    )
    state: str | None = Field(
        default=None,
        description="State filter. Accepts a comma-separated list of values.",
    )


class EiaStateElectricityProfilesEmissionsByStateByFuelData(EiaApiData):
    """Emissions from Energy Consumption at Conventional Power Plants and Combined-Heat-and-Power Plants. Emissions from electricity generation and the production of useful thermal output at conventional power plants and combined-heat-and-power plants. See Electric Power Annual, Technical Notes for a description of the sources and methodology used to develop the emissions estimates. Sources: Forms EIA-860, EIA-923, and calculations made by the Office of Energy Production, Conversion & Delivery (EPCD) Product: State Electricity Profiles, Table 7"""

    fuel: str | None = Field(
        default=None,
        description="Energy Source code.",
    )
    fuel_name: str | None = Field(
        default=None,
        description="Energy Source name.",
    )
    state: str | None = Field(
        default=None,
        description="State code.",
    )
    state_name: str | None = Field(
        default=None,
        description="State name.",
    )
    co2_rate_lbs_mwh: float | None = Field(
        default=None,
        description="CO2 Emissions Rate per MWh (pounds per megawatthour). Withheld or unavailable values return as null.",
    )
    co2_thousand_metric_tons: float | None = Field(
        default=None,
        description="CO2 Emissions (thousand metric tons). Withheld or unavailable values return as null.",
    )
    nox_rate_lbs_mwh: float | None = Field(
        default=None,
        description="NOx Emissions Rate per MWh (pounds per megawatthour). Withheld or unavailable values return as null.",
    )
    nox_short_tons: float | None = Field(
        default=None,
        description="NOx Emissions (short tons). Withheld or unavailable values return as null.",
    )
    so2_rate_lbs_mwh: float | None = Field(
        default=None,
        description="SO2 Emissions Rate per MWh (pounds per megawatthour). Withheld or unavailable values return as null.",
    )
    so2_short_tons: float | None = Field(
        default=None,
        description="SO2 Emissions (short tons). Withheld or unavailable values return as null.",
    )


class EiaStateElectricityProfilesEmissionsByStateByFuelFetcher(
    Fetcher[
        EiaStateElectricityProfilesEmissionsByStateByFuelQueryParams,
        list[EiaStateElectricityProfilesEmissionsByStateByFuelData],
    ]
):
    """Emissions from Energy Consumption at Conventional Power Plants and Combined-Heat-and-Power Plants fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaStateElectricityProfilesEmissionsByStateByFuelQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaStateElectricityProfilesEmissionsByStateByFuelQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaStateElectricityProfilesEmissionsByStateByFuelQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaStateElectricityProfilesEmissionsByStateByFuelQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaStateElectricityProfilesEmissionsByStateByFuelData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaStateElectricityProfilesEmissionsByStateByFuelData, query, data
        )
