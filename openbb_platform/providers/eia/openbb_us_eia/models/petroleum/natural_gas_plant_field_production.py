"""Natural Gas Plant Field Production model."""

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


class EiaPetroleumNaturalGasPlantFieldProductionQueryParams(EiaApiQueryParams):
    """Natural Gas Plant Field Production. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/gp
    """

    __group__ = "petroleum"
    __dataset__ = "natural_gas_plant_field_production"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "condensate_and_scrubber_oil",
                "ethane",
                "isobutane",
                "liquified_petroleum_gases",
                "natural_gas_plant_liquids",
                "natural_gasoline",
                "normal_butane",
                "pentanes_plus",
                "propane",
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
        description="Series filter. Accepts a comma-separated list of values. There are 284 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumNaturalGasPlantFieldProductionData(EiaApiData):
    """Natural Gas Plant Field Production. EIA petroleum gas survey data"""

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


class EiaPetroleumNaturalGasPlantFieldProductionFetcher(
    Fetcher[
        EiaPetroleumNaturalGasPlantFieldProductionQueryParams,
        list[EiaPetroleumNaturalGasPlantFieldProductionData],
    ]
):
    """Natural Gas Plant Field Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumNaturalGasPlantFieldProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumNaturalGasPlantFieldProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumNaturalGasPlantFieldProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumNaturalGasPlantFieldProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumNaturalGasPlantFieldProductionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumNaturalGasPlantFieldProductionData, query, data
        )
