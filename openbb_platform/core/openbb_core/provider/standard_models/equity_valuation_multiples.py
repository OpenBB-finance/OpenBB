"""Equity Valuation Multiples Standard Model."""

from datetime import date as dateType
from typing import Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EquityValuationMultiplesQueryParams(QueryParams):
    """Equity Valuation Multiples Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EquityValuationMultiplesData(Data):
    """Equity Valuation Multiples Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    period_ending: Optional[dateType] = Field(
        default=None, description="End date of the reporting period."
    )
    fiscal_year: Optional[int] = Field(
        default=None, description="Fiscal year for the fiscal period, if available."
    )
    fiscal_period: Optional[str] = Field(
        default=None, description="Fiscal period for the data, if available."
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency in which the data is reported.",
    )
    market_cap: Optional[Union[int, float]] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("market_cap", "")
    )
    enterprise_value: Optional[Union[int, float]] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("enterprise_value", "")
    )
