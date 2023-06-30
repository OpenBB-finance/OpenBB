"""FMP Stock Ownership fetcher."""

# IMPORT STANDARD
from typing import Dict, List, Optional

# IMPORT THIRD-PARTY
from builtin_providers.fmp.helpers import create_url, get_data_many

# IMPORT INTERNAL
from openbb_provider.model.data.stock_ownership import (
    StockOwnershipData,
    StockOwnershipQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer


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

    __name__ = "FMPStockOwnershipQueryParams"


class FMPStockOwnershipData(StockOwnershipData):
    __name__ = "FMPStockOwnershipData"


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
        query: FMPStockOwnershipQueryParams, api_key: str
    ) -> List[FMPStockOwnershipData]:
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
