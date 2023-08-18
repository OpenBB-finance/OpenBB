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
    long_term_investments: Optional[int] = Field(description="Long-term investments")

    inventory: Optional[int] = Field(description="Inventory")
    net_receivables: Optional[int] = Field(description="Receivables, net")

    property_plant_equipment_net: Optional[int] = Field(
        description="Property, plant and equipment, net"
    )
    goodwill: Optional[int] = Field(description="Goodwill")

    assets: Optional[int] = Field(description="Total assets")
    current_assets: Optional[int] = Field(description="Total current assets")
    other_current_assets: Optional[int] = Field(description="Other current assets")
    intangible_assets: Optional[int] = Field(description="Intangible assets")
    tax_assets: Optional[int] = Field(description="Accrued income taxes")
    other_assets: Optional[int] = Field(description="Other assets")
    non_current_assets: Optional[int] = Field(description="Total non-current assets")
    other_non_current_assets: Optional[int] = Field(
        description="Other non-current assets"
    )

    account_payables: Optional[int] = Field(description="Accounts payable")
    tax_payables: Optional[int] = Field(description="Accrued income taxes")
    deferred_revenue: Optional[int] = Field(
        description="Accrued income taxes, other deferred revenue"
    )

    long_term_debt: Optional[int] = Field(
        description="Long-term debt, Operating lease obligations, Long-term finance lease obligations"
    )
    short_term_debt: Optional[int] = Field(
        description="Short-term borrowings, Long-term debt due within one year, "
        "Operating lease obligations due within one year, "
        "Finance lease obligations due within one year"
    )

    liabilities: Optional[int] = Field(description="Total liabilities")
    other_current_liabilities: Optional[int] = Field(
        description="Other current liabilities"
    )
    current_liabilities: Optional[int] = Field(description="Total current liabilities")
    total_liabilities_and_total_equity: Optional[int] = Field(
        description="Total liabilities and total equity"
    )
    other_liabilities: Optional[int] = Field(description="Other liabilities")
    other_non_current_liabilities: Optional[int] = Field(
        description="Other non-current liabilities"
    )
    non_current_liabilities: Optional[int] = Field(
        description="Total non-current liabilities"
    )
    total_liabilities_and_stockholders_equity: Optional[int] = Field(
        description="Total liabilities and stockholders' equity"
    )
    other_stockholder_equity: Optional[int] = Field(
        description="Capital in excess of par value"
    )
    total_stockholders_equity: Optional[int] = Field(
        description="Total stockholders' equity"
    )

    common_stock: Optional[int] = Field(description="Common stock")
    preferred_stock: Optional[int] = Field(description="Preferred stock")

    accumulated_other_comprehensive_income_loss: Optional[int] = Field(
        description="Accumulated other comprehensive income (loss)"
    )
    retained_earnings: Optional[int] = Field(description="Retained earnings")
    minority_interest: Optional[int] = Field(description="Minority interest")
    total_equity: Optional[int] = Field(description="Total equity")
