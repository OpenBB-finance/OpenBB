"""FMP Cash Flow Statement Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.definitions import FinancialStatementPeriods
from pydantic import Field


class FMPCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """FMP Cash Flow Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Cash-Flow-Statement
    """

    period: FinancialStatementPeriods = Field(
        default="annual",
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
        "change_in_account_receivables": "accountsReceivables",
        "change_in_inventory": "inventory",
        "change_in_account_payable": "accountsPayables",
        "change_in_other_working_capital": "otherWorkingCapital",
        "change_in_other_non_cash_items": "otherNonCashItems",
        "net_cash_from_operating_activities": "netCashProvidedByOperatingActivities",
        "purchase_of_property_plant_and_equipment": "investmentsInPropertyPlantAndEquipment",
        "acquisitions": "acquisitionsNet",
        "purchase_of_investment_securities": "purchasesOfInvestments",
        "sale_and_maturity_of_investments": "salesMaturitiesOfInvestments",
        "other_investing_activities": "otherInvestingActivities",
        "net_cash_from_investing_activities": "netCashProvidedByInvestingActivities",
        "repayment_of_debt": "debtRepayment",
        "issuance_of_common_equity": "commonStockIssuance",
        "repurchase_of_common_equity": "commonStockRepurchased",
        "net_common_equity_issuance": "netCommonStockIssuance",
        "net_preferred_equity_issuance": "netPreferredStockIssuance",
        "net_equity_issuance": "netStockIssuance",
        "payment_of_dividends": "dividendsPaid",
        "other_financing_activities": "otherFinancingActivites",
        "net_cash_from_financing_activities": "netCashProvidedByFinancingActivities",
        "effect_of_exchange_rate_changes_on_cash": "effectOfForexChangesOnCash",
        "net_change_in_cash_and_equivalents": "netChangeInCash",
        "cash_at_beginning_of_period": "cashAtBeginningOfPeriod",
        "cash_at_end_of_period": "cashAtEndOfPeriod",
        "operating_cash_flow": "operatingCashFlow",
        "capital_expenditure": "capitalExpenditure",
        "free_cash_flow": "freeCashFlow",
    }

    fiscal_year: int | None = Field(
        default=None,
        description="The fiscal year of the fiscal period.",
    )
    filing_date: dateType | None = Field(
        default=None,
        description="The date of the filing.",
    )
    accepted_date: datetime | None = Field(
        default=None, description="The date the filing was accepted."
    )
    cik: str | None = Field(
        default=None,
        description="The Central Index Key (CIK) assigned by the SEC, if applicable.",
    )
    symbol: str | None = Field(
        default=None,
        description="The stock ticker symbol.",
    )
    reported_currency: str | None = Field(
        default=None,
        description="The currency in which the cash flow statement was reported.",
    )
    net_income: int | None = Field(
        default=None,
        description="Net income.",
    )
    depreciation_and_amortization: int | None = Field(
        default=None,
        description="Depreciation and amortization.",
    )
    deferred_income_tax: int | None = Field(
        default=None,
        description="Deferred income tax.",
    )
    stock_based_compensation: int | None = Field(
        default=None,
        description="Stock-based compensation.",
    )
    change_in_working_capital: int | None = Field(
        default=None,
        description="Change in working capital.",
    )
    change_in_account_receivables: int | None = Field(
        default=None,
        description="Change in account receivables.",
    )
    change_in_inventory: int | None = Field(
        default=None,
        description="Change in inventory.",
    )
    change_in_account_payable: int | None = Field(
        default=None,
        description="Change in account payable.",
    )
    change_in_other_working_capital: int | None = Field(
        default=None,
        description="Change in other working capital.",
    )
    change_in_other_non_cash_items: int | None = Field(
        default=None,
        description="Change in other non-cash items.",
    )
    net_cash_from_operating_activities: int | None = Field(
        default=None,
        description="Net cash from operating activities.",
    )
    purchase_of_property_plant_and_equipment: int | None = Field(
        default=None,
        description="Purchase of property, plant and equipment.",
    )
    acquisitions: int | None = Field(
        default=None,
        description="Acquisitions.",
    )
    purchase_of_investment_securities: int | None = Field(
        default=None,
        description="Purchase of investment securities.",
    )
    sale_and_maturity_of_investments: int | None = Field(
        default=None,
        description="Sale and maturity of investments.",
    )
    other_investing_activities: int | None = Field(
        default=None,
        description="Other investing activities.",
    )
    net_cash_from_investing_activities: int | None = Field(
        default=None,
        description="Net cash from investing activities.",
    )
    repayment_of_debt: int | None = Field(
        default=None,
        description="Repayment of debt.",
    )
    issuance_of_common_equity: int | None = Field(
        default=None,
        description="Issuance of common equity.",
    )
    repurchase_of_common_equity: int | None = Field(
        default=None,
        description="Repurchase of common equity.",
    )
    net_common_equity_issuance: int | None = Field(
        default=None,
        description="Net common equity issuance.",
    )
    net_preferred_equity_issuance: int | None = Field(
        default=None,
        description="Net preferred equity issuance.",
    )
    net_equity_issuance: int | None = Field(
        default=None,
        description="Net equity issuance.",
    )
    short_term_net_debt_issuance: int | None = Field(
        default=None,
        description="Short term net debt issuance.",
    )
    long_term_net_debt_issuance: int | None = Field(
        default=None,
        description="Long term net debt issuance.",
    )
    net_debt_issuance: int | None = Field(
        default=None,
        description="Net debt issuance.",
    )
    common_dividends_paid: int | None = Field(
        default=None,
        description="Payment of common dividends.",
    )
    preferred_dividends_paid: int | None = Field(
        default=None,
        description="Payment of preferred dividends.",
    )
    net_dividends_paid: int | None = Field(
        default=None,
        description="Net dividends paid.",
    )
    other_financing_activities: int | None = Field(
        default=None,
        description="Other financing activities.",
    )
    net_cash_from_financing_activities: int | None = Field(
        default=None,
        description="Net cash from financing activities.",
    )
    effect_of_exchange_rate_changes_on_cash: int | None = Field(
        default=None,
        description="Effect of exchange rate changes on cash.",
    )
    net_change_in_cash_and_equivalents: int | None = Field(
        default=None,
        description="Net change in cash and equivalents.",
    )
    cash_at_beginning_of_period: int | None = Field(
        default=None,
        description="Cash at beginning of period.",
    )
    cash_at_end_of_period: int | None = Field(
        default=None,
        description="Cash at end of period.",
    )
    operating_cash_flow: int | None = Field(
        default=None,
        description="Operating cash flow.",
    )
    capital_expenditure: int | None = Field(
        default=None,
        description="Capital expenditure.",
    )
    income_taxes_paid: int | None = Field(
        default=None,
        description="Income taxes paid.",
    )
    interest_paid: int | None = Field(
        default=None,
        description="Interest paid.",
    )
    free_cash_flow: int | None = Field(
        default=None,
    )


class FMPCashFlowStatementFetcher(
    Fetcher[
        FMPCashFlowStatementQueryParams,
        list[FMPCashFlowStatementData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCashFlowStatementQueryParams:
        """Transform the query params."""
        return FMPCashFlowStatementQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCashFlowStatementQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        base_url = "https://financialmodelingprep.com/stable/cash-flow-statement"

        if query.period == "ttm":
            base_url += "-ttm"

        url = (
            base_url
            + f"?symbol={query.symbol}{'&period=' + query.period if query.period != 'ttm' else ''}"
            + f"&limit={query.limit if query.limit else 5}"
            + f"&apikey={api_key}"
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCashFlowStatementQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCashFlowStatementData]:
        """Return the transformed data."""
        return [FMPCashFlowStatementData.model_validate(d) for d in data]
