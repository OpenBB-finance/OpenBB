"""GDP data and query params."""
from datetime import date as dateType
from typing import Literal, Optional, Union

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class GDPRealQueryParams(QueryParams):
    """Real GDP query."""

    units: Literal["idx", "qoq", "yoy"] = Field(
        default="yoy",
        description="Units to get real GDP in.  Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).)",
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class GDPRealData(Data):
    """Real GDP data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    value: Optional[float] = Field(
        default=None, description="Nominal GDP value on the date."
    )

    @field_validator("date", mode="before")
    @classmethod
    def date_validate(cls, date: Union[dateType, str]):  # pylint: disable=E0213
        """Validate value."""
        if isinstance(date, str):
            year, quarter = date.split("-")
            year = int(year)
            if quarter == "Q1":
                return dateType(year, 3, 31)
            elif quarter == "Q2":
                return dateType(year, 6, 30)
            elif quarter == "Q3":
                return dateType(year, 9, 30)
            elif quarter == "Q4":
                return dateType(year, 12, 31)
        return date
