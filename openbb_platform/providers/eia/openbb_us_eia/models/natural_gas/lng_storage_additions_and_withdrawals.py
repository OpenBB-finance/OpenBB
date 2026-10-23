"""Liquefied Natural Gas Additions to and Withdrawals from Storage model."""

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


class EiaNaturalGasLngStorageAdditionsAndWithdrawalsQueryParams(EiaApiQueryParams):
    """Liquefied Natural Gas Additions to and Withdrawals from Storage. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/stor/lng
    """

    __group__ = "natural_gas"
    __dataset__ = "lng_storage_additions_and_withdrawals"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "lng_storage_additions",
                "lng_storage_net_withdrawals",
                "lng_storage_withdrawals",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "florida",
                "massachusetts",
                "minnesota",
                "new_york",
                "texas",
                "us",
                "usa_ak",
                "usa_al",
                "usa_ar",
                "usa_az",
                "usa_ct",
                "usa_de",
                "usa_ga",
                "usa_ia",
                "usa_id",
                "usa_il",
                "usa_in",
                "usa_la",
                "usa_md",
                "usa_me",
                "usa_mo",
                "usa_mt",
                "usa_nc",
                "usa_ne",
                "usa_nh",
                "usa_nj",
                "usa_nm",
                "usa_nv",
                "usa_ok",
                "usa_or",
                "usa_pa",
                "usa_ri",
                "usa_sc",
                "usa_sd",
                "usa_tn",
                "usa_ut",
                "usa_va",
                "usa_wi",
                "usa_wy",
                "washington",
            ],
        },
        "series": {"multiple_items_allowed": True},
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
        description="Series filter. Accepts a comma-separated list of values. There are 123 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasLngStorageAdditionsAndWithdrawalsData(EiaApiData):
    """Liquefied Natural Gas Additions to and Withdrawals from Storage. EIA natural gas survey data"""

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


class EiaNaturalGasLngStorageAdditionsAndWithdrawalsFetcher(
    Fetcher[
        EiaNaturalGasLngStorageAdditionsAndWithdrawalsQueryParams,
        list[EiaNaturalGasLngStorageAdditionsAndWithdrawalsData],
    ]
):
    """Liquefied Natural Gas Additions to and Withdrawals from Storage fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasLngStorageAdditionsAndWithdrawalsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasLngStorageAdditionsAndWithdrawalsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasLngStorageAdditionsAndWithdrawalsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasLngStorageAdditionsAndWithdrawalsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasLngStorageAdditionsAndWithdrawalsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasLngStorageAdditionsAndWithdrawalsData, query, data
        )
