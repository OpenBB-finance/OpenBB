"""FMP Stock Peers fetcher."""

# IMPORT STANDARD
from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer

# IMPORT INTERNAL
from openbb_provider.models.stock_peers import StockPeersData, StockPeersQueryParams

from .helpers import get_data_many

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
        base_url = "https://financialmodelingprep.com/api/v4"
        url = f"{base_url}/stock_peers?symbol={query.symbol}&apikey={api_key}"
        return get_data_many(url, FMPStockPeersData, "peersList")

    @staticmethod
    def transform_data(data: List[FMPStockPeersData]) -> List[StockPeersData]:
        return data_transformer(data, StockPeersData)
