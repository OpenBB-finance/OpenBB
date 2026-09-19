"""Natural Gas Delivered for the Account of Others model."""

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


class EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersQueryParams(
    EiaApiQueryParams
):
    """Natural Gas Delivered for the Account of Others. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/cons/acct
    """

    __group__ = "natural_gas"
    __dataset__ = "natural_gas_delivered_for_the_account_of_others"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "total_residential_consumers_deliveries",
                "of_total_commercial_delivered_for_the_account_of_others",
                "of_total_industrial_delivered_for_the_account_of_others",
                "delivered_to_commercial_consumers_for_the_account_of_others",
                "delivered_to_industrial_consumers_for_the_account_of_others",
                "residential_transported",
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
                "ohio",
                "texas",
                "us",
                "usa_ak",
                "usa_al",
                "usa_ar",
                "usa_az",
                "usa_ct",
                "usa_dc",
                "usa_de",
                "usa_ga",
                "usa_ia",
                "usa_id",
                "usa_il",
                "usa_in",
                "usa_ks",
                "usa_ky",
                "usa_la",
                "usa_md",
                "usa_me",
                "usa_mi",
                "usa_mo",
                "usa_ms",
                "usa_mt",
                "usa_nc",
                "usa_nd",
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
                "usa_vt",
                "usa_wi",
                "usa_wv",
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
        description="Series filter. Accepts a comma-separated list of values. There are 269 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersData(EiaApiData):
    """Natural Gas Delivered for the Account of Others. EIA natural gas survey data"""

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


class EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersFetcher(
    Fetcher[
        EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersQueryParams,
        list[EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersData],
    ]
):
    """Natural Gas Delivered for the Account of Others fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasNaturalGasDeliveredForTheAccountOfOthersData, query, data
        )
