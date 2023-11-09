"""FMP Stocks end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import get_data_many, get_querystring
from openbb_provider.abstract.data import StrictInt
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from pydantic import Field, field_validator


class FMPEquityQuoteQueryParams(EquityQuoteQueryParams):
    """FMP Stock end of day Query.

    Source: https://financialmodelingprep.com/developer/docs/#Stock-Historical-Price
    """


class FMPEquityQuoteData(EquityQuoteData):
    """FMP Stock end of day Data."""

    __alias_dict__ = {
        "price_avg50": "priceAvg50",
        "price_avg200": "priceAvg200",
        "date": "timestamp",
    }

    symbol: Optional[str] = Field(default=None, description="Symbol of the company.")
    name: Optional[str] = Field(default=None, description="Name of the company.")
    price: Optional[float] = Field(
        default=None, description="Current trading price of the stock."
    )
    changes_percentage: Optional[float] = Field(
        default=None, description="Change percentage of the stock price."
    )
    change: Optional[float] = Field(
        default=None, description="Change in the stock price."
    )
    year_high: Optional[float] = Field(
        default=None, description="Highest price of the stock in the last 52 weeks."
    )
    year_low: Optional[float] = Field(
        default=None, description="Lowest price of the stock in the last 52 weeks."
    )
    market_cap: Optional[float] = Field(
        default=None, description="Market cap of the company."
    )
    price_avg50: Optional[float] = Field(
        default=None, description="50 days average price of the stock."
    )
    price_avg200: Optional[StrictInt] = Field(
        default=None, description="200 days average price of the stock."
    )
    volume: Optional[StrictInt] = Field(
        default=None,
        description="Volume of the stock in the current trading day.",
    )
    avg_volume: Optional[StrictInt] = Field(
        default=None,
        description="Average volume of the stock in the last 10 trading days.",
    )
    exchange: Optional[str] = Field(
        default=None, description="Exchange the stock is traded on."
    )
    open: Optional[float] = Field(
        default=None,
        description="Opening price of the stock in the current trading day.",
    )
    previous_close: Optional[float] = Field(
        default=None, description="Previous closing price of the stock."
    )
    eps: Optional[float] = Field(
        default=None, description="Earnings per share of the stock."
    )
    pe: Optional[float] = Field(
        default=None, description="Price earnings ratio of the stock."
    )
    earnings_announcement: Optional[str] = Field(
        default=None, description="Earnings announcement date of the stock."
    )
    shares_outstanding: Optional[StrictInt] = Field(
        default=None, description="Number of shares outstanding of the stock."
    )

    @field_validator("timestamp", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d")


class FMPEquityQuoteFetcher(
    Fetcher[
        FMPEquityQuoteQueryParams,
        List[FMPEquityQuoteData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPEquityQuoteQueryParams:
        """Transform the query params."""
        return FMPEquityQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.model_dump(), ["symbol"])
        url = f"{base_url}/quote/{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPEquityQuoteQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPEquityQuoteData]:
        """Return the transformed data."""
        return [FMPEquityQuoteData.model_validate(d) for d in data]
