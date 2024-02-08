"""YFinance Historical Dividends Model."""

# pylint: disable=unused-argument
import warnings
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from yfinance import Ticker

_warn = warnings.warn


class YFinanceHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """YFinance Historical Dividends Query."""


class YFinanceHistoricalDividendsData(HistoricalDividendsData):
    """YFinance Historical Dividends Data. All data is split-adjusted."""


class YFinanceHistoricalDividendsFetcher(
    Fetcher[
        YFinanceHistoricalDividendsQueryParams, List[YFinanceHistoricalDividendsData]
    ]
):
    """YFinance Historical Dividends Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> YFinanceHistoricalDividendsQueryParams:
        """Transform the query."""
        return YFinanceHistoricalDividendsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceHistoricalDividendsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance."""
        symbols = query.symbol.split(",")
        symbol = symbols[0]
        if len(symbols) > 1:
            _warn(f"{QUERY_DESCRIPTIONS.get('symbol_list_warning', '')} {symbol}")
        try:
            ticker = Ticker(symbol).get_dividends()
            if isinstance(ticker, List) and not ticker or ticker.empty:  # type: ignore
                raise ValueError(f"No dividend data found for {symbol}")
        except Exception as e:
            raise RuntimeError(f"Error getting data for {symbol}: {e}") from e
        ticker.index.name = "ex_dividend_date"
        ticker.name = "amount"  # type: ignore
        if query.start_date is not None:
            ticker = ticker[ticker.index.astype(str) >= query.start_date.strftime("%Y-%m-%d")]  # type: ignore
        if query.end_date is not None:
            ticker = ticker[ticker.index.astype(str) <= query.end_date.strftime("%Y-%m-%d")]  # type: ignore
        dividends = ticker.reset_index().to_dict("records")  # type: ignore

        return dividends

    @staticmethod
    def transform_data(
        query: YFinanceHistoricalDividendsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceHistoricalDividendsData]:
        """Transform the data."""
        return [YFinanceHistoricalDividendsData.model_validate(d) for d in data]
