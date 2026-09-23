"""Supply and Disposition model."""

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


class EiaPetroleumSupplyAndDispositionQueryParams(EiaApiQueryParams):
    """Supply and Disposition. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/sum/snd
    """

    __group__ = "petroleum"
    __dataset__ = "supply_and_disposition"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "ending_stocks",
                "exports",
                "field_production",
                "imports",
                "net_receipts_by_pipeline_tanker_barge_and_rail",
                "product_supplied",
                "refinery_and_blender_net_input",
                "refinery_and_blender_net_production",
                "renewable_fuels_plant_and_oxygenate_plant_net_production",
                "stock_change",
                "supply_adjustment",
                "transfers_to_crude_oil_supply",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil",
                "aviation_gasoline",
                "aviation_gasoline_blending_components",
                "biodiesel",
                "biofuel_fuels",
                "biofuel_fuels_excluding_fuel_ethanol",
                "condensate_and_scrubber_oil",
                "conventional_gasoline_blending_components",
                "conventional_motor_gasoline",
                "crude_oil",
                "crude_oil_and_petroleum_products",
                "distillate_fuel_oil",
                "distillate_fuel_oil_0_to_15_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
                "ethane",
                "ethylene",
                "finished_motor_gasoline",
                "finished_petroleum_products",
                "fuel_ethanol",
                "gasoline_blending_components",
                "hydrogen",
                "hydrogen_oxygenates_renewables_fuels_and_other_hydrocarbons",
                "isobutane",
                "isobutylene",
                "kerosene",
                "kerosene_type_jet_fuel",
                "lubricants",
                "miscellaneous_petroleum_products",
                "naphtha_for_petrochemical_feedstock_use",
                "natural_gas_liquids_and_liquid_refinery_gases",
                "natural_gas_plant_liquids",
                "natural_gasoline",
                "normal_butane",
                "normal_butylene",
                "other_biofuels",
                "other_hydrocarbons",
                "other_liquids",
                "other_oils_for_petrochemical_feedstock_use",
                "oxygenates",
                "petrochemical_feedstocks",
                "petroleum_coke",
                "petroleum_coke_catalyst",
                "petroleum_coke_marketable",
                "propane",
                "propylene",
                "refinery_olefins",
                "reformulated_gasoline_blending_components",
                "reformulated_motor_gasoline",
                "renewable_diesel_fuel",
                "residual_fuel_oil",
                "residual_fuel_oil_0_31_to_1_00_sulfur",
                "residual_fuel_oil_greater_than_1_sulfur",
                "residual_fuel_oil_less_than_0_31_sulfur",
                "special_naphthas",
                "still_gas",
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


class EiaPetroleumSupplyAndDispositionData(EiaApiData):
    """Supply and Disposition. EIA petroleum gas survey data"""

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


class EiaPetroleumSupplyAndDispositionFetcher(
    Fetcher[
        EiaPetroleumSupplyAndDispositionQueryParams,
        list[EiaPetroleumSupplyAndDispositionData],
    ]
):
    """Supply and Disposition fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumSupplyAndDispositionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumSupplyAndDispositionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumSupplyAndDispositionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumSupplyAndDispositionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumSupplyAndDispositionData]:
        """Transform the data."""
        return transform_dataset_data(EiaPetroleumSupplyAndDispositionData, query, data)
