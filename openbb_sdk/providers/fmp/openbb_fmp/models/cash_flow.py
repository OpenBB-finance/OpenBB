"""FMP Cash Flow Statement Fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.cash_flows import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from pydantic import Field, root_validator

from openbb_fmp.utils.helpers import create_url, get_data_many


class FMPCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """FMP Cash Flow Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Cash-Flow-Statement
    """

    cik: Optional[str] = Field(description="Central Index Key (CIK) of the company.")

    @root_validator()
    def check_symbol_or_cik(cls, values):  # pylint: disable=no-self-argument
        if values.get("symbol") is None and values.get("cik") is None:
            raise ValueError("symbol or cik must be provided")
        return values


class FMPCashFlowStatementData(CashFlowStatementData):
    """FMP Cash Flow Statement Data."""

    class Config:
        fields = {
            "currency": "reportedCurrency",
            "filing_date": "fillingDate",
            "accepted_date": "acceptedDate",
            "net_income": "netIncome",
            "depreciation_and_amortization": "depreciationAndAmortization",
            "stock_based_compensation": "stockBasedCompensation",
            "other_non_cash_items": "otherNonCashItems",
            "deferred_income_tax": "deferredIncomeTax",
            "change_in_working_capital": "changeInWorkingCapital",
            "accounts_receivables": "accountsReceivables",
            "inventory": "inventory",
            "accounts_payables": "accountsPayables",
            "other_working_capital": "otherWorkingCapital",
            "net_cash_flow_from_operating_activities": "netCashProvidedByOperatingActivities",
            "investments_in_property_plant_and_equipment": "investmentsInPropertyPlantAndEquipment",
            "acquisitions_net": "acquisitionsNet",
            "purchases_of_investments": "purchasesOfInvestments",
            "sales_maturities_of_investments": "salesMaturitiesOfInvestments",
            "other_investing_activities": "otherInvestingActivites",
            "net_cash_flow_from_investing_activities": "netCashUsedForInvestingActivites",
            "debt_repayment": "debtRepayment",
            "common_stock_issued": "commonStockIssued",
            "common_stock_repurchased": "commonStockRepurchased",
            "dividends_paid": "dividendsPaid",
            "other_financing_activities": "otherFinancingActivites",
            "net_cash_flow_from_financing_activities": "netCashUsedProvidedByFinancingActivities",
            "effect_of_forex_changes_on_cash": "effectOfForexChangesOnCash",
            "net_change_in_cash": "netChangeInCash",
            "cash_at_end_of_period": "cashAtEndOfPeriod",
            "cash_at_beginning_of_period": "cashAtBeginningOfPeriod",
            "operating_cash_flow": "operatingCashFlow",
            "capital_expenditure": "capitalExpenditure",
            "net_cash_flow": "freeCashFlow",
        }

    # Leftovers below
    calendarYear: Optional[int]
    link: Optional[str]
    finalLink: Optional[str]


class FMPCashFlowStatementFetcher(
    Fetcher[
        CashFlowStatementQueryParams,
        CashFlowStatementData,
        FMPCashFlowStatementQueryParams,
        FMPCashFlowStatementData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCashFlowStatementQueryParams:
        return FMPCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPCashFlowStatementData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        query.period = "annual" if query.period == "annually" else "quarter"

        url = create_url(
            3, f"cash-flow-statement/{query.symbol}", api_key, query, ["symbol"]
        )
        return get_data_many(url, FMPCashFlowStatementData, **kwargs)

    @staticmethod
    def transform_data(
        data: List[FMPCashFlowStatementData],
    ) -> List[FMPCashFlowStatementData]:
        return data
