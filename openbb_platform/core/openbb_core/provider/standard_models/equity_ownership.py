"""Equity Ownership Standard Model."""

from datetime import date as dateType

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

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EquityOwnershipData(Data):
    """Equity Ownership Data."""

    investor_name: str = Field(description="Investing entity's name.")
    cik: str | None = Field(default=None, description=DATA_DESCRIPTIONS.get("cik", ""))
    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", "") + " For the period ending."
    )
    filing_date: dateType | None = Field(description="Date when reported.")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
