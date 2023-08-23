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
        """Pydantic alias config using fields dict."""

        fields = {
            "price_avg50": "priceAvg50",
            "price_avg200": "priceAvg200",
            "date": "timestamp",
        }

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
        return [FMPStockQuoteData(**d) for d in data]
