"""FMP Balance Sheet Fetcher."""

# IMPORT STANDARD
from datetime import (
    date as dateType,
    datetime,
)
from typing import Dict, List, Literal, Optional

# IMPORT INTERNAL
from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.balance_sheet import (
    BalanceSheetData,
    BalanceSheetQueryParams,
)
from openbb_provider.provider.abstract.fetcher import Fetcher

# IMPORT THIRD-PARTY
from pydantic import Field, NonNegativeInt, root_validator

from openbb_fmp.helpers import create_url, get_data_many


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
    totalCurrentAssets: Optional[int]
    propertyPlantEquipmentNet: Optional[int]
    goodwill: Optional[int]
    intangibleAssets: Optional[int]
    goodwillAndIntangibleAssets: Optional[int]
    longTermInvestments: Optional[int]
    taxAssets: Optional[int]
    otherNonCurrentAssets: Optional[int]
    totalNonCurrentAssets: Optional[int]
    otherAssets: Optional[int]
    totalAssets: Optional[int]
    accountPayables: Optional[int]
    shortTermDebt: Optional[int]
    taxPayables: Optional[int]
    deferredRevenue: Optional[int]
    otherCurrentLiabilities: Optional[int]
    totalCurrentLiabilities: Optional[int]
    longTermDebt: Optional[int]
    deferredRevenueNonCurrent: Optional[int]
    deferredTaxLiabilitiesNonCurrent: Optional[int]
    otherNonCurrentLiabilities: Optional[int]
    totalNonCurrentLiabilities: Optional[int]
    otherLiabilities: Optional[int]
    capitalLeaseObligations: Optional[int]
    totalLiabilities: Optional[int]
    preferredStock: Optional[int]
    commonStock: Optional[int]
    retainedEarnings: Optional[int]
    accumulatedOtherComprehensiveIncomeLoss: Optional[int]
    othertotalStockholdersEquity: Optional[int]
    totalStockholdersEquity: Optional[int]
    totalLiabilitiesAndStockholdersEquity: Optional[int]
    minorityInterest: Optional[int]
    totalEquity: Optional[int]
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
        query: FMPBalanceSheetQueryParams, api_key: str
    ) -> List[FMPBalanceSheetData]:
        url = create_url(
            3, f"balance-sheet-statement/{query.symbol}", api_key, query, ["symbol"]
        )
        return get_data_many(url, FMPBalanceSheetData)

    @staticmethod
    def transform_data(
        data: List[FMPBalanceSheetData],
    ) -> List[BalanceSheetData]:
        final_items = []
        for item in data:
            tot_se = item.totalStockholdersEquity
            minority = item.minorityInterest
            parent: Optional[int] = None
            if tot_se:
                if tot_se is None:
                    pass
                elif minority is None:
                    parent = tot_se
                else:
                    parent = tot_se - minority

            final = BalanceSheetData(
                date=item.date,
                # symbol=item.symbol,
                # currency=item.reportedCurrency,
                cik=item.cik,
                # period=item.period,
                assets=item.totalAssets,
                current_assets=item.totalCurrentAssets,
                current_liabilities=item.totalCurrentLiabilities,
                equity=item.totalStockholdersEquity,
                equity_attributable_to_noncontrolling_interest=item.minorityInterest,
                equity_attributable_to_parent=parent,
                liabilities=item.totalLiabilities,
                liabilities_and_equity=item.totalLiabilitiesAndTotalEquity,
                noncurrent_assets=item.totalNonCurrentAssets,
                noncurrent_liabilities=item.totalNonCurrentLiabilities,
            )
            final_items.append(final)
        return final_items
