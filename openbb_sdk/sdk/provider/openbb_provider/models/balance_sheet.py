"""Balance Sheet Data Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.models.base import FinancialStatementQueryParams

# IMPORT THIRD PARTY


class BalanceSheetQueryParams(FinancialStatementQueryParams):
    """Cash flow statement query."""


class BalanceSheetData(Data):
    """Return Balance Sheet Data."""

    date: dateType = Field(description="Date of the income statement.")
    symbol: str = Field(description="Symbol of the company.")
    cik: Optional[int] = Field(description="Central Index Key.")
    currency: Optional[str] = Field(description="Reporting currency.")
    filing_date: Optional[dateType] = Field(description="Filling date.")
    accepted_date: Optional[datetime] = Field(description="Accepted date.")
    period: Optional[str] = Field(description="Period of the income statement.")

    cash_and_cash_equivalents: Optional[int]
    short_term_investments: Optional[int]
    cash_and_short_term_investments: Optional[int]
    net_receivables: Optional[int]
    tax_assets: Optional[int]
    inventory: Optional[int]
    other_current_assets: Optional[int]
    current_assets: Optional[int]

    long_term_investments: Optional[int]
    property_plant_equipment_net: Optional[int]
    goodwill: Optional[int]
    intangible_assets: Optional[int]
    other_non_current_assets: Optional[int]
    noncurrent_assets: Optional[int]
    other_assets: Optional[int]
    assets: Optional[int]

    short_term_debt: Optional[int]
    tax_payables: Optional[int]
    account_payables: Optional[int]
    other_current_liabilities: Optional[int]
    deferred_revenue: Optional[int]
    current_liabilities: Optional[int]

    long_term_debt: Optional[int]
    other_non_current_liabilities: Optional[int]
    noncurrent_liabilities: Optional[int]
    other_liabilities: Optional[int]
    liabilities: Optional[int]

    common_stock: Optional[int]
    retained_earnings: Optional[int]
    accumulated_other_comprehensive_income_loss: Optional[int]
    total_stockholders_equity: Optional[int]
    minority_interest: Optional[int]
    total_equity: Optional[int]
    total_liabilities_and_stockholders_equity: Optional[int]
