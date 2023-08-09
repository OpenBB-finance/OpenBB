"""FMP Cash Flow Statement Growth Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cash_flow_growth import (
    CashFlowStatementGrowthData,
    CashFlowStatementGrowthQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPCashFlowStatementGrowthQueryParams(CashFlowStatementGrowthQueryParams):
    """FMP Cash Flow Statement Growth QueryParams.

    Source: https://site.financialmodelingprep.com/developer/docs/financial-statements-growth-api/
    """


class FMPCashFlowStatementGrowthData(CashFlowStatementGrowthData):
    """FMP Cash Flow Statement Growth Data."""

    class Config:
        fields = {
            "growth_net_income": "growthNetIncome",
            "growth_depreciation_and_amortization": "growthDepreciationAndAmortization",
            "growth_deferred_income_tax": "growthDeferredIncomeTax",
            "growth_stock_based_compensation": "growthStockBasedCompensation",
            "growth_change_in_working_capital": "growthChangeInWorkingCapital",
            "growth_accounts_receivables": "growthAccountsReceivables",
            "growth_inventory": "growthInventory",
            "growth_accounts_payables": "growthAccountsPayables",
            "growth_other_working_capital": "growthOtherWorkingCapital",
            "growth_other_non_cash_items": "growthOtherNonCashItems",
            "growth_net_cash_provided_by_operating_activities": "growthNetCashProvidedByOperatingActivites",
            "growth_investments_in_property_plant_and_equipment": "growthInvestmentsInPropertyPlantAndEquipment",
            "growth_acquisitions_net": "growthAcquisitionsNet",
            "growth_purchases_of_investments": "growthPurchasesOfInvestments",
            "growth_sales_maturities_of_investments": "growthSalesMaturitiesOfInvestments",
            "growth_other_investing_activities": "growthOtherInvestingActivites",
            "growth_net_cash_used_for_investing_activities": "growthNetCashUsedForInvestingActivites",
            "growth_debt_repayment": "growthDebtRepayment",
            "growth_common_stock_issued": "growthCommonStockIssued",
            "growth_common_stock_repurchased": "growthCommonStockRepurchased",
            "growth_dividends_paid": "growthDividendsPaid",
            "growth_other_financing_activities": "growthOtherFinancingActivites",
            "growth_net_cash_used_provided_by_financing_activities": "growthNetCashUsedProvidedByFinancingActivities",
            "growth_effect_of_forex_changes_on_cash": "growthEffectOfForexChangesOnCash",
            "growth_net_change_in_cash": "growthNetChangeInCash",
            "growth_cash_at_end_of_period": "growthCashAtEndOfPeriod",
            "growth_cash_at_beginning_of_period": "growthCashAtBeginningOfPeriod",
            "growth_operating_cash_flow": "growthOperatingCashFlow",
            "growth_capital_expenditure": "growthCapitalExpenditure",
            "growth_free_cash_flow": "growthFreeCashFlow",
        }

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        return datetime.strptime(v, "%Y-%m-%d")


class FMPCashFlowStatementGrowthFetcher(
    Fetcher[
        FMPCashFlowStatementGrowthQueryParams,
        FMPCashFlowStatementGrowthData,
    ]
):
    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FMPCashFlowStatementGrowthQueryParams:
        return FMPCashFlowStatementGrowthQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCashFlowStatementGrowthQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPCashFlowStatementGrowthData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"cash-flow-statement-growth/{query.symbol}", api_key, query, ["symbol"]
        )
        return get_data_many(url, FMPCashFlowStatementGrowthData, **kwargs)

    @staticmethod
    def transform_data(
        data: List[FMPCashFlowStatementGrowthData],
    ) -> List[FMPCashFlowStatementGrowthData]:
        return data
