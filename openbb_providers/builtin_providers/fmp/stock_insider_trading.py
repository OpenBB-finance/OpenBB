"""FMP Stock Insider Trading fetcher."""

# IMPORT STANDARD
from typing import Dict, List, Optional

# IMPORT THIRD-PARTY
from builtin_providers.fmp.helpers import create_url, get_data_many

# IMPORT INTERNAL
from openbb_provider.model.data.stock_insider_trading import (
    StockInsiderTradingData,
    StockInsiderTradingQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher
from openbb_provider.provider.provider_helpers import data_transformer


class FMPStockInsiderTradingQueryParams(StockInsiderTradingQueryParams):
    """FMP Stock Insider Trading query.

    Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Insider-Trading

    Parameter
    ---------
    transactionType : List[TransactionTypes]
        The type of the transaction. Possible values are:
        A-Award, C-Conversion, D-Return, E-ExpireShort, F-InKind, G-Gift, H-ExpireLong
        I-Discretionary, J-Other, L-Small, M-Exempt, O-OutOfTheMoneym P-Purchase
        S-Sale, U-Tender, W-Will, X-InTheMoney, Z-Trust
    symbol : Optional[str]
        The symbol of the company.
    reportingCik : Optional[str]
        The CIK of the reporting owner.
    companyCik: Optional[str]
        The CIK of the company owner.
    page: int
        The page number to get
    """

    __name__ = "FMPStockInsiderTradingQueryParams"


class FMPStockInsiderTradingData(StockInsiderTradingData):
    __name__ = "FMPStockInsiderTradingData"


class FMPStockInsiderTradingFetcher(
    Fetcher[
        StockInsiderTradingQueryParams,
        StockInsiderTradingData,
        FMPStockInsiderTradingQueryParams,
        FMPStockInsiderTradingData,
    ]
):
    @staticmethod
    def transform_query(
        query: StockInsiderTradingQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPStockInsiderTradingQueryParams:
        return FMPStockInsiderTradingQueryParams.parse_obj(query)

    @staticmethod
    def extract_data(
        query: FMPStockInsiderTradingQueryParams, api_key: str
    ) -> List[FMPStockInsiderTradingData]:
        # This changes the actual type of a pydantic class, but its a quick and clean way to format properly
        query.transactionType = ",".join(query.transactionType)  # type: ignore
        url = create_url(4, "insider-trading", api_key, query)
        return get_data_many(url, FMPStockInsiderTradingData)

    @staticmethod
    def transform_data(
        data: List[FMPStockInsiderTradingData],
    ) -> List[StockInsiderTradingData]:
        return data_transformer(data, StockInsiderTradingData)
