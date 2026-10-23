"""Movements of Crude Oil and Selected Products by Rail model."""

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


class EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailQueryParams(
    EiaApiQueryParams
):
    """Movements of Crude Oil and Selected Products by Rail. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/move/railNA
    """

    __group__ = "petroleum"
    __dataset__ = "movements_of_crude_oil_and_selected_products_by_rail"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil",
                "biodiesel",
                "crude_oil",
                "fuel_ethanol",
                "isobutane",
                "normal_butane",
                "petroleum_coke_marketable",
                "propane",
                "propylene",
                "renewable_diesel_fuel",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "can",
                "na",
                "padd_1",
                "padd_2",
                "padd_3",
                "padd_4",
                "padd_5",
                "us",
            ],
        },
        "series": {"multiple_items_allowed": True},
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
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
        description="Series filter. Accepts a comma-separated list of values. There are 399 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailData(EiaApiData):
    """Movements of Crude Oil and Selected Products by Rail. EIA petroleum gas survey data"""

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


class EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailFetcher(
    Fetcher[
        EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailQueryParams,
        list[EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailData],
    ]
):
    """Movements of Crude Oil and Selected Products by Rail fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumMovementsOfCrudeOilAndSelectedProductsByRailData, query, data
        )
