"""Nasdaq Price Quote Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_nasdaq.utils.constants import CELL_CLICK_SYMBOL, SYMBOL_CHOICES_ENDPOINT


class NasdaqPriceQuoteQueryParams(QueryParams):
    """Nasdaq Price Quote Query.

    Source: https://www.nasdaq.com/market-activity
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }

    symbol: str = Field(description="The ticker symbol, or a comma-separated list.")


class NasdaqPriceQuoteData(Data):
    """Nasdaq Price Quote Data."""

    symbol: str = Field(
        description="The ticker symbol.",
        json_schema_extra={"x-widget_config": CELL_CLICK_SYMBOL},
    )
    name: str | None = Field(default=None, description="The name of the security.")
    asset_class: str | None = Field(
        default=None, description="The Nasdaq asset class of the security."
    )
    last_price: float | None = Field(default=None, description="The last price.")
    change: float | None = Field(
        default=None, description="The change from the previous close."
    )
    change_percent: float | None = Field(
        default=None,
        description="The change from the previous close, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: float | None = Field(default=None, description="The session volume.")
    url: str | None = Field(default=None, description="The Nasdaq quote page.")


class NasdaqPriceQuoteFetcher(
    Fetcher[
        NasdaqPriceQuoteQueryParams,
        list[NasdaqPriceQuoteData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqPriceQuoteQueryParams:
        """Transform the query."""
        return NasdaqPriceQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqPriceQuoteQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import get_basic_quotes

        return await get_basic_quotes(query.symbol.split(","))

    @staticmethod
    def transform_data(
        query: NasdaqPriceQuoteQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqPriceQuoteData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_number, to_percent

        results: list[NasdaqPriceQuoteData] = []

        for row in data:
            ticker = row.get("ticker") or []
            url = row.get("url")
            results.append(
                NasdaqPriceQuoteData.model_validate(
                    {
                        "symbol": str(row.get("key", "")).split("|", 1)[0].upper(),
                        "name": ticker[1] if len(ticker) > 1 else None,
                        "asset_class": row.get("assetclass"),
                        "last_price": to_number(row.get("lastSale")),
                        "change": to_number(row.get("change")),
                        "change_percent": to_percent(row.get("pctChange")),
                        "volume": to_number(row.get("volume")),
                        "url": f"https://www.nasdaq.com{url}" if url else None,
                    }
                )
            )

        return results
