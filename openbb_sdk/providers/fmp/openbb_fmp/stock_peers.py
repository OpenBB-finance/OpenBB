"""FMP Stock Peers fetcher."""

# IMPORT STANDARD
from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer

# IMPORT INTERNAL
from openbb_provider.models.stock_peers import StockPeersData, StockPeersQueryParams

from .helpers import create_url, get_data_many

# FMP SPECIFIC FUNCTIONALITY CURRENTLY


class FMPStockPeersQueryParams(StockPeersQueryParams):
    """FMP Stock Peers query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Peers

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    """


class FMPStockPeersData(StockPeersData):
    """FMP Stock Peers data."""


class FMPStockPeersFetcher(
    Fetcher[
        StockPeersQueryParams,
        StockPeersData,
        FMPStockPeersQueryParams,
        FMPStockPeersData,
    ]
):
    @staticmethod
    def transform_query(
        query: StockPeersQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPStockPeersQueryParams:
        return FMPStockPeersQueryParams(symbol=query.symbol, **extra_params or {})

    @staticmethod
    def extract_data(
        query: FMPStockPeersQueryParams, api_key: str
    ) -> List[FMPStockPeersData]:
        url = create_url(4, "stock_peers", api_key, query)
        return get_data_many(url, FMPStockPeersData)

    @staticmethod
    def transform_data(data: List[FMPStockPeersData]) -> List[StockPeersData]:
        return data_transformer(data, StockPeersData)
