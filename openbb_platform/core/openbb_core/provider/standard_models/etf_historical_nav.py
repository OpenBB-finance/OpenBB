"""ETF Historical NAV model."""

from datetime import date as dateType

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class EtfHistoricalNavQueryParams(QueryParams):
    """ETF Historical NAV Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol")
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Convert field to uppercase."""
        return v.upper()


class EtfHistoricalNavData(Data):
    """ETF Historical NAV Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    nav: float = Field(description="The net asset value on the date.")
