"""Cash Flow Statement Data Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.standard_models.base import FinancialStatementQueryParams


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

    cash_at_beginning_of_period: Optional[int] = Field(
        description="Cash at beginning of period."
    )
    net_income: Optional[int] = Field(description="Net income.")
    depreciation_and_amortization: Optional[int] = Field(
        description="Depreciation and amortization."
    )
    stock_based_compensation: Optional[int] = Field(
        description="Stock based compensation."
    )
    other_non_cash_items: Optional[int] = Field(description="Other non-cash items.")
    deferred_income_tax: Optional[int] = Field(description="Deferred income tax.")
    inventory: Optional[int] = Field(description="Inventory.")
    accounts_payables: Optional[int] = Field(description="Accounts payables.")
    accounts_receivables: Optional[int] = Field(description="Accounts receivables.")
    change_in_working_capital: Optional[int] = Field(
        description="Change in working capital."
    )
    other_working_capital: Optional[int] = Field(
        description="Accrued expenses and other, Unearned revenue."
    )

    capital_expenditure: Optional[int] = Field(
        description="Purchases of property and equipment."
    )
    other_investing_activities: Optional[int] = Field(
        description="Proceeds from property and equipment sales and incentives."
    )
    acquisitions_net: Optional[int] = Field(
        description="Acquisitions, net of cash acquired, and other"
    )
    sales_maturities_of_investments: Optional[int] = Field(
        description="Sales and maturities of investments."
    )
    purchases_of_investments: Optional[int] = Field(
        description="Purchases of investments."
    )
    net_cash_flow_from_operating_activities: Optional[int] = Field(
        description="Net cash flow from operating activities."
    )
    net_cash_flow_from_investing_activities: Optional[int] = Field(
        description="Net cash flow from investing activities."
    )
    net_cash_flow_from_financing_activities: Optional[int] = Field(
        description="Net cash flow from financing activities."
    )
    investments_in_property_plant_and_equipment: Optional[int] = Field(
        description="Investments in property, plant, and equipment."
    )
    net_cash_used_for_investing_activities: Optional[int] = Field(
        description="Net cash used for investing activities."
    )
    effect_of_forex_changes_on_cash: Optional[int] = Field(
        description="Foreign currency effect on cash, cash equivalents, and restricted cash"
    )

    dividends_paid: Optional[int] = Field(
        description="Payments for dividends and dividend equivalents"
    )
    common_stock_issued: Optional[int] = Field(
        description="Proceeds from issuance of common stock"
    )
    common_stock_repurchased: Optional[int] = Field(
        description="Payments related to repurchase of common stock"
    )
    debt_repayment: Optional[int] = Field(description="Payments of long-term debt")

    other_financing_activities: Optional[int] = Field(
        description="Other financing activities, net"
    )

    net_change_in_cash: Optional[int] = Field(
        description="Net increase (decrease) in cash, cash equivalents, and restricted cash"
    )

    cash_at_end_of_period: Optional[int] = Field(
        description="Cash, cash equivalents, and restricted cash at end of period"
    )
    free_cash_flow: Optional[int] = Field(
        description="Net cash flow from operating, investing and financing activities"
    )
    operating_cash_flow: Optional[int] = Field(
        description="Net cash flow from operating activities"
    )
