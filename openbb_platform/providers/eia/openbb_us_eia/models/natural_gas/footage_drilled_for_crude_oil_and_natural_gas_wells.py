"""Footage Drilled for Crude Oil and Natural Gas Wells model."""

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


class EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsQueryParams(
    EiaApiQueryParams
):
    """Footage Drilled for Crude Oil and Natural Gas Wells. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/enr/wellfoot
    """

    __group__ = "natural_gas"
    __dataset__ = "footage_drilled_for_crude_oil_and_natural_gas_wells"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "footage_drilled_for_developmental_wells",
                "footage_drilled_for_exploratory_wells",
                "footage_drilled_for_exploratory_and_developmental_wells",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": ["wells_dry", "wells_gas", "wells_oil", "wells_total"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_footage_drilled_for_crude_oil_developmental_wells",
                "us_footage_drilled_for_crude_oil_exploratory_wells",
                "us_footage_drilled_for_crude_oil_exploratory_and",
                "us_footage_drilled_for_crude_oil_natural_gas_and_dry_developmental_wells_thousand_feet",
                "us_footage_drilled_for_crude_oil_natural_gas_and_dry_exploratory_wells_thousand_feet",
                "us_footage_drilled_for_crude_oil_natural_gas_and_dry_exploratory_and_developmental_wells_thousand_feet",
                "us_footage_drilled_for_dry_developmental_wells",
                "us_footage_drilled_for_dry_exploratory_wells",
                "us_footage_drilled_for_dry_exploratory_and_developmental",
                "us_footage_drilled_for_natural_gas_developmental_wells",
                "us_footage_drilled_for_natural_gas_exploratory_wells",
                "us_footage_drilled_for_natural_gas_exploratory_and",
            ],
        },
    }

    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
    )
    product: str | None = Field(
        default=None,
        description="Product filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsData(EiaApiData):
    """Footage Drilled for Crude Oil and Natural Gas Wells. EIA natural gas survey data"""

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


class EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsFetcher(
    Fetcher[
        EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsQueryParams,
        list[EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsData],
    ]
):
    """Footage Drilled for Crude Oil and Natural Gas Wells fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasFootageDrilledForCrudeOilAndNaturalGasWellsData, query, data
        )
