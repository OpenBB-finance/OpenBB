"""PROJECTION Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class PROJECTIONQueryParams(QueryParams):
    """PROJECTION Query."""


class PROJECTIONData(Data):
    """PROJECTION Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    range_high: float | None = Field(description="High projection of rates.")
    central_tendency_high: float | None = Field(
        description="Central tendency of high projection of rates."
    )
    median: float | None = Field(description="Median projection of rates.")
    range_midpoint: float | None = Field(description="Midpoint projection of rates.")
    central_tendency_midpoint: float | None = Field(
        description="Central tendency of midpoint projection of rates."
    )
    range_low: float | None = Field(description="Low projection of rates.")
    central_tendency_low: float | None = Field(
        description="Central tendency of low projection of rates."
    )
