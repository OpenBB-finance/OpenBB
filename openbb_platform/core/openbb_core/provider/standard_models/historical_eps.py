"""Historical EPS Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class HistoricalEpsQueryParams(QueryParams):
    """Historical EPS Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class HistoricalEpsData(Data):
    """Historical EPS Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    eps_actual: int | float | None = Field(
        default=None, description="Actual EPS from the earnings date."
    )
    eps_estimated: int | float | None = Field(
        default=None, description="Estimated EPS for the earnings date."
    )
