"""Income Statement Data Model."""


from datetime import date as dateType
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, NonNegativeInt, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class IncomeStatementQueryParams(QueryParams):
    """Income Statement Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: Literal["annual", "quarter"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: NonNegativeInt = Field(
        default=12, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class IncomeStatementData(Data):
    """Income Statement Data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description="Date of the income statement.")
    period: Optional[str] = Field(description="Period of the income statement.")
    cik: Optional[str] = Field(description="Central Index Key.")

    revenue: Optional[int] = Field(description="Revenue.")
    cost_of_revenue: Optional[int] = Field(description="Cost of revenue.")
    gross_profit: Optional[int] = Field(description="Gross profit.")
    cost_and_expenses: Optional[int] = Field(description="Cost and expenses.")
    gross_profit_ratio: Optional[float] = Field(description="Gross profit ratio.")

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
    ebitda_ratio: Optional[float] = Field(
        description="Earnings before interest, taxes, depreciation and amortization ratio."
    )
    operating_income: Optional[int] = Field(description="Operating income.")
    operating_income_ratio: Optional[float] = Field(
        description="Operating income ratio."
    )

    interest_income: Optional[int] = Field(description="Interest income.")
    interest_expense: Optional[int] = Field(description="Interest expense.")
    total_other_income_expenses_net: Optional[int] = Field(
        description="Total other income expenses net."
    )

    income_before_tax: Optional[int] = Field(description="Income before tax.")
    income_before_tax_ratio: Optional[float] = Field(
        description="Income before tax ratio."
    )
    income_tax_expense: Optional[int] = Field(description="Income tax expense.")

    net_income: Optional[int] = Field(description="Net income.")
    net_income_ratio: Optional[float] = Field(description="Net income ratio.")
    eps: Optional[float] = Field(description="Earnings per share.")
    eps_diluted: Optional[float] = Field(description="Earnings per share diluted.")
    weighted_average_shares_outstanding: Optional[int] = Field(
        description="Weighted average shares outstanding."
    )
    weighted_average_shares_outstanding_dil: Optional[int] = Field(
        description="Weighted average shares outstanding diluted."
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
