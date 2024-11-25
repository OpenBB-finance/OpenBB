"""Crypto Historical Price Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Optional, Set, Union

from dateutil import parser
from pydantic import Field, PositiveFloat, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class CryptoHistoricalQueryParams(QueryParams):
    """Crypto Historical Price Query."""

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " Can use CURR1-CURR2 or CURR1CURR2 format."
    )
    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def validate_symbol(cls, v: Union[str, List[str], Set[str]]):
        """Convert field to uppercase and remove '-'."""
        if isinstance(v, str):
            return v.upper().replace("-", "")
        return ",".join([symbol.upper().replace("-", "") for symbol in list(v)])


class CryptoHistoricalData(Data):
    """Crypto Historical Price Data."""

    date: Union[dateType, datetime] = Field(
        description=DATA_DESCRIPTIONS.get("date", "")
    )
    open: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("open", ""))
    high: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("high", ""))
    low: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("low", ""))
    close: PositiveFloat = Field(description=DATA_DESCRIPTIONS.get("close", ""))
    volume: float = Field(description=DATA_DESCRIPTIONS.get("volume", ""))
    vwap: Optional[PositiveFloat] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("vwap", "")
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return formatted datetime."""
        if ":" in str(v):
            return parser.isoparse(str(v))
        return parser.parse(str(v)).date()
