"""FMP Cash Flow Statement Fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.cash_flows import (
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
        """Validate that either a symbol or CIK is provided."""
        if values.get("symbol") is None and values.get("cik") is None:
            raise ValueError("symbol or cik must be provided")
        return values


class FMPCashFlowStatementData(CashFlowStatementData):
    """FMP Cash Flow Statement Data."""

    class Config:
        """Pydantic alias config using fields dict."""

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
            "net_cash_used_for_investing_activities": "netCashUsedForInvestingActivites",
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
            "free_cash_flow": "freeCashFlow",
        }

    # Leftovers below
    calendarYear: Optional[int] = Field(
        description="Calendar Year", alias="calendar_year"
    )
    link: Optional[str] = Field(description="Link")
    finalLink: Optional[str] = Field(description="Final Link", alias="final_link")


class FMPCashFlowStatementFetcher(
    Fetcher[
        FMPCashFlowStatementQueryParams,
        List[FMPCashFlowStatementData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCashFlowStatementQueryParams:
        """Transform the query params."""

        return FMPCashFlowStatementQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"cash-flow-statement/{query.symbol}", api_key, query, ["symbol"]
        )

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPCashFlowStatementData]:
        """Return the transformed data."""

        return [FMPCashFlowStatementData(**d) for d in data]
