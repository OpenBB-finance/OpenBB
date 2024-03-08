"""Cash Flow Statement Growth Standard Model."""

import warnings
from datetime import date as dateType
from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)

_warn = warnings.warn


class CashFlowStatementGrowthQueryParams(QueryParams):
    """Cash Flow Statement Growth Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: str = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: int = Field(default=10, description=QUERY_DESCRIPTIONS.get("limit", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class CashFlowStatementGrowthData(Data):
    """Cash Flow Statement Growth Data. All values are normalized percent changes from the previous period."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    period_ending: dateType = Field(description="Data for the fiscal period ending.")
    fiscal_year: Optional[int] = Field(
        default=None, description="Fiscal year of the fiscal period."
    )
    fiscal_period: Optional[str] = Field(
        default=None, description="Fiscal period of the fiscal year."
    )
    growth_net_income: Optional[float] = Field(
        default=None,
        description="Growth rate of net income.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_depreciation_and_amortization: Optional[float] = Field(
        default=None,
        description="Growth rate of depreciation and amortization.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_deferred_income_tax: Optional[float] = Field(
        default=None,
        description="Growth rate of deferred income tax.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_stock_based_compensation: Optional[float] = Field(
        default=None,
        description="Growth rate of stock-based compensation.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_change_in_working_capital: Optional[float] = Field(
        default=None,
        description="Growth rate of change in working capital.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_accounts_receivables: Optional[float] = Field(
        default=None,
        description="Growth rate of accounts receivables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_inventory: Optional[float] = Field(
        default=None,
        description="Growth rate of inventory.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_accounts_payables: Optional[float] = Field(
        default=None,
        description="Growth rate of accounts payables.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_working_capital: Optional[float] = Field(
        default=None,
        description="Growth rate of other working capital.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_non_cash_items: Optional[float] = Field(
        default=None,
        description="Growth rate of other non-cash items.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_cash_provided_by_operating_activities: Optional[float] = Field(
        default=None,
        description="Growth rate of net cash provided by operating activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_investments_in_property_plant_and_equipment: Optional[float] = Field(
        default=None,
        description="Growth rate of investments in property, plant, and equipment.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_acquisitions_net: Optional[float] = Field(
        default=None,
        description="Growth rate of net acquisitions.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_purchases_of_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of purchases of investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_sales_maturities_of_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of sales maturities of investments.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_investing_activities: Optional[float] = Field(
        default=None,
        description="Growth rate of other investing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_cash_used_for_investing_activities: Optional[float] = Field(
        default=None,
        description="Growth rate of net cash used for investing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_debt_repayment: Optional[float] = Field(
        default=None,
        description="Growth rate of debt repayment.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_common_stock_issued: Optional[float] = Field(
        default=None,
        description="Growth rate of common stock issued.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_common_stock_repurchased: Optional[float] = Field(
        default=None,
        description="Growth rate of common stock repurchased.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_dividends_paid: Optional[float] = Field(
        default=None,
        description="Growth rate of dividends paid.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_other_financing_activities: Optional[float] = Field(
        default=None,
        description="Growth rate of other financing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_cash_used_provided_by_financing_activities: Optional[float] = Field(
        default=None,
        description="Growth rate of net cash used/provided by financing activities.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_effect_of_forex_changes_on_cash: Optional[float] = Field(
        default=None,
        description="Growth rate of the effect of foreign exchange changes on cash.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_net_change_in_cash: Optional[float] = Field(
        default=None,
        description="Growth rate of net change in cash.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cash_at_end_of_period: Optional[float] = Field(
        default=None,
        description="Growth rate of cash at the end of the period.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_cash_at_beginning_of_period: Optional[float] = Field(
        default=None,
        description="Growth rate of cash at the beginning of the period.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_operating_cash_flow: Optional[float] = Field(
        default=None,
        description="Growth rate of operating cash flow.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_capital_expenditure: Optional[float] = Field(
        default=None,
        description="Growth rate of capital expenditure.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    growth_free_cash_flow: Optional[float] = Field(
        default=None,
        description="Growth rate of free cash flow.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
