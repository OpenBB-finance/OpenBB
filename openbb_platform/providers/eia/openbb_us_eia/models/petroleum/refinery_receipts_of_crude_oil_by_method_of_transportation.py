"""Refinery Receipts of Crude Oil by Method of Transportation model."""

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


class EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationQueryParams(
    EiaApiQueryParams
):
    """Refinery Receipts of Crude Oil by Method of Transportation. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/caprec
    """

    __group__ = "petroleum"
    __dataset__ = "refinery_receipts_of_crude_oil_by_method_of_transportation"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "crude_oil_refinery_receipts",
                "crude_oil_refinery_receipts_by_barge",
                "crude_oil_refinery_receipts_by_pipeline",
                "crude_oil_refinery_receipts_by_tank_car",
                "crude_oil_refinery_receipts_by_tanker",
                "crude_oil_refinery_receipts_by_truck",
                "domestic_crude_oil_refinery_receipts",
                "domestic_crude_oil_refinery_receipts_by_barge",
                "domestic_crude_oil_refinery_receipts_by_pipeline",
                "domestic_crude_oil_refinery_receipts_by_tank_car",
                "domestic_crude_oil_refinery_receipts_by_tanker",
                "domestic_crude_oil_refinery_receipts_by_truck",
                "foreign_crude_oil_barge_refinery_receipts",
                "foreign_crude_oil_refinery_receipts",
                "foreign_crude_oil_refinery_receipts_by_pipeline",
                "foreign_crude_oil_refinery_receipts_by_tank_car",
                "foreign_crude_oil_refinery_receipts_by_tanker",
                "foreign_crude_oil_refinery_receipts_by_truck",
            ],
        },
        "product": {"multiple_items_allowed": True},
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {"multiple_items_allowed": True},
    }

    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. There are 108 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationData(EiaApiData):
    """Refinery Receipts of Crude Oil by Method of Transportation. EIA petroleum gas survey data"""

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


class EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationFetcher(
    Fetcher[
        EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationQueryParams,
        list[EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationData],
    ]
):
    """Refinery Receipts of Crude Oil by Method of Transportation fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumRefineryReceiptsOfCrudeOilByMethodOfTransportationData,
            query,
            data,
        )
