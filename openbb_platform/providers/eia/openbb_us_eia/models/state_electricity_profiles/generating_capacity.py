"""Generating Capacity model."""

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


class EiaStateElectricityProfilesGeneratingCapacityQueryParams(EiaApiQueryParams):
    """Generating Capacity. Electric generating capacity (summer capacity) by state, energy source, and sector. Source: Form EIA-860 Product: State Electricity Profiles, Table 4

    Source: https://www.eia.gov/opendata/browser/electricity/state-electricity-profiles/capability
    """

    __group__ = "state_electricity_profiles"
    __dataset__ = "generating_capacity"
    __json_schema_extra__ = {
        "energy_source": {
            "multiple_items_allowed": True,
            "choices": [
                "all",
                "battery",
                "coal",
                "geothermal",
                "hydroelectric",
                "natural_gas",
                "natural_gas_cc",
                "natural_gas_gt",
                "natural_gas_ic",
                "natural_gas_oth",
                "natural_gas_st",
                "nuclear",
                "other",
                "other_biomass",
                "other_gas",
                "petroleum",
                "petroleum_gt",
                "petroleum_ic",
                "petroleum_oth",
                "petroleum_st",
                "pumped_storage",
                "solar",
                "solar_pv",
                "solar_th",
                "wind",
                "wood",
            ],
        },
        "producer_type": {
            "multiple_items_allowed": True,
            "choices": [
                "all_sectors",
                "electric_utilities",
                "independent_power_producers",
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

    energy_source: str | None = Field(
        default=None,
        description="Energy Source filter. Accepts a comma-separated list of values.",
    )
    producer_type: (
        Literal["all_sectors", "electric_utilities", "independent_power_producers"]
        | None
    ) = Field(
        default=None,
        description="Sector filter.",
    )
    state: str | None = Field(
        default=None,
        description="State filter. Accepts a comma-separated list of values.",
    )


class EiaStateElectricityProfilesGeneratingCapacityData(EiaApiData):
    """Generating Capacity. Electric generating capacity (summer capacity) by state, energy source, and sector. Source: Form EIA-860 Product: State Electricity Profiles, Table 4"""

    energy_source: str | None = Field(
        default=None,
        description="Energy Source code.",
    )
    energy_source_name: str | None = Field(
        default=None,
        description="Energy Source name.",
    )
    producer_type: str | None = Field(
        default=None,
        description="Sector code.",
    )
    producer_type_name: str | None = Field(
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
    capability: float | None = Field(
        default=None,
        description="Net Summer Capacity  (megawatts). Withheld or unavailable values return as null.",
    )


class EiaStateElectricityProfilesGeneratingCapacityFetcher(
    Fetcher[
        EiaStateElectricityProfilesGeneratingCapacityQueryParams,
        list[EiaStateElectricityProfilesGeneratingCapacityData],
    ]
):
    """Generating Capacity fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaStateElectricityProfilesGeneratingCapacityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaStateElectricityProfilesGeneratingCapacityQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaStateElectricityProfilesGeneratingCapacityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaStateElectricityProfilesGeneratingCapacityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaStateElectricityProfilesGeneratingCapacityData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaStateElectricityProfilesGeneratingCapacityData, query, data
        )
