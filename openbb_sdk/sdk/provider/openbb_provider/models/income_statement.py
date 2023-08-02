"""Income Statement Data Model."""


from datetime import date as dateType, datetime
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.models.base import FinancialStatementQueryParams


class IncomeStatementQueryParams(FinancialStatementQueryParams):
    """Income Statement Query."""


class IncomeStatementData(Data):
    """Income Statement Data."""

    date: dateType = Field(description="Date of the income statement.")
    symbol: str = Field(description="Symbol of the company.")
    cik: Optional[int] = Field(description="Central Index Key.")
    currency: Optional[str] = Field(description="Reporting currency.")
    filing_date: Optional[dateType] = Field(description="Filling date.")
    accepted_date: Optional[datetime] = Field(description="Accepted date.")
    period: Optional[str] = Field(description="Period of the income statement.")

    revenue: Optional[int] = Field(description="Revenue.")
    cost_of_revenue: Optional[int] = Field(description="Cost of revenue.")
    gross_profit: Optional[int] = Field(description="Gross profit.")

    research_and_development_expenses: Optional[int] = Field(
        description="Research and development expenses."
    )
    general_and_administrative_expenses: Optional[int] = Field(
        description="General and administrative expenses."
    )
    selling_and_marketing_expenses: Optional[float] = Field(
        description="Selling and marketing expenses."
    )
    selling_general_and_administrative_expenses: Optional[int] = Field(
        description="Selling, general and administrative expenses."
    )
    other_expenses: Optional[int] = Field(description="Other expenses.")
    operating_expenses: Optional[int] = Field(description="Operating expenses.")

    depreciation_and_amortization: Optional[int] = Field(
        description="Depreciation and amortization."
    )
    ebitda: Optional[int] = Field(
        description="Earnings before interest, taxes, depreciation and amortization."
    )
    operating_income: Optional[int] = Field(description="Operating income.")

    interest_income: Optional[int] = Field(description="Interest income.")
    interest_expense: Optional[int] = Field(description="Interest expense.")
    total_other_income_expenses_net: Optional[int] = Field(
        description="Total other income expenses net."
    )
    income_before_tax: Optional[int] = Field(description="Income before tax.")
    income_tax_expense: Optional[int] = Field(description="Income tax expense.")

    net_income: Optional[int] = Field(description="Net income.")
    eps: Optional[float] = Field(description="Earnings per share.")
    eps_diluted: Optional[float] = Field(description="Earnings per share diluted.")
    weighted_average_shares_outstanding: Optional[int] = Field(
        description="Weighted average shares outstanding."
    )
    weighted_average_shares_outstanding_dil: Optional[int] = Field(
        description="Weighted average shares outstanding diluted."
    )
