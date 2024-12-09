"""Direction Of Trade Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class DirectionOfTradeQueryParams(QueryParams):
    """Direction Of Trade Query."""

    __json_schema_extra__ = {
        "direction": {
            "choices": ["exports", "imports", "balance", "all"],
        },
        "frequency": {
            "choices": ["month", "quarter", "annual"],
        },
    }

    country: Optional[str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("country", "")
        + " None is an equiavlent to 'all'. If 'all' is used, the counterpart field cannot be 'all'.",
    )
    counterpart: Optional[str] = Field(
        default=None,
        description="Counterpart country to the trade. None is an equiavlent to 'all'."
        + " If 'all' is used, the country field cannot be 'all'.",
    )
    direction: Literal["exports", "imports", "balance", "all"] = Field(
        default="balance",
        description="Trade direction. Use 'all' to get all data for this dimension.",
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )
    frequency: Literal["month", "quarter", "annual"] = Field(
        default="month", description=QUERY_DESCRIPTIONS.get("frequency", "")
    )


class DirectionOfTradeData(Data):
    """Direction Of Trade Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    country: str = Field(description=DATA_DESCRIPTIONS.get("country", ""))
    counterpart: str = Field(description="Counterpart country or region to the trade.")
    title: Optional[str] = Field(
        default=None, description="Title corresponding to the symbol."
    )
    value: float = Field(description="Trade value.")
    scale: Optional[str] = Field(default=None, description="Scale of the value.")
