"""Movements by Tanker and Barge between PAD Districts model."""

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


class EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsQueryParams(
    EiaApiQueryParams
):
    """Movements by Tanker and Barge between PAD Districts. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/move/tb
    """

    __group__ = "petroleum"
    __dataset__ = "movements_by_tanker_and_barge_between_pad_districts"
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
                "finished_motor_gasoline",
                "finished_motor_gasoline_reformulated_other",
                "fuel_ethanol",
                "gasoline_blending_components",
                "isobutane",
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
                "normal_butane",
                "other_biofuels",
                "other_conventional_motor_gasoline",
                "other_oils_for_petrochemical_feedstock_use",
                "petrochemical_feedstocks",
                "propane",
                "propane_and_propylene",
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
                "special_naphthas",
                "total_petroleum_products",
                "unfinished_oils",
                "waxes",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "padd_1",
                "padd_1a",
                "padd_1b",
                "padd_1c",
                "padd_2",
                "padd_3",
                "padd_5",
            ],
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
        description="Series filter. Accepts a comma-separated list of values. There are 545 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsData(EiaApiData):
    """Movements by Tanker and Barge between PAD Districts. EIA petroleum gas survey data"""

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


class EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsFetcher(
    Fetcher[
        EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsQueryParams,
        list[EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsData],
    ]
):
    """Movements by Tanker and Barge between PAD Districts fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumMovementsByTankerAndBargeBetweenPadDistrictsData, query, data
        )
