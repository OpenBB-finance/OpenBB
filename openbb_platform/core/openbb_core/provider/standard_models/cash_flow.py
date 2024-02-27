"""Cash Flow Statement Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field, NonNegativeInt, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS


class CashFlowStatementQueryParams(QueryParams):
    """Cash Flow Statement Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    period: str = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[NonNegativeInt] = Field(
        default=5, description=QUERY_DESCRIPTIONS.get("limit", "")
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str):
        """Convert symbol to uppercase."""
        return v.upper()


class CashFlowStatementData(Data):
    """Cash Flow Statement Data."""

    period_ending: dateType = Field(description="The end date of the reporting period.")
    fiscal_period: Optional[str] = Field(
        description="The fiscal period of the report.", default=None
    )
    fiscal_year: Optional[int] = Field(
        description="The fiscal year of the fiscal period.", default=None
    )
    purchase_of_investment_securities: Optional[float] = Field(
        default=None, description="Purchase of Investment Securities"
    )
    net_cash_from_operating_activities: Optional[float] = Field(
        default=None,
        description="Net cash from operating activities.",
    )
    purchase_of_property_plant_and_equipment: Optional[float] = Field(
        default=None,
        description="Purchase of property, plant and equipment.",
    )
    repurchase_of_common_equity: Optional[float] = Field(
        default=None,
        description="Repurchase of common equity.",
    )
    growth_other_financing_activities: Optional[float] = Field(
        description="Growth rate of other financing activities."
    )
    acquisitions: Optional[float] = Field(
        default=None,
        description="Acquisitions.",
    )
    net_income: Optional[float] = Field(
        default=None,
        description="Net income.",
    )
    net_change_in_cash_and_equivalents: Optional[float] = Field(
        default=None, description="Net Change in Cash and Equivalents"
    )
    repayment_of_debt: Optional[float] = Field(
        default=None, description="Repayment of Debt"
    )
    net_cash_from_investing_activities: Optional[float] = Field(
        default=None,
        description="Net cash from investing activities.",
    )
    payment_of_dividends: Optional[float] = Field(
        default=None,
        description="Payment of dividends.",
    )
    net_cash_from_financing_activities: Optional[float] = Field(
        default=None,
        description="Net cash from financing activities.",
    )
    reported_currency: Optional[str] = Field(
        default=None,
        description="The currency in which the cash flow statement was reported.",
    )
    other_investing_activities: Optional[float] = Field(
        default=None, description="Other Investing Activities."
    )
    sale_and_maturity_of_investments: Optional[float] = Field(
        default=None, description="Sale and Maturity of Investments."
    )
    issuance_of_common_equity: Optional[float] = Field(
        default=None, description="Issuance of Common Equity"
    )
