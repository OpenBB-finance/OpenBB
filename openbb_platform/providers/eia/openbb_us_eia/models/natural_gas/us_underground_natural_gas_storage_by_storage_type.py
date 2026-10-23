"""US Underground Natural Gas Storage by Storage Type model."""

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


class EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeQueryParams(
    EiaApiQueryParams
):
    """US Underground Natural Gas Storage by Storage Type. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/stor/type
    """

    __group__ = "natural_gas"
    __dataset__ = "us_underground_natural_gas_storage_by_storage_type"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "non_salt_underground_storage_base_gas",
                "non_salt_underground_storage_total",
                "non_salt_underground_storage_working_gas",
                "non_salt_underground_storage_activity_net",
                "non_salt_underground_storage_activity_withdraw",
                "non_salt_underground_storage_injections",
                "salt_underground_storage_base_gas",
                "salt_underground_storage_total",
                "salt_underground_storage_working_gas",
                "salt_underground_storage_activity_injects",
                "salt_underground_storage_activity_net",
                "salt_underground_storage_activity_withdraw",
                "total_underground_storage",
                "underground_storage_base_gas",
                "underground_storage_injections",
                "underground_storage_net_withdrawals",
                "underground_storage_withdrawals",
                "underground_storage_working_gas",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_natural_gas_underground_storage_withdrawals",
                "us_natural_gas_non_salt_underground_storage_base_gas",
                "us_natural_gas_non_salt_underground_storage_total",
                "us_natural_gas_non_salt_underground_storage_working_gas",
                "us_natural_gas_non_salt_underground_storage_activity_net",
                "us_natural_gas_non_salt_underground_storage_activity",
                "us_natural_gas_non_salt_underground_storage_injections",
                "us_natural_gas_salt_underground_storage_base_gas",
                "us_natural_gas_salt_underground_storage_total",
                "us_natural_gas_salt_underground_storage_working_gas",
                "us_natural_gas_salt_underground_storage_activity_injects",
                "us_natural_gas_salt_underground_storage_activity_net",
                "us_natural_gas_salt_underground_storage_activity_withdraw",
                "us_natural_gas_underground_storage_net_withdrawals",
                "us_natural_gas_underground_storage_volume",
                "us_total_natural_gas_injections_into_underground_storage",
                "us_total_natural_gas_in_underground_storage_base_gas_mmcf",
                "us_total_natural_gas_in_underground_storage_working_gas_mmcf",
            ],
        },
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )
    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeData(EiaApiData):
    """US Underground Natural Gas Storage by Storage Type. EIA natural gas survey data"""

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


class EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeFetcher(
    Fetcher[
        EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeQueryParams,
        list[EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeData],
    ]
):
    """US Underground Natural Gas Storage by Storage Type fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasUsUndergroundNaturalGasStorageByStorageTypeData, query, data
        )
