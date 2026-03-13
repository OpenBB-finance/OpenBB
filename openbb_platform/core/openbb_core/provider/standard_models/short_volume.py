"""Short Volume Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class ShortVolumeQueryParams(QueryParams):
    """Short Volume Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol"))


class ShortVolumeData(Data):
    """Short Volume Data."""

    date: dateType | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )

    market: str | None = Field(
        default=None,
        description="Reporting Facility ID. N=NYSE TRF, Q=NASDAQ TRF Carteret, B=NASDAQ TRY Chicago, D=FINRA ADF",
    )

    short_volume: int | None = Field(
        default=None,
        description=(
            "Aggregate reported share volume of executed short sale "
            "and short sale exempt trades during regular trading hours"
        ),
    )

    short_exempt_volume: int | None = Field(
        default=None,
        description="Aggregate reported share volume of executed short sale exempt trades during regular trading hours",
    )

    total_volume: int | None = Field(
        default=None,
        description="Aggregate reported share volume of executed trades during regular trading hours",
    )
