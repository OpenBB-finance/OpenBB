"""US Natural Gas Imports by Point of Entry model."""

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


class EiaNaturalGasUsNaturalGasImportsByPointOfEntryQueryParams(EiaApiQueryParams):
    """US Natural Gas Imports by Point of Entry. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/move/poe1
    """

    __group__ = "natural_gas"
    __dataset__ = "us_natural_gas_imports_by_point_of_entry"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "compressed_natural_gas_imports",
                "compressed_natural_gas_imports_for_price",
                "lng_imports",
                "liquefied_natural_gas_imports",
                "pipeline_imports",
                "pipeline_imports_price",
            ],
        },
        "region": {"multiple_items_allowed": True},
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
        description="DuoArea filter. Accepts a comma-separated list of values. There are 110 valid values - use the `facet_options` endpoint to list them.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. There are 252 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasUsNaturalGasImportsByPointOfEntryData(EiaApiData):
    """US Natural Gas Imports by Point of Entry. EIA natural gas survey data"""

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


class EiaNaturalGasUsNaturalGasImportsByPointOfEntryFetcher(
    Fetcher[
        EiaNaturalGasUsNaturalGasImportsByPointOfEntryQueryParams,
        list[EiaNaturalGasUsNaturalGasImportsByPointOfEntryData],
    ]
):
    """US Natural Gas Imports by Point of Entry fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasUsNaturalGasImportsByPointOfEntryQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasUsNaturalGasImportsByPointOfEntryQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasUsNaturalGasImportsByPointOfEntryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasUsNaturalGasImportsByPointOfEntryQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasUsNaturalGasImportsByPointOfEntryData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasUsNaturalGasImportsByPointOfEntryData, query, data
        )
