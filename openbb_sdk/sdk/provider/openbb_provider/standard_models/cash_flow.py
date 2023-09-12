"""Cash Flow Statement Data Model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data, StrictInt
from openbb_provider.standard_models.base import (
    BaseSymbol,
    FinancialStatementQueryParams,
)


class CashFlowStatementQueryParams(FinancialStatementQueryParams):
    """Cash Flow Statement Query."""


class CashFlowStatementData(Data, BaseSymbol):
    """Cash Flow Statement Data."""

    date: dateType = Field(description="Date of the fetched statement.")
    period: Optional[str] = Field(
        default=None, description="Reporting period of the statement."
    )
    cik: Optional[StrictInt] = Field(
        default=None, description="Central Index Key (CIK) of the company."
    )

    net_income: Optional[StrictInt] = Field(default=None, description="Net income.")

    depreciation_and_amortization: Optional[StrictInt] = Field(
        default=None, description="Depreciation and amortization."
    )
    stock_based_compensation: Optional[StrictInt] = Field(
        default=None, description="Stock based compensation."
    )
    deferred_income_tax: Optional[StrictInt] = Field(
        default=None, description="Deferred income tax."
    )
    other_non_cash_items: Optional[StrictInt] = Field(
        default=None, description="Other non-cash items."
    )
    changes_in_operating_assets_and_liabilities: Optional[StrictInt] = Field(
        default=None, description="Changes in operating assets and liabilities."
    )

    accounts_receivables: Optional[StrictInt] = Field(
        default=None, description="Accounts receivables."
    )
    inventory: Optional[StrictInt] = Field(default=None, description="Inventory.")
    vendor_non_trade_receivables: Optional[StrictInt] = Field(
        default=None, description="Vendor non-trade receivables."
    )
    other_current_and_non_current_assets: Optional[StrictInt] = Field(
        default=None, description="Other current and non-current assets."
    )
    accounts_payables: Optional[StrictInt] = Field(
        default=None, description="Accounts payables."
    )
    deferred_revenue: Optional[StrictInt] = Field(
        default=None, description="Deferred revenue."
    )
    other_current_and_non_current_liabilities: Optional[StrictInt] = Field(
        default=None, description="Other current and non-current liabilities."
    )
    net_cash_flow_from_operating_activities: Optional[StrictInt] = Field(
        default=None, description="Net cash flow from operating activities."
    )

    purchases_of_marketable_securities: Optional[StrictInt] = Field(
        default=None, description="Purchases of investments."
    )
    sales_from_maturities_of_investments: Optional[StrictInt] = Field(
        default=None, description="Sales and maturities of investments."
    )
    investments_in_property_plant_and_equipment: Optional[StrictInt] = Field(
        default=None, description="Investments in property, plant, and equipment."
    )
    payments_from_acquisitions: Optional[StrictInt] = Field(
        default=None, description="Acquisitions, net of cash acquired, and other"
    )
    other_investing_activities: Optional[StrictInt] = Field(
        default=None, description="Other investing activities"
    )
    net_cash_flow_from_investing_activities: Optional[StrictInt] = Field(
        default=None, description="Net cash used for investing activities."
    )

    taxes_paid_on_net_share_settlement: Optional[StrictInt] = Field(
        default=None, description="Taxes paid on net share settlement of equity awards."
    )
    dividends_paid: Optional[StrictInt] = Field(
        default=None, description="Payments for dividends and dividend equivalents"
    )
    common_stock_repurchased: Optional[StrictInt] = Field(
        default=None, description="Payments related to repurchase of common stock"
    )
    debt_proceeds: Optional[StrictInt] = Field(
        default=None, description="Proceeds from issuance of term debt"
    )
    debt_repayment: Optional[StrictInt] = Field(
        default=None, description="Payments of long-term debt"
    )
    other_financing_activities: Optional[StrictInt] = Field(
        default=None, description="Other financing activities, net"
    )
    net_cash_flow_from_financing_activities: Optional[StrictInt] = Field(
        default=None, description="Net cash flow from financing activities."
    )
    net_change_in_cash: Optional[StrictInt] = Field(
        default=None,
        description="Net increase (decrease) in cash, cash equivalents, and restricted cash",
    )
