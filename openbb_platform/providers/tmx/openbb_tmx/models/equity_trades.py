"""TMX Equity Trades Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class TmxEquityTradesQueryParams(QueryParams):
    """TMX Equity Trades Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: int = Field(
        default=50,
        description="The number of trades to return, most recent first.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk response cache. Set to False to bypass.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert the symbol to uppercase."""
        return v.upper()


class TmxEquityTradesData(Data):
    """TMX Equity Trades Data."""

    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    price: float | None = Field(
        default=None, description="The price the trade printed at."
    )
    volume: int | None = Field(default=None, description="The number of shares traded.")
    exchange: str | None = Field(
        default=None, description="The marketplace the trade printed on."
    )
    buyer_id: str | None = Field(
        default=None, description="The broker number on the buy side."
    )
    buyer_name: str | None = Field(
        default=None, description="The broker on the buy side."
    )
    seller_id: str | None = Field(
        default=None, description="The broker number on the sell side."
    )
    seller_name: str | None = Field(
        default=None, description="The broker on the sell side."
    )


class TmxEquityTradesFetcher(
    Fetcher[TmxEquityTradesQueryParams, list[TmxEquityTradesData]]
):
    """TMX Equity Trades Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEquityTradesQueryParams:
        """Transform the query."""
        return TmxEquityTradesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEquityTradesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        import asyncio

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import normalize_symbol

        results: list[dict] = []

        async def create_task(symbol: str) -> None:
            """Fetch the most recent trades for a single symbol."""
            symbol = normalize_symbol(symbol)
            response = await amake_gql_request(
                "getCompanyMostRecentTrades",
                gql.MOST_RECENT_TRADES,
                {"symbol": symbol, "limit": query.limit},
                symbol=symbol,
                use_cache=query.use_cache,
            )
            trades = (response or {}).get("getCompanyMostRecentTrades") or []
            results.extend({"symbol": symbol, **trade} for trade in trades)

        await asyncio.gather(*(create_task(s) for s in query.symbol.split(",")))

        if not results:
            raise EmptyDataError(f"No trades were returned for {query.symbol}.")

        return results

    @staticmethod
    def transform_data(
        query: TmxEquityTradesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxEquityTradesData]:
        """Transform the data and validate the model."""
        return [
            TmxEquityTradesData.model_validate(
                {
                    "date": d.get("datetime"),
                    "symbol": d.get("symbol"),
                    "price": d.get("price"),
                    "volume": d.get("volume"),
                    "exchange": d.get("exchangeCode"),
                    "buyer_id": d.get("buyerId"),
                    "buyer_name": d.get("buyerName"),
                    "seller_id": d.get("sellerId"),
                    "seller_name": d.get("sellerName"),
                }
            )
            for d in sorted(data, key=lambda d: d.get("datetime") or "", reverse=True)
        ]
