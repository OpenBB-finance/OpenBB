"""Deribit Settlements Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_deribit.utils.constants import (
    INSTRUMENT_CHOICES_ENDPOINT,
    MAX_SETTLEMENT_COUNT,
    SYMBOL_STYLE,
    Currencies,
    SettlementTypes,
)


class DeribitSettlementsQueryParams(QueryParams):
    """Deribit Settlements Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_last_settlements_by_currency
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": INSTRUMENT_CHOICES_ENDPOINT,
                "style": SYMBOL_STYLE,
            },
        }
    }

    symbol: str | None = Field(
        default=None,
        description="One or more instrument names. When given, the currency is"
        + " ignored.",
    )
    currency: Currencies = Field(
        default="BTC", description="The settlement currency of the instruments."
    )
    settlement_type: SettlementTypes | None = Field(
        default=None,
        description="The kind of settlement. Default is all of them.",
    )
    start_date: Any | None = Field(
        default=None, description="Search back no further than this date."
    )
    limit: int = Field(
        default=100,
        description="The number of settlements to return, at most"
        f" {MAX_SETTLEMENT_COUNT}.",
        ge=1,
        le=MAX_SETTLEMENT_COUNT,
    )


class DeribitSettlementsData(Data):
    """Deribit Settlements Data."""

    __alias_dict__ = {"symbol": "instrument_name", "settlement_type": "type"}

    timestamp: datetime = Field(
        description="When the instrument settled.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "category", "pinned": "left"}
        },
    )
    symbol: str | None = Field(
        default=None,
        description="The name of the instrument.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    settlement_type: str | None = Field(
        default=None,
        description="Whether the event was a settlement or a delivery.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Type", "chartDataType": "excluded"}
        },
    )
    position: float | None = Field(
        default=None,
        description="The size that settled.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    index_price: float | None = Field(
        default=None,
        description="The level of the index at settlement.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    mark_price: float | None = Field(
        default=None,
        description="The price the instrument settled at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "series"},
        },
    )
    profit_loss: float | None = Field(
        default=None,
        description="The profit and loss the settlement realized.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Profit & Loss",
                "chartDataType": "excluded",
                "renderFn": "greenRed",
            }
        },
    )
    session_profit_loss: float | None = Field(
        default=None,
        description="The profit and loss of the whole session.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Session Profit & Loss",
                "chartDataType": "excluded",
                "renderFn": "greenRed",
            }
        },
    )
    funding: float | None = Field(
        default=None,
        description="The funding the session paid.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    session_bankruptcy: float | None = Field(
        default=None,
        description="The loss the session could not cover.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    session_tax: float | None = Field(
        default=None,
        description="The socialised loss the session was charged.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    session_tax_rate: float | None = Field(
        default=None,
        description="The rate the socialised loss was charged at.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    socialized: float | None = Field(
        default=None,
        description="The loss spread across other accounts.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )

    @field_validator("timestamp", mode="before", check_fields=False)
    @classmethod
    def validate_timestamp(cls, v):
        """Read the timestamp as a datetime."""
        from openbb_deribit.utils.helpers import from_timestamp

        return from_timestamp(v)


class DeribitSettlementsFetcher(
    Fetcher[DeribitSettlementsQueryParams, list[DeribitSettlementsData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitSettlementsQueryParams:
        """Transform the query."""
        return DeribitSettlementsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitSettlementsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If nothing settled over the span.
        """
        from openbb_deribit.utils.client import gather, request
        from openbb_deribit.utils.helpers import get_perpetual_symbols, to_timestamp

        shared = {
            "type": query.settlement_type,
            "count": query.limit,
            "search_start_timestamp": (
                to_timestamp(query.start_date) if query.start_date else None
            ),
        }

        if query.symbol:
            symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
            perpetuals = await get_perpetual_symbols()
            results = await gather(
                [
                    (
                        "get_last_settlements_by_instrument",
                        {
                            "instrument_name": perpetuals.get(symbol, symbol),
                            **shared,
                        },
                    )
                    for symbol in symbols
                ]
            )
            data = [
                record
                for result in results
                if isinstance(result, dict)
                for record in result.get("settlements") or []
            ]
        else:
            result = await request(
                "get_last_settlements_by_currency",
                {"currency": query.currency.upper(), **shared},
            )
            data = (result or {}).get("settlements") or []

        if not data:
            raise EmptyDataError("Deribit reports nothing settled over the span.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitSettlementsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitSettlementsData]:
        """Transform the data to the model."""
        return [
            DeribitSettlementsData.model_validate(record)
            for record in sorted(
                data, key=lambda d: d.get("timestamp") or 0, reverse=True
            )
        ]
