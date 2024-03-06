"""Cash Flow Statement Growth Standard Model."""

from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class CashFlowStatementGrowthQueryParams(QueryParams):
    """Cash Flow Statement Growth Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: int = Field(default=10, description=QUERY_DESCRIPTIONS.get("limit", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class CashFlowStatementGrowthData(Data):
    """Cash Flow Statement Growth Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    period: str = Field(description="Period the statement is returned for.")
    growth_net_income: float = Field(description="Growth rate of net income.")
    growth_depreciation_and_amortization: float = Field(
        description="Growth rate of depreciation and amortization."
    )
    growth_deferred_income_tax: float = Field(
        description="Growth rate of deferred income tax."
    )
    growth_stock_based_compensation: float = Field(
        description="Growth rate of stock-based compensation."
    )
    growth_change_in_working_capital: float = Field(
        description="Growth rate of change in working capital."
    )
    growth_accounts_receivables: float = Field(
        description="Growth rate of accounts receivables."
    )
    growth_inventory: float = Field(description="Growth rate of inventory.")
    growth_accounts_payables: float = Field(
        description="Growth rate of accounts payables."
    )
    growth_other_working_capital: float = Field(
        description="Growth rate of other working capital."
    )
    growth_other_non_cash_items: float = Field(
        description="Growth rate of other non-cash items."
    )
    growth_net_cash_provided_by_operating_activities: float = Field(
        description="Growth rate of net cash provided by operating activities."
    )
    growth_investments_in_property_plant_and_equipment: float = Field(
        description="Growth rate of investments in property, plant, and equipment."
    )
    growth_acquisitions_net: float = Field(
        description="Growth rate of net acquisitions."
    )
    growth_purchases_of_investments: float = Field(
        description="Growth rate of purchases of investments."
    )
    growth_sales_maturities_of_investments: float = Field(
        description="Growth rate of sales maturities of investments."
    )
    growth_other_investing_activities: float = Field(
        description="Growth rate of other investing activities."
    )
    growth_net_cash_used_for_investing_activities: float = Field(
        description="Growth rate of net cash used for investing activities."
    )
    growth_debt_repayment: float = Field(description="Growth rate of debt repayment.")
    growth_common_stock_issued: float = Field(
        description="Growth rate of common stock issued."
    )
    growth_common_stock_repurchased: float = Field(
        description="Growth rate of common stock repurchased."
    )
    growth_dividends_paid: float = Field(description="Growth rate of dividends paid.")
    growth_other_financing_activities: float = Field(
        description="Growth rate of other financing activities."
    )
    growth_net_cash_used_provided_by_financing_activities: float = Field(
        description="Growth rate of net cash used/provided by financing activities."
    )
    growth_effect_of_forex_changes_on_cash: float = Field(
        description="Growth rate of the effect of foreign exchange changes on cash."
    )
    growth_net_change_in_cash: float = Field(
        description="Growth rate of net change in cash."
    )
    growth_cash_at_end_of_period: float = Field(
        description="Growth rate of cash at the end of the period."
    )
    growth_cash_at_beginning_of_period: float = Field(
        description="Growth rate of cash at the beginning of the period."
    )
    growth_operating_cash_flow: float = Field(
        description="Growth rate of operating cash flow."
    )
    growth_capital_expenditure: float = Field(
        description="Growth rate of capital expenditure."
    )
    growth_free_cash_flow: float = Field(description="Growth rate of free cash flow.")

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: Union[str, List[str], Set[str]]):
        """Convert field to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None
