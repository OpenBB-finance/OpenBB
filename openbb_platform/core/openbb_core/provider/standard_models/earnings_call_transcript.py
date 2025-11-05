"""Earnings Call Transcript Standard Model."""

from datetime import date as dateType
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class EarningsCallTranscriptQueryParams(QueryParams):
    """Earnings Call Transcript rating Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    year: int | None = Field(
        default=None, description="Year of the earnings call transcript."
    )
    quarter: Literal[1, 2, 3, 4] | None = Field(
        default=None, description="Quarterly period of the earnings call transcript."
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EarningsCallTranscriptData(Data):
    """Earnings Call Transcript Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    year: int = Field(description="Year of the earnings call transcript.")
    quarter: str = Field(description="Quarter of the earnings call transcript.")
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    content: str = Field(description="Content of the earnings call transcript.")
