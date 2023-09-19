"""Analyst estimates data model."""


from datetime import date as dateType
from typing import List, Literal, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class AnalystEstimatesQueryParams(QueryParams):
    """Analyst Estimates query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: Literal["quarter", "annual"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: int = Field(default=30, description=QUERY_DESCRIPTIONS.get("limit", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class AnalystEstimatesData(Data):
    """Analyst estimates data."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description=QUERY_DESCRIPTIONS.get("date", ""))
    estimated_revenue_low: int = Field(description="Estimated revenue low.")
    estimated_revenue_high: int = Field(description="Estimated revenue high.")
    estimated_revenue_avg: int = Field(description="Estimated revenue average.")
    estimated_ebitda_low: int = Field(description="Estimated EBITDA low.")
    estimated_ebitda_high: int = Field(description="Estimated EBITDA high.")
    estimated_ebitda_avg: int = Field(description="Estimated EBITDA average.")
    estimated_ebit_low: int = Field(description="Estimated EBIT low.")
    estimated_ebit_high: int = Field(description="Estimated EBIT high.")
    estimated_ebit_avg: int = Field(description="Estimated EBIT average.")
    estimated_net_income_low: int = Field(description="Estimated net income low.")
    estimated_net_income_high: int = Field(description="Estimated net income high.")
    estimated_net_income_avg: int = Field(description="Estimated net income average.")
    estimated_sga_expense_low: int = Field(description="Estimated SGA expense low.")
    estimated_sga_expense_high: int = Field(description="Estimated SGA expense high.")
    estimated_sga_expense_avg: int = Field(description="Estimated SGA expense average.")
    estimated_eps_avg: float = Field(description="Estimated EPS average.")
    estimated_eps_high: float = Field(description="Estimated EPS high.")
    estimated_eps_low: float = Field(description="Estimated EPS low.")
    number_analyst_estimated_revenue: int = Field(
        description="Number of analysts who estimated revenue."
    )
    number_analysts_estimated_eps: int = Field(
        description="Number of analysts who estimated EPS."
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])
