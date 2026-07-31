"""Wood Pellet Plant Capacity model."""

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


class EiaDensifiedBiomassWoodPelletPlantCapacityQueryParams(EiaApiQueryParams):
    """Wood Pellet Plant Capacity. Details on wood pellet plants includes region, respondent, capacity, and status. Source: EIA-63C Report: www.eia.gov/biomass/

    Source: https://www.eia.gov/opendata/browser/densified-biomass/wood-pellet-plants
    """

    __group__ = "densified_biomass"
    __dataset__ = "wood_pellet_plant_capacity"
    __json_schema_extra__ = {
        "region": {
            "multiple_items_allowed": True,
            "choices": ["east", "south", "west"],
        },
        "respondent": {"multiple_items_allowed": True},
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
                "florida",
                "georgia",
                "idaho",
                "illinois",
                "indiana",
                "iowa",
                "kentucky",
                "louisiana",
                "maine",
                "michigan",
                "mississippi",
                "missouri",
                "new_hampshire",
                "new_mexico",
                "new_york",
                "north_carolina",
                "ohio",
                "oregon",
                "pennsylvania",
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
            ],
        },
        "status": {
            "multiple_items_allowed": True,
            "choices": [
                "currently_operating",
                "none",
                "temporarily_not_in_operation",
                "under_construction_planned",
                "currently_operating_currently_operating",
            ],
        },
    }

    region: Literal["east", "south", "west"] | None = Field(
        default=None,
        description="Region filter.",
    )
    respondent: str | None = Field(
        default=None,
        description="Respondent filter. Accepts a comma-separated list of values. There are 161 valid values - use the `facet_options` endpoint to list them.",
    )
    state: str | None = Field(
        default=None,
        description="State filter. Accepts a comma-separated list of values.",
    )
    status: (
        Literal[
            "currently_operating",
            "none",
            "temporarily_not_in_operation",
            "under_construction_planned",
            "currently_operating_currently_operating",
        ]
        | None
    ) = Field(
        default=None,
        description="Operational Status filter.",
    )


class EiaDensifiedBiomassWoodPelletPlantCapacityData(EiaApiData):
    """Wood Pellet Plant Capacity. Details on wood pellet plants includes region, respondent, capacity, and status. Source: EIA-63C Report: www.eia.gov/biomass/"""

    region: str | None = Field(
        default=None,
        description="Region code.",
    )
    region_name: str | None = Field(
        default=None,
        description="Region name.",
    )
    respondent: str | None = Field(
        default=None,
        description="Respondent code.",
    )
    respondent_name: str | None = Field(
        default=None,
        description="Respondent name.",
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
        description="Operational Status code.",
    )
    status_name: str | None = Field(
        default=None,
        description="Operational Status name.",
    )
    capacity: float | None = Field(
        default=None,
        description="Capacity (tons per year). Withheld or unavailable values return as null.",
    )


class EiaDensifiedBiomassWoodPelletPlantCapacityFetcher(
    Fetcher[
        EiaDensifiedBiomassWoodPelletPlantCapacityQueryParams,
        list[EiaDensifiedBiomassWoodPelletPlantCapacityData],
    ]
):
    """Wood Pellet Plant Capacity fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaDensifiedBiomassWoodPelletPlantCapacityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaDensifiedBiomassWoodPelletPlantCapacityQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaDensifiedBiomassWoodPelletPlantCapacityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaDensifiedBiomassWoodPelletPlantCapacityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaDensifiedBiomassWoodPelletPlantCapacityData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaDensifiedBiomassWoodPelletPlantCapacityData, query, data
        )
