"""Balance Sheet Statement Growth Standard Model."""

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

class BalanceSheetGrowthQueryParams(QueryParams):
    """Balance Sheet Statement Growth Query. All values are normalized percent changes from the previous period."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: str = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: int = Field(default=10, description=QUERY_DESCRIPTIONS.get("limit", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str):
        """Convert symbol to uppercase."""
        if "," in v:
            _warn(
                f"{QUERY_DESCRIPTIONS.get('symbol_list_warning', '')} {v.split(',')[0].upper()}"
            )
        return v.split(",")[0].upper() if "," in v else v.upper()


class BalanceSheetGrowthData(Data):
    """Balance Sheet Statement Growth Data. All values are normalized percent changes from the previous period."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    period_ending: dateType = Field(description="Data for the fiscal period ending.")
    fiscal_year: Optional[int] = Field(default= None, description="Fiscal year of the fiscal period.")
    fiscal_period: Optional[str] = Field(default=None, description="Fiscal period of the fiscal year.")
    growth_cash_and_cash_equivalents: Optional[float] = Field(
        default=None,
        description="Growth rate of cash and cash equivalents.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_short_term_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of short-term investments.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_cash_and_short_term_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of cash and short-term investments.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_net_receivables: Optional[float] = Field(
        default=None,
        description="Growth rate of net receivables.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_inventory: Optional[float] = Field(
        default=None,
        description="Growth rate of inventory.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_other_current_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of other current assets.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_current_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of total current assets.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_property_plant_equipment_net: Optional[float] = Field(
        default=None,
        description="Growth rate of net property, plant, and equipment.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_goodwill: Optional[float] = Field(
        default=None,
        description="Growth rate of goodwill.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_intangible_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of intangible assets.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_goodwill_and_intangible_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of goodwill and intangible assets.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_long_term_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of long-term investments.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_tax_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of tax assets.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_other_non_current_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of other non-current assets.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_non_current_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of total non-current assets.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_other_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of other assets.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_assets: Optional[float] = Field(
        default=None,
        description="Growth rate of total assets.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_account_payables: Optional[float] = Field(
        default=None,
        description="Growth rate of accounts payable.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_short_term_debt: Optional[float] = Field(
        default=None,
        description="Growth rate of short-term debt.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_tax_payables: Optional[float] = Field(
        default=None,
        description="Growth rate of tax payables.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_deferred_revenue: Optional[float] = Field(
        default=None,
        description="Growth rate of deferred revenue.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_other_current_liabilities: Optional[float] = Field(
        default=None,
        description="Growth rate of other current liabilities.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_current_liabilities: Optional[float] = Field(
        default=None,
        description="Growth rate of total current liabilities.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_long_term_debt: Optional[float] = Field(
        default=None,
        description="Growth rate of long-term debt.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_deferred_revenue_non_current: Optional[float] = Field(
        default=None,
        description="Growth rate of non-current deferred revenue.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_deferrred_tax_liabilities_non_current: Optional[float] = Field(
        default=None,
        description="Growth rate of non-current deferred tax liabilities.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_other_non_current_liabilities: Optional[float] = Field(
        default=None,
        description="Growth rate of other non-current liabilities.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_non_current_liabilities: Optional[float] = Field(
        default=None,
        description="Growth rate of total non-current liabilities.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_other_liabilities: Optional[float] = Field(
        default=None,
        description="Growth rate of other liabilities.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_liabilities: Optional[float] = Field(
        default=None,
        description="Growth rate of total liabilities.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_common_stock: Optional[float] = Field(
        default=None,
        description="Growth rate of common stock.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_retained_earnings: Optional[float] = Field(
        default=None,
        description="Growth rate of retained earnings.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_accumulated_other_comprehensive_income: Optional[float] = Field(
        default=None,
        description="Growth rate of accumulated other comprehensive income/loss.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_other_total_shareholders_equity: Optional[float] = Field(
        default=None,
        description="Growth rate of other total shareholders' equity.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_shareholders_equity: Optional[float] = Field(
        default=None,
        description="Growth rate of total shareholders' equity.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_liabilities_and_shareholders_equity: Optional[float] = Field(
        default=None,
        description="Growth rate of total liabilities and shareholders' equity.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_investments: Optional[float] = Field(
        default=None,
        description="Growth rate of total investments.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_total_debt: Optional[float] = Field(
        default=None,
        description="Growth rate of total debt.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    growth_net_debt: Optional[float] = Field(
        default=None,
        description="Growth rate of net debt.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
