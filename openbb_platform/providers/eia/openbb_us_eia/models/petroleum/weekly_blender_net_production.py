"""Weekly Blender Net Production model."""

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


class EiaPetroleumWeeklyBlenderNetProductionQueryParams(EiaApiQueryParams):
    """Weekly Blender Net Production. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/wprodb
    """

    __group__ = "petroleum"
    __dataset__ = "weekly_blender_net_production"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "conventional_motor_gasoline",
                "conventional_motor_gasoline_with_alcohol",
                "distillate_fuel_oil",
                "distillate_fuel_oil_0_to_15_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
                "finished_motor_gasoline",
                "finished_motor_gasoline_conventional_55",
                "finished_motor_gasoline_reformulated_other",
                "kerosene",
                "kerosene_type_jet_fuel",
                "motor_gasoline_finished_conventional_ed55_and_lower",
                "other_conventional_motor_gasoline",
                "reformulated_motor_gasoline",
                "reformulated_motor_gasoline_with_alcohol",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "east_coast_blender_net_production_of_finished_motor_gasoline",
                "gulf_coast_blender_net_production_of_finished_motor_gasoline",
                "midwest_blender_net_production_of_finished_motor_gasoline",
                "rocky_mountain_blender_net_production_of_finished_motor",
                "us_blender_net_production_of_conventional_motor_gasoline_thousand_barrels_per_day",
                "us_blender_net_production_of_conventional_motor_gasoline_with_fuel_ethanol_thousand_barrels_per_day",
                "us_blender_net_production_of_distillate_fuel_oil",
                "us_blender_net_production_of_distillate_fuel_oil_0_to_15",
                "us_blender_net_production_of_distillate_fuel_oil_greater_than_500_ppm_sulfur_thousand_barrels_per_day",
                "us_blender_net_production_of_distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur_thousand_barrels_per_day",
                "us_blender_net_production_of_finished_motor_gasoline",
                "us_blender_net_production_of_kerosene",
                "us_blender_net_production_of_kerosene_type_jet_fuel",
                "us_blender_net_production_of_motor_gasoline_finished_conventional_ed55_and_lower_thousand_barrels_per_day",
                "us_blender_net_production_of_motor_gasoline_finished_conventional_greater_than_ed55_thousand_barrels_per_day",
                "us_blender_net_production_of_other_conventional_motor",
                "us_blender_net_production_of_other_reformulated_motor",
                "us_blender_net_production_of_reformulated_motor_gasoline_thousand_barrels_per_day",
                "us_blender_net_production_of_reformulated_motor_gasoline_with_fuel_alcohol_thousand_barrels_per_day",
                "west_coast_blender_net_production_of_finished_motor_gasoline",
            ],
        },
    }

    frequency: Literal["four-week-average", "weekly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'weekly'.",
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


class EiaPetroleumWeeklyBlenderNetProductionData(EiaApiData):
    """Weekly Blender Net Production. EIA petroleum gas survey data"""

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


class EiaPetroleumWeeklyBlenderNetProductionFetcher(
    Fetcher[
        EiaPetroleumWeeklyBlenderNetProductionQueryParams,
        list[EiaPetroleumWeeklyBlenderNetProductionData],
    ]
):
    """Weekly Blender Net Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumWeeklyBlenderNetProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumWeeklyBlenderNetProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumWeeklyBlenderNetProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumWeeklyBlenderNetProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumWeeklyBlenderNetProductionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumWeeklyBlenderNetProductionData, query, data
        )
