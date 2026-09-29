"""Refinery Net Input model."""

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


class EiaPetroleumRefineryNetInputQueryParams(EiaApiQueryParams):
    """Refinery Net Input. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pnp/inpt2
    """

    __group__ = "petroleum"
    __dataset__ = "refinery_net_input"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": ["refinery_net_input", "refinery_receipts_of_alaskan_oil"],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "aviation_gasoline_blending_components",
                "biodiesel",
                "biodiesel_renewable_diesel_fuel",
                "biofuel_fuels",
                "biofuel_fuels_excluding_fuel_ethanol",
                "conventional_cbob_gasoline_blending_components",
                "conventional_gtab_gasoline_blending_components",
                "conventional_gasoline_blending_components",
                "conventional_other_gasoline_blending_components",
                "crude_oil",
                "crude_oil_and_petroleum_products",
                "fuel_ethanol",
                "gasoline_blending_components",
                "heavy_gas_oils",
                "hydrogen",
                "hydrogen_oxygenates_renewables_fuels_and_other_hydrocarbons",
                "isobutane",
                "kerosene_and_light_oils",
                "liquified_petroleum_gases",
                "mtbe",
                "motor_gasoline_blending_components_reformulated_rbob",
                "naphthas_and_lighter",
                "natural_gas_liquids_and_liquid_refinery_gases",
                "natural_gas_plant_liquids",
                "natural_gasoline",
                "normal_butane",
                "other_biofuels",
                "other_hydrocarbons",
                "other_liquids",
                "other_oxygenates",
                "oxygenates",
                "pentanes_plus",
                "reformulated_gasoline_blending_components",
                "reformulated_rbob_with_alcohol_gasoline_blending_components",
                "reformulated_rbob_with_ether_gasoline_blending_components",
                "renewable_diesel_fuel",
                "residuum",
                "unfinished_oils",
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


class EiaPetroleumRefineryNetInputData(EiaApiData):
    """Refinery Net Input. EIA petroleum gas survey data"""

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


class EiaPetroleumRefineryNetInputFetcher(
    Fetcher[
        EiaPetroleumRefineryNetInputQueryParams, list[EiaPetroleumRefineryNetInputData]
    ]
):
    """Refinery Net Input fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumRefineryNetInputQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaPetroleumRefineryNetInputQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumRefineryNetInputQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumRefineryNetInputQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumRefineryNetInputData]:
        """Transform the data."""
        return transform_dataset_data(EiaPetroleumRefineryNetInputData, query, data)
