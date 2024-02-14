"""Balance Sheet Statement Growth Standard Model."""

from datetime import date as dateType
from typing import List, Optional, Set, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class BalanceSheetGrowthQueryParams(QueryParams):
    """Balance Sheet Statement Growth Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    limit: int = Field(default=10, description=QUERY_DESCRIPTIONS.get("limit", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str):
        """Convert symbol to uppercase."""
        return v.upper()


class BalanceSheetGrowthData(Data):
    """Balance Sheet Statement Growth Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    period: str = Field(description="Reporting period.")
    growth_cash_and_cash_equivalents: float = Field(
        description="Growth rate of cash and cash equivalents."
    )
    growth_short_term_investments: float = Field(
        description="Growth rate of short-term investments."
    )
    growth_cash_and_short_term_investments: float = Field(
        description="Growth rate of cash and short-term investments."
    )
    growth_net_receivables: float = Field(description="Growth rate of net receivables.")
    growth_inventory: float = Field(description="Growth rate of inventory.")
    growth_other_current_assets: float = Field(
        description="Growth rate of other current assets."
    )
    growth_total_current_assets: float = Field(
        description="Growth rate of total current assets."
    )
    growth_property_plant_equipment_net: float = Field(
        description="Growth rate of net property, plant, and equipment."
    )
    growth_goodwill: float = Field(description="Growth rate of goodwill.")
    growth_intangible_assets: float = Field(
        description="Growth rate of intangible assets."
    )
    growth_goodwill_and_intangible_assets: float = Field(
        description="Growth rate of goodwill and intangible assets."
    )
    growth_long_term_investments: float = Field(
        description="Growth rate of long-term investments."
    )
    growth_tax_assets: float = Field(description="Growth rate of tax assets.")
    growth_other_non_current_assets: float = Field(
        description="Growth rate of other non-current assets."
    )
    growth_total_non_current_assets: float = Field(
        description="Growth rate of total non-current assets."
    )
    growth_other_assets: float = Field(description="Growth rate of other assets.")
    growth_total_assets: float = Field(description="Growth rate of total assets.")
    growth_account_payables: float = Field(
        description="Growth rate of accounts payable."
    )
    growth_short_term_debt: float = Field(description="Growth rate of short-term debt.")
    growth_tax_payables: float = Field(description="Growth rate of tax payables.")
    growth_deferred_revenue: float = Field(
        description="Growth rate of deferred revenue."
    )
    growth_other_current_liabilities: float = Field(
        description="Growth rate of other current liabilities."
    )
    growth_total_current_liabilities: float = Field(
        description="Growth rate of total current liabilities."
    )
    growth_long_term_debt: float = Field(description="Growth rate of long-term debt.")
    growth_deferred_revenue_non_current: float = Field(
        description="Growth rate of non-current deferred revenue."
    )
    growth_deferrred_tax_liabilities_non_current: float = Field(
        description="Growth rate of non-current deferred tax liabilities."
    )
    growth_other_non_current_liabilities: float = Field(
        description="Growth rate of other non-current liabilities."
    )
    growth_total_non_current_liabilities: float = Field(
        description="Growth rate of total non-current liabilities."
    )
    growth_other_liabilities: float = Field(
        description="Growth rate of other liabilities."
    )
    growth_total_liabilities: float = Field(
        description="Growth rate of total liabilities."
    )
    growth_common_stock: float = Field(description="Growth rate of common stock.")
    growth_retained_earnings: float = Field(
        description="Growth rate of retained earnings."
    )
    growth_accumulated_other_comprehensive_income_loss: float = Field(
        description="Growth rate of accumulated other comprehensive income/loss."
    )
    growth_othertotal_stockholders_equity: float = Field(
        description="Growth rate of other total stockholders' equity."
    )
    growth_total_stockholders_equity: float = Field(
        description="Growth rate of total stockholders' equity."
    )
    growth_total_liabilities_and_stockholders_equity: float = Field(
        description="Growth rate of total liabilities and stockholders' equity."
    )
    growth_total_investments: float = Field(
        description="Growth rate of total investments."
    )
    growth_total_debt: float = Field(description="Growth rate of total debt.")
    growth_net_debt: float = Field(description="Growth rate of net debt.")

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None
