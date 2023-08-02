"""Cash Flow Statement Data Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.models.base import FinancialStatementQueryParams


class CashFlowStatementQueryParams(FinancialStatementQueryParams):
    """Cash Flow Statement Query."""


class CashFlowStatementData(Data):
    """Cash Flow Statement Data."""

    date: dateType = Field(description="Date of the fetched statement.")
    symbol: Optional[str] = Field(description="Symbol of the company.")
    cik: Optional[int] = Field(description="Central Index Key.")
    currency: Optional[str] = Field(description="Reporting currency.")
    filing_date: Optional[dateType] = Field(description="Filling date.")
    accepted_date: Optional[datetime] = Field(description="Accepted date.")
    period: Optional[str] = Field(description="Reporting period of the statement.")

    cash_at_beginning_of_period: Optional[int]
    net_income: Optional[int]
    depreciation_and_amortization: Optional[int]
    stock_based_compensation: Optional[int]
    other_non_cash_items: Optional[int] = Field(description="Other non-cash items.")
    deferred_income_tax: Optional[int] = Field(description="Deferred income tax.")

    inventory: Optional[int]
    accounts_receivables: Optional[int]

    accounts_payables: Optional[int]
    other_working_capital: Optional[int] = Field(
        description="Accrued expenses and other, Unearned revenue."
    )
    net_cash_flow_from_operating_activities: Optional[int]

    capital_expenditure: Optional[int] = Field(
        description="Purchases of property and equipment."
    )
    other_investing_activities: Optional[int] = Field(
        description="Proceeds from property and equipment sales and incentives."
    )
    acquisitions_net: Optional[int] = Field(
        description="Acquisitions, net of cash acquired, and other"
    )
    sales_maturities_of_investments: Optional[int]
    purchases_of_investments: Optional[int]
    net_cash_flow_from_investing_activities: Optional[int]
    investments_in_property_plant_and_equipment: Optional[int]

    dividends_paid: Optional[int]
    common_stock_repurchased: Optional[int]
    debt_repayment: Optional[int]

    other_financing_activities: Optional[int]

    net_cash_flow_from_financing_activities: Optional[int]
    effect_of_forex_changes_on_cash: Optional[int] = Field(
        description="Foreign currency effect on cash, cash equivalents, and restricted cash"
    )

    net_change_in_cash: Optional[int] = Field(
        description="Net increase (decrease) in cash, cash equivalents, and restricted cash"
    )

    cash_at_end_of_period: Optional[int]
