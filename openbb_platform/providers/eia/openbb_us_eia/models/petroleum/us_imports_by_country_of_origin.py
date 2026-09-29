"""US Imports by Country of Origin model."""

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


class EiaPetroleumUsImportsByCountryOfOriginQueryParams(EiaApiQueryParams):
    """US Imports by Country of Origin. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/move/impcus
    """

    __group__ = "petroleum"
    __dataset__ = "us_imports_by_country_of_origin"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "asphalt_and_road_oil",
                "aviation_gasoline",
                "aviation_gasoline_blending_components",
                "biodiesel",
                "conventional_gasoline_blending_components",
                "conventional_motor_gasoline",
                "crude_oil",
                "crude_oil_and_petroleum_products",
                "distillate_fuel_oil",
                "distillate_fuel_oil_0_to_15_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_15_to_500_ppm_sulfur",
                "distillate_fuel_oil_greater_than_2000_ppm_sulfur",
                "distillate_fuel_oil_greater_than_500_to_2000_ppm_sulfur",
                "ethane",
                "ethylene",
                "finished_motor_gasoline",
                "fuel_ethanol",
                "gasoline_blending_components",
                "isobutane",
                "isobutylene",
                "kerosene",
                "kerosene_type_jet_fuel",
                "liquified_petroleum_gases",
                "lubricants",
                "mtbe",
                "miscellaneous_petroleum_products",
                "naphtha_for_petrochemical_feedstock_use",
                "natural_gas_liquids_and_liquid_refinery_gases",
                "natural_gas_plant_liquids",
                "natural_gasoline",
                "normal_butane",
                "normal_butylene",
                "other_biofuels",
                "other_oils_for_petrochemical_feedstock_use",
                "other_oxygenates",
                "pentanes_plus",
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
                "total_petroleum_products",
                "unfinished_oils",
                "waxes",
            ],
        },
        "region": {"multiple_items_allowed": True},
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
        description="DuoArea filter. Accepts a comma-separated list of values. There are 140 valid values - use the `facet_options` endpoint to list them.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values. Use the `facet_options` endpoint for the valid values.",
    )


class EiaPetroleumUsImportsByCountryOfOriginData(EiaApiData):
    """US Imports by Country of Origin. EIA petroleum gas survey data"""

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


class EiaPetroleumUsImportsByCountryOfOriginFetcher(
    Fetcher[
        EiaPetroleumUsImportsByCountryOfOriginQueryParams,
        list[EiaPetroleumUsImportsByCountryOfOriginData],
    ]
):
    """US Imports by Country of Origin fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumUsImportsByCountryOfOriginQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumUsImportsByCountryOfOriginQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumUsImportsByCountryOfOriginQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumUsImportsByCountryOfOriginQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumUsImportsByCountryOfOriginData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumUsImportsByCountryOfOriginData, query, data
        )
