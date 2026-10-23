"""Crude Oil Stocks at Tank Farms & Pipelines model."""

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


class EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesQueryParams(EiaApiQueryParams):
    """Crude Oil Stocks at Tank Farms & Pipelines. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/stoc/cu
    """

    __group__ = "petroleum"
    __dataset__ = "crude_oil_stocks_at_tank_farms_pipelines"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": ["ending_stocks", "stocks_at_tank_farms"],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["na", "padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "cushing_ok_ending_stocks_of_crude_oil",
                "east_coast_crude_oil_stocks_at_tank_farms_and_pipelines",
                "gulf_coast_crude_oil_stocks_at_tank_farms_and_pipelines",
                "midwest_crude_oil_stocks_at_tank_farms_and_pipelines",
                "rocky_mountain_crude_oil_stocks_at_tank_farms_and_pipelines",
                "us_crude_oil_stocks_at_tank_farms_and_pipelines",
                "west_coast_crude_oil_stocks_at_tank_farms_and_pipelines",
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
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesData(EiaApiData):
    """Crude Oil Stocks at Tank Farms & Pipelines. EIA petroleum gas survey data"""

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


class EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesFetcher(
    Fetcher[
        EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesQueryParams,
        list[EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesData],
    ]
):
    """Crude Oil Stocks at Tank Farms & Pipelines fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumCrudeOilStocksAtTankFarmsPipelinesData, query, data
        )
