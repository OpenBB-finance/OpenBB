"""Key Metrics fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.key_metrics import KeyMetricsData, KeyMetricsQueryParams
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPKeyMetricsQueryParams(KeyMetricsQueryParams):
    """FMP Key Metrics Query.

    Source: https://site.financialmodelingprep.com/developer/docs/company-key-metrics-api/
    """


class FMPKeyMetricsData(KeyMetricsData):
    """FMP Key Metrics Data."""

    class Config:
        fields = {
            "revenue_per_share": "revenuePerShare",
            "net_income_per_share": "netIncomePerShare",
            "operating_cash_flow_per_share": "operatingCashFlowPerShare",
            "free_cash_flow_per_share": "freeCashFlowPerShare",
            "cash_per_share": "cashPerShare",
            "book_value_per_share": "bookValuePerShare",
            "tangible_book_value_per_share": "tangibleBookValuePerShare",
            "shareholders_equity_per_share": "shareholdersEquityPerShare",
            "interest_debt_per_share": "interestDebtPerShare",
            "market_cap": "marketCap",
            "enterprise_value": "enterpriseValue",
            "pe_ratio": "peRatio",
            "price_to_sales_ratio": "priceToSalesRatio",
            "pocf_ratio": "pocfratio",
            "pfcf_ratio": "pfcfRatio",
            "pb_ratio": "pbRatio",
            "ptb_ratio": "ptbRatio",
            "ev_to_sales": "evToSales",
            "enterprise_value_over_ebitda": "enterpriseValueOverEBITDA",
            "ev_to_operating_cash_flow": "evToOperatingCashFlow",
            "ev_to_free_cash_flow": "evToFreeCashFlow",
            "earnings_yield": "earningsYield",
            "free_cash_flow_yield": "freeCashFlowYield",
            "debt_to_equity": "debtToEquity",
            "debt_to_assets": "debtToAssets",
            "net_debt_to_ebitda": "netDebtToEBITDA",
            "current_ratio": "currentRatio",
            "interest_coverage": "interestCoverage",
            "income_quality": "incomeQuality",
            "dividend_yield": "dividendYield",
            "payout_ratio": "payoutRatio",
            "sales_general_and_administrative_to_revenue": "salesGeneralAndAdministrativeToRevenue",
            "research_and_development_to_revenue": "researchAndDdevelopementToRevenue",
            "intangibles_to_total_assets": "intangiblesToTotalAssets",
            "capex_to_operating_cash_flow": "capexToOperatingCashFlow",
            "capex_to_revenue": "capexToRevenue",
            "capex_to_depreciation": "capexToDepreciation",
            "stock_based_compensation_to_revenue": "stockBasedCompensationToRevenue",
            "graham_number": "grahamNumber",
            "return_on_tangible_assets": "returnOnTangibleAssets",
            "graham_net_net": "grahamNetNet",
            "working_capital": "workingCapital",
            "tangible_asset_value": "tangibleAssetValue",
            "net_current_asset_value": "netCurrentAssetValue",
            "invested_capital": "investedCapital",
            "average_receivables": "averageReceivables",
            "average_payables": "averagePayables",
            "average_inventory": "averageInventory",
            "days_sales_outstanding": "daysSalesOutstanding",
            "days_payables_outstanding": "daysPayablesOutstanding",
            "days_of_inventory_on_hand": "daysOfInventoryOnHand",
            "receivables_turnover": "receivablesTurnover",
            "payables_turnover": "payablesTurnover",
            "inventory_turnover": "inventoryTurnover",
            "capex_per_share": "capexPerShare",
        }

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=no-self-argument
        return datetime.strptime(v, "%Y-%m-%d")


class FMPKeyMetricsFetcher(
    Fetcher[
        FMPKeyMetricsQueryParams,
        FMPKeyMetricsData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPKeyMetricsQueryParams:
        return FMPKeyMetricsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPKeyMetricsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPKeyMetricsData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        query.period = "annual" if query.period == "annually" else "quarter"

        url = create_url(
            3, f"key-metrics/{query.symbol}", api_key, query, exclude=["symbol"]
        )
        return get_data_many(url, FMPKeyMetricsData, **kwargs)

    @staticmethod
    def transform_data(data: List[FMPKeyMetricsData]) -> List[FMPKeyMetricsData]:
        return data
