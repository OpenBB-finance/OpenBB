"""Historical Splits Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class HistoricalSplitsQueryParams(QueryParams):
    """Historical Splits Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class HistoricalSplitsData(Data):
    """Historical Splits Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    numerator: float | None = Field(
        default=None,
        description="Numerator of the split.",
    )
    denominator: float | None = Field(
        default=None,
        description="Denominator of the split.",
    )
    split_ratio: str | None = Field(
        default=None,
        description="Split ratio.",
    )
