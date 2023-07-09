"""FMP Stock Splits Calendar fetcher."""

# IMPORT STANDARD
from datetime import date
from typing import Dict, List, Optional

# IMPORT INTERNAL
from openbb_provider.model.data.stock_splits import (
    StockSplitCalendarData,
    StockSplitCalendarQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer

# IMPORT THIRD-PARTY
from builtin_providers.fmp.helpers import create_url, get_data_many


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
        return FMPStockSplitCalendarQueryParams(
            start_date=query.start_date,
            end_date=query.end_date,
        )

    @staticmethod
    def extract_data(
        query: FMPStockSplitCalendarQueryParams, api_key: str
    ) -> List[FMPStockSplitCalendarData]:
        query_str = f"from={query.start_date}&to={query.end_date}"
        url = create_url(3, f"stock_split_calendar?{query_str}", api_key)
        return get_data_many(url, FMPStockSplitCalendarData)

    @staticmethod
    def transform_data(
        data: List[FMPStockSplitCalendarData],
    ) -> List[StockSplitCalendarData]:
        return data_transformer(data, StockSplitCalendarData)
