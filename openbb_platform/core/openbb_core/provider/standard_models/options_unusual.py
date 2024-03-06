"""Unusual Options Standard Model."""

from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class OptionsUnusualQueryParams(QueryParams):
    """Unusual Options Query."""

    symbol: Optional[str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("symbol", "") + " (the underlying symbol)",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str):
        """Convert field to uppercase."""
        return v.upper() if v else None


class OptionsUnusualData(Data):
    """Unusual Options Data."""

    underlying_symbol: Optional[str] = Field(
        description=DATA_DESCRIPTIONS.get("symbol", "") + " (the underlying symbol)",
        default=None,
    )
    contract_symbol: str = Field(description="Contract symbol for the option.")
