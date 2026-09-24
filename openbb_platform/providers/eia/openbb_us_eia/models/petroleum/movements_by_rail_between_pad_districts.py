"""Movements of Crude Oil and Selected Products by Rail between PAD Districts model."""

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


class EiaPetroleumMovementsByRailBetweenPadDistrictsQueryParams(EiaApiQueryParams):
    """Movements of Crude Oil and Selected Products by Rail between PAD Districts. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/move/rail
    """

    __group__ = "petroleum"
    __dataset__ = "movements_by_rail_between_pad_districts"
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
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5"],
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
        description="Series filter. Accepts a comma-separated list of values. There are 144 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumMovementsByRailBetweenPadDistrictsData(EiaApiData):
    """Movements of Crude Oil and Selected Products by Rail between PAD Districts. EIA petroleum gas survey data"""

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


class EiaPetroleumMovementsByRailBetweenPadDistrictsFetcher(
    Fetcher[
        EiaPetroleumMovementsByRailBetweenPadDistrictsQueryParams,
        list[EiaPetroleumMovementsByRailBetweenPadDistrictsData],
    ]
):
    """Movements of Crude Oil and Selected Products by Rail between PAD Districts fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumMovementsByRailBetweenPadDistrictsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumMovementsByRailBetweenPadDistrictsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumMovementsByRailBetweenPadDistrictsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumMovementsByRailBetweenPadDistrictsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumMovementsByRailBetweenPadDistrictsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumMovementsByRailBetweenPadDistrictsData, query, data
        )
