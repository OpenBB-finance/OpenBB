"""Futures Expirations Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class FuturesExpirationsQueryParams(QueryParams):
    """Futures Expirations Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """Convert field to uppercase."""
        return v.upper()


class FuturesExpirationsData(Data):
    """Futures Expirations Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    contract_symbol: str = Field(description="Vendor-specific futures contract symbol.")
    expiration: dateType | None = Field(
        default=None,
        description="Contract expiration date, when available from the provider.",
    )
    expiration_month: str | None = Field(
        default=None,
        description="Futures expiration month in YYYY-MM format.",
    )
    exchange: str | None = Field(
        default=None,
        description="Exchange where the contract is listed.",
    )
    name: str | None = Field(
        default=None,
        description="Human-readable contract name.",
    )
