"""Maritime chokepoint transit calls and trade volume estimates time series."""

from datetime import date as dateType
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class MaritimeChokePointVolumeQueryParams(QueryParams):
    """MaritimeChokepointVolume Query."""

    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class MaritimeChokePointVolumeData(Data):
    """MaritimeChokepointVolume Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
