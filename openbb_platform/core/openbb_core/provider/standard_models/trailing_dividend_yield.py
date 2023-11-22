"""Trailing Dividend Yield Standard Model."""


from datetime import date as dateType

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class TrailingDivYieldQueryParams(QueryParams):
    """Trailing Dividend Yield Query."""

    symbol: str = Field(default=None, description=QUERY_DESCRIPTIONS.get("symbol", ""))


class TrailingDivYieldData(Data):
    """Trailing Dividend Yield Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    trailing_dividend_yield: float = Field(description="Trailing dividend yield.")
