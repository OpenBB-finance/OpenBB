"""FMP Income Statement Model."""

# pylint: disable=unused-argument
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_fmp.utils.helpers import get_data_many
from pydantic import Field, model_validator


class FMPIncomeStatementQueryParams(IncomeStatementQueryParams):
    """FMP Income Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
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
        "gross_profit_margin": "grossProfitRatio",
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
        "ebitda_margin": "ebitdaratio",
        "total_operating_income": "operatingIncome",
        "operating_income_margin": "operatingIncomeRatio",
        "total_other_income_expenses": "totalOtherIncomeExpensesNet",
        "total_pre_tax_income": "incomeBeforeTax",
        "pre_tax_income_margin": "incomeBeforeTaxRatio",
        "income_tax_expense": "incomeTaxExpense",
        "consolidated_net_income": "netIncome",
        "net_income_margin": "netIncomeRatio",
        "basic_earnings_per_share": "eps",
        "diluted_earnings_per_share": "epsdiluted",
        "weighted_average_basic_shares_outstanding": "weightedAverageShsOut",
        "weighted_average_diluted_shares_outstanding": "weightedAverageShsOutDil",
        "link": "link",
        "final_link": "finalLink",
    }

    filing_date: Optional[dateType] = Field(
        default=None,
        description="The date when the filing was made.",
    )
    accepted_date: Optional[datetime] = Field(
        default=None,
        description="The date and time when the filing was accepted.",
    )
    reported_currency: Optional[str] = Field(
        default=None,
        description="The currency in which the balance sheet was reported.",
    )
    revenue: Optional[float] = Field(
        default=None,
        description="Total revenue.",
    )
    cost_of_revenue: Optional[float] = Field(
        default=None,
        description="Cost of revenue.",
    )
    gross_profit: Optional[float] = Field(
        default=None,
        description="Gross profit.",
    )
    gross_profit_margin: Optional[float] = Field(
        default=None,
        description="Gross profit margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    general_and_admin_expense: Optional[float] = Field(
        default=None,
        description="General and administrative expenses.",
    )
    research_and_development_expense: Optional[float] = Field(
        default=None,
        description="Research and development expenses.",
    )
    selling_and_marketing_expense: Optional[float] = Field(
        default=None,
        description="Selling and marketing expenses.",
    )
    selling_general_and_admin_expense: Optional[float] = Field(
        default=None,
        description="Selling, general and administrative expenses.",
    )
    other_expenses: Optional[float] = Field(
        default=None,
        description="Other expenses.",
    )
    total_operating_expenses: Optional[float] = Field(
        default=None,
        description="Total operating expenses.",
    )
    cost_and_expenses: Optional[float] = Field(
        default=None,
        description="Cost and expenses.",
    )
    interest_income: Optional[float] = Field(
        default=None,
        description="Interest income.",
    )
    total_interest_expense: Optional[float] = Field(
        default=None,
        description="Total interest expenses.",
    )
    depreciation_and_amortization: Optional[float] = Field(
        default=None,
        description="Depreciation and amortization.",
    )
    ebitda: Optional[float] = Field(
        default=None,
        description="EBITDA.",
    )
    ebitda_margin: Optional[float] = Field(
        default=None,
        description="EBITDA margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    total_operating_income: Optional[float] = Field(
        default=None,
        description="Total operating income.",
    )
    operating_income_margin: Optional[float] = Field(
        default=None,
        description="Operating income margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    total_other_income_expenses: Optional[float] = Field(
        default=None,
        description="Total other income and expenses.",
    )
    total_pre_tax_income: Optional[float] = Field(
        default=None,
        description="Total pre-tax income.",
    )
    pre_tax_income_margin: Optional[float] = Field(
        default=None,
        description="Pre-tax income margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    income_tax_expense: Optional[float] = Field(
        default=None,
        description="Income tax expense.",
    )
    consolidated_net_income: Optional[float] = Field(
        default=None,
        description="Consolidated net income.",
    )
    net_income_margin: Optional[float] = Field(
        default=None,
        description="Net income margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    basic_earnings_per_share: Optional[float] = Field(
        default=None,
        description="Basic earnings per share.",
    )
    diluted_earnings_per_share: Optional[float] = Field(
        default=None,
        description="Diluted earnings per share.",
    )
    weighted_average_basic_shares_outstanding: Optional[float] = Field(
        default=None,
        description="Weighted average basic shares outstanding.",
    )
    weighted_average_diluted_shares_outstanding: Optional[float] = Field(
        default=None,
        description="Weighted average diluted shares outstanding.",
    )
    link: Optional[str] = Field(
        default=None,
        description="Link to the filing.",
    )
    final_link: Optional[str] = Field(
        default=None,
        description="Link to the filing document.",
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class FMPIncomeStatementFetcher(
    Fetcher[
        FMPIncomeStatementQueryParams,
        List[FMPIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPIncomeStatementQueryParams:
        """Transform the query params."""
        return FMPIncomeStatementQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        symbol = query.symbol
        base_url = "https://financialmodelingprep.com/api/v3"

        url = (
            f"{base_url}/income-statement/{symbol}?"
            f"period={query.period}&limit={query.limit}&apikey={api_key}"
        )

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPIncomeStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPIncomeStatementData]:
        """Return the transformed data."""
        for result in data:
            result.pop("symbol", None)
            result.pop("cik", None)
        return [FMPIncomeStatementData.model_validate(d) for d in data]
