"""Key Metrics fetcher."""

# IMPORT STANDARD
from datetime import date as dateType
from typing import Dict, List, Literal, Optional

# IMPORT INTERNAL
from openbb_provider.abstract.data import Data, QueryParams
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.helpers import data_transformer
from openbb_provider.models.key_metrics import KeyMetricsData, KeyMetricsQueryParams

# IMPORT THIRD-PARTY
from pydantic import Field

from .helpers import create_url, get_data_many


class FMPKeyMetricsQueryParams(QueryParams):
    """FMP Key Metrics QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/company-key-metrics-api/

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    period : Literal["quarter", "annual"]
        The period of the key metrics. Default is "annual".
    limit : Optional[int]
        The limit of the key metrics to be returned.
    """

    symbol: str
    period: Literal["quarter", "annual"] = "annual"
    limit: Optional[int] = None


class FMPKeyMetricsData(Data):
    symbol: str
    date: dateType
    period: str
    revenuePerShare: float
    netIncomePerShare: float
    operatingCashFlowPerShare: Optional[float]
    freeCashFlowPerShare: Optional[float]
    cashPerShare: Optional[float]
    bookValuePerShare: Optional[float]
    tangibleBookValuePerShare: Optional[float]
    shareholdersEquityPerShare: Optional[float]
    interestDebtPerShare: Optional[float]
    marketCap: Optional[float]
    enterpriseValue: Optional[float]
    peRatio: Optional[float]
    priceToSalesRatio: Optional[float]
    pocfratio: Optional[float] = Field(alias="pocf_ratio")
    pfcfRatio: Optional[float]
    pbRatio: Optional[float]
    ptbRatio: Optional[float]
    evToSales: Optional[float]
    enterpriseValueOverEBITDA: Optional[float] = Field(
        alias="enterprise_value_over_ebitda"
    )
    evToOperatingCashFlow: Optional[float]
    evToFreeCashFlow: Optional[float]
    earningsYield: Optional[float]
    freeCashFlowYield: Optional[Optional[float]]
    debtToEquity: Optional[float]
    debtToAssets: Optional[float]
    netDebtToEBITDA: Optional[float] = Field(alias="net_debt_to_ebitda")
    currentRatio: Optional[float]
    interestCoverage: Optional[float]
    incomeQuality: Optional[float]
    dividendYield: Optional[Optional[float]]
    payoutRatio: Optional[Optional[float]]
    salesGeneralAndAdministrativeToRevenue: Optional[float]
    researchAndDdevelopementToRevenue: Optional[float] = Field(
        alias="research_and_developement_to_revenue"
    )
    intangiblesToTotalAssets: Optional[float]
    capexToOperatingCashFlow: Optional[float]
    capexToRevenue: Optional[float]
    capexToDepreciation: Optional[float]
    stockBasedCompensationToRevenue: Optional[float]
    grahamNumber: Optional[float]
    roic: Optional[float]
    returnOnTangibleAssets: Optional[float]
    grahamNetNet: Optional[float]
    workingCapital: Optional[float]
    tangibleAssetValue: Optional[float]
    netCurrentAssetValue: Optional[float]
    investedCapital: Optional[float]
    averageReceivables: Optional[float]
    averagePayables: Optional[float]
    averageInventory: Optional[float]
    daysSalesOutstanding: Optional[float]
    daysPayablesOutstanding: Optional[float]
    daysOfInventoryOnHand: Optional[float]
    receivablesTurnover: Optional[float]
    payablesTurnover: Optional[float]
    inventoryTurnover: Optional[float]
    roe: Optional[float]
    capexPerShare: Optional[float]


class FMPKeyMetricsFetcher(
    Fetcher[
        KeyMetricsQueryParams,
        KeyMetricsData,
        FMPKeyMetricsQueryParams,
        FMPKeyMetricsData,
    ]
):
    @staticmethod
    def transform_query(
        query: KeyMetricsQueryParams, extra_params: Optional[Dict] = None
    ) -> FMPKeyMetricsQueryParams:
        return FMPKeyMetricsQueryParams(
            symbol=query.symbol,
            limit=query.limit,
            period="annual" if query.period == "annually" else "quarter",
        )

    @staticmethod
    def extract_data(
        query: FMPKeyMetricsQueryParams, api_key: str
    ) -> List[FMPKeyMetricsData]:
        url = create_url(
            3, f"key-metrics/{query.symbol}", api_key, query, exclude=["symbol"]
        )
        return get_data_many(url, FMPKeyMetricsData)

    @staticmethod
    def transform_data(data: List[FMPKeyMetricsData]) -> List[KeyMetricsData]:
        return data_transformer(data, KeyMetricsData)
