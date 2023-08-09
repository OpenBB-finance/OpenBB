"""FMP Stock Peers fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_peers import (
    StockPeersData,
    StockPeersQueryParams,
)

from openbb_fmp.utils.helpers import create_url, get_data_many

# FMP SPECIFIC FUNCTIONALITY CURRENTLY


class FMPStockPeersQueryParams(StockPeersQueryParams):
    """FMP Stock Peers query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Peers
    """


class FMPStockPeersData(StockPeersData):
    """FMP Stock Peers data."""

    class Config:
        fields = {
            "peers_list": "peersList",
        }


class FMPStockPeersFetcher(
    Fetcher[
        FMPStockPeersQueryParams,
        FMPStockPeersData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockPeersQueryParams:
        return FMPStockPeersQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPStockPeersQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> List[FMPStockPeersData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(4, "stock_peers", api_key, query)
        return get_data_many(url, FMPStockPeersData, **kwargs)

    @staticmethod
    def transform_data(data: List[FMPStockPeersData]) -> List[FMPStockPeersData]:
        return data
