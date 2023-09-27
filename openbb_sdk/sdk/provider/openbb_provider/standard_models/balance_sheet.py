"""Balance Sheet Data Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, NonNegativeInt, field_validator, validator

from openbb_provider.abstract.data import Data, StrictInt
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class BalanceSheetQueryParams(QueryParams):
    """Balance Sheet query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: Literal["annual", "quarter"] = Field(
        default="annual", description=QUERY_DESCRIPTIONS.get("period", "")
    )
    limit: NonNegativeInt = Field(
        default=12, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class BalanceSheetData(Data):
    """Balance Sheet Data."""

    symbol: Optional[str] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("symbol", "")
    )
    date: dateType = Field(description="Date of the fetched statement.")
    cik: Optional[str] = Field(
        default=None, description="Central Index Key (CIK) of the company."
    )
    currency: Optional[str] = Field(default=None, description="Reporting currency.")
    filling_date: Optional[dateType] = Field(default=None, description="Filling date.")
    accepted_date: Optional[datetime] = Field(
        default=None, description="Accepted date."
    )
    period: Optional[str] = Field(
        default=None, description="Reporting period of the statement."
    )

    cash_and_cash_equivalents: Optional[StrictInt] = Field(
        default=None, description="Cash and cash equivalents"
    )
    short_term_investments: Optional[StrictInt] = Field(
        default=None, description="Short-term investments"
    )
    long_term_investments: Optional[StrictInt] = Field(
        default=None, description="Long-term investments"
    )

    inventory: Optional[StrictInt] = Field(default=None, description="Inventory")
    net_receivables: Optional[StrictInt] = Field(
        default=None, description="Receivables, net"
    )

    marketable_securities: Optional[StrictInt] = Field(
        default=None, description="Marketable securities"
    )
    property_plant_equipment_net: Optional[StrictInt] = Field(
        default=None, description="Property, plant and equipment, net"
    )
    goodwill: Optional[StrictInt] = Field(default=None, description="Goodwill")

    assets: Optional[StrictInt] = Field(default=None, description="Total assets")
    current_assets: Optional[StrictInt] = Field(
        default=None, description="Total current assets"
    )
    other_current_assets: Optional[StrictInt] = Field(
        default=None, description="Other current assets"
    )
    intangible_assets: Optional[StrictInt] = Field(
        default=None, description="Intangible assets"
    )
    tax_assets: Optional[StrictInt] = Field(
        default=None, description="Accrued income taxes"
    )
    other_assets: Optional[StrictInt] = Field(default=None, description="Other assets")
    non_current_assets: Optional[StrictInt] = Field(
        default=None, description="Total non-current assets"
    )
    other_non_current_assets: Optional[StrictInt] = Field(
        default=None, description="Other non-current assets"
    )

    account_payables: Optional[StrictInt] = Field(
        default=None, description="Accounts payable"
    )
    tax_payables: Optional[StrictInt] = Field(
        default=None, description="Accrued income taxes"
    )
    deferred_revenue: Optional[StrictInt] = Field(
        default=None, description="Accrued income taxes, other deferred revenue"
    )
    other_assets: Optional[StrictInt] = Field(default=None, description="Other assets")
    total_assets: Optional[StrictInt] = Field(default=None, description="Total assets")

    long_term_debt: Optional[StrictInt] = Field(
        default=None,
        description="Long-term debt, Operating lease obligations, Long-term finance lease obligations",
    )
    short_term_debt: Optional[StrictInt] = Field(
        default=None,
        description="Short-term borrowings, Long-term debt due within one year, "
        "Operating lease obligations due within one year, "
        "Finance lease obligations due within one year",
    )

    liabilities: Optional[StrictInt] = Field(
        default=None, description="Total liabilities"
    )
    other_current_liabilities: Optional[StrictInt] = Field(
        default=None, description="Other current liabilities"
    )
    current_liabilities: Optional[StrictInt] = Field(
        default=None, description="Total current liabilities"
    )
    total_liabilities_and_total_equity: Optional[StrictInt] = Field(
        default=None, description="Total liabilities and total equity"
    )
    other_liabilities: Optional[StrictInt] = Field(
        default=None, description="Other liabilities"
    )
    other_non_current_liabilities: Optional[StrictInt] = Field(
        default=None, description="Other non-current liabilities"
    )
    non_current_liabilities: Optional[StrictInt] = Field(
        default=None, description="Total non-current liabilities"
    )
    total_liabilities_and_stockholders_equity: Optional[StrictInt] = Field(
        default=None, description="Total liabilities and stockholders' equity"
    )
    other_stockholder_equity: Optional[StrictInt] = Field(
        default=None, description="Other stockholders equity"
    )
    total_stockholders_equity: Optional[StrictInt] = Field(
        default=None, description="Total stockholders' equity"
    )
    other_liabilities: Optional[StrictInt] = Field(
        default=None, description="Other liabilities"
    )
    total_liabilities: Optional[StrictInt] = Field(
        default=None, description="Total liabilities"
    )

    common_stock: Optional[StrictInt] = Field(default=None, description="Common stock")
    preferred_stock: Optional[StrictInt] = Field(
        default=None, description="Preferred stock"
    )

    accumulated_other_comprehensive_income_loss: Optional[StrictInt] = Field(
        default=None, description="Accumulated other comprehensive income (loss)"
    )
    retained_earnings: Optional[StrictInt] = Field(
        default=None, description="Retained earnings"
    )
    minority_interest: Optional[StrictInt] = Field(
        default=None, description="Minority interest"
    )
    total_equity: Optional[StrictInt] = Field(default=None, description="Total equity")

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None
