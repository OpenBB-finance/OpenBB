"""ETF Info Standard Model."""

from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class EtfInfoQueryParams(QueryParams):
    """ETF Info Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", "") + " (ETF)")

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EtfInfoData(Data):
    """ETF Info Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", "") + " (ETF)")
    name: Optional[str] = Field(description="Name of the ETF.")
    description: Optional[str] = Field(
        default=None, description="Description of the fund."
    )
    inception_date: Optional[str] = Field(description="Inception date of the ETF.")
