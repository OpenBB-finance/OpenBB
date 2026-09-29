"""Coalbed Methane model."""

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


class EiaNaturalGasCoalbedMethaneQueryParams(EiaApiQueryParams):
    """Coalbed Methane. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/enr/coalbed
    """

    __group__ = "natural_gas"
    __dataset__ = "coalbed_methane"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "coalbed_methane_proved_reserves",
                "coalbed_methane_reserves_acquisitions",
                "coalbed_methane_reserves_adjustments",
                "coalbed_methane_reserves_based_production",
                "coalbed_methane_reserves_extensions",
                "coalbed_methane_reserves_extensions_and_discoveries",
                "coalbed_methane_reserves_new_field_discoveries",
                "coalbed_methane_reserves_new_reservoir_discoveries_in_old",
                "coalbed_methane_reserves_revision_decreases",
                "coalbed_methane_reserves_revision_increases",
                "coalbed_methane_reserves_sales",
            ],
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
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. There are 560 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasCoalbedMethaneData(EiaApiData):
    """Coalbed Methane. EIA natural gas survey data"""

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


class EiaNaturalGasCoalbedMethaneFetcher(
    Fetcher[
        EiaNaturalGasCoalbedMethaneQueryParams, list[EiaNaturalGasCoalbedMethaneData]
    ]
):
    """Coalbed Methane fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasCoalbedMethaneQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaNaturalGasCoalbedMethaneQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasCoalbedMethaneQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasCoalbedMethaneQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasCoalbedMethaneData]:
        """Transform the data."""
        return transform_dataset_data(EiaNaturalGasCoalbedMethaneData, query, data)
