"""Balance Sheet Standard Model."""


from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Literal, Optional, Set, Union

from pydantic import Field, NonNegativeInt, StrictFloat, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class BalanceSheetQueryParams(QueryParams):
    """Balance Sheet Query."""

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


class BalanceSheetData(Data):
    """Balance Sheet Data."""

    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    cik: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("cik", ""),
    )
    currency: Optional[str] = Field(default=None, description="Reporting currency.")
    filling_date: Optional[dateType] = Field(default=None, description="Filling date.")
    accepted_date: Optional[datetime] = Field(
        default=None, description="Accepted date."
    )
    period: Optional[str] = Field(
        default=None, description="Reporting period of the statement."
    )

    cash_and_cash_equivalents: Optional[StrictFloat] = Field(
        default=None, description="Cash and cash equivalents"
    )
    short_term_investments: Optional[StrictFloat] = Field(
        default=None, description="Short-term investments"
    )
    long_term_investments: Optional[StrictFloat] = Field(
        default=None, description="Long-term investments"
    )

    inventory: Optional[StrictFloat] = Field(default=None, description="Inventory")
    net_receivables: Optional[StrictFloat] = Field(
        default=None, description="Receivables, net"
    )

    marketable_securities: Optional[StrictFloat] = Field(
        default=None, description="Marketable securities"
    )
    property_plant_equipment_net: Optional[StrictFloat] = Field(
        default=None, description="Property, plant and equipment, net"
    )
    goodwill: Optional[StrictFloat] = Field(default=None, description="Goodwill")

    assets: Optional[StrictFloat] = Field(default=None, description="Total assets")
    current_assets: Optional[StrictFloat] = Field(
        default=None, description="Total current assets"
    )
    other_current_assets: Optional[StrictFloat] = Field(
        default=None, description="Other current assets"
    )
    intangible_assets: Optional[StrictFloat] = Field(
        default=None, description="Intangible assets"
    )
    tax_assets: Optional[StrictFloat] = Field(
        default=None, description="Accrued income taxes"
    )
    non_current_assets: Optional[StrictFloat] = Field(
        default=None, description="Total non-current assets"
    )
    other_non_current_assets: Optional[StrictFloat] = Field(
        default=None, description="Other non-current assets"
    )

    account_payables: Optional[StrictFloat] = Field(
        default=None, description="Accounts payable"
    )
    tax_payables: Optional[StrictFloat] = Field(
        default=None, description="Accrued income taxes"
    )
    deferred_revenue: Optional[StrictFloat] = Field(
        default=None, description="Accrued income taxes, other deferred revenue"
    )
    other_assets: Optional[StrictFloat] = Field(
        default=None, description="Other assets"
    )
    total_assets: Optional[StrictFloat] = Field(
        default=None, description="Total assets"
    )

    long_term_debt: Optional[StrictFloat] = Field(
        default=None,
        description="Long-term debt, Operating lease obligations, Long-term finance lease obligations",
    )
    short_term_debt: Optional[StrictFloat] = Field(
        default=None,
        description="Short-term borrowings, Long-term debt due within one year, "
        "Operating lease obligations due within one year, "
        "Finance lease obligations due within one year",
    )

    liabilities: Optional[StrictFloat] = Field(
        default=None, description="Total liabilities"
    )
    other_current_liabilities: Optional[StrictFloat] = Field(
        default=None, description="Other current liabilities"
    )
    current_liabilities: Optional[StrictFloat] = Field(
        default=None, description="Total current liabilities"
    )
    total_liabilities_and_total_equity: Optional[StrictFloat] = Field(
        default=None, description="Total liabilities and total equity"
    )
    other_non_current_liabilities: Optional[StrictFloat] = Field(
        default=None, description="Other non-current liabilities"
    )
    non_current_liabilities: Optional[StrictFloat] = Field(
        default=None, description="Total non-current liabilities"
    )
    total_liabilities_and_stockholders_equity: Optional[StrictFloat] = Field(
        default=None, description="Total liabilities and stockholders' equity"
    )
    other_stockholder_equity: Optional[StrictFloat] = Field(
        default=None, description="Other stockholders equity"
    )
    total_stockholders_equity: Optional[StrictFloat] = Field(
        default=None, description="Total stockholders' equity"
    )
    other_liabilities: Optional[StrictFloat] = Field(
        default=None, description="Other liabilities"
    )
    total_liabilities: Optional[StrictFloat] = Field(
        default=None, description="Total liabilities"
    )

    common_stock: Optional[StrictFloat] = Field(
        default=None, description="Common stock"
    )
    preferred_stock: Optional[StrictFloat] = Field(
        default=None, description="Preferred stock"
    )

    accumulated_other_comprehensive_income_loss: Optional[StrictFloat] = Field(
        default=None, description="Accumulated other comprehensive income (loss)"
    )
    retained_earnings: Optional[StrictFloat] = Field(
        default=None, description="Retained earnings"
    )
    minority_interest: Optional[StrictFloat] = Field(
        default=None, description="Minority interest"
    )
    total_equity: Optional[StrictFloat] = Field(
        default=None, description="Total equity"
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)]) if v else None
