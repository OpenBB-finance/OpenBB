"""Average Depth of Crude Oil and Natural Gas Wells model."""

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


class EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsQueryParams(
    EiaApiQueryParams
):
    """Average Depth of Crude Oil and Natural Gas Wells. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/enr/welldep
    """

    __group__ = "natural_gas"
    __dataset__ = "average_depth_of_crude_oil_and_natural_gas_wells"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "average_depth_of_developmental_wells_drilled",
                "average_depth_of_exploratory_wells_drilled",
                "average_depth_of_exploratory_and_developmental_wells_drilled",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": ["wells_dry", "wells_gas", "wells_oil", "wells_total"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_average_depth_of_crude_oil_developmental_wells_drilled",
                "us_average_depth_of_crude_oil_exploratory_wells_drilled",
                "us_average_depth_of_crude_oil_exploratory_and_developmental",
                "us_average_depth_of_crude_oil_natural_gas_and_dry_developmental_wells_drilled_feet_per_well",
                "us_average_depth_of_crude_oil_natural_gas_and_dry_exploratory_wells_drilled_feet_per_well",
                "us_average_depth_of_crude_oil_natural_gas_and_dry_exploratory_and_developmental_wells_drilled_feet_per_well",
                "us_average_depth_of_dry_exploratory_and_developmental_wells",
                "us_average_depth_of_dry_holes_developmental_wells_drilled",
                "us_average_depth_of_dry_holes_exploratory_wells_drilled",
                "us_average_depth_of_natural_gas_developmental_wells_drilled",
                "us_average_depth_of_natural_gas_exploratory_wells_drilled",
                "us_average_depth_of_natural_gas_exploratory_and",
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


class EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsData(EiaApiData):
    """Average Depth of Crude Oil and Natural Gas Wells. EIA natural gas survey data"""

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


class EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsFetcher(
    Fetcher[
        EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsQueryParams,
        list[EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsData],
    ]
):
    """Average Depth of Crude Oil and Natural Gas Wells fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasAverageDepthOfCrudeOilAndNaturalGasWellsData, query, data
        )
