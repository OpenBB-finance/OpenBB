"""Historical Stock Splits data model."""


from datetime import date as dateType
from typing import List, Set, Union

from pydantic import Field, validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class HistoricalStockSplitsQueryParams(QueryParams):
    """Historical Stock Splits Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @validator("symbol", pre=True, check_fields=False, always=True)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class HistoricalStockSplitsData(Data):
    """Historical Stock Splits Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    label: str = Field(description="Label of the historical stock splits.")
    numerator: float = Field(description="Numerator of the historical stock splits.")
    denominator: float = Field(
        description="Denominator of the historical stock splits."
    )
