"""Movements by Pipeline between PAD Districts model."""

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


class EiaPetroleumMovementsByPipelineBetweenPadDistrictsQueryParams(EiaApiQueryParams):
    """Movements by Pipeline between PAD Districts. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/move/pipe
    """

    __group__ = "petroleum"
    __dataset__ = "movements_by_pipeline_between_pad_districts"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "aviation_gasoline",
                "biodiesel",
                "biodiesel_renewable_diesel_fuel",
                "biofuel_fuels",
                "conventional_cbob_gasoline_blending_components",
                "conventional_gtab_gasoline_blending_components",
                "conventional_gasoline_blending_components",
                "conventional_motor_gasoline",
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
                "gasoline_blending_components",
                "isobutane",
                "isobutane_isobutylene",
                "kerosene",
                "kerosene_type_jet_fuel",
                "liquified_petroleum_gases",
                "miscellaneous_petroleum_products",
                "motor_gasoline_blending_components_reformulated_rbob",
                "natural_gas_liquids_and_liquid_refinery_gases",
                "natural_gas_plant_liquids",
                "natural_gasoline",
                "normal_butane",
                "normal_butane_butylene",
                "other_conventional_motor_gasoline",
                "pentanes_plus",
                "propane",
                "propane_and_propylene",
                "reformulated_gasoline_blending_components",
                "reformulated_motor_gasoline",
                "reformulated_rbob_with_alcohol_gasoline_blending_components",
                "total_petroleum_products",
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
        description="Series filter. Accepts a comma-separated list of values. There are 413 valid values - use the `facet_options` endpoint to list them.",
    )


class EiaPetroleumMovementsByPipelineBetweenPadDistrictsData(EiaApiData):
    """Movements by Pipeline between PAD Districts. EIA petroleum gas survey data"""

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


class EiaPetroleumMovementsByPipelineBetweenPadDistrictsFetcher(
    Fetcher[
        EiaPetroleumMovementsByPipelineBetweenPadDistrictsQueryParams,
        list[EiaPetroleumMovementsByPipelineBetweenPadDistrictsData],
    ]
):
    """Movements by Pipeline between PAD Districts fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumMovementsByPipelineBetweenPadDistrictsQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumMovementsByPipelineBetweenPadDistrictsQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumMovementsByPipelineBetweenPadDistrictsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumMovementsByPipelineBetweenPadDistrictsQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumMovementsByPipelineBetweenPadDistrictsData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumMovementsByPipelineBetweenPadDistrictsData, query, data
        )
