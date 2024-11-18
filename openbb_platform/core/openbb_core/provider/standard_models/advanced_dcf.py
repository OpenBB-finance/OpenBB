"""Advanced Dcf Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class AdvancedDcfQueryParams(QueryParams):
    """Advanced Dcf Query."""

    symbol: Optional[str] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    debt: bool = Field(
        default=False, description="Take the debt level into account or not."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class AdvancedDcfData(Data):
    """Advanced Dcf data."""

    year: Optional[int] = Field(default=None, description="Year of the data.")
    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    revenue: Optional[float] = Field(
        default=None, description="Annual revenue of the company, i.e., total sales."
    )
    revenue_percentage: Optional[float] = Field(
        default=None,
        description="Revenue percentage, typically relative to industry or overall financials.",
    )
    capital_expenditure: Optional[float] = Field(
        default=None,
        description="Capital expenditure, i.e., spending on fixed assets or asset expansion.",
    )
    capital_expenditure_percentage: Optional[float] = Field(
        default=None,
        description="Capital expenditure percentage, usually relative to revenue.",
    )
    price: Optional[float] = Field(default=None, description="Stock price.")
    beta: Optional[float] = Field(
        default=None,
        description="Stock beta, indicating volatility relative to the market.",
    )
    diluted_shares_outstanding: Optional[float] = Field(
        default=None,
        description="Diluted shares outstanding, i.e., total shares after all potential issuances.",
    )
    cost_of_debt: Optional[float] = Field(
        default=None,
        description="Cost of debt, or the average interest rate on the company's borrowing.",
    )
    tax_rate: Optional[float] = Field(
        default=None, description="Corporate income tax rate."
    )
    after_tax_cost_of_debt: Optional[float] = Field(
        default=None,
        description="After-tax cost of debt, actual debt cost after tax deductions.",
    )
    risk_free_rate: Optional[float] = Field(
        default=None,
        description="Risk-free rate, typically represented by government bond yields.",
    )
    market_risk_premium: Optional[float] = Field(
        default=None,
        description="Market risk premium, i.e., the difference between market returns and the risk-free rate.",
    )
    cost_of_equity: Optional[float] = Field(
        default=None,
        description="Cost of equity, or the expected return rate by investors.",
    )
    total_debt: Optional[float] = Field(
        default=None, description="Total debt of the company."
    )
    total_equity: Optional[float] = Field(
        default=None, description="Total equity or shareholder assets of the company."
    )
    total_capital: Optional[float] = Field(
        default=None, description="Total capital, or the sum of debt and equity."
    )
    debt_weighting: Optional[float] = Field(
        default=None, description="Debt weighting in capital structure, in percentage."
    )
    equity_weighting: Optional[float] = Field(
        default=None,
        description="Equity weighting in capital structure, in percentage.",
    )
    wacc: Optional[float] = Field(
        default=None,
        description="Weighted average cost of capital, or the company's overall financing cost.",
    )
    long_term_growth_rate: Optional[float] = Field(
        default=None, description="Long-term growth rate forecast for the company."
    )
    terminal_value: Optional[float] = Field(
        default=None,
        description="Terminal value, an estimate of future cash flows in DCF models.",
    )
    present_terminal_value: Optional[float] = Field(
        default=None,
        description="Present terminal value, i.e., the discounted value of terminal value.",
    )
    enterprise_value: Optional[float] = Field(
        default=None,
        description="Enterprise value, or the total value of the company excluding cash and debt.",
    )
    net_debt: Optional[float] = Field(
        default=None, description="Net debt, or total debt minus cash."
    )
    equity_value: Optional[float] = Field(
        default=None,
        description="Equity value of the company, or enterprise value minus net debt.",
    )
    equity_value_per_share: Optional[float] = Field(
        default=None,
        description="Equity value per share, calculated as equity value divided by shares outstanding.",
    )
    free_cash_flow_t1: Optional[float] = Field(
        default=None, description="Projected free cash flow for the first year."
    )
