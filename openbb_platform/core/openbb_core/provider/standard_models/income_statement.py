"""Income Statement Standard Model."""


from datetime import date as dateType
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, NonNegativeInt, StrictFloat, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class IncomeStatementQueryParams(QueryParams):
    """Income Statement Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: Optional[Literal["annual", "quarter"]] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[NonNegativeInt] = Field(
        default=5, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    # pylint: disable=inconsistent-return-statements
    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            if v.isdigit() or v.isalpha():
                return v.upper()
            raise ValueError(f"Invalid symbol: {v}. Must be either a ticker or CIK.")
        if isinstance(v, List):
            symbols = []
            for symbol in v:
                if symbol.isdigit() or symbol.isalpha():
                    symbols.append(symbol.upper())
                else:
                    raise ValueError(
                        f"Invalid symbol: {symbol}. Must be either a ticker or CIK."
                    )
            return ",".join(symbols)


class IncomeStatementData(Data):
    """Income Statement Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
        + " In this case, the date of the income statement."
    )
    period: Optional[str] = Field(
        default=None, description="Period of the income statement."
    )
    cik: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )

    revenue: Optional[StrictFloat] = Field(default=None, description="Revenue.")
    cost_of_revenue: Optional[StrictFloat] = Field(
        default=None, description="Cost of revenue."
    )
    gross_profit: Optional[StrictFloat] = Field(
        default=None, description="Gross profit."
    )
    cost_and_expenses: Optional[StrictFloat] = Field(
        default=None, description="Cost and expenses."
    )
    gross_profit_ratio: Optional[float] = Field(
        default=None, description="Gross profit ratio."
    )

    research_and_development_expenses: Optional[StrictFloat] = Field(
        default=None, description="Research and development expenses."
    )
    general_and_administrative_expenses: Optional[StrictFloat] = Field(
        default=None, description="General and administrative expenses."
    )
    selling_and_marketing_expenses: Optional[float] = Field(
        default=None, description="Selling and marketing expenses."
    )
    selling_general_and_administrative_expenses: Optional[StrictFloat] = Field(
        default=None, description="Selling, general and administrative expenses."
    )
    other_expenses: Optional[StrictFloat] = Field(
        default=None, description="Other expenses."
    )
    operating_expenses: Optional[StrictFloat] = Field(
        default=None, description="Operating expenses."
    )

    depreciation_and_amortization: Optional[StrictFloat] = Field(
        default=None, description="Depreciation and amortization."
    )
    ebit: Optional[StrictFloat] = Field(
        default=None,
        description="Earnings before interest, and taxes.",
    )
    ebitda: Optional[StrictFloat] = Field(
        default=None,
        description="Earnings before interest, taxes, depreciation and amortization.",
    )
    ebitda_ratio: Optional[float] = Field(
        default=None,
        description="Earnings before interest, taxes, depreciation and amortization ratio.",
    )
    operating_income: Optional[StrictFloat] = Field(
        default=None, description="Operating income."
    )
    operating_income_ratio: Optional[float] = Field(
        default=None, description="Operating income ratio."
    )

    interest_income: Optional[StrictFloat] = Field(
        default=None, description="Interest income."
    )
    interest_expense: Optional[StrictFloat] = Field(
        default=None, description="Interest expense."
    )
    total_other_income_expenses_net: Optional[StrictFloat] = Field(
        default=None, description="Total other income expenses net."
    )

    income_before_tax: Optional[StrictFloat] = Field(
        default=None, description="Income before tax."
    )
    income_before_tax_ratio: Optional[float] = Field(
        default=None, description="Income before tax ratio."
    )
    income_tax_expense: Optional[StrictFloat] = Field(
        default=None, description="Income tax expense."
    )

    net_income: Optional[StrictFloat] = Field(default=None, description="Net income.")
    net_income_ratio: Optional[float] = Field(
        default=None, description="Net income ratio."
    )
    eps: Optional[float] = Field(default=None, description="Earnings per share.")
    eps_diluted: Optional[float] = Field(
        default=None, description="Earnings per share diluted."
    )
    weighted_average_shares_outstanding: Optional[StrictFloat] = Field(
        default=None, description="Weighted average shares outstanding."
    )
    weighted_average_shares_outstanding_dil: Optional[StrictFloat] = Field(
        default=None, description="Weighted average shares outstanding diluted."
    )
    link: Optional[str] = Field(
        default=None, description="Link to the income statement."
    )
    final_link: Optional[str] = Field(
        default=None, description="Final link to the income statement."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None
