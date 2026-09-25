"""Movements by Pipeline, Tanker, Barge and Rail between PAD Districts model."""

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


class EiaPetroleumMovementsBetweenPadDistrictsQueryParams(EiaApiQueryParams):
    """Movements by Pipeline, Tanker, Barge and Rail between PAD Districts. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/move/ptb
    """

    __group__ = "petroleum"
    __dataset__ = "movements_between_pad_districts"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil",
                "aviation_gasoline",
                "biodiesel",
                "biodiesel_renewable_diesel_fuel",
                "biofuel_fuels",
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
                "finished_motor_gasoline",
                "finished_motor_gasoline_reformulated_other",
                "fuel_ethanol",
                "gasoline_blending_components",
                "isobutane",
                "isobutane_isobutylene",
                "kerosene",
                "kerosene_type_jet_fuel",
                "liquified_petroleum_gases",
                "lubricants",
                "miscellaneous_petroleum_products",
                "motor_gasoline_blending_components_reformulated_rbob",
                "motor_gasoline_finished_conventional_ed55_and_lower",
                "naphtha_for_petrochemical_feedstock_use",
                "natural_gas_liquids_and_liquid_refinery_gases",
                "natural_gas_plant_liquids",
                "natural_gasoline",
                "normal_butane",
                "normal_butane_butylene",
                "other_biofuels",
                "other_conventional_motor_gasoline",
                "other_oils_for_petrochemical_feedstock_use",
                "pentanes_plus",
                "petrochemical_feedstocks",
                "petroleum_coke_marketable",
                "propane",
                "propane_and_propylene",
                "propylene",
                "refinery_olefins",
                "reformulated_gtab_gasoline_blending_components",
                "reformulated_gasoline_blending_components",
                "reformulated_motor_gasoline",
                "reformulated_motor_gasoline_with_alcohol",
                "reformulated_rbob_with_alcohol_gasoline_blending_components",
                "reformulated_rbob_with_ether_gasoline_blending_components",
                "renewable_diesel_fuel",
                "residual_fuel_oil",
                "special_naphthas",
                "total_petroleum_products",
                "unfinished_oils",
                "waxes",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["padd_1", "padd_2", "padd_3", "padd_4", "padd_5"],
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
        description="Series filter. Accepts a comma-separated list of values. There are 740 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumMovementsBetweenPadDistrictsData(EiaApiData):
    """Movements by Pipeline, Tanker, Barge and Rail between PAD Districts. EIA petroleum gas survey data"""

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


class EiaPetroleumMovementsBetweenPadDistrictsFetcher(
    Fetcher[
        EiaPetroleumMovementsBetweenPadDistrictsQueryParams,
        list[EiaPetroleumMovementsBetweenPadDistrictsData],
    ]
):
    """Movements by Pipeline, Tanker, Barge and Rail between PAD Districts fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumMovementsBetweenPadDistrictsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumMovementsBetweenPadDistrictsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumMovementsBetweenPadDistrictsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumMovementsBetweenPadDistrictsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumMovementsBetweenPadDistrictsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumMovementsBetweenPadDistrictsData, query, data
        )
