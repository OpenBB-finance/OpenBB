"""Intrinio Equity Quote Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_requests,
)
from openbb_intrinio.utils.references import SOURCES
from pydantic import Field, field_validator


class IntrinioEquityQuoteQueryParams(EquityQuoteQueryParams):
    """Intrinio Equity Quote Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_security_realtime_price_v2
    """

    symbol: str = Field(
        description="A Security identifier (Ticker, FIGI, ISIN, CUSIP, Intrinio ID)."
    )
    source: SOURCES = Field(default="iex", description="Source of the data.")


class IntrinioEquityQuoteData(EquityQuoteData):
    """Intrinio Equity Quote Data."""

    __alias_dict__ = {
        "day_low": "low_price",
        "day_high": "high_price",
        "date": "last_time",
    }

    last_price: float = Field(description="Price of the last trade.")
    last_time: datetime = Field(
        description="Date and Time when the last trade occurred.", alias="date"
    )
    last_size: Optional[int] = Field(description="Size of the last trade.")
    bid_price: float = Field(description="Price of the top bid order.")
    bid_size: int = Field(description="Size of the top bid order.")
    ask_price: float = Field(description="Price of the top ask order.")
    ask_size: int = Field(description="Size of the top ask order.")
    open_price: float = Field(description="Open price for the trading day.")
    close_price: Optional[float] = Field(
        default=None, description="Closing price for the trading day (IEX source only)."
    )
    high_price: float = Field(
        description="High Price for the trading day.", alias="day_high"
    )
    low_price: float = Field(
        description="Low Price for the trading day.", alias="day_low"
    )
    exchange_volume: Optional[int] = Field(
        default=None,
        description="Number of shares exchanged during the trading day on the exchange.",
    )
    market_volume: Optional[int] = Field(
        default=None,
        description="Number of shares exchanged during the trading day for the whole market.",
    )
    updated_on: datetime = Field(
        description="Date and Time when the data was last updated."
    )
    source: str = Field(description="Source of the data.")
    listing_venue: Optional[str] = Field(
        default=None,
        description="Listing venue where the trade took place (SIP source only).",
    )
    sales_conditions: Optional[str] = Field(
        default=None,
        description="Indicates any sales condition modifiers associated with the trade.",
    )
    quote_conditions: Optional[str] = Field(
        default=None,
        description="Indicates any quote condition modifiers associated with the trade.",
    )
    market_center_code: Optional[str] = Field(
        default=None, description="Market center character code."
    )
    is_darkpool: Optional[bool] = Field(
        default=None, description="Whether or not the current trade is from a darkpool."
    )
    messages: Optional[List[str]] = Field(
        default=None, description="Messages associated with the endpoint."
    )
    security: Optional[Dict[str, Any]] = Field(
        default=None, description="Security details related to the quote."
    )

    @field_validator("last_time", "updated_on", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return (
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            if v.endswith(("Z", "+00:00"))
            else datetime.fromisoformat(v)
        )


class IntrinioEquityQuoteFetcher(
    Fetcher[
        IntrinioEquityQuoteQueryParams,
        List[IntrinioEquityQuoteData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioEquityQuoteQueryParams:
        """Transform the query params."""
        return IntrinioEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"

        async def callback(response: ClientResponse, _: Any) -> dict:
            """Return the response."""
            if response.status != 200:
                return {}

            response_data = await response.json()
            response_data["symbol"] = response.url.parts[-2]

            return response_data

        urls = [
            f"{base_url}/securities/{s.strip()}/prices/realtime?source={query.source}&api_key={api_key}"
            for s in query.symbol.split(",")
        ]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioEquityQuoteQueryParams, data: dict, **kwargs: Any
    ) -> List[IntrinioEquityQuoteData]:
        """Return the transformed data."""
        return [IntrinioEquityQuoteData.model_validate(d) for d in data]
