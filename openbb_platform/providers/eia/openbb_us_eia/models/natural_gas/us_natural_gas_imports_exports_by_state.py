"""US Natural Gas Imports & Exports by State model."""

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


class EiaNaturalGasUsNaturalGasImportsExportsByStateQueryParams(EiaApiQueryParams):
    """US Natural Gas Imports & Exports by State. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/move/state
    """

    __group__ = "natural_gas"
    __dataset__ = "us_natural_gas_imports_exports_by_state"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": ["exports", "exports_price", "imports", "imports_price"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "price_of_us_natural_gas_exports",
                "price_of_us_natural_gas_imports",
                "us_natural_gas_exports",
                "us_natural_gas_imports",
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


class EiaNaturalGasUsNaturalGasImportsExportsByStateData(EiaApiData):
    """US Natural Gas Imports & Exports by State. EIA natural gas survey data"""

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


class EiaNaturalGasUsNaturalGasImportsExportsByStateFetcher(
    Fetcher[
        EiaNaturalGasUsNaturalGasImportsExportsByStateQueryParams,
        list[EiaNaturalGasUsNaturalGasImportsExportsByStateData],
    ]
):
    """US Natural Gas Imports & Exports by State fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasUsNaturalGasImportsExportsByStateQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasUsNaturalGasImportsExportsByStateQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasUsNaturalGasImportsExportsByStateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasUsNaturalGasImportsExportsByStateQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasUsNaturalGasImportsExportsByStateData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasUsNaturalGasImportsExportsByStateData, query, data
        )
