"""Supplemental Gas Supplies model."""

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


class EiaNaturalGasSupplementalGasSuppliesQueryParams(EiaApiQueryParams):
    """Supplemental Gas Supplies. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/prod/ss
    """

    __group__ = "natural_gas"
    __dataset__ = "supplemental_gas_supplies"
    __json_schema_extra__ = {}

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
    )


class EiaNaturalGasSupplementalGasSuppliesData(EiaApiData):
    """Supplemental Gas Supplies. EIA natural gas survey data"""

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


class EiaNaturalGasSupplementalGasSuppliesFetcher(
    Fetcher[
        EiaNaturalGasSupplementalGasSuppliesQueryParams,
        list[EiaNaturalGasSupplementalGasSuppliesData],
    ]
):
    """Supplemental Gas Supplies fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasSupplementalGasSuppliesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasSupplementalGasSuppliesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasSupplementalGasSuppliesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasSupplementalGasSuppliesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasSupplementalGasSuppliesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasSupplementalGasSuppliesData, query, data
        )
