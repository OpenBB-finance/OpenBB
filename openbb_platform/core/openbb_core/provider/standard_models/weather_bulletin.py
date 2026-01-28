"""Weather Bulletin Standard Model."""

from datetime import datetime

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class WeatherBulletinQueryParams(QueryParams):
    """Weather Bulletin Query."""

    year: int = Field(
        description="Year of the data. Default is the current year.",
        default=datetime.now().year,
    )
    month: int | None = Field(
        description="Month of the data. If not provided, data for the entire year is returned.",
        ge=1,
        le=12,
        default=None,
    )
    week: int | None = Field(
        description="Numeric week of the data, relative to the month."
        + " If not provided, data for the entire month is returned.",
        ge=1,
        le=5,
        default=None,
    )


class WeatherBulletinData(Data):
    """Weather Bulletin Data."""

    label: str | None = Field(
        default=None,
        description="Label representing the weather bulletin file.",
    )
    value: str | None = Field(
        default=None,
        description="URL to the weather bulletin document.",
    )
