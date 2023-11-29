"""Cash Flow Statement Standard Model."""


from datetime import date as dateType
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, NonNegativeInt, StrictFloat, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class CashFlowStatementQueryParams(QueryParams):
    """Cash Flow Statement Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: Optional[Literal["annual", "quarter"]] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[NonNegativeInt] = Field(
        default=5, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    # pylint: disable=inconsistent-return-statements
    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            if v.isdigit() or v.isalpha():
                return v.upper()
            raise ValueError(f"Invalid symbol: {v}. Must be either a ticker or CIK.")
        if isinstance(v, List):
            symbols = []
            for symbol in v:
                if symbol.isdigit() or symbol.isalpha():
                    symbols.append(symbol.upper())
                else:
                    raise ValueError(
                        f"Invalid symbol: {symbol}. Must be either a ticker or CIK."
                    )
            return ",".join(symbols)


class CashFlowStatementData(Data):
    """Cash Flow Statement Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date" ""))
    period: Optional[str] = Field(
        default=None, description="Reporting period of the statement."
    )
    cik: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )

    net_income: Optional[StrictFloat] = Field(default=None, description="Net income.")

    depreciation_and_amortization: Optional[StrictFloat] = Field(
        default=None, description="Depreciation and amortization."
    )
    stock_based_compensation: Optional[StrictFloat] = Field(
        default=None, description="Stock based compensation."
    )
    deferred_income_tax: Optional[StrictFloat] = Field(
        default=None, description="Deferred income tax."
    )
    other_non_cash_items: Optional[StrictFloat] = Field(
        default=None, description="Other non-cash items."
    )
    changes_in_operating_assets_and_liabilities: Optional[StrictFloat] = Field(
        default=None, description="Changes in operating assets and liabilities."
    )

    accounts_receivables: Optional[StrictFloat] = Field(
        default=None, description="Accounts receivables."
    )
    inventory: Optional[StrictFloat] = Field(default=None, description="Inventory.")
    vendor_non_trade_receivables: Optional[StrictFloat] = Field(
        default=None, description="Vendor non-trade receivables."
    )
    other_current_and_non_current_assets: Optional[StrictFloat] = Field(
        default=None, description="Other current and non-current assets."
    )
    accounts_payables: Optional[StrictFloat] = Field(
        default=None, description="Accounts payables."
    )
    deferred_revenue: Optional[StrictFloat] = Field(
        default=None, description="Deferred revenue."
    )
    other_current_and_non_current_liabilities: Optional[StrictFloat] = Field(
        default=None, description="Other current and non-current liabilities."
    )
    net_cash_flow_from_operating_activities: Optional[StrictFloat] = Field(
        default=None, description="Net cash flow from operating activities."
    )

    purchases_of_marketable_securities: Optional[StrictFloat] = Field(
        default=None, description="Purchases of investments."
    )
    sales_from_maturities_of_investments: Optional[StrictFloat] = Field(
        default=None, description="Sales and maturities of investments."
    )
    investments_in_property_plant_and_equipment: Optional[StrictFloat] = Field(
        default=None, description="Investments in property, plant, and equipment."
    )
    payments_from_acquisitions: Optional[StrictFloat] = Field(
        default=None, description="Acquisitions, net of cash acquired, and other"
    )
    other_investing_activities: Optional[StrictFloat] = Field(
        default=None, description="Other investing activities"
    )
    net_cash_flow_from_investing_activities: Optional[StrictFloat] = Field(
        default=None, description="Net cash used for investing activities."
    )

    taxes_paid_on_net_share_settlement: Optional[StrictFloat] = Field(
        default=None, description="Taxes paid on net share settlement of equity awards."
    )
    dividends_paid: Optional[StrictFloat] = Field(
        default=None, description="Payments for dividends and dividend equivalents"
    )
    common_stock_repurchased: Optional[StrictFloat] = Field(
        default=None, description="Payments related to repurchase of common stock"
    )
    debt_proceeds: Optional[StrictFloat] = Field(
        default=None, description="Proceeds from issuance of term debt"
    )
    debt_repayment: Optional[StrictFloat] = Field(
        default=None, description="Payments of long-term debt"
    )
    other_financing_activities: Optional[StrictFloat] = Field(
        default=None, description="Other financing activities, net"
    )
    net_cash_flow_from_financing_activities: Optional[StrictFloat] = Field(
        default=None, description="Net cash flow from financing activities."
    )
    net_change_in_cash: Optional[StrictFloat] = Field(
        default=None,
        description="Net increase (decrease) in cash, cash equivalents, and restricted cash",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None
