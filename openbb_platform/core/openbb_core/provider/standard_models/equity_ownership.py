"""Equity Ownership Standard Model."""

from datetime import date as dateType
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EquityOwnershipQueryParams(QueryParams):
    """Equity Ownership Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("date", "")
    )
    page: Optional[int] = Field(
        default=0, description="Page number of the data to fetch."
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def time_validate(cls, v: str):
        """Validate the date."""
        if v is None:
            v = dateType.today()

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EquityOwnershipData(Data):
    """Equity Ownership Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    cik: int = Field(description=DATA_DESCRIPTIONS.get("cik", ""))
    filing_date: dateType = Field(description="Filing date of the stock ownership.")
    investor_name: str = Field(
        ...,
        description="Investor name of the stock ownership.",
    )
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    security_name: str = Field(
        ...,
        description="Security name of the stock ownership.",
    )
    type_of_security: str = Field(
        ...,
        description="Type of security of the stock ownership.",
    )
    security_cusip: str = Field(
        ...,
        description="Security cusip of the stock ownership.",
    )
    shares_type: str = Field(description="Shares type of the stock ownership.")
    put_call_share: str = Field(
        ...,
        description="Put call share of the stock ownership.",
    )
    investment_discretion: str = Field(
        ...,
        description="Investment discretion of the stock ownership.",
    )
    industry_title: str = Field(
        ...,
        description="Industry title of the stock ownership.",
    )
    weight: float = Field(description="Weight of the stock ownership.")
    last_weight: float = Field(description="Last weight of the stock ownership.")
    change_in_weight: float = Field(
        ...,
        description="Change in weight of the stock ownership.",
    )
    change_in_weight_percentage: float = Field(
        ...,
        description="Change in weight percentage of the stock ownership.",
    )
    market_value: int = Field(description="Market value of the stock ownership.")
    last_market_value: int = Field(
        ...,
        description="Last market value of the stock ownership.",
    )
    change_in_market_value: int = Field(
        ...,
        description="Change in market value of the stock ownership.",
    )
    change_in_market_value_percentage: float = Field(
        ...,
        description="Change in market value percentage of the stock ownership.",
    )
    shares_number: int = Field(
        ...,
        description="Shares number of the stock ownership.",
    )
    last_shares_number: int = Field(
        ...,
        description="Last shares number of the stock ownership.",
    )
    change_in_shares_number: float = Field(
        ...,
        description="Change in shares number of the stock ownership.",
    )
    change_in_shares_number_percentage: float = Field(
        ...,
        description="Change in shares number percentage of the stock ownership.",
    )
    quarter_end_price: float = Field(
        ...,
        description="Quarter end price of the stock ownership.",
    )
    avg_price_paid: float = Field(
        ...,
        description="Average price paid of the stock ownership.",
    )
    is_new: bool = Field(description="Is the stock ownership new.")
    is_sold_out: bool = Field(description="Is the stock ownership sold out.")
    ownership: float = Field(description="How much is the ownership.")
    last_ownership: float = Field(description="Last ownership amount.")
    change_in_ownership: float = Field(description="Change in ownership amount.")
    change_in_ownership_percentage: float = Field(
        ...,
        description="Change in ownership percentage.",
    )
    holding_period: int = Field(
        ...,
        description="Holding period of the stock ownership.",
    )
    first_added: dateType = Field(
        ...,
        description="First added date of the stock ownership.",
    )
    performance: float = Field(description="Performance of the stock ownership.")
    performance_percentage: float = Field(
        ...,
        description="Performance percentage of the stock ownership.",
    )
    last_performance: float = Field(
        ...,
        description="Last performance of the stock ownership.",
    )
    change_in_performance: float = Field(
        ...,
        description="Change in performance of the stock ownership.",
    )
    is_counted_for_performance: bool = Field(
        ...,
        description="Is the stock ownership counted for performance.",
    )
