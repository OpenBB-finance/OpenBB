"""ETF Historical NAV model."""

from datetime import date as dateType
from typing import List, Set, Union

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
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EtfHistoricalNavData(Data):
    """ETF Historical NAV Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    nav: float = Field(description="The net asset value on the date.")
