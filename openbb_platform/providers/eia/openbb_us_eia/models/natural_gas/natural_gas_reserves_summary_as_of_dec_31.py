"""Natural Gas Reserves Summary as of Dec model."""

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


class EiaNaturalGasNaturalGasReservesSummaryAsOfDec31QueryParams(EiaApiQueryParams):
    """Natural Gas Reserves Summary as of Dec. 31. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/enr/sum
    """

    __group__ = "natural_gas"
    __dataset__ = "natural_gas_reserves_summary_as_of_dec_31"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "associated_dissolved_proved_reserves",
                "dry_expected_future_production",
                "nonassociated_proved_reserves",
                "proved_reserves",
                "wet_after_lease_separation_proved_reserves",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": ["natural_gas", "natural_gas_liquids_and_liquid_refinery_gases"],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "california",
                "colorado",
                "florida",
                "na",
                "new_york",
                "ohio",
                "texas",
                "us",
                "usa_ak",
                "usa_al",
                "usa_ar",
                "usa_ks",
                "usa_ky",
                "usa_la",
                "usa_mi",
                "usa_ms",
                "usa_mt",
                "usa_nd",
                "usa_ne",
                "usa_nm",
                "usa_ok",
                "usa_pa",
                "usa_ut",
                "usa_va",
                "usa_wv",
                "usa_wy",
            ],
        },
        "series": {"multiple_items_allowed": True},
    }

    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. There are 256 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasNaturalGasReservesSummaryAsOfDec31Data(EiaApiData):
    """Natural Gas Reserves Summary as of Dec. 31. EIA natural gas survey data"""

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


class EiaNaturalGasNaturalGasReservesSummaryAsOfDec31Fetcher(
    Fetcher[
        EiaNaturalGasNaturalGasReservesSummaryAsOfDec31QueryParams,
        list[EiaNaturalGasNaturalGasReservesSummaryAsOfDec31Data],
    ]
):
    """Natural Gas Reserves Summary as of Dec fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasNaturalGasReservesSummaryAsOfDec31QueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasNaturalGasReservesSummaryAsOfDec31QueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasNaturalGasReservesSummaryAsOfDec31QueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasNaturalGasReservesSummaryAsOfDec31QueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasNaturalGasReservesSummaryAsOfDec31Data]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasNaturalGasReservesSummaryAsOfDec31Data, query, data
        )
