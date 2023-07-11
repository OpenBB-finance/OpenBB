"""FMP Historical Stock Splits fetcher."""

# IMPORT STANDARD
from typing import Dict, List, Optional

# IMPORT THIRD-PARTY
from builtin_providers.fmp.helpers import create_url, get_data_many

# IMPORT INTERNAL
from openbb_provider.model.data.historical_stock_splits import (
    HistoricalStockSplitsData,
    HistoricalStockSplitsQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer


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
        query: FMPHistoricalStockSplitsQueryParams, api_key: str
    ) -> List[FMPHistoricalStockSplitsData]:
        url = create_url(
            3, f"historical-price-full/stock_split/{query.symbol}", api_key
        )
        return get_data_many(url, FMPHistoricalStockSplitsData, "historical")

    @staticmethod
    def transform_data(
        data: List[FMPHistoricalStockSplitsData],
    ) -> List[HistoricalStockSplitsData]:
        return data_transformer(data, HistoricalStockSplitsData)
