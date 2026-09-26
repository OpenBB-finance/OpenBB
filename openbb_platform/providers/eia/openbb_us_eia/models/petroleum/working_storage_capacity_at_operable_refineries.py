"""Working Storage Capacity at Operable Refineries model."""

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


class EiaPetroleumWorkingStorageCapacityAtOperableRefineriesQueryParams(
    EiaApiQueryParams
):
    """Working Storage Capacity at Operable Refineries. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/capwork
    """

    __group__ = "petroleum"
    __dataset__ = "working_storage_capacity_at_operable_refineries"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "working_storage_capacity",
                "working_storage_capacity_for_asphalt_and_road_oil",
                "working_storage_capacity_for_biomass_based_diesel_fuel",
                "working_storage_capacity_for_crude_oil",
                "working_storage_capacity_for_distillate_fuel_oil",
                "working_storage_capacity_for_distillate_fuel_oil_15_ppm",
                "working_storage_capacity_for_distillate_fuel_oil_15_to_500",
                "working_storage_capacity_for_distillate_fuel_oil_500_ppm",
                "working_storage_capacity_for_finished_conventional_gasoline",
                "working_storage_capacity_for_finished_gasoline",
                "working_storage_capacity_for_finished_reformulated_gasoline",
                "working_storage_capacity_for_fuel_ethanol",
                "working_storage_capacity_for_gasoline_blending_components",
                "working_storage_capacity_for_kerosene",
                "working_storage_capacity_for_kerosene_type_jet_fuel",
                "working_storage_capacity_for_liquefied_petroleum_products",
                "working_storage_capacity_for_lubricants",
                "working_storage_capacity_for_mtbe",
                "working_storage_capacity_for_normal_butane_butylene",
                "working_storage_capacity_for_other_liquids",
                "working_storage_capacity_for_other_oxygenates",
                "working_storage_capacity_for_other_products",
                "working_storage_capacity_for_other_renewable_diesel_fuel",
                "working_storage_capacity_for_other_renewable_fuels",
                "working_storage_capacity_for_oxygenates",
                "working_storage_capacity_for_petroleum_products",
                "working_storage_capacity_for_propane_propylene",
                "working_storage_capacity_for_residual_fuel_oil",
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
        description="Series filter. Accepts a comma-separated list of values. There are 168 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumWorkingStorageCapacityAtOperableRefineriesData(EiaApiData):
    """Working Storage Capacity at Operable Refineries. EIA petroleum gas survey data"""

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


class EiaPetroleumWorkingStorageCapacityAtOperableRefineriesFetcher(
    Fetcher[
        EiaPetroleumWorkingStorageCapacityAtOperableRefineriesQueryParams,
        list[EiaPetroleumWorkingStorageCapacityAtOperableRefineriesData],
    ]
):
    """Working Storage Capacity at Operable Refineries fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumWorkingStorageCapacityAtOperableRefineriesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumWorkingStorageCapacityAtOperableRefineriesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumWorkingStorageCapacityAtOperableRefineriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumWorkingStorageCapacityAtOperableRefineriesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumWorkingStorageCapacityAtOperableRefineriesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumWorkingStorageCapacityAtOperableRefineriesData, query, data
        )
