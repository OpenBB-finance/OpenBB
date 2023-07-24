"""FMP Historical Stock Splits fetcher."""


from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer

# IMPORT INTERNAL
from openbb_provider.models.historical_stock_splits import (
    HistoricalStockSplitsData,
    HistoricalStockSplitsQueryParams,
)

# IMPORT THIRD-PARTY
from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPHistoricalStockSplitsQueryParams(HistoricalStockSplitsQueryParams):
    """FMP Historical Stock Splits query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-stock-splits-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class FMPHistoricalStockSplitsData(HistoricalStockSplitsData):
    """FMP Historical Stock Splits data."""


class FMPHistoricalStockSplitsFetcher(
    Fetcher[
        HistoricalStockSplitsQueryParams,
        HistoricalStockSplitsData,
        FMPHistoricalStockSplitsQueryParams,
        FMPHistoricalStockSplitsData,
    ]
):
    @staticmethod
    def transform_query(
        query: HistoricalStockSplitsQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPHistoricalStockSplitsQueryParams:
        return FMPHistoricalStockSplitsQueryParams(symbol=query.symbol)

    @staticmethod
    def extract_data(
        query: FMPHistoricalStockSplitsQueryParams,
        credentials: Optional[Dict[str, str]],
    ) -> List[FMPHistoricalStockSplitsData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(
            3, f"historical-price-full/stock_split/{query.symbol}", api_key
        )
        return get_data_many(url, FMPHistoricalStockSplitsData, "historical")

    @staticmethod
    def transform_data(
        data: List[FMPHistoricalStockSplitsData],
    ) -> List[HistoricalStockSplitsData]:
        return data_transformer(data, HistoricalStockSplitsData)
