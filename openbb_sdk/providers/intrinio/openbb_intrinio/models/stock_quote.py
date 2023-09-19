"""Intrinio Stock Quote fetcher."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_intrinio.utils.helpers import get_data_one
from openbb_intrinio.utils.references import SOURCES
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_quote import (
    StockQuoteData,
    StockQuoteQueryParams,
)
from pydantic import Field, validator


class IntrinioStockQuoteQueryParams(StockQuoteQueryParams):
    """Intrinio Stock Quote Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_security_realtime_price_v2
    """

    symbol: str = Field(
        description="A Security identifier (Ticker, FIGI, ISIN, CUSIP, Intrinio ID)."
    )
    source: SOURCES = Field(default="iex", description="Source of the data.")


class IntrinioStockQuoteData(StockQuoteData):
    """Intrinio Stock Quote Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "day_low": "low_price",
            "day_high": "high_price",
            "date": "last_time",
        }

    last_price: float = Field(description="Price of the last trade.")
    last_time: datetime = Field(
        description="Date and Time when the last trade occurred."
    )
    last_size: int = Field(description="Size of the last trade.")
    bid_price: float = Field(description="Price of the top bid order.")
    bid_size: int = Field(description="Size of the top bid order.")
    ask_price: float = Field(description="Price of the top ask order.")
    ask_size: int = Field(description="Size of the top ask order.")
    open_price: float = Field(description="Open price for the trading day.")
    close_price: Optional[float] = Field(
        description="Closing price for the trading day (IEX source only)."
    )
    high_price: float = Field(description="High Price for the trading day.")
    low_price: float = Field(description="Low Price for the trading day.")
    exchange_volume: Optional[int] = Field(
        description="Number of shares exchanged during the trading day on the exchange."
    )
    market_volume: Optional[int] = Field(
        description="Number of shares exchanged during the trading day for the whole market."
    )
    updated_on: datetime = Field(
        description="Date and Time when the data was last updated."
    )
    source: str = Field(description="Source of the data.")
    listing_venue: Optional[str] = Field(
        description="Listing venue where the trade took place (SIP source only)."
    )
    sales_conditions: Optional[str] = Field(
        description="Indicates any sales condition modifiers associated with the trade."
    )
    quote_conditions: Optional[str] = Field(
        description="Indicates any quote condition modifiers associated with the trade."
    )
    market_center_code: Optional[str] = Field(
        description="Market center character code."
    )
    is_darkpool: Optional[bool] = Field(
        description="Whether or not the current trade is from a darkpool."
    )
    messages: Optional[List[str]] = Field(
        description="Messages associated with the endpoint."
    )
    security: Optional[Dict[str, Any]] = Field(
        description="Security details related to the quote."
    )

    @validator("last_time", "updated_on", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return (
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            if v.endswith(("Z", "+00:00"))
            else datetime.fromisoformat(v)
        )


class IntrinioStockQuoteFetcher(
    Fetcher[
        IntrinioStockQuoteQueryParams,
        IntrinioStockQuoteData,
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioStockQuoteQueryParams:
        """Transform the query params."""
        return IntrinioStockQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioStockQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com"
        url = f"{base_url}/securities/{query.symbol}/prices/realtime?source={query.source}&api_key={api_key}"

        return get_data_one(url, **kwargs)

    @staticmethod
    def transform_data(data: Dict) -> IntrinioStockQuoteData:
        """Return the transformed data."""
        return IntrinioStockQuoteData.parse_obj(data)
