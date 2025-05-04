"""YFinance Historical Dividends Model."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)


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
        params: Dict[str, Any],
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
        # pylint: disable=import-outside-toplevel
        from curl_adapter import CurlCffiAdapter
        from openbb_core.provider.utils.helpers import get_requests_session
        from yfinance import Ticker

        session = get_requests_session()
        session.mount("https://", CurlCffiAdapter())
        session.mount("http://", CurlCffiAdapter())

        try:
            ticker = Ticker(
                query.symbol,
                session=session,
            ).get_dividends()
            if isinstance(ticker, List) and not ticker or ticker.empty:  # type: ignore
                raise OpenBBError(f"No dividend data found for {query.symbol}")
        except Exception as e:
            raise OpenBBError(f"Error getting data for {query.symbol}: {e}") from e
        ticker.index.name = "ex_dividend_date"  # type: ignore[union-attr]
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
