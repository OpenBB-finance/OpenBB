"""FMP Income Statement Fetcher."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from pydantic import Field, root_validator

PeriodType = Literal["annual", "quarter"]


class FMPIncomeStatementQueryParams(IncomeStatementQueryParams):
    """FMP Income Statement QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement
    """

    symbol: str = Field(description="Symbol/CIK of the company.")

    @root_validator()
    def check_symbol_or_cik(cls, values):  # pylint: disable=no-self-argument
        """Validate that either a symbol or CIK is provided."""
        if values.get("symbol") is None and values.get("cik") is None:
            raise ValueError("symbol or cik must be provided")
        return values


class FMPIncomeStatementData(IncomeStatementData):
    """FMP Income Statement Data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "cost_of_revenue": "costOfRevenue",
            "gross_profit": "grossProfit",
            "gross_profit_ratio": "grossProfitRatio",
            "research_and_development_expenses": "researchAndDevelopmentExpenses",
            "general_and_administrative_expenses": "generalAndAdministrativeExpenses",
            "selling_and_marketing_expenses": "sellingAndMarketingExpenses",
            "selling_general_and_administrative_expenses": "sellingGeneralAndAdministrativeExpenses",
            "other_expenses": "otherExpenses",
            "operating_expenses": "operatingExpenses",
            "depreciation_and_amortization": "depreciationAndAmortization",
            "ebitda_ratio": "ebitdaratio",
            "operating_income": "operatingIncome",
            "operating_income_ratio": "operatingIncomeRatio",
            "interest_income": "interestIncome",
            "interest_expense": "interestExpense",
            "total_other_income_expenses_net": "totalOtherIncomeExpensesNet",
            "income_before_tax": "incomeBeforeTax",
            "income_before_tax_ratio": "incomeBeforeTaxRatio",
            "income_tax_expense": "incomeTaxExpense",
            "net_income": "netIncome",
            "net_income_ratio": "netIncomeRatio",
            "eps_diluted": "epsdiluted",
            "weighted_average_shares_outstanding": "weightedAverageShsOut",
            "weighted_average_shares_outstanding_dil": "weightedAverageShsOutDil",
        }

        reported_currency: Optional[str] = Field(description="Reporting currency.")
        filing_date: Optional[dateType] = Field(description="Filling date.")
        accepted_date: Optional[datetime] = Field(description="Accepted date.")
        calendar_year: Optional[int] = Field(description="Calendar year.")

        cost_of_revenue: Optional[float] = Field(description="Cost of revenue.")
        gross_profit: Optional[float] = Field(description="Gross profit.")
        gross_profit_ratio: Optional[float] = Field(description="Gross profit ratio.")
        research_and_development_expenses: Optional[float] = Field(
            description="Research and development expenses."
        )
        general_and_administrative_expenses: Optional[float] = Field(
            description="General and administrative expenses."
        )
        selling_and_marketing_expenses: Optional[float] = Field(
            description="Selling and marketing expenses."
        )
        selling_general_and_administrative_expenses: Optional[float] = Field(
            description="Selling, general and administrative expenses."
        )
        other_expenses: Optional[float] = Field(description="Other expenses.")

        operating_expenses: Optional[float] = Field(description="Operating expenses.")
        depreciation_and_amortization: Optional[float] = Field(
            description="Depreciation and amortization."
        )
        ebitda_ratio: Optional[float] = Field(description="EBIDTA ratio.")
        operating_income: Optional[float] = Field(description="Operating income.")
        operating_income_ratio: Optional[float] = Field(
            description="Operating income ratio."
        )
        interest_income: Optional[float] = Field(description="Interest income.")
        interest_expense: Optional[float] = Field(description="Interest expense.")

        total_other_income_expenses_net: Optional[float] = Field(
            description="Total other income expenses net."
        )
        income_before_tax: Optional[float] = Field(description="Income before tax.")
        income_before_tax_ratio: Optional[float] = Field(
            description="Income before tax ratio."
        )
        income_tax_expense: Optional[float] = Field(description="Income tax expense.")
        net_income: Optional[float] = Field(description="Net income.")
        net_income_ratio: Optional[float] = Field(description="Net income ratio.")

        link: Optional[str] = Field(description="Link to the income statement.")
        final_link: Optional[str] = Field(
            description="Final link to the income statement."
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
    def extract_data(
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

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPIncomeStatementData]:
        """Return the transformed data."""
        return [FMPIncomeStatementData.parse_obj(d) for d in data]
