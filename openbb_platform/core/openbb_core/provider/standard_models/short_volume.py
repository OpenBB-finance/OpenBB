"""Short Volume Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class ShortVolumeQueryParams(QueryParams):
    """Short Volume Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))


class ShortVolumeData(Data):
    """Short Volume Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )

    market: Optional[str] = Field(
        default=None,
        description="Reporting Facility ID. N=NYSE TRF, Q=NASDAQ TRF Carteret, B=NASDAQ TRY Chicago, D=FINRA ADF",
    )

    short_volume: Optional[int] = Field(
        default=None,
        description=(
            "Aggregate reported share volume of executed short sale "
            "and short sale exempt trades during regular trading hours"
        ),
    )

    short_exempt_volume: Optional[int] = Field(
        default=None,
        description="Aggregate reported share volume of executed short sale exempt trades during regular trading hours",
    )

    total_volume: Optional[int] = Field(
        default=None,
        description="Aggregate reported share volume of executed trades during regular trading hours",
    )
