"""Deribit Trades Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator, model_validator

from openbb_deribit.utils.constants import (
    INSTRUMENT_CHOICES_ENDPOINT,
    MAX_TRADE_COUNT,
    SYMBOL_STYLE,
    ListingCurrencies,
    Sorting,
    TradeKinds,
)


class DeribitTradesQueryParams(QueryParams):
    """Deribit Trades Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_last_trades_by_instrument
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
    currency: ListingCurrencies = Field(
        default="BTC", description="The settlement currency of the instruments."
    )
    kind: TradeKinds = Field(
        default="future",
        description="The kind of instrument. Only used when reading by currency,"
        + " where the exchange rejects a request that leaves it out, and where"
        + " spot is not offered at all. Read spot trades by symbol instead.",
    )
    start_date: Any | None = Field(
        default=None, description="Return trades from this date onwards."
    )
    end_date: Any | None = Field(
        default=None, description="Return trades up to this date."
    )
    limit: int = Field(
        default=100,
        description=f"The number of trades to return, at most {MAX_TRADE_COUNT}.",
        ge=1,
        le=MAX_TRADE_COUNT,
    )
    sorting: Sorting = Field(
        default="desc", description="The order the trades are returned in."
    )

    @model_validator(mode="after")
    def _options_are_listed_by_underlying(self):
        """Refuse a listing of options scoped to a currency that only settles them."""
        from openbb_deribit.utils.helpers import reject_options_by_settlement

        if not self.symbol:
            reject_options_by_settlement(self.currency, self.kind)

        return self


class DeribitTradesData(Data):
    """Deribit Trades Data."""

    __alias_dict__ = {"symbol": "instrument_name"}

    timestamp: datetime = Field(
        description="When the trade printed.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "category", "pinned": "left"}
        },
    )
    symbol: str = Field(
        description="The name of the instrument.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    direction: str | None = Field(
        default=None,
        description="Which side the aggressor was on.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Side", "chartDataType": "excluded"}
        },
    )
    price: float = Field(
        description="The price the trade printed at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "series"},
        },
    )
    amount: float | None = Field(
        default=None,
        description="The size of the trade, in base currency.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    contracts: float | None = Field(
        default=None,
        description="The size of the trade, in contracts.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    iv: float | None = Field(
        default=None,
        description="The volatility the option trade implies.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "IV", "chartDataType": "excluded"},
        },
    )
    mark_price: float | None = Field(
        default=None,
        description="The price the exchange marked the instrument at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    index_price: float | None = Field(
        default=None,
        description="The price of the index at the time of the trade.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    tick_direction: int | None = Field(
        default=None,
        description="How the price moved against the previous trade. 0 and 1 are"
        + " upticks, 2 and 3 are downticks.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded", "hide": True}
        },
    )
    trade_id: str | None = Field(
        default=None,
        description="The identifier of the trade.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Trade ID",
                "cellDataType": "text",
                "chartDataType": "excluded",
                "hide": True,
            }
        },
    )
    trade_seq: int | None = Field(
        default=None,
        description="The sequence number of the trade.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Trade Seq",
                "cellDataType": "text",
                "chartDataType": "excluded",
                "hide": True,
            }
        },
    )
    block_trade_id: str | None = Field(
        default=None,
        description="The block trade the print belongs to.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Block Trade ID",
                "cellDataType": "text",
                "chartDataType": "excluded",
                "hide": True,
            }
        },
    )
    liquidation: str | None = Field(
        default=None,
        description="Which side of the trade was liquidated.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    starbase_match_id: int | None = Field(
        default=None,
        description="The matching engine's identifier for the fill.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Match ID",
                "cellDataType": "text",
                "chartDataType": "excluded",
                "hide": True,
            }
        },
    )
    starbase_timestamp: int | None = Field(
        default=None,
        description="When the matching engine recorded the fill, in nanoseconds"
        + " since the epoch.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Match Timestamp",
                "cellDataType": "text",
                "chartDataType": "excluded",
                "hide": True,
            }
        },
    )

    @field_validator("timestamp", mode="before", check_fields=False)
    @classmethod
    def validate_timestamp(cls, v):
        """Read the timestamp as a datetime."""
        from openbb_deribit.utils.helpers import from_timestamp

        return from_timestamp(v)


class DeribitTradesFetcher(Fetcher[DeribitTradesQueryParams, list[DeribitTradesData]]):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitTradesQueryParams:
        """Transform the query."""
        return DeribitTradesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitTradesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        OpenBBError
            If the symbol is one of the spot pairs the exchange routes to Coinbase,
            which publish no trade history here.
        EmptyDataError
            If the exchange printed no trades over the span.
        """
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_deribit.utils.client import gather, request
        from openbb_deribit.utils.constants import ROUTED_SPOT_ERROR
        from openbb_deribit.utils.helpers import get_perpetual_symbols, to_timestamp

        window = {
            "start_timestamp": (
                to_timestamp(query.start_date) if query.start_date else None
            ),
            "end_timestamp": to_timestamp(query.end_date) if query.end_date else None,
        }
        timed = window["start_timestamp"] and window["end_timestamp"]
        shared = {"count": query.limit, "sorting": query.sorting}

        if query.symbol:
            symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
            perpetuals = await get_perpetual_symbols()
            method = (
                "get_last_trades_by_instrument_and_time"
                if timed
                else "get_last_trades_by_instrument"
            )
            results = await gather(
                [
                    (
                        method,
                        {
                            "instrument_name": perpetuals.get(symbol, symbol),
                            **window,
                            **shared,
                        },
                    )
                    for symbol in symbols
                ],
                use_cache=False,
            )
            data = [
                trade
                for result in results
                if isinstance(result, dict)
                for trade in result.get("trades") or []
            ]

            if not data and any(
                ROUTED_SPOT_ERROR in str(result)
                for result in results
                if isinstance(result, Exception)
            ):
                raise OpenBBError(
                    f"Deribit publishes no trade history for {', '.join(symbols)}."
                    " Spot pairs it routes to Coinbase carry none."
                )
        else:
            method = (
                "get_last_trades_by_currency_and_time"
                if timed
                else "get_last_trades_by_currency"
            )
            try:
                result = await request(
                    method,
                    {
                        "currency": query.currency.upper(),
                        "kind": query.kind,
                        **window,
                        **shared,
                    },
                    use_cache=False,
                )
            except OpenBBError as error:
                if ROUTED_SPOT_ERROR not in str(error):
                    raise

                raise OpenBBError(
                    "Deribit publishes no trade history for the spot pairs it"
                    " routes to Coinbase. Read the other kinds by currency, or"
                    " a specific spot pair by symbol."
                ) from error

            data = (result or {}).get("trades") or []

        if not data:
            raise EmptyDataError("Deribit printed no trades matching the query.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitTradesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitTradesData]:
        """Transform the data to the model."""
        return [
            DeribitTradesData.model_validate(record)
            for record in sorted(
                data,
                key=lambda d: d.get("timestamp") or 0,
                reverse=query.sorting != "asc",
            )
        ]
