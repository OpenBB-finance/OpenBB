"""Deribit Order Book Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_deribit.utils.constants import (
    INSTRUMENT_CHOICES_ENDPOINT,
    SYMBOL_STYLE,
    OrderBookDepths,
)


class DeribitOrderBookQueryParams(QueryParams):
    """Deribit Order Book Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_order_book
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
        description="One or more instrument names. A perpetual can also be given"
        + " by its shortened root, such as 'SOLUSDC'.",
    )
    instrument_id: int | None = Field(
        default=None,
        description="The numeric identifier of one instrument, used in place of"
        + " its name.",
    )
    depth: OrderBookDepths = Field(
        default="10", description="The number of levels to return on each side."
    )

    @field_validator("depth", mode="before", check_fields=False)
    @classmethod
    def validate_depth(cls, v):
        """Read the depth as text, so a number is accepted from Python as well."""
        return str(v) if v is not None else v


class DeribitOrderBookData(Data):
    """Deribit Order Book Data."""

    symbol: str = Field(
        description="The name of the instrument.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    timestamp: datetime | None = Field(
        default=None,
        description="When the book was published.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    side: str = Field(
        description="Whether the level is a bid or an ask.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    level: int = Field(
        description="How far the level sits from the top of the book.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    price: float = Field(
        description="The price of the level.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "category", "pinned": "left"},
        },
    )
    size: float = Field(
        description="The size resting at the level.",
        json_schema_extra={"x-widget_config": {"chartDataType": "series"}},
    )
    mark_price: float | None = Field(
        default=None,
        description="The price the exchange marks positions at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    index_price: float | None = Field(
        default=None,
        description="The price of the index the instrument is priced against.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    change_id: int | None = Field(
        default=None,
        description="The revision of the book the level came from.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Change ID",
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

        return from_timestamp(v) if v else None


class DeribitOrderBookFetcher(
    Fetcher[DeribitOrderBookQueryParams, list[DeribitOrderBookData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitOrderBookQueryParams:
        """Transform the query.

        Raises
        ------
        OpenBBError
            If neither a symbol nor an instrument ID was given.
        """
        from openbb_core.app.model.abstract.error import OpenBBError

        query = DeribitOrderBookQueryParams(**params)

        if not query.symbol and query.instrument_id is None:
            raise OpenBBError("Give either a symbol or an instrument ID.")

        return query

    @staticmethod
    async def aextract_data(
        query: DeribitOrderBookQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If none of the instruments published a book.
        """
        from openbb_deribit.utils.client import gather
        from openbb_deribit.utils.helpers import get_perpetual_symbols

        calls: list[tuple[str, dict[str, Any] | None]]

        if query.symbol:
            symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
            perpetuals = await get_perpetual_symbols()
            calls = [
                (
                    "get_order_book",
                    {
                        "instrument_name": perpetuals.get(symbol, symbol),
                        "depth": int(query.depth),
                    },
                )
                for symbol in symbols
            ]
        else:
            calls = [
                (
                    "get_order_book_by_instrument_id",
                    {
                        "instrument_id": query.instrument_id,
                        "depth": int(query.depth),
                    },
                )
            ]

        results = await gather(calls, use_cache=False)
        data = [result for result in results if isinstance(result, dict) and result]

        if not data:
            raise EmptyDataError("Deribit published no book for the query.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitOrderBookQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitOrderBookData]:
        """Transform the data to the model.

        Raises
        ------
        EmptyDataError
            If every book came back with no resting orders.
        """
        records: list[dict] = []

        for book in data:
            context = {
                "symbol": book.get("instrument_name"),
                "timestamp": book.get("timestamp"),
                "mark_price": book.get("mark_price"),
                "index_price": book.get("index_price"),
                "change_id": book.get("change_id"),
            }

            for side in ("bids", "asks"):
                for level, entry in enumerate(book.get(side) or [], start=1):
                    records.append(
                        {
                            **context,
                            "side": side[:-1],
                            "level": level,
                            "price": entry[0],
                            "size": entry[1],
                        }
                    )

        if not records:
            raise EmptyDataError("Deribit published no resting orders for the query.")

        return [DeribitOrderBookData.model_validate(record) for record in records]
