"""Natural Gas Proved Reserves, Wet After Lease Separation model."""

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


class EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationQueryParams(
    EiaApiQueryParams
):
    """Natural Gas Proved Reserves, Wet After Lease Separation. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/enr/wals
    """

    __group__ = "natural_gas"
    __dataset__ = "natural_gas_proved_reserves_wet_after_lease_separation"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "wet_after_lease_separation_proved_reserves",
                "wet_after_lease_separation_reserves_acquisitions",
                "wet_after_lease_separation_reserves_adjustments",
                "wet_after_lease_separation_reserves_based_production_from",
                "wet_after_lease_separation_reserves_extensions",
                "wet_after_lease_separation_reserves_extensions_and",
                "wet_after_lease_separation_reserves_new_field_discoveries",
                "wet_after_lease_separation_reserves_new_reservoir",
                "wet_after_lease_separation_reserves_revision_decreases",
                "wet_after_lease_separation_reserves_revision_increases",
                "wet_after_lease_separation_reserves_sales",
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
        description="Series filter. Accepts a comma-separated list of values. There are 561 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationData(EiaApiData):
    """Natural Gas Proved Reserves, Wet After Lease Separation. EIA natural gas survey data"""

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


class EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationFetcher(
    Fetcher[
        EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationQueryParams,
        list[EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationData],
    ]
):
    """Natural Gas Proved Reserves, Wet After Lease Separation fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasNaturalGasProvedReservesWetAfterLeaseSeparationData,
            query,
            data,
        )
