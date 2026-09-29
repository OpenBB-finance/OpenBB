"""Stocks by Type model."""

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


class EiaPetroleumStocksByTypeQueryParams(EiaApiQueryParams):
    """Stocks by Type. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/stoc/typ
    """

    __group__ = "petroleum"
    __dataset__ = "stocks_by_type"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "ending_stocks",
                "ending_stocks_excluding_spr",
                "ending_stocks_excluding_spr_and_lease",
                "ending_stocks_spr",
                "natural_gas_plant_stocks",
                "stocks_at_bulk_terminals",
                "stocks_at_leases",
                "stocks_at_refineries",
                "stocks_at_tank_farms",
                "stocks_in_pipelines",
                "stocks_in_transit_from_alaska",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil",
                "aviation_gasoline",
                "aviation_gasoline_blending_components",
                "biodiesel",
                "biodiesel_renewable_diesel_fuel",
                "biofuel_fuels",
                "biofuel_fuels_excluding_fuel_ethanol",
                "condensate_and_scrubber_oil",
                "conventional_cbob_gasoline_blending_components",
                "conventional_gtab_gasoline_blending_components",
                "conventional_gasoline_blending_components",
                "conventional_motor_gasoline",
                "conventional_motor_gasoline_with_alcohol",
                "conventional_other_gasoline_blending_components",
                "crude_oil",
                "crude_oil_and_petroleum_products",
                "distillate_fuel_oil",
                "distillate_fuel_oil_0_to_15_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
                "ethane",
                "ethane_ethylene",
                "ethylene",
                "finished_motor_gasoline",
                "finished_motor_gasoline_conventional_55",
                "finished_motor_gasoline_reformulated_other",
                "finished_petroleum_products",
                "fuel_ethanol",
                "gasoline_blending_components",
                "heavy_gas_oils",
                "hydrogen_oxygenates_renewables_fuels_and_other_hydrocarbons",
                "isobutane",
                "isobutane_isobutylene",
                "isobutylene",
                "kerosene",
                "kerosene_and_light_oils",
                "kerosene_type_jet_fuel",
                "liquified_petroleum_gases",
                "lubricants",
                "mtbe",
                "miscellaneous_petroleum_products",
                "motor_gasoline_blending_components_reformulated_rbob",
                "motor_gasoline_finished_conventional_ed55_and_lower",
                "naphtha_for_petrochemical_feedstock_use",
                "naphthas_and_lighter",
                "natural_gas_liquids_and_liquid_refinery_gases",
                "natural_gas_plant_liquids",
                "natural_gasoline",
                "normal_butane",
                "normal_butane_butylene",
                "normal_butylene",
                "other_biofuels",
                "other_conventional_motor_gasoline",
                "other_hydrocarbons",
                "other_liquids",
                "other_oils_for_petrochemical_feedstock_use",
                "other_oxygenates",
                "oxygenates",
                "pentanes_plus",
                "petrochemical_feedstocks",
                "petroleum_coke",
                "propane",
                "propane_and_propylene",
                "propane_fractionated_and_ready_for_sale",
                "propylene",
                "propylene_nonfuel_use",
                "refinery_grade_butane",
                "refinery_olefins",
                "reformulated_gtab_gasoline_blending_components",
                "reformulated_gasoline_blending_components",
                "reformulated_motor_gasoline",
                "reformulated_motor_gasoline_with_alcohol",
                "reformulated_rbob_with_alcohol_gasoline_blending_components",
                "reformulated_rbob_with_ether_gasoline_blending_components",
                "renewable_diesel_fuel",
                "residual_fuel_oil",
                "residual_fuel_oil_0_31_to_1_00_sulfur",
                "residual_fuel_oil_greater_than_1_sulfur",
                "residual_fuel_oil_less_than_0_31_sulfur",
                "residuum",
                "special_naphthas",
                "total_petroleum_products",
                "unfinished_oils",
                "waxes",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
        },
        "series": {"multiple_items_allowed": True},
    }

    frequency: Literal["annual", "monthly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'monthly'.",
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
        description="Series filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )


class EiaPetroleumStocksByTypeData(EiaApiData):
    """Stocks by Type. EIA petroleum gas survey data"""

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


class EiaPetroleumStocksByTypeFetcher(
    Fetcher[EiaPetroleumStocksByTypeQueryParams, list[EiaPetroleumStocksByTypeData]]
):
    """Stocks by Type fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaPetroleumStocksByTypeQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaPetroleumStocksByTypeQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumStocksByTypeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumStocksByTypeQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumStocksByTypeData]:
        """Transform the data."""
        return transform_dataset_data(EiaPetroleumStocksByTypeData, query, data)
