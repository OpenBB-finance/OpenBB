"""Spot Prices model."""

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


class EiaPetroleumSpotPricesQueryParams(EiaApiQueryParams):
    """Spot Prices. EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/spt
    """

    __group__ = "petroleum"
    __dataset__ = "spot_prices"
    __json_schema_extra__ = {
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "carb_diesel",
                "conventional_regular_gasoline",
                "kerosene_type_jet_fuel",
                "no_2_diesel_low_sulfur",
                "no_2_fuel_oil_heating_oil",
                "propane",
                "reformulated_regular_gasoline",
                "uk_brent_crude_oil",
                "wti_crude_oil",
            ],
        },
        "region": {
            "multiple_items_allowed": True,
            "choices": ["los_angeles", "na", "new_york_city"],
        },
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "cushing_ok_wti_spot_price_fob",
                "europe_brent_spot_price_fob",
                "los_angeles_reformulated_rbob_regular_gasoline_spot_price",
                "los_angeles_ca_ultra_low_sulfur_carb_diesel_spot_price",
                "mont_belvieu_tx_propane_spot_price_fob",
                "new_york_harbor_conventional_gasoline_regular_spot_price_fob",
                "new_york_harbor_no_2_heating_oil_spot_price_fob",
                "new_york_harbor_ultra_low_sulfur_no_2_diesel_spot_price",
                "us_gulf_coast_conventional_gasoline_regular_spot_price_fob",
                "us_gulf_coast_kerosene_type_jet_fuel_spot_price_fob",
                "us_gulf_coast_ultra_low_sulfur_no_2_diesel_spot_price",
            ],
        },
    }

    frequency: Literal["annual", "daily", "monthly", "weekly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'weekly'.",
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
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumSpotPricesData(EiaApiData):
    """Spot Prices. EIA petroleum gas survey data"""

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


class EiaPetroleumSpotPricesFetcher(
    Fetcher[EiaPetroleumSpotPricesQueryParams, list[EiaPetroleumSpotPricesData]]
):
    """Spot Prices fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> EiaPetroleumSpotPricesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(EiaPetroleumSpotPricesQueryParams, params)

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumSpotPricesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumSpotPricesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumSpotPricesData]:
        """Transform the data."""
        return transform_dataset_data(EiaPetroleumSpotPricesData, query, data)
