"""FMP Stock Insider Trading fetcher."""


from datetime import date, datetime
from typing import Dict, List, Optional

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.stock_insider_trading import (
    StockInsiderTradingData,
    StockInsiderTradingQueryParams,
)
from pydantic import Field

from openbb_fmp.utils.helpers import create_url, get_data_many


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
    symbol : str]
        The symbol of the company.
    reportingCik : str]
        The CIK of the reporting owner.
    companyCik: str]
        The CIK of the company owner.
    page: int
        The page number to get
    """


class FMPStockInsiderTradingData(Data):
    """FMP Stock Insider Trading data."""

    symbol: str
    filingDate: datetime = Field(alias="filing_date")
    transactionDate: date = Field(alias="transaction_date")
    reportingCik: int = Field(alias="reporting_cik")
    transactionType: str = Field(alias="transaction_type")
    securitiesOwned: int = Field(alias="securities_owned")
    companyCik: int = Field(alias="company_cik")
    reportingName: str = Field(alias="reporting_name")
    typeOfOwner: str = Field(alias="type_of_owner")
    acquistionOrDisposition: str = Field(alias="acquistion_or_disposition")
    formType: str = Field(alias="form_type")
    securitiesTransacted: float = Field(alias="securities_transacted")
    price: float
    securityName: str = Field(alias="security_name")
    link: str


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
        return FMPStockInsiderTradingQueryParams(
            transactionType=query.transactionType,
            symbol=query.symbol,
            reportingCik=query.reportingCik,
            companyCik=query.companyCik,
            page=query.page,
        )

    @staticmethod
    def extract_data(
        query: FMPStockInsiderTradingQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPStockInsiderTradingData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        # This changes the actual type of a pydantic class, but its a quick and clean way to format properly
        query.transactionType = ",".join(query.transactionType)  # type: ignore
        url = create_url(4, "insider-trading", api_key, query)
        return get_data_many(url, FMPStockInsiderTradingData)

    @staticmethod
    def transform_data(
        data: List[FMPStockInsiderTradingData],
    ) -> List[StockInsiderTradingData]:
        return data_transformer(data, StockInsiderTradingData)
