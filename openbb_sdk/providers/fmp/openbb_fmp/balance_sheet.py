"""FMP Balance Sheet Fetcher."""

# IMPORT STANDARD
from datetime import (
    date as dateType,
    datetime,
)
from typing import Dict, List, Literal, Optional

# IMPORT INTERNAL
from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)

# IMPORT THIRD-PARTY
from pydantic import Field, NonNegativeInt, root_validator

from .helpers import create_url, get_data_many


class FMPBalanceSheetQueryParams(QueryParams):
    """FMP Balance Sheet QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Balance-Sheet

    Parameter
    ---------
    symbol : Optional[str]
        The symbol of the company if cik is not provided.
    cik : Optional[str]
        The CIK of the company if symbol is not provided.
    period : Literal["annual", "quarter"]
        The period of the balance sheet. Default is "annual".
    limit : Optional[NonNegativeInt]
        The limit of the balance sheet.
    """

    symbol: Optional[str]
    cik: Optional[str]
    period: Literal["annual", "quarter"] = Field(default="annual")
    limit: Optional[NonNegativeInt]

    @root_validator()
    def check_symbol_or_cik(cls, values):  # pylint: disable=no-self-argument
        if values.get("symbol") is None and values.get("cik") is None:
            raise ValueError("symbol or cik must be provided")
        return values


class FMPBalanceSheetData(Data):
    date: dateType
    symbol: str
    cik: Optional[int]
    reportedCurrency: Optional[str]
    fillingDate: Optional[dateType]
    acceptedDate: Optional[datetime]
    calendarYear: Optional[int]
    period: Optional[str]

    cashAndCashEquivalents: Optional[int]
    shortTermInvestments: Optional[int]
    cashAndShortTermInvestments: Optional[int]
    netReceivables: Optional[int]
    inventory: Optional[int]
    otherCurrentAssets: Optional[int]
    totalCurrentAssets: Optional[int] = Field(alias="current_assets")

    longTermInvestments: Optional[int]
    propertyPlantEquipmentNet: Optional[int]

    goodwill: Optional[int]
    intangibleAssets: Optional[int]
    goodwillAndIntangibleAssets: Optional[int]
    taxAssets: Optional[int]
    otherNonCurrentAssets: Optional[int]

    totalNonCurrentAssets: Optional[int] = Field(alias="noncurrent_assets")
    totalAssets: Optional[int] = Field(alias="assets")

    accountPayables: Optional[int]
    otherCurrentLiabilities: Optional[int]
    deferredRevenue: Optional[int]
    shortTermDebt: Optional[int]
    taxPayables: Optional[int]
    totalCurrentLiabilities: Optional[int] = Field(alias="current_liabilities")

    longTermDebt: Optional[int]
    deferredRevenueNonCurrent: Optional[int]
    deferredTaxLiabilitiesNonCurrent: Optional[int]
    otherNonCurrentLiabilities: Optional[int]
    totalNonCurrentLiabilities: Optional[int] = Field(alias="noncurrent_liabilities")
    totalLiabilities: Optional[int] = Field(alias="liabilities")

    commonStock: Optional[int]
    retainedEarnings: Optional[int]
    accumulatedOtherComprehensiveIncomeLoss: Optional[int]
    othertotalStockholdersEquity: Optional[int]
    totalEquity: Optional[int]
    totalLiabilitiesAndStockholdersEquity: Optional[int]

    # Leftovers below
    totalStockholdersEquity: Optional[int]
    minorityInterest: Optional[int]
    totalLiabilitiesAndTotalEquity: Optional[int]
    totalInvestments: Optional[int]
    netDebt: Optional[int]
    finalLink: Optional[str]


class FMPBalanceSheetFetcher(
    Fetcher[
        BalanceSheetQueryParams,
        BalanceSheetData,
        FMPBalanceSheetQueryParams,
        FMPBalanceSheetData,
    ]
):
    @staticmethod
    def transform_query(
        query: BalanceSheetQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPBalanceSheetQueryParams:
        period = "annual" if query.period == "annually" else "quarter"
        return FMPBalanceSheetQueryParams(
            symbol=query.symbol, period=period, **extra_params if extra_params else {}  # type: ignore
        )

    @staticmethod
    def extract_data(
        query: FMPBalanceSheetQueryParams, credentials: Optional[Dict[str, str]]
    ) -> List[FMPBalanceSheetData]:
        if credentials:
            api_key = credentials.get("fmp_api_key")

        url = create_url(
            3, f"balance-sheet-statement/{query.symbol}", api_key, query, ["symbol"]
        )
        return get_data_many(url, FMPBalanceSheetData)

    @staticmethod
    def transform_data(
        data: List[FMPBalanceSheetData],
    ) -> List[BalanceSheetData]:
        return data_transformer(data, BalanceSheetData)
