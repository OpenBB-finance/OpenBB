"""ETF Info Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


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
    name: str | None = Field(description="Name of the ETF.")
    issuer: str | None = Field(default=None, description="Issuer of the ETF.")
    domicile: str | None = Field(default=None, description="Domicile of the ETF.")
    website: str | None = Field(default=None, description="Website of the ETF.")
    description: str | None = Field(
        default=None, description="Description of the fund."
    )
    inception_date: dateType | None = Field(
        default=None, description="Inception date of the ETF."
    )
