"""Balance Sheet Data Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.standard_models.base import FinancialStatementQueryParams

# IMPORT THIRD PARTY


class BalanceSheetQueryParams(FinancialStatementQueryParams):
    """Balance Sheet query."""


class BalanceSheetData(Data):
    """Balance Sheet Data."""

    date: dateType = Field(description="Date of the fetched statement.")
    symbol: Optional[str] = Field(description="Symbol of the company.")
    cik: Optional[int] = Field(description="Central Index Key.")
    currency: Optional[str] = Field(description="Reporting currency.")
    filing_date: Optional[dateType] = Field(description="Filling date.")
    accepted_date: Optional[datetime] = Field(description="Accepted date.")
    period: Optional[str] = Field(description="Reporting period of the statement.")

    cash_and_cash_equivalents: Optional[int] = Field(
        description="Cash and cash equivalents"
    )
    short_term_investments: Optional[int] = Field(description="Short-term investments")
    inventory: Optional[int] = Field(description="Inventory")
    net_receivables: Optional[int] = Field(description="Receivables, net")
    other_current_assets: Optional[int] = Field(description="Other current assets")
    current_assets: Optional[int] = Field(description="Total current assets")

    long_term_investments: Optional[int] = Field(description="Long-term investments")
    property_plant_equipment_net: Optional[int] = Field(
        description="Property, plant and equipment, net"
    )
    goodwill: Optional[int] = Field(description="Goodwill")
    intangible_assets: Optional[int] = Field(description="Intangible assets")
    other_non_current_assets: Optional[int] = Field(
        description="Other non-current assets"
    )
    tax_assets: Optional[int] = Field(description="Accrued income taxes")
    other_assets: Optional[int] = Field(description="Other assets")
    noncurrent_assets: Optional[int]
    assets: Optional[int]

    account_payables: Optional[int]
    other_current_liabilities: Optional[int]
    tax_payables: Optional[int] = Field(description="Accrued income taxes")
    deferred_revenue: Optional[int] = Field(
        description="Accrued income taxes, other deferred revenue"
    )
    short_term_debt: Optional[int] = Field(
        description="Short-term borrowings, Long-term debt due within one year, "
        "Operating lease obligations due within one year, "
        "Finance lease obligations due within one year"
    )
    current_liabilities: Optional[int]

    long_term_debt: Optional[int] = Field(
        description="Long-term debt, Operating lease obligations, Long-term finance lease obligations"
    )
    other_non_current_liabilities: Optional[int] = Field(
        description="Deferred income taxes and other"
    )
    other_liabilities: Optional[int]
    noncurrent_liabilities: Optional[int]
    liabilities: Optional[int]

    common_stock: Optional[int]
    other_stockholder_equity: Optional[int] = Field(
        description="Capital in excess of par value"
    )

    accumulated_other_comprehensive_income_loss: Optional[int] = Field(
        description="Accumulated other comprehensive income (loss)"
    )
    preferred_stock: Optional[int] = Field(description="Preferred stock")
    retained_earnings: Optional[int] = Field(description="Retained earnings")
    minority_interest: Optional[int] = Field(description="Minority interest")
    total_stockholders_equity: Optional[int]
    total_equity: Optional[int]
    total_liabilities_and_stockholders_equity: Optional[int]
    total_liabilities_and_total_equity: Optional[int]
