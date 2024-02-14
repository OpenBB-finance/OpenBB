"""PROJECTION Standard Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


class PROJECTIONQueryParams(QueryParams):
    """PROJECTION Query."""


class PROJECTIONData(Data):
    """PROJECTION Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    range_high: Optional[float] = Field(description="High projection of rates.")
    central_tendency_high: Optional[float] = Field(
        description="Central tendency of high projection of rates."
    )
    median: Optional[float] = Field(description="Median projection of rates.")
    range_midpoint: Optional[float] = Field(description="Midpoint projection of rates.")
    central_tendency_midpoint: Optional[float] = Field(
        description="Central tendency of midpoint projection of rates."
    )
    range_low: Optional[float] = Field(description="Low projection of rates.")
    central_tendency_low: Optional[float] = Field(
        description="Central tendency of low projection of rates."
    )
