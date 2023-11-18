"""Market Indices Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Optional, Set, Union

from dateutil import parser
from pydantic import Field, StrictFloat, StrictInt, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class MarketIndicesQueryParams(QueryParams):
    """Market Indices Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert symbol to uppercase."""
        if isinstance(v, str):
            return v.upper()
        return ",".join([symbol.upper() for symbol in list(v)])


class MarketIndicesData(Data):
    """Market Indices Data."""

    date: datetime = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    open: StrictFloat = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: StrictFloat = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: StrictFloat = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: StrictFloat = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: Optional[StrictInt] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("volume", "")
    )

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        return parser.isoparse(str(v))
