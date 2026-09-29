"""Exports model."""

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


class EiaPetroleumExportsQueryParams(EiaApiQueryParams):
    """Exports. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/move/exp
    """

    __group__ = "petroleum"
    __dataset__ = "exports"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil",
                "aviation_gasoline",
                "aviation_gasoline_blending_components",
                "biodiesel",
                "biofuel_fuels",
                "conventional_gasoline_blending_components",
                "conventional_motor_gasoline",
                "crude_oil",
                "crude_oil_and_petroleum_products",
                "distillate_fuel_oil",
                "distillate_fuel_oil_0_to_15_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
                "ethane",
                "ethane_ethylene",
                "finished_motor_gasoline",
                "finished_petroleum_products",
                "fuel_ethanol",
                "gasoline_blending_components",
                "hydrogen_oxygenates_renewables_fuels_and_other_hydrocarbons",
                "isobutane",
                "isobutane_isobutylene",
                "kerosene",
                "kerosene_and_light_oils",
                "kerosene_type_jet_fuel",
                "liquified_petroleum_gases",
                "lubricants",
                "mtbe",
                "miscellaneous_petroleum_products",
                "naphtha_for_petrochemical_feedstock_use",
                "naphthas_and_lighter",
                "natural_gas_liquids_and_liquid_refinery_gases",
                "natural_gas_plant_liquids",
                "natural_gasoline",
                "normal_butane",
                "normal_butane_butylene",
                "other_biofuels",
                "other_liquids",
                "other_oils_for_petrochemical_feedstock_use",
                "other_oxygenates",
                "oxygenates",
                "pentanes_plus",
                "petroleum_coke",
                "propane",
                "propane_and_propylene",
                "reformulated_gasoline_blending_components",
                "reformulated_motor_gasoline",
                "renewable_diesel_fuel",
                "residual_fuel_oil",
                "special_naphthas",
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
        description="Series filter. Accepts a comma-separated list of values. There are 612 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumExportsData(EiaApiData):
    """Exports. EIA petroleum gas survey data"""

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


class EiaPetroleumExportsFetcher(
    Fetcher[EiaPetroleumExportsQueryParams, list[EiaPetroleumExportsData]]
):
    """Exports fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaPetroleumExportsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaPetroleumExportsQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumExportsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumExportsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumExportsData]:
        """Transform the data."""
        return transform_dataset_data(EiaPetroleumExportsData, query, data)
