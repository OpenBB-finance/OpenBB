"""FMP Stock Splits Calendar fetcher."""


from datetime import date
from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.stock_splits import (
    StockSplitCalendarData,
    StockSplitCalendarQueryParams,
)

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPStockSplitCalendarQueryParams(StockSplitCalendarQueryParams):
    """FMP Stock Split Calendar query.

    Source: https://site.financialmodelingprep.com/developer/docs/stock-split-calendar-api/

    Parameter
    ---------
    start_date : date
        The start date of the stock splits from which to retrieve the data.
    end_date : date
        The end date of the stock splits up to which to retrieve the data.
    """

    start_date: date
    end_date: date


class FMPStockSplitCalendarData(StockSplitCalendarData):
    """FMP Stock Split Calendar data."""


class FMPStockSplitCalendarFetcher(
    Fetcher[
        StockSplitCalendarQueryParams,
        StockSplitCalendarData,
        FMPStockSplitCalendarQueryParams,
        FMPStockSplitCalendarData,
    ]
):
    @staticmethod
    def transform_query(
        query: StockSplitCalendarQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPStockSplitCalendarQueryParams:
        now = date.today()
        start_date = query.start_date if query.start_date else now
        end_date = query.end_date if query.end_date else now
        return FMPStockSplitCalendarQueryParams(
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def extract_data(
        query: FMPStockSplitCalendarQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPStockSplitCalendarData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        query_str = f"from={query.start_date}&to={query.end_date}"
        url = create_url(3, f"stock_split_calendar?{query_str}", api_key)
        return get_data_many(url, FMPStockSplitCalendarData)

    @staticmethod
    def transform_data(
        data: List[FMPStockSplitCalendarData],
    ) -> List[StockSplitCalendarData]:
        return data_transformer(data, StockSplitCalendarData)
