"""US Refiner Gasoline Prices by Formulation, Grade, Sales Type model."""

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


class EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeQueryParams(
    EiaApiQueryParams
):
    """US Refiner Gasoline Prices by Formulation, Grade, Sales Type. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/refmg2
    """

    __group__ = "petroleum"
    __dataset__ = "us_refiner_gasoline_prices_by_formulation_grade_sales_type"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "bulk_sales_by_refiners_and_gas_plants",
                "dtw_sales_price_by_refiners_and_gas_plants",
                "rack_sales_price_by_refiners_and_gas_plants",
                "retail_sales_by_refiners_and_gas_plants",
                "through_company_outlets_price_by_refiners_and_gas_plants",
                "wholesale_resale_price_by_refiners_and_gas_plants",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "conventional_gasoline",
                "conventional_premium_gasoline",
                "conventional_regular_gasoline",
                "gasoline_conventional_midgrade",
                "gasoline_oxygenated_midgrade",
                "gasoline_reformulated_midgrade",
                "oxygenated_gasoline",
                "oxygenated_premium_gasoline",
                "oxygenated_regular_gasoline",
                "reformulated_motor_gasoline",
                "reformulated_premium_gasoline",
                "reformulated_regular_gasoline",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "us_conventional_gasoline_bulk_sales_price_by_refiners",
                "us_conventional_gasoline_dtw_sales_price_by_refiners",
                "us_conventional_gasoline_midgrade_bulk_sales_price_by",
                "us_conventional_gasoline_midgrade_dtw_sales_price_by",
                "us_conventional_gasoline_midgrade_rack_sales_price_by",
                "us_conventional_gasoline_midgrade_retail_sales_by_refiners",
                "us_conventional_gasoline_midgrade_through_company_outlets",
                "us_conventional_gasoline_midgrade_wholesale_resale_price_by",
                "us_conventional_gasoline_premium_bulk_sales_price_by",
                "us_conventional_gasoline_premium_dtw_sales_price_by_refiners",
                "us_conventional_gasoline_premium_rack_sales_price_by",
                "us_conventional_gasoline_premium_retail_sales_by_refiners",
                "us_conventional_gasoline_premium_through_company_outlets",
                "us_conventional_gasoline_premium_wholesale_resale_price_by",
                "us_conventional_gasoline_rack_sales_price_by_refiners",
                "us_conventional_gasoline_regular_bulk_sales_price_by",
                "us_conventional_gasoline_regular_dtw_sales_price_by_refiners",
                "us_conventional_gasoline_regular_rack_sales_price_by",
                "us_conventional_gasoline_regular_retail_sales_by_refiners",
                "us_conventional_gasoline_regular_through_company_outlets",
                "us_conventional_gasoline_regular_wholesale_resale_price_by",
                "us_conventional_gasoline_retail_sales_by_refiners",
                "us_conventional_gasoline_through_company_outlets_price_by",
                "us_conventional_gasoline_wholesale_resale_price_by_refiners",
                "us_oxygenated_gasoline_bulk_sales_price_by_refiners",
                "us_oxygenated_gasoline_dtw_sales_price_by_refiners",
                "us_oxygenated_gasoline_midgrade_bulk_sales_price_by_refiners",
                "us_oxygenated_gasoline_midgrade_dtw_sales_price_by_refiners",
                "us_oxygenated_gasoline_midgrade_rack_sales_price_by_refiners",
                "us_oxygenated_gasoline_midgrade_retail_sales_by_refiners",
                "us_oxygenated_gasoline_midgrade_through_company_outlets",
                "us_oxygenated_gasoline_midgrade_wholesale_resale_price_by",
                "us_oxygenated_gasoline_premium_bulk_sales_price_by_refiners",
                "us_oxygenated_gasoline_premium_dtw_sales_price_by_refiners",
                "us_oxygenated_gasoline_premium_rack_sales_price_by_refiners",
                "us_oxygenated_gasoline_premium_retail_sales_by_refiners",
                "us_oxygenated_gasoline_premium_through_company_outlets",
                "us_oxygenated_gasoline_premium_wholesale_resale_price_by",
                "us_oxygenated_gasoline_rack_sales_price_by_refiners",
                "us_oxygenated_gasoline_regular_bulk_sales_price_by_refiners",
                "us_oxygenated_gasoline_regular_dtw_sales_price_by_refiners",
                "us_oxygenated_gasoline_regular_rack_sales_price_by_refiners",
                "us_oxygenated_gasoline_regular_retail_sales_by_refiners",
                "us_oxygenated_gasoline_regular_through_company_outlets",
                "us_oxygenated_gasoline_regular_wholesale_resale_price_by",
                "us_oxygenated_gasoline_retail_sales_by_refiners",
                "us_oxygenated_gasoline_through_company_outlets_price_by",
                "us_oxygenated_gasoline_wholesale_resale_price_by_refiners",
                "us_reformulated_gasoline_bulk_sales_price_by_refiners",
                "us_reformulated_gasoline_dtw_sales_price_by_refiners",
                "us_reformulated_gasoline_midgrade_bulk_sales_price_by",
                "us_reformulated_gasoline_midgrade_dtw_sales_price_by",
                "us_reformulated_gasoline_midgrade_rack_sales_price_by",
                "us_reformulated_gasoline_midgrade_retail_sales_by_refiners",
                "us_reformulated_gasoline_midgrade_through_company_outlets",
                "us_reformulated_gasoline_midgrade_wholesale_resale_price_by",
                "us_reformulated_gasoline_premium_bulk_sales_price_by",
                "us_reformulated_gasoline_premium_dtw_sales_price_by_refiners",
                "us_reformulated_gasoline_premium_rack_sales_price_by",
                "us_reformulated_gasoline_premium_retail_sales_by_refiners",
                "us_reformulated_gasoline_premium_through_company_outlets",
                "us_reformulated_gasoline_premium_wholesale_resale_price_by",
                "us_reformulated_gasoline_rack_sales_price_by_refiners",
                "us_reformulated_gasoline_regular_bulk_sales_price_by",
                "us_reformulated_gasoline_regular_dtw_sales_price_by_refiners",
                "us_reformulated_gasoline_regular_rack_sales_price_by",
                "us_reformulated_gasoline_regular_retail_sales_by_refiners",
                "us_reformulated_gasoline_regular_through_company_outlets",
                "us_reformulated_gasoline_regular_wholesale_resale_price_by",
                "us_reformulated_gasoline_retail_sales_by_refiners",
                "us_reformulated_gasoline_through_company_outlets_price_by",
                "us_reformulated_gasoline_wholesale_resale_price_by_refiners",
            ],
        },
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
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeData(EiaApiData):
    """US Refiner Gasoline Prices by Formulation, Grade, Sales Type. EIA petroleum gas survey data"""

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


class EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeFetcher(
    Fetcher[
        EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeQueryParams,
        list[EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeData],
    ]
):
    """US Refiner Gasoline Prices by Formulation, Grade, Sales Type fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeQueryParams,
            params,
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaPetroleumUsRefinerGasolinePricesByFormulationGradeSalesTypeData,
            query,
            data,
        )
