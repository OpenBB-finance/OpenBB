"""Forecast GDP Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class GdpForecastQueryParams(QueryParams):
    """Forecast GDP Query."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class GdpForecastData(Data):
    """Forecast GDP Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    country: str = Field(description=DATA_DESCRIPTIONS.get("country"))
    value: int | float = Field(
        description="Forecasted GDP value for the country and date."
    )
