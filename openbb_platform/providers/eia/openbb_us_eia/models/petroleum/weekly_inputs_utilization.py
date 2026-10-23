"""Weekly Inputs & Utilization model."""

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


class EiaPetroleumWeeklyInputsUtilizationQueryParams(EiaApiQueryParams):
    """Weekly Inputs & Utilization. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/wiup
    """

    __group__ = "petroleum"
    __dataset__ = "weekly_inputs_utilization"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "utilization_refinery_operable_capacity",
                "refinery_net_input",
                "refinery_operable_capacity",
                "refinery_and_blender_net_input",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "conventional_cbob_gasoline_blending_components",
                "conventional_gtab_gasoline_blending_components",
                "conventional_other_gasoline_blending_components",
                "crude_oil",
                "fuel_ethanol",
                "gasoline_blending_components",
                "gross_inputs",
                "motor_gasoline_blending_components_reformulated_rbob",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "east_coast_gross_inputs_into_refineries",
                "east_coast_operable_crude_oil_distillation_capacity",
                "east_coast_percent_utilization_of_refinery_operable_capacity",
                "east_coast_refiner_net_input_of_crude_oil",
                "east_coast_padd_1_refiner_and_blender_net_input_of_conventional_cbob_gasoline_blending_components_thousand_barrels_per_day",
                "east_coast_padd_1_refiner_and_blender_net_input_of_conventional_gtab_gasoline_blending_components_thousand_barrels_per_day",
                "east_coast_padd_1_refiner_and_blender_net_input_of_conventional_other_gasoline_blending_components_thousand_barrels_per_day",
                "east_coast_refiner_and_blender_net_input_of_fuel_ethanol",
                "east_coast_refiner_and_blender_net_input_of_gasoline",
                "east_coast_refiner_and_blender_net_input_of_motor_gasoline",
                "gulf_coast_gross_inputs_into_refineries",
                "gulf_coast_operable_crude_oil_distillation_capacity",
                "gulf_coast_percent_utilization_of_refinery_operable_capacity",
                "gulf_coast_refiner_net_input_of_crude_oil",
                "gulf_coast_padd_3_refiner_and_blender_net_input_of_conventional_cbob_gasoline_blending_components_thousand_barrels_per_day",
                "gulf_coast_padd_3_refiner_and_blender_net_input_of_conventional_gtab_gasoline_blending_components_thousand_barrels_per_day",
                "gulf_coast_padd_3_refiner_and_blender_net_input_of_conventional_other_gasoline_blending_components_thousand_barrels_per_day",
                "gulf_coast_refiner_and_blender_net_input_of_fuel_ethanol",
                "gulf_coast_refiner_and_blender_net_input_of_gasoline",
                "gulf_coast_refiner_and_blender_net_input_of_motor_gasoline",
                "midwest_gross_inputs_into_refineries",
                "midwest_operable_crude_oil_distillation_capacity",
                "midwest_percent_utilization_of_refinery_operable_capacity",
                "midwest_refiner_net_input_of_crude_oil",
                "midwest_refiner_and_blender_net_input_of_conventional_cbob",
                "midwest_refiner_and_blender_net_input_of_conventional_gtab",
                "midwest_refiner_and_blender_net_input_of_conventional_other",
                "midwest_refiner_and_blender_net_input_of_fuel_ethanol",
                "midwest_refiner_and_blender_net_input_of_gasoline_blending",
                "midwest_refiner_and_blender_net_input_of_motor_gasoline",
                "rocky_mountain_gross_inputs_into_refineries",
                "rocky_mountain_refiner_net_input_of_crude_oil",
                "rocky_mountain_padd_4_refiner_and_blender_net_input_of_conventional_cbob_gasoline_blending_components_thousand_barrels_per_day",
                "rocky_mountain_padd_4_refiner_and_blender_net_input_of_conventional_gtab_gasoline_blending_components_thousand_barrels_per_day",
                "rocky_mountain_padd_4_refiner_and_blender_net_input_of_conventional_other_gasoline_blending_components_thousand_barrels_per_day",
                "rocky_mountain_refiner_and_blender_net_input_of_fuel_ethanol",
                "rocky_mountain_refiner_and_blender_net_input_of_gasoline",
                "rocky_mountain_refiner_and_blender_net_input_of_motor",
                "rocky_mountains_operable_crude_oil_distillation_capacity",
                "rocky_mountains_percent_utilization_of_refinery_operable",
                "u_s_operable_crude_oil_distillation_capacity",
                "us_gross_inputs_into_refineries",
                "us_percent_utilization_of_refinery_operable_capacity",
                "us_refiner_net_input_of_crude_oil",
                "us_refiner_and_blender_net_input_of_conventional_cbob",
                "us_refiner_and_blender_net_input_of_conventional_gtab",
                "us_refiner_and_blender_net_input_of_conventional_other",
                "us_refiner_and_blender_net_input_of_fuel_ethanol",
                "us_refiner_and_blender_net_input_of_gasoline_blending",
                "us_refiner_and_blender_net_input_of_motor_gasoline_blending",
                "west_coast_gross_inputs_into_refineries",
                "west_coast_operable_crude_oil_distillation_capacity",
                "west_coast_percent_utilization_of_refinery_operable_capacity",
                "west_coast_refiner_net_input_of_crude_oil",
                "west_coast_padd_5_refiner_and_blender_net_input_of_conventional_cbob_gasoline_blending_components_thousand_barrels_per_day",
                "west_coast_padd_5_refiner_and_blender_net_input_of_conventional_gtab_gasoline_blending_components_thousand_barrels_per_day",
                "west_coast_padd_5_refiner_and_blender_net_input_of_conventional_other_gasoline_blending_components_thousand_barrels_per_day",
                "west_coast_refiner_and_blender_net_input_of_fuel_ethanol",
                "west_coast_refiner_and_blender_net_input_of_gasoline",
                "west_coast_refiner_and_blender_net_input_of_motor_gasoline",
            ],
        },
    }

    frequency: Literal["four-week-average", "weekly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'weekly'.",
    )
    process: str | None = Field(
        default=None,
        description="Process filter. Accepts a comma-separated list of values.",
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
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumWeeklyInputsUtilizationData(EiaApiData):
    """Weekly Inputs & Utilization. EIA petroleum gas survey data"""

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


class EiaPetroleumWeeklyInputsUtilizationFetcher(
    Fetcher[
        EiaPetroleumWeeklyInputsUtilizationQueryParams,
        list[EiaPetroleumWeeklyInputsUtilizationData],
    ]
):
    """Weekly Inputs & Utilization fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumWeeklyInputsUtilizationQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumWeeklyInputsUtilizationQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumWeeklyInputsUtilizationQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumWeeklyInputsUtilizationQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumWeeklyInputsUtilizationData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumWeeklyInputsUtilizationData, query, data
        )
