"""Analyst estimates data model."""


from datetime import date as dateType
from typing import Literal

from pydantic import Field

from openbb_provider.abstract.data import Data, StrictInt
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class AnalystEstimatesQueryParams(QueryParams, BaseSymbol):
    """Analyst Estimates query."""

    period: Literal["quarter", "annual"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: int = Field(default=30, description=QUERY_DESCRIPTIONS.get("limit", ""))


class AnalystEstimatesData(Data, BaseSymbol):
    """Analyst estimates data."""

    date: dateType = Field(description=QUERY_DESCRIPTIONS.get("date", ""))
    estimated_revenue_low: StrictInt = Field(description="Estimated revenue low.")
    estimated_revenue_high: StrictInt = Field(description="Estimated revenue high.")
    estimated_revenue_avg: StrictInt = Field(description="Estimated revenue average.")
    estimated_ebitda_low: StrictInt = Field(description="Estimated EBITDA low.")
    estimated_ebitda_high: StrictInt = Field(description="Estimated EBITDA high.")
    estimated_ebitda_avg: StrictInt = Field(description="Estimated EBITDA average.")
    estimated_ebit_low: StrictInt = Field(description="Estimated EBIT low.")
    estimated_ebit_high: StrictInt = Field(description="Estimated EBIT high.")
    estimated_ebit_avg: StrictInt = Field(description="Estimated EBIT average.")
    estimated_net_income_low: StrictInt = Field(description="Estimated net income low.")
    estimated_net_income_high: StrictInt = Field(
        description="Estimated net income high."
    )
    estimated_net_income_avg: StrictInt = Field(
        description="Estimated net income average."
    )
    estimated_sga_expense_low: StrictInt = Field(
        description="Estimated SGA expense low."
    )
    estimated_sga_expense_high: StrictInt = Field(
        description="Estimated SGA expense high."
    )
    estimated_sga_expense_avg: StrictInt = Field(
        description="Estimated SGA expense average."
    )
    estimated_eps_avg: float = Field(description="Estimated EPS average.")
    estimated_eps_high: float = Field(description="Estimated EPS high.")
    estimated_eps_low: float = Field(description="Estimated EPS low.")
    number_analyst_estimated_revenue: StrictInt = Field(
        description="Number of analysts who estimated revenue."
    )
    number_analysts_estimated_eps: StrictInt = Field(
        description="Number of analysts who estimated EPS."
    )
