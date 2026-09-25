"""Deribit Currencies Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class DeribitCurrenciesQueryParams(QueryParams):
    """Deribit Currencies Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_currencies
    """


class DeribitCurrenciesData(Data):
    """Deribit Currencies Data."""

    currency: str = Field(
        description="The abbreviation of the currency.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "category", "pinned": "left"}
        },
    )
    currency_long: str | None = Field(
        default=None,
        description="The full name of the currency.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded", "headerName": "Name"}
        },
    )
    coin_type: str | None = Field(
        default=None,
        description="The type of the currency.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    currency_uuid: str | None = Field(
        default=None,
        description="The unique identifier of the currency.",
        json_schema_extra={
            "x-widget_config": {
                "chartDataType": "excluded",
                "headerName": "Currency UUID",
                "hide": True,
            }
        },
    )
    network_currency: str | None = Field(
        default=None,
        description="The currency the network fee is charged in.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    apr: float | None = Field(
        default=None,
        description="The annual percentage rate earned by holding the currency.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"chartDataType": "series", "headerName": "APR"},
        },
    )
    decimals: int | None = Field(
        default=None,
        description="The number of decimal places the currency is held to.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    onchain_operations_precision: int | None = Field(
        default=None,
        description="The number of decimal places an on-chain operation is held to.",
        json_schema_extra={
            "x-widget_config": {
                "chartDataType": "excluded",
                "headerName": "On-chain Precision",
            }
        },
    )
    min_confirmations: int | None = Field(
        default=None,
        description="The confirmations a deposit needs before it is credited.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    min_withdrawal_fee: float | None = Field(
        default=None,
        description="The smallest fee a withdrawal is charged.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    withdrawal_fee: float | None = Field(
        default=None,
        description="The fee a withdrawal is charged.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    network_fee: float | None = Field(
        default=None,
        description="The fee the network itself charges.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    in_cross_collateral_pool: bool | None = Field(
        default=None,
        description="Whether the currency counts towards cross collateral.",
        json_schema_extra={
            "x-widget_config": {
                "chartDataType": "excluded",
                "cellDataType": "boolean",
            }
        },
    )


class DeribitCurrenciesFetcher(
    Fetcher[DeribitCurrenciesQueryParams, list[DeribitCurrenciesData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitCurrenciesQueryParams:
        """Transform the query."""
        return DeribitCurrenciesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitCurrenciesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If the exchange listed no currencies.
        """
        from openbb_deribit.utils.helpers import get_currencies

        data = await get_currencies()

        if not data:
            raise EmptyDataError("Deribit listed no currencies.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitCurrenciesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitCurrenciesData]:
        """Transform the data to the model."""
        return [
            DeribitCurrenciesData.model_validate(record)
            for record in sorted(data, key=lambda d: str(d.get("currency")))
        ]
