"""Equity Ownership Standard Model."""

from datetime import date as dateType
from typing import Optional, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class EquityOwnershipQueryParams(QueryParams):
    """Equity Ownership Query."""

    __validator_dict__ = {"check_single": ("symbol",)}

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def upper_symbol(cls, v: str) -> str:
        """Convert symbol to uppercase."""
        return v.upper()


class EquityOwnershipData(Data):
    """Equity Ownership Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    cik: Optional[Union[str, int]] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("cik", "")
    )
    filing_date: Optional[dateType] = Field(
        default=None, description="Filing date of the disclosure."
    )
    investor_name: Optional[str] = Field(
        default=None,
        description="Name of the investor.",
    )
    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    security_name: Optional[str] = Field(
        default=None,
        description="Name of the security.",
    )
    type_of_security: Optional[str] = Field(
        default=None,
        description="The type of security.",
    )
    security_cusip: Optional[str] = Field(
        default=None,
        description="CUSIP of the security.",
    )
    shares_type: Optional[str] = Field(
        default=None,
        description="The type of shares.",
    )
    put_call_share: Optional[str] = Field(
        default=None,
        description="Whether the security is a share, put or call.",
    )
    investment_discretion: Optional[str] = Field(
        default=None,
        description="Investment discretion of the ownership.",
    )
    industry_title: Optional[str] = Field(
        default=None,
        description="Industry title of the stock ownership.",
    )
    weight: Optional[float] = Field(
        default=None,
        description="Weight of ownership, as a normalized percentage.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    last_weight: Optional[float] = Field(
        default=None,
        description="The weight of ownership from the previous reporting period, as a normalized percentage.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    change_in_weight: Optional[float] = Field(
        default=None,
        description="Previous weight minus the current weight.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    change_in_weight_percent: Optional[float] = Field(
        default=None,
        description="The change as a percent of the weight, as a normalized percentage.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    market_value: Optional[int] = Field(
        default=None,
        description="Market value of the position.",
    )
    last_market_value: Optional[int] = Field(
        default=None,
        description="The previous report's market value.",
    )
    change_in_market_value: Optional[int] = Field(
        default=None,
        description="Change in market value from the previous report.",
    )
    change_in_market_value_percent: Optional[float] = Field(
        default=None,
        description="Percent change in market value, as a normalized percentage.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    shares_number: Optional[int] = Field(
        default=None,
        description="Number of shares owned.",
    )
    last_shares_number: Optional[int] = Field(
        default=None,
        description="The previous report's number of shares.",
    )
    change_in_shares_number: Optional[float] = Field(
        default=None,
        description="Change in the number of shares owned.",
    )
    change_in_shares_percent: Optional[float] = Field(
        default=None,
        description="Percent change in the number of shares owned, as a normalized percentage.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    quarter_end_price: Optional[float] = Field(
        default=None,
        description="End of quarter price of the security.",
    )
    avg_price_paid: Optional[float] = Field(
        default=None,
        description="Average price paid.",
    )
    is_new: Optional[bool] = Field(
        default=None,
        description="Is the stock ownership new.",
    )
    is_sold_out: Optional[bool] = Field(
        default=None,
        description="Is the position sold out.",
    )
    ownership: Optional[float] = Field(
        default=None,
        description="The ownership of the outstanding shares, as a normalized percentage.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    last_ownership: Optional[float] = Field(
        default=None,
        description="The ownership of the outstanding shares from the previous report,"
        + " as a normalized percentage.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    change_in_ownership: Optional[float] = Field(
        default=None,
        description="Change in ownership amount.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    change_in_ownership_percent: Optional[float] = Field(
        default=None,
        description="Percent change in ownership from the previous report, as a normalized percentage.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    holding_period: Optional[int] = Field(
        default=None,
        description="Holding period of the position.",
    )
    first_added: Optional[dateType] = Field(
        default=None,
        description="The first date of ownership.",
    )
    performance: Optional[float] = Field(
        default=None,
        description="Performance of the position in dollars.",
    )
    performance_percent: Optional[float] = Field(
        default=None,
        description="Performance of the position as a normalized percentage.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    last_performance: Optional[float] = Field(
        default=None,
        description="Performance of the position from the previous report.",
    )
    change_in_performance: Optional[float] = Field(
        default=None,
        description="Change in the performance value from the previous report.",
    )
    is_counted_for_performance: Optional[bool] = Field(
        default=None,
        description="Is the stock ownership counted for performance.",
    )
