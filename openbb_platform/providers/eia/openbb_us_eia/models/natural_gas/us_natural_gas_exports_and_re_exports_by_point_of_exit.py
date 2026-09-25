"""US Natural Gas Exports and Re-Exports by Point of Exit model."""

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


class EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitQueryParams(
    EiaApiQueryParams
):
    """US Natural Gas Exports and Re-Exports by Point of Exit. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/move/poe2
    """

    __group__ = "natural_gas"
    __dataset__ = "us_natural_gas_exports_and_re_exports_by_point_of_exit"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "compressed_natural_gas_exports",
                "compressed_natural_gas_exports_for_price",
                "liquefied_natural_gas_exports",
                "liquefied_natural_gas_exports_price",
                "pipeline_exports",
                "pipeline_exports_price",
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
        description="DuoArea filter. Accepts a comma-separated list of values. There are 446 valid values - use the `facet_options` endpoint to list them.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. There are 934 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitData(EiaApiData):
    """US Natural Gas Exports and Re-Exports by Point of Exit. EIA natural gas survey data"""

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


class EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitFetcher(
    Fetcher[
        EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitQueryParams,
        list[EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitData],
    ]
):
    """US Natural Gas Exports and Re-Exports by Point of Exit fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasUsNaturalGasExportsAndReExportsByPointOfExitData, query, data
        )
