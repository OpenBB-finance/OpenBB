"""FMP Stock Splits Calendar fetcher."""


from datetime import date
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.stock_splits import (
    StockSplitCalendarData,
    StockSplitCalendarQueryParams,
)

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPStockSplitCalendarQueryParams(StockSplitCalendarQueryParams):
    """FMP Stock Split Calendar query.

    Source: https://site.financialmodelingprep.com/developer/docs/stock-split-calendar-api/
    """


class FMPStockSplitCalendarData(StockSplitCalendarData):
    """FMP Stock Split Calendar data."""


class FMPStockSplitCalendarFetcher(
    Fetcher[
        StockSplitCalendarQueryParams,
        List[StockSplitCalendarData],
        FMPStockSplitCalendarQueryParams,
        List[FMPStockSplitCalendarData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockSplitCalendarQueryParams:
        today = date.today()
        start_date = params.pop("start_date", today)
        end_date = params.pop("end_date", today)
        return FMPStockSplitCalendarQueryParams(
            **params, start_date=start_date, end_date=end_date
        )

    @staticmethod
    def extract_data(
        query: FMPStockSplitCalendarQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPStockSplitCalendarData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        query_str = f"from={query.start_date}&to={query.end_date}"
        url = create_url(3, f"stock_split_calendar?{query_str}", api_key)
        return get_data_many(url, FMPStockSplitCalendarData)

    @staticmethod
    def transform_data(
        data: List[FMPStockSplitCalendarData],
    ) -> List[FMPStockSplitCalendarData]:
        return data
