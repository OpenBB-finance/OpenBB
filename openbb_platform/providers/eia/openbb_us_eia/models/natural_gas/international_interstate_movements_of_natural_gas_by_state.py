"""International & Interstate Movements of Natural Gas by State model."""

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


class EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateQueryParams(
    EiaApiQueryParams
):
    """International & Interstate Movements of Natural Gas by State. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/move/ist
    """

    __group__ = "natural_gas"
    __dataset__ = "international_interstate_movements_of_natural_gas_by_state"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "exports_intransit",
                "imports_intransit",
                "interstate_and_across_us_borders_delivered_exports_to",
                "interstate_and_across_us_borders_net_interstate_receipts",
                "interstate_and_across_us_borders_receipts_imports",
                "interstate_movements_deliveries",
                "interstate_movements_net_receipts",
                "interstate_movements_receipts",
                "net_movements_across_us_borders",
            ],
        },
        "region": {"multiple_items_allowed": True},
        "series": {"multiple_items_allowed": True},
    }

    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values. There are 738 valid values - use the `facet_options` endpoint to list them.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )


class EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateData(EiaApiData):
    """International & Interstate Movements of Natural Gas by State. EIA natural gas survey data"""

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


class EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateFetcher(
    Fetcher[
        EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateQueryParams,
        list[EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateData],
    ]
):
    """International & Interstate Movements of Natural Gas by State fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasInternationalInterstateMovementsOfNaturalGasByStateData,
            query,
            data,
        )
