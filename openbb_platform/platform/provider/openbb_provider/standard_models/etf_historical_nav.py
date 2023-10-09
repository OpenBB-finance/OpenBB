"""ETF Historical NAV model."""

from datetime import date as dateType
from typing import List, Set, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class EtfHistoricalNavQueryParams(QueryParams):
    """ETF Historical Net Asset Value Query Params."""

    symbol: str = Field(description="The exchange ticker symbol for the ETF.")

    @field_validator("symbol")
    @classmethod
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class EtfHistoricalNavData(Data):
    """ETF Historical Net Asset Value Data."""

    date: dateType = Field(description="The date of the NAV.")
    nav: float = Field(description="The net asset value on the date.")
