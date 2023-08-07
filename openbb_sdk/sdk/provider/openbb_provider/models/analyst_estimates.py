"""Analyst estimates data model."""


from datetime import date as dateType
from typing import Literal

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.models.base import BaseSymbol
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class AnalystEstimatesQueryParams(QueryParams, BaseSymbol):
    """Analyst Estimates query."""

    period: Literal["quarterly", "annually"] = Field(
        default="annually", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: int = Field(default=30, description=QUERY_DESCRIPTIONS.get("limit", ""))


class AnalystEstimatesData(Data, BaseSymbol):
    """Analyst estimates data."""

    date: dateType = Field(description=QUERY_DESCRIPTIONS.get("date", ""))
    estimated_revenue_low: int = Field(description="The estimated revenue low.")
    estimated_revenue_high: int = Field(description="The estimated revenue high.")
    estimated_revenue_avg: int = Field(description="The estimated revenue average.")
    estimated_ebitda_low: int = Field(description="The estimated EBITDA low.")
    estimated_ebitda_high: int = Field(description="The estimated EBITDA high.")
    estimated_ebitda_avg: int = Field(description="The estimated EBITDA average.")
    estimated_ebit_low: int = Field(description="The estimated EBIT low.")
    estimated_ebit_high: int = Field(description="The estimated EBIT high.")
    estimated_ebit_avg: int = Field(description="The estimated EBIT average.")
    estimated_net_income_low: int = Field(description="The estimated net income low.")
    estimated_net_income_high: int = Field(description="The estimated net income high.")
    estimated_net_income_avg: int = Field(
        description="The estimated net income average."
    )
    estimated_sga_expense_low: int = Field(description="The estimated SGA expense low.")
    estimated_sga_expense_high: int = Field(
        description="The estimated SGA expense high."
    )
    estimated_sga_expense_avg: int = Field(
        description="The estimated SGA expense average."
    )
    estimated_eps_avg: float = Field(description="The estimated EPS average.")
    estimated_eps_high: float = Field(description="The estimated EPS high.")
    estimated_eps_low: float = Field(description="The estimated EPS low.")
    number_analyst_estimated_revenue: int = Field(
        description="The number of analysts who estimated revenue."
    )
    number_analysts_estimated_eps: int = Field(
        description="The number of analysts who estimated EPS."
    )
