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
    cash_at_beginning_of_period : Optional[int]
        The cash at the beginning of the period.
    net_income : Optional[int]
        The net income.
    depreciation_and_amortization : Optional[int]
        The depreciation and amortization.
    stock_based_compensation : Optional[int]
        The stock based compensation.
    accounts_receivables : Optional[int]
        The accounts receivables.
    inventory : Optional[int]
        The inventory.
    accounts_payables : Optional[int]
        The accounts payables.
    net_cash_flow_from_operating_activities : Optional[int]
        The net cash flow from operating activities.
    purchases_of_investments : Optional[int]
        The purchases of investments.
    sales_maturities_of_investments : Optional[int]
        The sales maturities of investments.
    investments_in_property_plant_and_equipment : Optional[int]
        The investments in property plant and equipment.
    net_cash_flow_from_investing_activities : Optional[int]
        The net cash flow from investing activities.
    dividends_paid : Optional[int]
        The dividends paid.
    common_stock_repurchased : Optional[int]
        The common stock repurchased.
    debt_repayment : Optional[int]
        The debt repayment.
    other_financing_activites : Optional[int]
        The other financing activites.
    net_cash_flow_from_financing_activities : Optional[int]
        The net cash flow from financing activities.
    net_cash_flow : Optional[int]
        The net cash flow.
    cash_at_end_of_period : Optional[int]
        The cash at the end of the period.
    """

    date: dateType
    symbol: str
    currency: Optional[str] = None
    cik: Optional[int]
    period: Optional[str]

    cash_at_beginning_of_period: Optional[int]
    net_income: Optional[int]
    depreciation_and_amortization: Optional[int]
    stock_based_compensation: Optional[int]
    # OTHER

    accounts_receivables: Optional[int]
    inventory: Optional[int]
    # VENDOR NON-TRADE_RECEIVABLES
    # OTHER CURRENT AND NON-CURRENT ASSETS
    accounts_payables: Optional[int]
    # DEFERRED_REVENUE
    # OTHER CURRENT AND NON-CURRENT LIABILITIES

    net_cash_flow_from_operating_activities: Optional[int]

    purchases_of_investments: Optional[int]
    sales_maturities_of_investments: Optional[int]
    investments_in_property_plant_and_equipment: Optional[int]
    # OTHER
    net_cash_flow_from_investing_activities: Optional[int]

    dividends_paid: Optional[int]
    common_stock_repurchased: Optional[int]
    debt_repayment: Optional[int]

    other_financing_activites: Optional[int]
    # REPAYMENT OF COMMERCIAL PAPER
    # OTHER

    net_cash_flow_from_financing_activities: Optional[int]

    net_cash_flow: Optional[int]
    cash_at_end_of_period: Optional[int]
