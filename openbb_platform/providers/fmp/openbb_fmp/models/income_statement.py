"""FMP Income Statement Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.definitions import FinancialStatementPeriods
from pydantic import Field


class FMPIncomeStatementQueryParams(IncomeStatementQueryParams):
    """FMP Income Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement
    """

    period: FinancialStatementPeriods = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )


class FMPIncomeStatementData(IncomeStatementData):
    """FMP Income Statement Data."""

    __alias_dict__ = {
        "period_ending": "date",
        "fiscal_period": "period",
        "fiscal_year": "calendarYear",
        "filing_date": "fillingDate",
        "accepted_date": "acceptedDate",
        "reported_currency": "reportedCurrency",
        "revenue": "revenue",
        "cost_of_revenue": "costOfRevenue",
        "gross_profit": "grossProfit",
        "general_and_admin_expense": "generalAndAdministrativeExpenses",
        "research_and_development_expense": "researchAndDevelopmentExpenses",
        "selling_and_marketing_expense": "sellingAndMarketingExpenses",
        "selling_general_and_admin_expense": "sellingGeneralAndAdministrativeExpenses",
        "other_expenses": "otherExpenses",
        "total_operating_expenses": "operatingExpenses",
        "cost_and_expenses": "costAndExpenses",
        "interest_income": "interestIncome",
        "total_interest_expense": "interestExpense",
        "depreciation_and_amortization": "depreciationAndAmortization",
        "ebitda": "ebitda",
        "total_operating_income": "operatingIncome",
        "total_other_income_expenses": "totalOtherIncomeExpensesNet",
        "total_pre_tax_income": "incomeBeforeTax",
        "income_tax_expense": "incomeTaxExpense",
        "consolidated_net_income": "netIncome",
        "basic_earnings_per_share": "eps",
        "diluted_earnings_per_share": "epsDiluted",
        "weighted_average_basic_shares_outstanding": "weightedAverageShsOut",
        "weighted_average_diluted_shares_outstanding": "weightedAverageShsOutDil",
    }

    filing_date: dateType | None = Field(
        default=None,
        description="The date when the filing was made.",
    )
    accepted_date: datetime | None = Field(
        default=None,
        description="The date and time when the filing was accepted.",
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
        description="The currency in which the balance sheet was reported.",
    )
    revenue: int | None = Field(
        default=None,
        description="Total revenue.",
    )
    cost_of_revenue: int | None = Field(
        default=None,
        description="Cost of revenue.",
    )
    gross_profit: int | None = Field(
        default=None,
        description="Gross profit.",
    )
    general_and_admin_expense: int | None = Field(
        default=None,
        description="General and administrative expenses.",
    )
    research_and_development_expense: int | None = Field(
        default=None,
        description="Research and development expenses.",
    )
    selling_and_marketing_expense: int | None = Field(
        default=None,
        description="Selling and marketing expenses.",
    )
    selling_general_and_admin_expense: int | None = Field(
        default=None,
        description="Selling, general and administrative expenses.",
    )
    other_expenses: int | None = Field(
        default=None,
        description="Other expenses.",
    )
    total_operating_expenses: int | None = Field(
        default=None,
        description="Total operating expenses.",
    )
    cost_and_expenses: int | None = Field(
        default=None,
        description="Cost and expenses.",
    )
    interest_income: int | None = Field(
        default=None,
        description="Interest income.",
    )
    total_interest_expense: int | None = Field(
        default=None,
        description="Total interest expenses.",
    )
    net_interest_income: int | None = Field(
        default=None,
        description="Net interest income.",
    )
    depreciation_and_amortization: int | None = Field(
        default=None,
        description="Depreciation and amortization.",
    )
    ebit: int | None = Field(
        default=None,
        description="Earnings before interest and taxes (EBIT).",
        title="EBIT",
    )
    ebitda: int | None = Field(
        default=None,
        description="EBITDA.",
        title="EBITDA",
    )
    total_operating_income: int | None = Field(
        default=None,
        description="Total operating income.",
    )
    non_operating_income_excluding_interest: int | None = Field(
        default=None,
        description="Non-operating income excluding interest.",
    )
    net_income_from_continuing_operations: int | None = Field(
        default=None,
        description="Net income from continuing operations.",
    )
    net_income_from_discontinued_operations: int | None = Field(
        default=None,
        description="Net income from discontinued operations.",
    )
    total_other_income_expenses: int | None = Field(
        default=None,
        description="Total other income and expenses.",
    )
    total_pre_tax_income: int | None = Field(
        default=None,
        description="Total pre-tax income.",
    )
    income_tax_expense: int | None = Field(
        default=None,
        description="Income tax expense.",
    )
    other_adjustments_to_net_income: int | None = Field(
        default=None,
        description="Other adjustments to net income.",
    )
    net_income_deductions: int | None = Field(
        default=None,
        description="Net income deductions.",
    )
    consolidated_net_income: int | None = Field(
        default=None,
        description="Consolidated net income.",
    )
    bottom_line_net_income: int | None = Field(
        default=None,
        description="Bottom line net income.",
    )
    basic_earnings_per_share: float | None = Field(
        default=None,
        description="Basic earnings per share.",
    )
    diluted_earnings_per_share: float | None = Field(
        default=None,
        description="Diluted earnings per share.",
    )
    weighted_average_basic_shares_outstanding: int | None = Field(
        default=None,
        description="Weighted average basic shares outstanding.",
    )
    weighted_average_diluted_shares_outstanding: int | None = Field(
        default=None,
        description="Weighted average diluted shares outstanding.",
    )


class FMPIncomeStatementFetcher(
    Fetcher[
        FMPIncomeStatementQueryParams,
        list[FMPIncomeStatementData],
    ]
):
    """FMP Income Statement Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPIncomeStatementQueryParams:
        """Transform the query params."""
        return FMPIncomeStatementQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPIncomeStatementQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""
        base_url = "https://financialmodelingprep.com/stable/income-statement"

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
        query: FMPIncomeStatementQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPIncomeStatementData]:
        """Return the transformed data."""
        return [FMPIncomeStatementData.model_validate(d) for d in data]
