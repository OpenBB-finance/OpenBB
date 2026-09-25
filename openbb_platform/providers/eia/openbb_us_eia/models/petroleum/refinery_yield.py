"""Refinery Yield model."""

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


class EiaPetroleumRefineryYieldQueryParams(EiaApiQueryParams):
    """Refinery Yield. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/pct
    """

    __group__ = "petroleum"
    __dataset__ = "refinery_yield"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil",
                "aviation_gasoline",
                "distillate_fuel_oil",
                "finished_motor_gasoline",
                "kerosene",
                "kerosene_type_jet_fuel",
                "lubricants",
                "miscellaneous_petroleum_products",
                "naphtha_for_petrochemical_feedstock_use",
                "natural_gas_liquids_and_liquid_refinery_gases",
                "other_oils_for_petrochemical_feedstock_use",
                "petroleum_coke",
                "processing_gain",
                "residual_fuel_oil",
                "special_naphthas",
                "still_gas",
                "waxes",
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
        description="Series filter. Accepts a comma-separated list of values. There are 262 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumRefineryYieldData(EiaApiData):
    """Refinery Yield. EIA petroleum gas survey data"""

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


class EiaPetroleumRefineryYieldFetcher(
    Fetcher[EiaPetroleumRefineryYieldQueryParams, list[EiaPetroleumRefineryYieldData]]
):
    """Refinery Yield fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaPetroleumRefineryYieldQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaPetroleumRefineryYieldQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumRefineryYieldQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumRefineryYieldQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumRefineryYieldData]:
        """Transform the data."""
        return transform_dataset_data(EiaPetroleumRefineryYieldData, query, data)
