"""US Nuclear Outages model."""

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


class EiaNuclearOutagesUsNuclearOutagesQueryParams(EiaApiQueryParams):
    """US Nuclear Outages. Nuclear outages daily with capacity, outages, and percent outage. Source: Nuclear Regulatory Commission's Power Reactor Status Report. Interactive data report: Daily Status of Nuclear Reactors.

    Source: https://www.eia.gov/opendata/browser/nuclear-outages/us-nuclear-outages
    """

    __group__ = "nuclear_outages"
    __dataset__ = "us_nuclear_outages"
    __json_schema_extra__ = {
        "data_type": {
            "multiple_items_allowed": True,
            "choices": ["capacity", "outage", "percent_outage"],
        },
    }

    data_type: str | None = Field(
        default=None,
        description="Data column(s) to return, comma-separated. The default returns every column. Choices: capacity (megawatts); outage (megawatts); percent_outage (percent).",
    )


class EiaNuclearOutagesUsNuclearOutagesData(EiaApiData):
    """US Nuclear Outages. Nuclear outages daily with capacity, outages, and percent outage. Source: Nuclear Regulatory Commission's Power Reactor Status Report. Interactive data report: Daily Status of Nuclear Reactors."""

    capacity: float | None = Field(
        default=None,
        description="Capacity (megawatts). Withheld or unavailable values return as null.",
    )
    outage: float | None = Field(
        default=None,
        description="Outage (megawatts). Withheld or unavailable values return as null.",
    )
    percent_outage: float | None = Field(
        default=None,
        description="Percent outage (percent). Withheld or unavailable values return as null.",
    )


class EiaNuclearOutagesUsNuclearOutagesFetcher(
    Fetcher[
        EiaNuclearOutagesUsNuclearOutagesQueryParams,
        list[EiaNuclearOutagesUsNuclearOutagesData],
    ]
):
    """US Nuclear Outages fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNuclearOutagesUsNuclearOutagesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNuclearOutagesUsNuclearOutagesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNuclearOutagesUsNuclearOutagesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNuclearOutagesUsNuclearOutagesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNuclearOutagesUsNuclearOutagesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNuclearOutagesUsNuclearOutagesData, query, data
        )
