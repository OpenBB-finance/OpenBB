"""GDP data and query params."""
from datetime import date as dateType
from typing import Literal, Optional, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class GDPForecastQueryParams(QueryParams):
    """GDP Forecast query."""

    units: Literal["quarter", "annual"] = Field(
        default="annual",
        description="Units to get nominal GDP in.  Either quarter or annual.",
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )
    type: Literal["nominal", "real"] = Field(
        default="real",
        description="Type of GDP to get forecast of.  Either nominal or real.",
    )


class GDPForecastData(Data):
    """Nominal GDP data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    value: Optional[float] = Field(
        default=None, description="Nominal GDP value on the date."
    )

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(
        cls, date: Union[dateType, Union[str, int]]
    ):  # pylint: disable=E0213
        """Validate value."""
        import re

        if isinstance(date, str):
            if re.match(r"\d{4}-Q[1-4]$", date):
                year, quarter = date.split("-")
                quarter = int(quarter[1])
                month = quarter * 3
                return dateType(int(year), month, 1)
            else:
                raise ValueError("Date string does not match the format YYYY-QN")
        if isinstance(date, int):
            return dateType(date, 12, 31)
        return date
