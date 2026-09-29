"""Maximum US Active Seismic Crew Counts model."""

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


class EiaNaturalGasMaximumUsActiveSeismicCrewCountsQueryParams(EiaApiQueryParams):
    """Maximum US Active Seismic Crew Counts. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/enr/seis
    """

    __group__ = "natural_gas"
    __dataset__ = "maximum_us_active_seismic_crew_counts"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "maximum_number_of_active_crews_engaged_in_four_dimensional",
                "maximum_number_of_active_crews_engaged_in_sismic_surveying",
                "maximum_number_of_active_crews_engaged_in_three_dimensional",
                "maximum_number_of_active_crews_engaged_in_two_dimensional",
            ],
        },
        "region": {"multiple_items_allowed": True, "choices": ["na", "us", "usa_ak"]},
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "alaska_maximum_number_of_active_crews_engaged_in_four",
                "alaska_maximum_number_of_active_crews_engaged_in_seismic",
                "alaska_maximum_number_of_active_crews_engaged_in_three",
                "alaska_maximum_number_of_active_crews_engaged_in_two",
                "us_lower_48_states_offshore_maximum_number_of_active_crews_engaged_in_seismic_surveying_count",
                "us_lower_48_states_onshore_maximum_number_of_active_crews_engaged_in_seismic_surveying_count",
                "us_maximum_number_of_active_crews_engaged_in_seismic",
                "us_lower_48_states_offshore_maximum_number_of_active_crews_engaged_in_four_dimensional_seismic_surveying_count",
                "us_lower_48_states_offshore_maximum_number_of_active_crews_engaged_in_three_dimensional_seismic_surveying_count",
                "us_lower_48_states_offshore_maximum_number_of_active_crews_engaged_in_two_dimensional_seismic_surveying_count",
                "us_lower_48_states_onshore_maximum_number_of_active_crews_engaged_in_four_dimensional_seismic_surveying_count",
                "us_lower_48_states_onshore_maximum_number_of_active_crews_engaged_in_three_dimensional_seismic_surveying_count",
                "us_lower_48_states_onshore_maximum_number_of_active_crews_engaged_in_two_dimensional_seismic_surveying_count",
            ],
        },
    }

    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasMaximumUsActiveSeismicCrewCountsData(EiaApiData):
    """Maximum US Active Seismic Crew Counts. EIA natural gas survey data"""

    process: str | None = Field(
        default=None,
        description="Process code.",
    )
    process_name: str | None = Field(
        default=None,
        description="Process name.",
    )
    product: str | None = Field(
        default=None,
        description="Product code.",
    )
    product_name: str | None = Field(
        default=None,
        description="Product name.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea code.",
    )
    region_name: str | None = Field(
        default=None,
        description="DuoArea name.",
    )
    series: str | None = Field(
        default=None,
        description="Series code.",
    )
    series_name: str | None = Field(
        default=None,
        description="Series name.",
    )
    value: float | None = Field(
        default=None,
        description="Value. Withheld or unavailable values return as null.",
    )
    units: str | None = Field(
        default=None,
        description="Unit of the value.",
    )


class EiaNaturalGasMaximumUsActiveSeismicCrewCountsFetcher(
    Fetcher[
        EiaNaturalGasMaximumUsActiveSeismicCrewCountsQueryParams,
        list[EiaNaturalGasMaximumUsActiveSeismicCrewCountsData],
    ]
):
    """Maximum US Active Seismic Crew Counts fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasMaximumUsActiveSeismicCrewCountsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasMaximumUsActiveSeismicCrewCountsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasMaximumUsActiveSeismicCrewCountsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasMaximumUsActiveSeismicCrewCountsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasMaximumUsActiveSeismicCrewCountsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasMaximumUsActiveSeismicCrewCountsData, query, data
        )
