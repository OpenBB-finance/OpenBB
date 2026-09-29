"""Blender Net Production model."""

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


class EiaPetroleumBlenderNetProductionQueryParams(EiaApiQueryParams):
    """Blender Net Production. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/refp3
    """

    __group__ = "petroleum"
    __dataset__ = "blender_net_production"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil",
                "aviation_gasoline",
                "conventional_motor_gasoline",
                "conventional_motor_gasoline_with_alcohol",
                "crude_oil_and_petroleum_products",
                "distillate_fuel_oil",
                "distillate_fuel_oil_0_to_15_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
                "finished_motor_gasoline",
                "finished_motor_gasoline_conventional_55",
                "finished_motor_gasoline_reformulated_other",
                "kerosene",
                "kerosene_type_jet_fuel",
                "lubricants",
                "miscellaneous_petroleum_products",
                "motor_gasoline_finished_conventional_ed55_and_lower",
                "other_conventional_motor_gasoline",
                "processing_gain",
                "reformulated_motor_gasoline",
                "reformulated_motor_gasoline_with_alcohol",
                "residual_fuel_oil",
                "residual_fuel_oil_0_31_to_1_00_sulfur",
                "residual_fuel_oil_greater_than_1_sulfur",
                "residual_fuel_oil_less_than_0_31_sulfur",
                "special_naphthas",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["na", "padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
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
        description="Series filter. Accepts a comma-separated list of values. There are 652 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumBlenderNetProductionData(EiaApiData):
    """Blender Net Production. EIA petroleum gas survey data"""

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


class EiaPetroleumBlenderNetProductionFetcher(
    Fetcher[
        EiaPetroleumBlenderNetProductionQueryParams,
        list[EiaPetroleumBlenderNetProductionData],
    ]
):
    """Blender Net Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumBlenderNetProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumBlenderNetProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumBlenderNetProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumBlenderNetProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumBlenderNetProductionData]:
        """Transform the data."""
        return transform_dataset_data(EiaPetroleumBlenderNetProductionData, query, data)
