"""Underground Natural Gas Storage by All Operators model."""

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


class EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsQueryParams(
    EiaApiQueryParams
):
    """Underground Natural Gas Storage by All Operators. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/stor/sum
    """

    __group__ = "natural_gas"
    __dataset__ = "underground_natural_gas_storage_by_all_operators"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "total_underground_storage",
                "underground_change_in_working_gas",
                "underground_storage_base_gas",
                "underground_storage_injections",
                "underground_storage_net_withdrawals",
                "underground_storage_withdrawals",
                "underground_storage_working_gas",
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
                "usa_ri",
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
        description="Series filter. Accepts a comma-separated list of values. There are 329 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsData(EiaApiData):
    """Underground Natural Gas Storage by All Operators. EIA natural gas survey data"""

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


class EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsFetcher(
    Fetcher[
        EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsQueryParams,
        list[EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsData],
    ]
):
    """Underground Natural Gas Storage by All Operators fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasUndergroundNaturalGasStorageByAllOperatorsData, query, data
        )
