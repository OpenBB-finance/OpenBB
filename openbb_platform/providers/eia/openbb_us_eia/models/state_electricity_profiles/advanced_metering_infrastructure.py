"""Advanced Metering Infrastructure model."""

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


class EiaStateElectricityProfilesAdvancedMeteringInfrastructureQueryParams(
    EiaApiQueryParams
):
    """Advanced Metering Infrastructure. Advanced meterting counts by technology, state, and sector Source: Forms EIA-861, EIA-861S Product: State Electricity Profiles, Table 12

    Source: https://www.eia.gov/opendata/browser/electricity/state-electricity-profiles/meters
    """

    __group__ = "state_electricity_profiles"
    __dataset__ = "advanced_metering_infrastructure"
    __json_schema_extra__ = {
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
        "technology": {
            "multiple_items_allowed": True,
            "choices": [
                "advanced_metering_infrastructure",
                "all_meters",
                "automated_meter_reading",
                "standard_meters",
            ],
        },
    }

    sector: str | None = Field(
        default=None,
        description="sector filter. Accepts a comma-separated list of values.",
    )
    state: str | None = Field(
        default=None,
        description="State filter. Accepts a comma-separated list of values.",
    )
    technology: str | None = Field(
        default=None,
        description="Meter Technology filter. Accepts a comma-separated list of values.",
    )


class EiaStateElectricityProfilesAdvancedMeteringInfrastructureData(EiaApiData):
    """Advanced Metering Infrastructure. Advanced meterting counts by technology, state, and sector Source: Forms EIA-861, EIA-861S Product: State Electricity Profiles, Table 12"""

    sector: str | None = Field(
        default=None,
        description="sector code.",
    )
    sector_name: str | None = Field(
        default=None,
        description="sector name.",
    )
    state: str | None = Field(
        default=None,
        description="State code.",
    )
    state_name: str | None = Field(
        default=None,
        description="State name.",
    )
    technology: str | None = Field(
        default=None,
        description="Meter Technology code.",
    )
    technology_name: str | None = Field(
        default=None,
        description="Meter Technology name.",
    )
    meters: float | None = Field(
        default=None,
        description="Meter Count (number of meters). Withheld or unavailable values return as null.",
    )


class EiaStateElectricityProfilesAdvancedMeteringInfrastructureFetcher(
    Fetcher[
        EiaStateElectricityProfilesAdvancedMeteringInfrastructureQueryParams,
        list[EiaStateElectricityProfilesAdvancedMeteringInfrastructureData],
    ]
):
    """Advanced Metering Infrastructure fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaStateElectricityProfilesAdvancedMeteringInfrastructureQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaStateElectricityProfilesAdvancedMeteringInfrastructureQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaStateElectricityProfilesAdvancedMeteringInfrastructureQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaStateElectricityProfilesAdvancedMeteringInfrastructureQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaStateElectricityProfilesAdvancedMeteringInfrastructureData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaStateElectricityProfilesAdvancedMeteringInfrastructureData, query, data
        )
