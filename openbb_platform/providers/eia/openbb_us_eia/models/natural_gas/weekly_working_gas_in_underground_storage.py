"""Weekly Working Gas in Underground Storage model."""

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


class EiaNaturalGasWeeklyWorkingGasInUndergroundStorageQueryParams(EiaApiQueryParams):
    """Weekly Working Gas in Underground Storage. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/stor/wkly
    """

    __group__ = "natural_gas"
    __dataset__ = "weekly_working_gas_in_underground_storage"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "non_salt_underground_storage_working_gas",
                "salt_underground_storage_working_gas",
                "underground_storage_working_gas",
            ],
        },
        "region": {"multiple_items_allowed": True, "choices": ["na"]},
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "weekly_east_region_natural_gas_working_underground_storage",
                "weekly_lower_48_states_natural_gas_working_underground",
                "weekly_midwest_region_natural_gas_working_underground",
                "weekly_mountain_region_natural_gas_working_underground",
                "weekly_nonsalt_region_natural_gas_working_underground",
                "weekly_pacific_region_natural_gas_working_underground",
                "weekly_salt_region_natural_gas_working_underground_storage",
                "weekly_south_central_region_natural_gas_working_underground",
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


class EiaNaturalGasWeeklyWorkingGasInUndergroundStorageData(EiaApiData):
    """Weekly Working Gas in Underground Storage. EIA natural gas survey data"""

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


class EiaNaturalGasWeeklyWorkingGasInUndergroundStorageFetcher(
    Fetcher[
        EiaNaturalGasWeeklyWorkingGasInUndergroundStorageQueryParams,
        list[EiaNaturalGasWeeklyWorkingGasInUndergroundStorageData],
    ]
):
    """Weekly Working Gas in Underground Storage fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasWeeklyWorkingGasInUndergroundStorageQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasWeeklyWorkingGasInUndergroundStorageQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasWeeklyWorkingGasInUndergroundStorageQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasWeeklyWorkingGasInUndergroundStorageQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasWeeklyWorkingGasInUndergroundStorageData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasWeeklyWorkingGasInUndergroundStorageData, query, data
        )
