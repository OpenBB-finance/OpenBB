"""FMP Stock Ownership fetcher."""

# IMPORT STANDARD
from typing import Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer

# IMPORT INTERNAL
from openbb_provider.models.stock_ownership import (
    StockOwnershipData,
    StockOwnershipQueryParams,
)

# IMPORT THIRD-PARTY
from .helpers import create_url, get_data_many


class FMPStockOwnershipQueryParams(StockOwnershipQueryParams):
    """FMP Stock Ownership query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Ownership-by-Holders

    Parameter
    ---------
    symbol : string
        The symbol of the company.
    page : int
        The page number to get
    date : date
        The CIK of the company owner.
    """


class FMPStockOwnershipData(StockOwnershipData):
    """FMP Stock Ownership data."""


class FMPStockOwnershipFetcher(
    Fetcher[
        StockOwnershipQueryParams,
        StockOwnershipData,
        FMPStockOwnershipQueryParams,
        FMPStockOwnershipData,
    ]
):
    @staticmethod
    def transform_query(
        query: StockOwnershipQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPStockOwnershipQueryParams:
        return FMPStockOwnershipQueryParams.parse_obj(query)

    @staticmethod
    def extract_data(
        query: FMPStockOwnershipQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPStockOwnershipData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(
            4,
            "institutional-ownership/institutional-holders/symbol-ownership-percent",
            api_key,
            query,
        )
        return get_data_many(url, FMPStockOwnershipData)

    @staticmethod
    def transform_data(data: List[FMPStockOwnershipData]) -> List[StockOwnershipData]:
        return data_transformer(data, StockOwnershipData)
