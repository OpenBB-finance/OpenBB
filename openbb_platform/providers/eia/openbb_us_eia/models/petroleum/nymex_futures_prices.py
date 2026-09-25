"""NYMEX Futures Prices (Futures prices after April 5, 2024, are not available) model."""

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


class EiaPetroleumNymexFuturesPricesQueryParams(EiaApiQueryParams):
    """NYMEX Futures Prices (Futures prices after April 5, 2024, are not available). EIA petroleum gas survey data

    Source: https://www.eia.gov/opendata/browser/petroleum/pri/fut
    """

    __group__ = "petroleum"
    __dataset__ = "nymex_futures_prices"
    __json_schema_extra__ = {
        "process": {
            "multiple_items_allowed": True,
            "choices": [
                "future_contract_1",
                "future_contract_2",
                "future_contract_3",
                "future_contract_4",
            ],
        },
        "product": {
            "multiple_items_allowed": True,
            "choices": [
                "crude_oil",
                "no_2_fuel_oil_heating_oil",
                "propane",
                "reformulated_regular_gasoline",
                "regular_gasoline",
            ],
        },
        "region": {"multiple_items_allowed": True, "choices": ["na", "new_york_city"]},
        "series": {
            "multiple_items_allowed": True,
            "choices": [
                "cushing_ok_crude_oil_future_contract_1",
                "cushing_ok_crude_oil_future_contract_2",
                "cushing_ok_crude_oil_future_contract_3",
                "cushing_ok_crude_oil_future_contract_4",
                "mont_belvieu_tx_propane_future_contract_1",
                "mont_belvieu_tx_propane_future_contract_2",
                "mont_belvieu_tx_propane_future_contract_3",
                "mont_belvieu_tx_propane_future_contract_4",
                "new_york_harbor_no_2_heating_oil_future_contract_1",
                "new_york_harbor_no_2_heating_oil_future_contract_2",
                "new_york_harbor_no_2_heating_oil_future_contract_3",
                "new_york_harbor_no_2_heating_oil_future_contract_4",
                "new_york_harbor_reformulated_rbob_regular_gasoline_future_contract_1_dollars_per_gallon",
                "new_york_harbor_reformulated_rbob_regular_gasoline_future_contract_2_dollars_per_gallon",
                "new_york_harbor_reformulated_rbob_regular_gasoline_future_contract_3_dollars_per_gallon",
                "new_york_harbor_reformulated_rbob_regular_gasoline_future_contract_4_dollars_per_gallon",
                "new_york_harbor_regular_gasoline_future_contract_1",
                "new_york_harbor_regular_gasoline_future_contract_2",
                "new_york_harbor_regular_gasoline_future_contract_3",
                "new_york_harbor_regular_gasoline_future_contract_4",
            ],
        },
    }

    frequency: Literal["annual", "daily", "monthly", "weekly"] | None = Field(
        default=None,
        description="The data frequency. The default is 'weekly'.",
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
        description="Series filter. Accepts a comma-separated list of values.",
    )


class EiaPetroleumNymexFuturesPricesData(EiaApiData):
    """NYMEX Futures Prices (Futures prices after April 5, 2024, are not available). EIA petroleum gas survey data"""

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


class EiaPetroleumNymexFuturesPricesFetcher(
    Fetcher[
        EiaPetroleumNymexFuturesPricesQueryParams,
        list[EiaPetroleumNymexFuturesPricesData],
    ]
):
    """NYMEX Futures Prices (Futures prices after April 5, 2024, are not available) fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> EiaPetroleumNymexFuturesPricesQueryParams:
        """Transform the query parameters."""
        return transform_dataset_query(
            EiaPetroleumNymexFuturesPricesQueryParams, params
        )

    @staticmethod
    async def aextract_data(
        query: EiaPetroleumNymexFuturesPricesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract the data from the EIA API."""
        return await extract_dataset_data(query, credentials)

    @staticmethod
    def transform_data(
        query: EiaPetroleumNymexFuturesPricesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[EiaPetroleumNymexFuturesPricesData]:
        """Transform the data."""
        return transform_dataset_data(EiaPetroleumNymexFuturesPricesData, query, data)
