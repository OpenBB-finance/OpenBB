"""Average Price of Natural Gas Delivered to Residential and Commercial Consumers by Local Distribution and Marketers in Selected States model."""

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


class EiaNaturalGasResidentialAndCommercialPricesSelectedStatesQueryParams(
    EiaApiQueryParams
):
    """Average Price of Natural Gas Delivered to Residential and Commercial Consumers by Local Distribution and Marketers in Selected States. EIA natural gas survey data

    Source: https://www.eia.gov/opendata/browser/natural-gas/pri/rescom
    """

    __group__ = "natural_gas"
    __dataset__ = "residential_and_commercial_prices_selected_states"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "price_delivered_to_commercial_sectors",
                "price_delivered_to_residential_consumers",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": [
                "florida",
                "new_york",
                "ohio",
                "usa_dc",
                "usa_ga",
                "usa_md",
                "usa_mi",
                "usa_nj",
                "usa_pa",
                "usa_va",
            ],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "district_of_columbia_price_of_natural_gas_delivered_to",
                "district_of_columbia_price_of_natural_gas_sold_to",
                "florida_price_of_natural_gas_delivered_to_residential",
                "florida_price_of_natural_gas_sold_to_commercial_consumers",
                "georgia_price_of_natural_gas_delivered_to_residential",
                "georgia_price_of_natural_gas_sold_to_commercial_consumers",
                "maryland_price_of_natural_gas_delivered_to_residential",
                "maryland_price_of_natural_gas_sold_to_commercial_consumers",
                "michigan_price_of_natural_gas_delivered_to_residential",
                "michigan_price_of_natural_gas_sold_to_commercial_consumers",
                "new_jersey_price_of_natural_gas_delivered_to_residential",
                "new_jersey_price_of_natural_gas_sold_to_commercial_consumers",
                "new_york_price_of_natural_gas_delivered_to_residential",
                "new_york_price_of_natural_gas_sold_to_commercial_consumers",
                "ohio_price_of_natural_gas_delivered_to_residential_consumers",
                "ohio_price_of_natural_gas_sold_to_commercial_consumers",
                "pennsylvania_price_of_natural_gas_delivered_to_residential",
                "pennsylvania_price_of_natural_gas_sold_to_commercial",
                "virginia_price_of_natural_gas_delivered_to_residential",
                "virginia_price_of_natural_gas_sold_to_commercial_consumers",
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
    region: str | None = Field(
        default=None,
        description="DuoArea filter. Accepts a comma-separated list of values.",
    )
    series: str | None = Field(
        default=None,
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaNaturalGasResidentialAndCommercialPricesSelectedStatesData(EiaApiData):
    """Average Price of Natural Gas Delivered to Residential and Commercial Consumers by Local Distribution and Marketers in Selected States. EIA natural gas survey data"""

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


class EiaNaturalGasResidentialAndCommercialPricesSelectedStatesFetcher(
    Fetcher[
        EiaNaturalGasResidentialAndCommercialPricesSelectedStatesQueryParams,
        list[EiaNaturalGasResidentialAndCommercialPricesSelectedStatesData],
    ]
):
    """Average Price of Natural Gas Delivered to Residential and Commercial Consumers by Local Distribution and Marketers in Selected States fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaNaturalGasResidentialAndCommercialPricesSelectedStatesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaNaturalGasResidentialAndCommercialPricesSelectedStatesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaNaturalGasResidentialAndCommercialPricesSelectedStatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaNaturalGasResidentialAndCommercialPricesSelectedStatesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaNaturalGasResidentialAndCommercialPricesSelectedStatesData]:
        """Transform the data."""
        return transform_dataset_data(
            EiaNaturalGasResidentialAndCommercialPricesSelectedStatesData, query, data
        )
