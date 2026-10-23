"""Crude Oil and Natural Gas Drilling Activity model."""

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


class EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityQueryParams(EiaApiQueryParams):
    """Crude Oil and Natural Gas Drilling Activity. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/enr/drill
    """

    __group__ = "natural_gas"
    __dataset__ = "crude_oil_and_natural_gas_drilling_activity"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "active_well_service_rigs_in_operation",
                "rotary_rigs_in_operation",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "crude_oil_and_natural_gas",
                "rotary_rigs_in_operation",
                "rotary_rigs_in_operation_gas",
                "rotary_rigs_in_operation_oil",
            ],
        },
        "region": {"multiple_items_allowed": True, "choices": ["na", "us"]},
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_crude_oil_rotary_rigs_in_operation",
                "us_crude_oil_and_natural_gas_active_well_service_rigs_in",
                "us_crude_oil_and_natural_gas_rotary_rigs_in_operation",
                "us_natural_gas_rotary_rigs_in_operation",
                "us_offshore_crude_oil_and_natural_gas_rotary_rigs_in",
                "us_onshore_crude_oil_and_natural_gas_rotary_rigs_in",
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
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityData(EiaApiData):
    """Crude Oil and Natural Gas Drilling Activity. EIA natural gas survey data"""

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


class EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityFetcher(
    Fetcher[
        EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityQueryParams,
        list[EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityData],
    ]
):
    """Crude Oil and Natural Gas Drilling Activity fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasCrudeOilAndNaturalGasDrillingActivityData, query, data
        )
