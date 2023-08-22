"""FED Data Model."""


from datetime import date as dateType

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS


class PROJECTIONQueryParams(QueryParams):
    """FED Query."""


class PROJECTIONData(Data):
    """Return Treasury Rates Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    range_high: float = Field(description="High projection of rates.")
    central_tendency_high: float = Field(
        description="Central tendency of high projection of rates."
    )
    median: float = Field(description="Median projection of rates.")
    range_midpoint: float = Field(description="Midpoint projection of rates.")
    central_tendency_midpoint: float = Field(
        description="Central tendency of midpoint projection of rates."
    )
    range_low: float = Field(description="Low projection of rates.")
    central_tendency_low: float = Field(
        description="Central tendency of low projection of rates."
    )
