"""FMP Cash Flow Statement Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import Field, model_validator


class FMPCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """FMP Cash Flow Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Cash-Flow-Statement
    """

    period: Optional[Literal["annual", "quarter"]] = Field(
        default="quarter",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )


class FMPCashFlowStatementData(CashFlowStatementData):
    """FMP Cash Flow Statement Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_period": "period",
        "fiscal_year": "calendarYear",
        "filing_date": "fillingDate",
        "accepted_date": "acceptedDate",
        "reported_currency": "reportedCurrency",
        "net_income": "netIncome",
        "depreciation_and_amortization": "depreciationAndAmortization",
        "deferred_income_tax": "deferredIncomeTax",
        "stock_based_compensation": "stockBasedCompensation",
        "change_in_working_capital": "changeInWorkingCapital",
        "accounts_receivables": "accountsReceivables",
        "inventory": "inventory",
        "accounts_payables": "accountsPayables",
        "other_working_capital": "otherWorkingCapital",
        "other_non_cash_items": "otherNonCashItems",
        "net_cash_flow_from_operating_activities": "netCashProvidedByOperatingActivities",
        "investments_in_property_plant_and_equipment": "investmentsInPropertyPlantAndEquipment",
        "acquisitions_net": "acquisitionsNet",
        "purchases_of_marketable_securities": "purchasesOfInvestments",
        "sales_from_maturities_of_investments": "salesMaturitiesOfInvestments",
        "other_investing_activities": "otherInvestingActivites",
        "net_cash_flow_from_investing_activities": "netCashUsedForInvestingActivites",
        "debt_repayment": "debtRepayment",
        "common_stock_issued": "commonStockIssued",
        "common_stock_repurchased": "commonStockRepurchased",
        "dividends_paid": "dividendsPaid",
        "other_financing_activities": "otherFinancingActivites",
        "net_cash_flow_from_financing_activities": "netCashUsedProvidedByFinancingActivities",
        "effect_of_exchange_rate_changes_on_cash": "effectOfForexChangesOnCash",
        "net_change_in_cash": "netChangeInCash",
        "cash_at_beginning_of_period": "cashAtBeginningOfPeriod",
        "cash_at_end_of_period": "cashAtEndOfPeriod",
        "operating_cash_flow": "operatingCashFlow",
        "capital_expenditure": "capitalExpenditure",
        "free_cash_flow": "freeCashFlow",
        "link": "link",
        "final_link": "finalLink",
    }

    fiscal_year: int = Field(description="The fiscal year of the fiscal period.")
    filing_date: dateType = Field(description="The date of the filing.")
    accepted_date: datetime = Field(description="The date the filing was accepted.")

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return {k: None if v == 0 else v for k, v in values.items()}


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
    async def aextract_data(
        query: FMPCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"cash-flow-statement/{query.symbol}", api_key, query, ["symbol"]
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCashFlowStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCashFlowStatementData]:
        """Return the transformed data."""
        results = data
        [result.pop("symbol", None) for result in results]
        [result.pop("cik", None) for result in results]
        return [FMPCashFlowStatementData.model_validate(d) for d in results]
