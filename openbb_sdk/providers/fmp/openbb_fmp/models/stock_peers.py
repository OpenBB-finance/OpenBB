"""FMP Stock Peers fetcher."""


from typing import Any, Dict, Optional

from openbb_fmp.utils.helpers import create_url, get_data_one
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_peers import (
    StockPeersData,
    StockPeersQueryParams,
)

# FMP SPECIFIC FUNCTIONALITY CURRENTLY


class FMPStockPeersQueryParams(StockPeersQueryParams):
    """FMP Stock Peers query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Peers
    """


class FMPStockPeersData(StockPeersData):
    """FMP Stock Peers data."""


class FMPStockPeersFetcher(
    Fetcher[
        FMPStockPeersQueryParams,
        FMPStockPeersData,
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPStockPeersQueryParams:
        """Transform the query params."""
        return FMPStockPeersQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPStockPeersQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = create_url(4, "stock_peers", api_key, query)

        return get_data_one(url, **kwargs)

    @staticmethod
    def transform_data(data: Dict) -> FMPStockPeersData:
        """Return the transformed data."""
        return FMPStockPeersData.parse_obj(data)
