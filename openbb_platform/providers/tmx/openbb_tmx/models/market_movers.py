"""TMX Market Movers Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.market_movers import (
    MarketMoversData,
    MarketMoversQueryParams,
)
from pydantic import Field

from openbb_tmx.utils.choices import literal_choices

EXCHANGES = {
    "tsx": "TSX",
    "tsxv": "TSXV",
}

SORT_ORDERS = {
    "gainers": "desc",
    "losers": "asc",
}


class TmxMarketMoversQueryParams(MarketMoversQueryParams):
    """TMX Market Movers Query."""

    __json_schema_extra__ = {
        "exchange": {
            "x-widget_config": {
                "options": literal_choices(
                    ("tsx", "tsxv"),
                    tsx="Toronto Stock Exchange",
                    tsxv="TSX Venture Exchange",
                )
            }
        },
        "category": {
            "x-widget_config": {"options": literal_choices(("gainers", "losers"))}
        },
    }

    exchange: Literal["tsx", "tsxv"] = Field(
        default="tsx",
        description="The exchange to rank.",
    )
    category: Literal["gainers", "losers"] = Field(
        default="gainers",
        description="The direction to rank by.",
    )
    limit: int = Field(default=25, description="The number of movers to return.")
    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk response cache. Set to False to bypass.",
    )


class TmxMarketMoversData(MarketMoversData):
    """TMX Market Movers Data."""

    price: float | None = Field(
        default=None, description="The last price of the ticker."
    )
    change: float | None = Field(default=None, description="The change in price.")
    change_percent: float | None = Field(
        default=None,
        description="The change in percent.",
    )
    open: float | None = Field(default=None, description="The session open price.")
    high: float | None = Field(default=None, description="The session high price.")
    low: float | None = Field(default=None, description="The session low price.")
    volume: int | None = Field(default=None, description="The session share volume.")
    trade_volume: int | None = Field(
        default=None, description="The number of trades in the session."
    )
    week_52_high: float | None = Field(
        default=None, description="The fifty-two week high."
    )
    week_52_low: float | None = Field(
        default=None, description="The fifty-two week low."
    )
    exchange: str | None = Field(
        default=None, description="The exchange the ticker trades on."
    )


class TmxMarketMoversFetcher(
    Fetcher[TmxMarketMoversQueryParams, list[TmxMarketMoversData]]
):
    """TMX Market Movers Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxMarketMoversQueryParams:
        """Transform the query."""
        return TmxMarketMoversQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxMarketMoversQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request

        response = await amake_gql_request(
            "getMarketMovers",
            gql.MARKET_MOVERS,
            {
                "sortOrder": SORT_ORDERS[query.category],
                "statExchange": EXCHANGES[query.exchange],
                "limit": query.limit,
            },
            use_cache=query.use_cache,
        )
        results = (response or {}).get("getMarketMovers") or []

        if not results:
            raise EmptyDataError("No market movers were returned.")

        return results

    @staticmethod
    def transform_data(
        query: TmxMarketMoversQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxMarketMoversData]:
        """Transform the data and validate the model."""
        return [
            TmxMarketMoversData.model_validate(
                {
                    "symbol": d.get("symbol"),
                    "name": d.get("name"),
                    "price": d.get("price"),
                    "change": d.get("priceChange"),
                    "change_percent": (
                        d["percentChange"] / 100
                        if d.get("percentChange") is not None
                        else None
                    ),
                    "open": d.get("open"),
                    "high": d.get("high"),
                    "low": d.get("low"),
                    "volume": d.get("volume"),
                    "trade_volume": d.get("tradeVolume"),
                    "week_52_high": d.get("weeks52high"),
                    "week_52_low": d.get("weeks52low"),
                    "exchange": d.get("exchangeCode"),
                }
            )
            for d in data
        ]
