"""FMP Financial Ratios Fetcher."""


from typing import Any, Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.base import FinancialStatementQueryParams
from openbb_provider.standard_models.financial_ratios import FinancialRatiosData

from openbb_fmp.utils.helpers import get_data_many

PeriodType = Literal["annual", "quarter"]


class FMPFinancialRatiosQueryParams(FinancialStatementQueryParams):
    """FMP Financial Ratios QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Company-Financial-Ratios

    Symbol must be provided.
    """


class FMPFinancialRatiosData(FinancialRatiosData):
    """FMP Financial Ratios Data."""

    class Config:
        fields = {
            "current_ratio": "currentRatio",
            "quick_ratio": "quickRatio",
            "cash_ratio": "cashRatio",
            "days_of_sales_outstanding": "daysOfSalesOutstanding",
            "days_of_inventory_outstanding": "daysOfInventoryOutstanding",
            "operating_cycle": "operatingCycle",
            "days_of_payables_outstanding": "daysOfPayablesOutstanding",
            "cash_conversion_cycle": "cashConversionCycle",
            "gross_profit_margin": "grossProfitMargin",
            "operating_profit_margin": "operatingProfitMargin",
            "pretax_profit_margin": "pretaxProfitMargin",
            "net_profit_margin": "netProfitMargin",
            "effective_tax_rate": "effectiveTaxRate",
            "return_on_assets": "returnOnAssets",
            "return_on_equity": "returnOnEquity",
            "return_on_capital_employed": "returnOnCapitalEmployed",
            "net_income_per_ebt": "netIncomePerEBT",
            "ebt_per_ebit": "ebtPerEbit",
            "ebit_per_revenue": "ebitPerRevenue",
            "debt_ratio": "debtRatio",
            "debt_equity_ratio": "debtEquityRatio",
            "long_term_debt_to_capitalization": "longTermDebtToCapitalization",
            "total_debt_to_capitalization": "totalDebtToCapitalization",
            "interest_coverage": "interestCoverage",
            "cash_flow_to_debt_ratio": "cashFlowToDebtRatio",
            "company_equity_multiplier": "companyEquityMultiplier",
            "receivables_turnover": "receivablesTurnover",
            "payables_turnover": "payablesTurnover",
            "inventory_turnover": "inventoryTurnover",
            "fixed_asset_turnover": "fixedAssetTurnover",
            "asset_turnover": "assetTurnover",
            "operating_cash_flow_per_share": "operatingCashFlowPerShare",
            "free_cash_flow_per_share": "freeCashFlowPerShare",
            "cash_per_share": "cashPerShare",
            "payout_ratio": "payoutRatio",
            "operating_cash_flow_sales_ratio": "operatingCashFlowSalesRatio",
            "free_cash_flow_operating_cash_flow_ratio": "freeCashFlowOperatingCashFlowRatio",
            "cash_flow_coverage_ratios": "cashFlowCoverageRatios",
            "short_term_coverage_ratios": "shortTermCoverageRatios",
            "capital_expenditure_coverage_ratio": "capitalExpenditureCoverageRatio",
            "dividend_paid_and_capex_coverage_ratio": "dividendPaidAndCapexCoverageRatio",
            "dividend_payout_ratio": "dividendPayoutRatio",
            "price_book_value_ratio": "priceBookValueRatio",
            "price_to_book_ratio": "priceToBookRatio",
            "price_to_sales_ratio": "priceToSalesRatio",
            "price_earnings_ratio": "priceEarningsRatio",
            "price_to_free_cash_flows_ratio": "priceToFreeCashFlowsRatio",
            "price_to_operating_cash_flows_ratio": "priceToOperatingCashFlowsRatio",
            "price_cash_flow_ratio": "priceCashFlowRatio",
            "price_earnings_to_growth_ratio": "priceEarningsToGrowthRatio",
            "price_sales_ratio": "priceSalesRatio",
            "dividend_yield": "dividendYield",
            "enterprise_value_multiple": "enterpriseValueMultiple",
            "price_fair_value": "priceFairValue",
        }


class FMPFinancialRatiosFetcher(
    Fetcher[
        FMPFinancialRatiosQueryParams,
        List[FMPFinancialRatiosData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPFinancialRatiosQueryParams:
        return FMPFinancialRatiosQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPFinancialRatiosQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPFinancialRatiosData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        query.period = "annual" if query.period == "annually" else "quarter"
        base_url = "https://financialmodelingprep.com/api/v3"

        url = (
            f"{base_url}/ratios/{query.symbol}?"
            f"period={query.period}&limit={query.limit}&apikey={api_key}"
        )

        return get_data_many(url, FMPFinancialRatiosData, **kwargs)

    @staticmethod
    def transform_data(
        data: List[FMPFinancialRatiosData],
    ) -> List[FinancialRatiosData]:
        return [FinancialRatiosData.parse_obj(d.dict()) for d in data]
