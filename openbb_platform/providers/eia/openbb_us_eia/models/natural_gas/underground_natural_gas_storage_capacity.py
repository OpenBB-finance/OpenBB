"""Underground Natural Gas Storage Capacity model."""

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


class EiaNaturalGasUndergroundNaturalGasStorageCapacityQueryParams(EiaApiQueryParams):
    """Underground Natural Gas Storage Capacity. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/stor/cap
    """

    __group__ = "natural_gas"
    __dataset__ = "underground_natural_gas_storage_capacity"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "count_of_underground_storage_capacity",
                "total_underground_storage_capacity",
                "working_underground_storage_capacity",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "minnesota",
                "na",
                "new_york",
                "ohio",
                "texas",
                "us",
                "usa_ak",
                "usa_al",
                "usa_ar",
                "usa_ia",
                "usa_il",
                "usa_in",
                "usa_ks",
                "usa_ky",
                "usa_la",
                "usa_md",
                "usa_mi",
                "usa_mo",
                "usa_ms",
                "usa_mt",
                "usa_ne",
                "usa_nm",
                "usa_ok",
                "usa_or",
                "usa_pa",
                "usa_tn",
                "usa_ut",
                "usa_va",
                "usa_wv",
                "usa_wy",
                "washington",
            ],
        },
        "series": {"multiple_items_allowed": True},
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
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
        description="Series filter. Accepts a comma-separated list of values. There are 123 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasUndergroundNaturalGasStorageCapacityData(EiaApiData):
    """Underground Natural Gas Storage Capacity. EIA natural gas survey data"""

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


class EiaNaturalGasUndergroundNaturalGasStorageCapacityFetcher(
    Fetcher[
        EiaNaturalGasUndergroundNaturalGasStorageCapacityQueryParams,
        list[EiaNaturalGasUndergroundNaturalGasStorageCapacityData],
    ]
):
    """Underground Natural Gas Storage Capacity fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasUndergroundNaturalGasStorageCapacityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasUndergroundNaturalGasStorageCapacityQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasUndergroundNaturalGasStorageCapacityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasUndergroundNaturalGasStorageCapacityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasUndergroundNaturalGasStorageCapacityData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasUndergroundNaturalGasStorageCapacityData, query, data
        )
