"""Cash Flow Statement Data Model."""


from datetime import date as dateType
from typing import Optional

from openbb_provider.model.abstract.data import Data
from openbb_provider.model.data.base import FinancialStatementQueryParams


class CashFlowStatementQueryParams(FinancialStatementQueryParams):
    """Cash flow statement query.

    Parameter
    ---------
    symbol : str
        The symbol of the company.
    period : Literal["annually", "quarterly"]
        The period of the income statement.
    """


class CashFlowStatementData(Data):
    """Return Cash Flow Statement Data.

    Returns
    -------
    date : date
        The date of the cash flow statement.
    symbol : str
        The symbol of the company.
    currency : Optional[str]
        The currency of the cash flow statement.
    cik : Optional[int]
        The Central Index Key (CIK) of the company.
    period : Optional[str]
        The period of the cash flow statement.
    exchange_gain_losses : Optional[int]
        The exchange gain losses of the cash flow statement.
    net_cash_flow : Optional[int]
        The net cash flow of the cash flow statement.
    net_cash_flow_continuing : Optional[int]
        The net cash flow continuing of the cash flow statement.
    net_cash_flow_from_financing_activities : Optional[int]
        The net cash flow from financing activities of the cash flow statement.
    net_cash_flow_from_financing_activities_continuing : Optional[int]
        The net cash flow from financing activities continuing of the cash flow statement.
    net_cash_flow_from_investing_activities : Optional[int]
        The net cash flow from investing activities of the cash flow statement.
    net_cash_flow_from_investing_activities_continuing : Optional[int]
        The net cash flow from investing activities continuing of the cash flow statement.
    net_cash_flow_from_operating_activities : Optional[int]
        The net cash flow from operating activities of the cash flow statement.
    net_cash_flow_from_operating_activities_continuing : Optional[int]
        The net cash flow from operating activities continuing of the cash flow statement.
    """

    date: dateType
    symbol: str
    currency: Optional[str] = None
    cik: Optional[int]
    period: Optional[str]
    exchange_gain_losses: Optional[int] = None
    net_cash_flow: Optional[int]
    net_cash_flow_continuing: Optional[int]
    net_cash_flow_from_financing_activities: Optional[int]
    net_cash_flow_from_financing_activities_continuing: Optional[int]
    net_cash_flow_from_investing_activities: Optional[int]
    net_cash_flow_from_investing_activities_continuing: Optional[int]
    net_cash_flow_from_operating_activities: Optional[int]
    net_cash_flow_from_operating_activities_continuing: Optional[int]
