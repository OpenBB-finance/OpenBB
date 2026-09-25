"""Refinery Net Production model."""

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


class EiaPetroleumRefineryNetProductionQueryParams(EiaApiQueryParams):
    """Refinery Net Production. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/refp2
    """

    __group__ = "petroleum"
    __dataset__ = "refinery_net_production"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil",
                "aviation_gasoline",
                "commercial_kerosene_type_jet_fuel",
                "conventional_motor_gasoline",
                "conventional_motor_gasoline_with_alcohol",
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
                "isobutane",
                "isobutane_isobutylene",
                "isobutylene",
                "kerosene",
                "kerosene_type_jet_fuel",
                "liquified_petroleum_gases",
                "lubricants",
                "military_kerosene_type_jet_fuel",
                "miscellaneous_petroleum_products",
                "miscellaneous_petroleum_products_for_fuel_use",
                "miscellaneous_petroleum_products_for_nonfuel_use",
                "motor_gasoline_finished_conventional_ed55_and_lower",
                "naphtha_for_petrochemical_feedstock_use",
                "naphthenic_lubricants",
                "natural_gas_liquids_and_liquid_refinery_gases",
                "natural_gas_plant_liquids",
                "normal_butane",
                "normal_butane_butylene",
                "normal_butylene",
                "other_conventional_motor_gasoline",
                "other_oils_for_petrochemical_feedstock_use",
                "paraffinic_lubricants",
                "petrochemical_feedstocks",
                "petroleum_coke",
                "petroleum_coke_catalyst",
                "petroleum_coke_marketable",
                "processing_gain",
                "propane",
                "propane_and_propylene",
                "propylene",
                "refinery_olefins",
                "reformulated_motor_gasoline",
                "reformulated_motor_gasoline_with_alcohol",
                "residual_fuel_oil",
                "residual_fuel_oil_0_31_to_1_00_sulfur",
                "residual_fuel_oil_greater_than_1_sulfur",
                "residual_fuel_oil_less_than_0_31_sulfur",
                "special_naphthas",
                "still_gas",
                "waxes",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["na", "padd_1", "padd_2", "padd_3", "padd_4", "padd_5", "us"],
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
        description="Series filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )


class EiaPetroleumRefineryNetProductionData(EiaApiData):
    """Refinery Net Production. EIA petroleum gas survey data"""

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


class EiaPetroleumRefineryNetProductionFetcher(
    Fetcher[
        EiaPetroleumRefineryNetProductionQueryParams,
        list[EiaPetroleumRefineryNetProductionData],
    ]
):
    """Refinery Net Production fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumRefineryNetProductionQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumRefineryNetProductionQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumRefineryNetProductionQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumRefineryNetProductionQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumRefineryNetProductionData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumRefineryNetProductionData, query, data
        )
