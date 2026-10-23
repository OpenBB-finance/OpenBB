"""Nasdaq Insider Trading Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.insider_trading import (
    InsiderTradingData,
    InsiderTradingQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT


class NasdaqInsiderTradingQueryParams(InsiderTradingQueryParams):
    """Nasdaq Insider Trading Query.

    Source: https://www.nasdaq.com/market-activity/stocks
    """

    __json_schema_extra__ = {
        "symbol": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }

    limit: int | None = Field(
        default=100, description="The number of insider transactions to return."
    )


class NasdaqInsiderTradingData(InsiderTradingData):
    """Nasdaq Insider Trading Data."""

    shares_held: float | None = Field(
        default=None, description="Shares held by the insider after the transaction."
    )
    url: str | None = Field(
        default=None, description="The Nasdaq profile page for the insider."
    )


class NasdaqInsiderTradingFetcher(
    Fetcher[
        NasdaqInsiderTradingQueryParams,
        list[NasdaqInsiderTradingData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqInsiderTradingQueryParams:
        """Transform the query, defaulting an unset limit."""
        transformed = params.copy()

        if transformed.get("limit") is None:
            transformed["limit"] = 100

        return NasdaqInsiderTradingQueryParams(**transformed)

    @staticmethod
    async def aextract_data(
        query: NasdaqInsiderTradingQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data, rows_from_table

        symbol = query.symbol.upper()
        data = await get_nasdaq_data(
            f"company/{symbol}/insider-trades?limit={query.limit}&type=ALL"
            "&sortColumn=lastDate&sortOrder=DESC"
        )
        rows = rows_from_table((data or {}).get("transactionTable"))

        if not rows:
            raise EmptyDataError(f"No insider trades were found for {symbol}.")

        return [{**row, "symbol": symbol} for row in rows]

    @staticmethod
    def transform_data(
        query: NasdaqInsiderTradingQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqInsiderTradingData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_date, to_number

        results: list[NasdaqInsiderTradingData] = []

        for row in data[: query.limit]:
            url = row.get("url")
            results.append(
                NasdaqInsiderTradingData.model_validate(
                    {
                        "symbol": row["symbol"],
                        "owner_name": row.get("insider"),
                        "owner_title": row.get("relation"),
                        "transaction_date": to_date(row.get("lastDate")),
                        "transaction_type": row.get("transactionType"),
                        "ownership_type": row.get("ownType"),
                        "securities_transacted": to_number(row.get("sharesTraded")),
                        "transaction_price": to_number(row.get("lastPrice")),
                        "shares_held": to_number(row.get("sharesHeld")),
                        "url": f"https://www.nasdaq.com{url}" if url else None,
                    }
                )
            )

        return results
