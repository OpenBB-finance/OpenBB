"""Weekly Supply Estimates model."""

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


class EiaPetroleumWeeklySupplyEstimatesQueryParams(EiaApiQueryParams):
    """Weekly Supply Estimates. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/sum/sndw
    """

    __group__ = "petroleum"
    __dataset__ = "weekly_supply_estimates"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "utilization_refinery_operable_capacity",
                "all_plants",
                "days_of_supply",
                "ending_stocks",
                "ending_stocks_excluding_propylene_at_terminal",
                "ending_stocks_excluding_spr",
                "ending_stocks_excluding_spr_and_lease",
                "ending_stocks_spr",
                "exports",
                "field_production",
                "imports",
                "imports_excluding_spr",
                "imports_by_others_for_spr",
                "imports_by_spr",
                "net_imports",
                "oxygenate_plant_production",
                "product_supplied",
                "production",
                "refinery_net_input",
                "refinery_operable_capacity",
                "refinery_and_blender_net_input",
                "refinery_and_blender_net_production",
                "stocks_at_bulk_terminals",
                "stocks_in_transit_from_alaska",
                "supply_adjustment",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil",
                "commercial_kerosene_type_jet_fuel",
                "conventional_cbob_gasoline_blending_components",
                "conventional_gtab_gasoline_blending_components",
                "conventional_motor_gasoline",
                "conventional_motor_gasoline_with_alcohol",
                "conventional_other_gasoline_blending_components",
                "crude_oil",
                "crude_oil_and_petroleum_products",
                "distillate_fuel_oil",
                "distillate_fuel_oil_0_to_15_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_2000_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_to_2000_ppm_sulfur",
                "finished_motor_gasoline",
                "finished_motor_gasoline_conventional_55",
                "finished_motor_gasoline_reformulated_other",
                "fuel_ethanol",
                "gasoline_blending_components",
                "gross_inputs",
                "kerosene",
                "kerosene_type_jet_fuel",
                "military_kerosene_type_jet_fuel",
                "motor_gasoline_blending_components_reformulated_rbob",
                "motor_gasoline_finished_conventional_ed55_and_lower",
                "ngpls_lrgs",
                "other_conventional_motor_gasoline",
                "other_oils",
                "other_oils_excluding_fuel_ethanol",
                "propane_and_propylene",
                "propane_fractionated_and_ready_for_sale",
                "propylene_nonfuel_use",
                "reformulated_motor_gasoline",
                "reformulated_motor_gasoline_with_alcohol",
                "reformulated_motor_gasoline_non_oxygentated",
                "reformulated_rbob_with_alcohol_gasoline_blending_components",
                "reformulated_rbob_with_ether_gasoline_blending_components",
                "residual_fuel_oil",
                "total_gasoline",
                "total_petroleum_products",
                "unfinished_oils",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "na",
                "padd_1",
                "padd_1a",
                "padd_1b",
                "padd_1c",
                "padd_2",
                "padd_3",
                "padd_4",
                "padd_5",
                "us",
                "usa_ak",
            ],
        },
        "series": {"multiple_items_allowed": True},
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
        description="Series filter. Accepts a comma-separated list of values. There are 608 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumWeeklySupplyEstimatesData(EiaApiData):
    """Weekly Supply Estimates. EIA petroleum gas survey data"""

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


class EiaPetroleumWeeklySupplyEstimatesFetcher(
    Fetcher[
        EiaPetroleumWeeklySupplyEstimatesQueryParams,
        list[EiaPetroleumWeeklySupplyEstimatesData],
    ]
):
    """Weekly Supply Estimates fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumWeeklySupplyEstimatesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumWeeklySupplyEstimatesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumWeeklySupplyEstimatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumWeeklySupplyEstimatesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumWeeklySupplyEstimatesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumWeeklySupplyEstimatesData, query, data
        )
