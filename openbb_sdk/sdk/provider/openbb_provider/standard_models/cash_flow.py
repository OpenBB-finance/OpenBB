"""Cash Flow Statement Data Model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.standard_models.base import (
    BaseSymbol,
    FinancialStatementQueryParams,
)


class CashFlowStatementQueryParams(FinancialStatementQueryParams):
    """Cash Flow Statement Query."""


class CashFlowStatementData(Data, BaseSymbol):
    """Cash Flow Statement Data."""

    date: dateType = Field(description="Date of the fetched statement.")
    period: Optional[str] = Field(description="Reporting period of the statement.")
    cik: Optional[int] = Field(description="Central Index Key (CIK) of the company.")

    net_income: Optional[int] = Field(description="Net income.")

    depreciation_and_amortization: Optional[int] = Field(
        description="Depreciation and amortization."
    )
    stock_based_compensation: Optional[int] = Field(
        description="Stock based compensation."
    )
    deferred_income_tax: Optional[int] = Field(description="Deferred income tax.")
    other_non_cash_items: Optional[int] = Field(description="Other non-cash items.")
    changes_in_operating_assets_and_liabilities: Optional[int] = Field(
        description="Changes in operating assets and liabilities."
    )

    accounts_receivables: Optional[int] = Field(description="Accounts receivables.")
    inventory: Optional[int] = Field(description="Inventory.")
    vendor_non_trade_receivables: Optional[int] = Field(
        description="Vendor non-trade receivables."
    )
    other_current_and_non_current_assets: Optional[int] = Field(
        description="Other current and non-current assets."
    )
    accounts_payables: Optional[int] = Field(description="Accounts payables.")
    deferred_revenue: Optional[int] = Field(description="Deferred revenue.")
    other_current_and_non_current_liabilities: Optional[int] = Field(
        description="Other current and non-current liabilities."
    )
    net_cash_flow_from_operating_activities: Optional[int] = Field(
        description="Net cash flow from operating activities."
    )

    purchases_of_marketable_securities: Optional[int] = Field(
        description="Purchases of investments."
    )
    sales_from_maturities_of_investments: Optional[int] = Field(
        description="Sales and maturities of investments."
    )
    investments_in_property_plant_and_equipment: Optional[int] = Field(
        description="Investments in property, plant, and equipment."
    )
    payments_from_acquisitions: Optional[int] = Field(
        description="Acquisitions, net of cash acquired, and other"
    )
    other_investing_activities: Optional[int] = Field(
        description="Other investing activities"
    )
    net_cash_flow_from_investing_activities: Optional[int] = Field(
        description="Net cash used for investing activities."
    )

    taxes_paid_on_net_share_settlement: Optional[int] = Field(
        description="Taxes paid on net share settlement of equity awards."
    )
    dividends_paid: Optional[int] = Field(
        description="Payments for dividends and dividend equivalents"
    )
    common_stock_repurchased: Optional[int] = Field(
        description="Payments related to repurchase of common stock"
    )
    debt_proceeds: Optional[int] = Field(
        description="Proceeds from issuance of term debt"
    )
    debt_repayment: Optional[int] = Field(description="Payments of long-term debt")
    other_financing_activities: Optional[int] = Field(
        description="Other financing activities, net"
    )
    net_cash_flow_from_financing_activities: Optional[int] = Field(
        description="Net cash flow from financing activities."
    )
    net_change_in_cash: Optional[int] = Field(
        description="Net increase (decrease) in cash, cash equivalents, and restricted cash"
    )
