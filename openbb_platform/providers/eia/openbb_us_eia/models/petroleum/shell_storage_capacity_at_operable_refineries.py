"""Shell Storage Capacity at Operable Refineries model."""

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


class EiaPetroleumShellStorageCapacityAtOperableRefineriesQueryParams(
    EiaApiQueryParams
):
    """Shell Storage Capacity at Operable Refineries. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/capshell
    """

    __group__ = "petroleum"
    __dataset__ = "shell_storage_capacity_at_operable_refineries"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil_shell_storage_capacity_at_refineries",
                "biomass_based_diesel_fuel_shell_storage_capacity_at",
                "crude_oil_shell_storage_capacity_at_refineries",
                "distillate_fuel_oil_shell_storage_capacity_at_refineries",
                "distillate_fuel_oil_15_ppm_sulfur_and_under_shell_storage",
                "distillate_fuel_oil_greater_than_15_ppm_sulfur_to_500_ppm",
                "distillate_fuel_oil_greater_than_500_ppm_sulfur_shell",
                "finished_conventional_motor_gasoline_shell_storage_capacity",
                "finished_motor_gasoline_shell_storage_capacity_at_refineries",
                "finished_petroleum_products_shell_storage_capacity_at",
                "finished_reformulated_motor_gasoline_shell_storage_capacity",
                "fuel_ethanol_shell_storage_capacity_at_refineries",
                "kerosene_shell_storage_capacity_at_refineries",
                "kerosene_type_jet_fuel_shell_storage_capacity_at_refineries",
                "liquefied_petroleum_gases_shell_storage_capacity_at",
                "lubricants_shell_storage_capacity_at_refineries",
                "mtbe_shell_storage_capacity_at_refineries",
                "motor_gasoline_blending_components_shell_storage_capacity",
                "normal_butane_butylene_shell_storage_capacity_at_refineries",
                "other_liquids_shell_storage_capacity_at_refineries",
                "other_oxygenates_shell_storage_capacity_at_refineries",
                "other_petroleum_products_shell_storage_capacity_at",
                "other_renewable_diesel_fuel_shell_storage_capacity_at",
                "other_renewable_fuels_shell_storage_capacity_at_refineries",
                "oxygenates_shell_storage_capacity_at_refineries",
                "propane_propylene_shell_storage_capacity_at_refineries",
                "residual_fuel_oil_shell_storage_capacity_at_refineries",
                "shell_storage_capacity_at_refineries",
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


class EiaPetroleumShellStorageCapacityAtOperableRefineriesData(EiaApiData):
    """Shell Storage Capacity at Operable Refineries. EIA petroleum gas survey data"""

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


class EiaPetroleumShellStorageCapacityAtOperableRefineriesFetcher(
    Fetcher[
        EiaPetroleumShellStorageCapacityAtOperableRefineriesQueryParams,
        list[EiaPetroleumShellStorageCapacityAtOperableRefineriesData],
    ]
):
    """Shell Storage Capacity at Operable Refineries fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumShellStorageCapacityAtOperableRefineriesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumShellStorageCapacityAtOperableRefineriesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumShellStorageCapacityAtOperableRefineriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumShellStorageCapacityAtOperableRefineriesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumShellStorageCapacityAtOperableRefineriesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumShellStorageCapacityAtOperableRefineriesData, query, data
        )
