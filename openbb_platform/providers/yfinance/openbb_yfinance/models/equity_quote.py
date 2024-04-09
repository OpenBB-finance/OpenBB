"""YFinance Equity Quote Model."""

# pylint: disable=unused-argument
import asyncio
import warnings
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_quote import (
    EquityQuoteData,
    EquityQuoteQueryParams,
)
from pydantic import Field
from yfinance import Ticker

_warn = warnings.warn


class YFinanceEquityQuoteQueryParams(EquityQuoteQueryParams):
    """YFinance Equity Quote Query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class YFinanceEquityQuoteData(EquityQuoteData):
    """YFinance Equity Quote Data."""

    __alias_dict__ = {
        "name": "longName",
        "asset_type": "quoteType",
        "last_price": "currentPrice",
        "high": "dayHigh",
        "low": "dayLow",
        "prev_close": "previousClose",
        "year_high": "fiftyTwoWeekHigh",
        "year_low": "fiftyTwoWeekLow",
    }

    ma_50d: Optional[float] = Field(
        default=None,
        description="50-day moving average price.",
        alias="fiftyDayAverage",
    )
    ma_200d: Optional[float] = Field(
        default=None,
        description="200-day moving average price.",
        alias="twoHundredDayAverage",
    )
    volume_average: Optional[float] = Field(
        default=None,
        description="Average daily trading volume.",
        alias="averageVolume",
    )
    volume_average_10d: Optional[float] = Field(
        default=None,
        description="Average daily trading volume in the last 10 days.",
        alias="averageDailyVolume10Day",
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency of the price.",
    )


class YFinanceEquityQuoteFetcher(
    Fetcher[YFinanceEquityQuoteQueryParams, List[YFinanceEquityQuoteData]]
):
    """YFinance Equity Quote Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceEquityQuoteQueryParams:
        """Transform the query."""
        return YFinanceEquityQuoteQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceEquityQuoteQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance."""
        symbols = query.symbol.split(",")
        results = []
        fields = [
            "symbol",
            "longName",
            "exchange",
            "quoteType",
            "bid",
            "bidSize",
            "ask",
            "askSize",
            "currentPrice",
            "open",
            "dayHigh",
            "dayLow",
            "previousClose",
            "volume",
            "averageVolume",
            "averageDailyVolume10Day",
            "fiftyTwoWeekHigh",
            "fiftyTwoWeekLow",
            "fiftyDayAverage",
            "twoHundredDayAverage",
            "currency",
        ]

        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            result = {}
            ticker = {}
            try:
                ticker = Ticker(symbol).get_info()
            except Exception as e:
                _warn(f"Error getting data for {symbol}: {e}")
            if ticker:
                for field in fields:
                    if field in ticker:
                        result[field] = ticker.get(field, None)
                if result:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: YFinanceEquityQuoteQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceEquityQuoteData]:
        """Transform the data."""
        return [YFinanceEquityQuoteData.model_validate(d) for d in data]
