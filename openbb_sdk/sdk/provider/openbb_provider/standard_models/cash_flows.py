"""Cash Flow Statement Data Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data, StrictInt
from openbb_provider.standard_models.base import FinancialStatementQueryParams


class CashFlowStatementQueryParams(FinancialStatementQueryParams):
    """Cash Flow Statement Query."""


class CashFlowStatementData(Data):
    """Cash Flow Statement Data."""

    date: dateType = Field(description="Date of the fetched statement.")
    symbol: Optional[str] = Field(default=None, description="Symbol of the company.")
    cik: Optional[StrictInt] = Field(default=None, description="Central Index Key.")
    currency: Optional[str] = Field(default=None, description="Reporting currency.")
    filling_date: Optional[dateType] = Field(default=None, description="Filling date.")
    accepted_date: Optional[datetime] = Field(
        default=None, description="Accepted date."
    )
    period: Optional[str] = Field(
        default=None, description="Reporting period of the statement."
    )

    cash_at_beginning_of_period: Optional[StrictInt] = Field(
        default=None, description="Cash at beginning of period."
    )
    net_income: Optional[StrictInt] = Field(default=None, description="Net income.")
    depreciation_and_amortization: Optional[StrictInt] = Field(
        default=None, description="Depreciation and amortization."
    )
    stock_based_compensation: Optional[StrictInt] = Field(
        default=None, description="Stock based compensation."
    )
    other_non_cash_items: Optional[StrictInt] = Field(
        default=None, description="Other non-cash items."
    )
    deferred_income_tax: Optional[StrictInt] = Field(
        default=None, description="Deferred income tax."
    )
    inventory: Optional[StrictInt] = Field(default=None, description="Inventory.")
    accounts_payables: Optional[StrictInt] = Field(
        default=None, description="Accounts payables."
    )
    accounts_receivables: Optional[StrictInt] = Field(
        default=None, description="Accounts receivables."
    )
    change_in_working_capital: Optional[StrictInt] = Field(
        default=None, description="Change in working capital."
    )
    other_working_capital: Optional[StrictInt] = Field(
        default=None, description="Accrued expenses and other, Unearned revenue."
    )

    capital_expenditure: Optional[StrictInt] = Field(
        default=None, description="Purchases of property and equipment."
    )
    other_investing_activities: Optional[StrictInt] = Field(
        default=None,
        description="Proceeds from property and equipment sales and incentives.",
    )
    acquisitions_net: Optional[StrictInt] = Field(
        default=None, description="Acquisitions, net of cash acquired, and other"
    )
    sales_maturities_of_investments: Optional[StrictInt] = Field(
        default=None, description="Sales and maturities of investments."
    )
    purchases_of_investments: Optional[StrictInt] = Field(
        default=None, description="Purchases of investments."
    )
    net_cash_flow_from_operating_activities: Optional[StrictInt] = Field(
        default=None, description="Net cash flow from operating activities."
    )
    net_cash_flow_from_investing_activities: Optional[StrictInt] = Field(
        default=None, description="Net cash flow from investing activities."
    )
    net_cash_flow_from_financing_activities: Optional[StrictInt] = Field(
        default=None, description="Net cash flow from financing activities."
    )
    investments_in_property_plant_and_equipment: Optional[StrictInt] = Field(
        default=None, description="Investments in property, plant, and equipment."
    )
    net_cash_used_for_investing_activities: Optional[StrictInt] = Field(
        default=None, description="Net cash used for investing activities."
    )
    effect_of_forex_changes_on_cash: Optional[StrictInt] = Field(
        default=None,
        description="Foreign currency effect on cash, cash equivalents, and restricted cash",
    )

    dividends_paid: Optional[StrictInt] = Field(
        default=None, description="Payments for dividends and dividend equivalents"
    )
    common_stock_issued: Optional[StrictInt] = Field(
        default=None, description="Proceeds from issuance of common stock"
    )
    common_stock_repurchased: Optional[StrictInt] = Field(
        default=None, description="Payments related to repurchase of common stock"
    )
    debt_repayment: Optional[StrictInt] = Field(
        default=None, description="Payments of long-term debt"
    )

    other_financing_activities: Optional[StrictInt] = Field(
        default=None, description="Other financing activities, net"
    )

    net_change_in_cash: Optional[StrictInt] = Field(
        default=None,
        description="Net increase (decrease) in cash, cash equivalents, and restricted cash",
    )

    cash_at_end_of_period: Optional[StrictInt] = Field(
        default=None,
        description="Cash, cash equivalents, and restricted cash at end of period",
    )
    free_cash_flow: Optional[StrictInt] = Field(
        default=None,
        description="Net cash flow from operating, investing and financing activities",
    )
    operating_cash_flow: Optional[StrictInt] = Field(
        default=None, description="Net cash flow from operating activities"
    )
