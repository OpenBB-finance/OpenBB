"""Analyst estimates data model."""


from datetime import date as dateType
from typing import Literal

from openbb_provider.model.abstract.data import Data, QueryParams
from openbb_provider.model.data.base import BaseSymbol


class AnalystEstimatesQueryParams(QueryParams, BaseSymbol):
    """Analyst Estimates query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    period : Literal["quarter", "annual"]
        The period of the analyst estimates.
    limit : int
        The limit of the analyst estimates.
    """

    period: Literal["quarter", "annual"] = "annual"
    limit: int = 30


class AnalystEstimatesData(Data, BaseSymbol):
    """Analyst estimates data.

    Returns
    -------
    symbol : str
        The symbol of the asset.
    date : date
        The date of the analyst estimates.
    estimated_revenue_low : int
        The estimated revenue low of the analyst estimates.
    estimated_revenue_high : int
        The estimated revenue high of the analyst estimates.
    estimated_revenue_avg : int
        The estimated revenue average of the analyst estimates.
    estimated_ebitda_low : int
        The estimated EBITDA low of the analyst estimates.
    estimated_ebitda_high : int
        The estimated EBITDA high of the analyst estimates.
    estimated_ebitda_avg : int
        The estimated EBITDA average of the analyst estimates.
    estimated_ebit_low : int
        The estimated EBIT low of the analyst estimates.
    estimated_ebit_high : int
        The estimated EBIT high of the analyst estimates.
    estimated_ebit_avg : int
        The estimated EBIT average of the analyst estimates.
    estimated_net_income_low : int
        The estimated net income low of the analyst estimates.
    estimated_net_income_high : int
        The estimated net income high of the analyst estimates.
    estimated_net_income_avg : int
        The estimated net income average of the analyst estimates.
    estimated_sga_expense_low : int
        The estimated SGA expense low of the analyst estimates.
    estimated_sga_expense_high : int
        The estimated SGA expense high of the analyst estimates.
    estimated_sga_expense_avg : int
        The estimated SGA expense average of the analyst estimates.
    estimated_eps_avg : float
        The estimated EPS average of the analyst estimates.
    estimated_eps_high : float
        The estimated EPS high of the analyst estimates.
    estimated_eps_low : float
        The estimated EPS low of the analyst estimates.
    number_analyst_estimated_revenue : int
        The number of analysts who estimated revenue of the analyst estimates.
    number_analysts_estimated_eps : int
        The number of analysts who estimated EPS of the analyst estimates.
    """

    symbol: str
    date: dateType
    estimated_revenue_low: int
    estimated_revenue_high: int
    estimated_revenue_avg: int
    estimated_ebitda_low: int
    estimated_ebitda_high: int
    estimated_ebitda_avg: int
    estimated_ebit_low: int
    estimated_ebit_high: int
    estimated_ebit_avg: int
    estimated_net_income_low: int
    estimated_net_income_high: int
    estimated_net_income_avg: int
    estimated_sga_expense_low: int
    estimated_sga_expense_high: int
    estimated_sga_expense_avg: int
    estimated_eps_avg: float
    estimated_eps_high: float
    estimated_eps_low: float
    number_analyst_estimated_revenue: int
    number_analysts_estimated_eps: int
