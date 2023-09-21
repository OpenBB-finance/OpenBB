"""FMP Stocks end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import get_data_many, get_querystring
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_quote import (
    StockQuoteData,
    StockQuoteQueryParams,
)
from pydantic import Field, validator


class FMPStockQuoteQueryParams(StockQuoteQueryParams):
    """FMP Stock end of day Query.

    Source: https://financialmodelingprep.com/developer/docs/#Stock-Historical-Price
    """


class FMPStockQuoteData(StockQuoteData):
    """FMP Stock end of day Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "date": "timestamp",
        }

    symbol: Optional[str] = Field(description="Symbol of the company.")
    name: Optional[str] = Field(description="Name of the company.")
    price: Optional[float] = Field(description="Current trading price of the stock.")
    changes_percentage: Optional[float] = Field(
        description="Change percentage of the stock price."
    )
    change: Optional[float] = Field(description="Change in the stock price.")
    year_high: Optional[float] = Field(
        description="Highest price of the stock in the last 52 weeks."
    )
    year_low: Optional[float] = Field(
        description="Lowest price of the stock in the last 52 weeks."
    )
    market_cap: Optional[float] = Field(description="Market cap of the company.")
    price_avg50: Optional[float] = Field(
        description="50 days average price of the stock."
    )
    price_avg200: Optional[float] = Field(
        description="200 days average price of the stock."
    )
    volume: Optional[int] = Field(
        description="Volume of the stock in the current trading day."
    )
    avg_volume: Optional[int] = Field(
        default=None,
        description="Average volume of the stock in the last 10 trading days.",
    )
    exchange: Optional[str] = Field(description="Exchange the stock is traded on.")
    open: Optional[float] = Field(
        default=None,
        description="Opening price of the stock in the current trading day.",
    )
    previous_close: Optional[float] = Field(
        description="Previous closing price of the stock."
    )
    eps: Optional[float] = Field(description="Earnings per share of the stock.")
    pe: Optional[float] = Field(description="Price earnings ratio of the stock.")
    earnings_announcement: Optional[str] = Field(
        description="Earnings announcement date of the stock."
    )
    shares_outstanding: Optional[int] = Field(
        description="Number of shares outstanding of the stock."
    )

    @validator("timestamp", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FMPStockQuoteFetcher(
    Fetcher[
        FMPStockQuoteQueryParams,
        List[FMPStockQuoteData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockQuoteQueryParams:
        """Transform the query params."""
        return FMPStockQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPStockQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.dict(), ["symbol"])
        url = f"{base_url}/quote/{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPStockQuoteData]:
        """Return the transformed data."""
        return [FMPStockQuoteData.parse_obj(d) for d in data]
