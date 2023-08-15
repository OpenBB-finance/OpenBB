"""FMP Stocks end of day fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_quote import (
    StockQuoteData,
    StockQuoteQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import get_data_many, get_querystring


class FMPStockQuoteQueryParams(StockQuoteQueryParams):
    """FMP Stock end of day Query.

    Source: https://financialmodelingprep.com/developer/docs/#Stock-Historical-Price
    """


class FMPStockQuoteData(StockQuoteData):
    """FMP Stock end of day Data."""

    class Config:
        fields = {
            "changes_percentage": "changesPercentage",
            "day_low": "dayLow",
            "day_high": "dayHigh",
            "year_high": "yearHigh",
            "year_low": "yearLow",
            "market_cap": "marketCap",
            "price_avg50": "priceAvg50",
            "price_avg200": "priceAvg200",
            "avg_volume": "avgVolume",
            "previous_close": "previousClose",
            "earnings_announcement": "earningsAnnouncement",
            "shares_outstanding": "sharesOutstanding",
            "date": "timestamp",
        }

    @validator("timestamp", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPStockQuoteFetcher(
    Fetcher[
        FMPStockQuoteQueryParams,
        List[FMPStockQuoteData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockQuoteQueryParams:
        return FMPStockQuoteQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPStockQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPStockQuoteData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        base_url = "https://financialmodelingprep.com/api/v3"
        query_str = get_querystring(query.dict(), ["symbol"])
        url = f"{base_url}/quote/{query.symbol}?{query_str}&apikey={api_key}"

        return get_data_many(url, FMPStockQuoteData, **kwargs)

    @staticmethod
    def transform_data(data: List[FMPStockQuoteData]) -> List[StockQuoteData]:
        return [StockQuoteData.parse_obj(d.dict()) for d in data]
