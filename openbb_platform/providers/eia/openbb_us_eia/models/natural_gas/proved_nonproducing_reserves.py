"""Proved Nonproducing Reserves model."""

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


class EiaNaturalGasProvedNonproducingReservesQueryParams(EiaApiQueryParams):
    """Proved Nonproducing Reserves. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/enr/nprod
    """

    __group__ = "natural_gas"
    __dataset__ = "proved_nonproducing_reserves"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "associated_dissolved_reserves_in_nonproducing_reservoirs",
                "lease_condensate_reserves_in_nonproducing_reservoirs",
                "nonassociated_reserves_in_nonproducing_reservoirs",
                "reserves_in_nonproducing_reservoirs",
                "wet_after_lease_separation_reserves_in_nonproducing",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "crude_oil",
                "natural_gas",
                "natural_gas_liquids_and_liquid_refinery_gases",
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
                "usa_il",
                "usa_in",
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
        description="Series filter. Accepts a comma-separated list of values. There are 270 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasProvedNonproducingReservesData(EiaApiData):
    """Proved Nonproducing Reserves. EIA natural gas survey data"""

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


class EiaNaturalGasProvedNonproducingReservesFetcher(
    Fetcher[
        EiaNaturalGasProvedNonproducingReservesQueryParams,
        list[EiaNaturalGasProvedNonproducingReservesData],
    ]
):
    """Proved Nonproducing Reserves fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasProvedNonproducingReservesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasProvedNonproducingReservesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasProvedNonproducingReservesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasProvedNonproducingReservesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasProvedNonproducingReservesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasProvedNonproducingReservesData, query, data
        )
