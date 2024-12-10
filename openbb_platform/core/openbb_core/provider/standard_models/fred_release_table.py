"""FRED Release Table Standard Model."""

from datetime import date as dateType
from typing import Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class ReleaseTableQueryParams(QueryParams):
    """FRED Release Table Query."""

    release_id: str = Field(
        description="The ID of the release." + " Use `fred_search` to find releases.",
    )
    element_id: Optional[str] = Field(
        default=None,
        description="The element ID of a specific table in the release.",
    )
    date: Union[None, dateType, str] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("date", ""),
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def _validate_date(cls, v):
        """Validate the date."""
        # pylint: disable=import-outside-toplevel
        from pandas import to_datetime

        if v is None:
            return None
        if isinstance(v, dateType):
            return v.strftime("%Y-%m-%d")
        new_dates: list = []
        if isinstance(v, str):
            dates = v.split(",")
        if isinstance(v, list):
            dates = v
        for date in dates:
            new_dates.append(to_datetime(date).date().strftime("%Y-%m-%d"))

        return ",".join(new_dates) if new_dates else None


class ReleaseTableData(Data):
    """FRED Release Table Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date", "")
    )
    level: Optional[int] = Field(
        default=None,
        description="The indentation level of the element.",
    )
    element_type: Optional[str] = Field(
        default=None,
        description="The type of the element.",
    )
    line: Optional[int] = Field(
        default=None,
        description="The line number of the element.",
    )
    element_id: Optional[str] = Field(
        default=None,
        description="The element id in the parent/child relationship.",
    )
    parent_id: Optional[str] = Field(
        default=None,
        description="The parent id in the parent/child relationship.",
    )
    children: Optional[str] = Field(
        default=None,
        description="The element_id of each child, as a comma-separated string.",
    )
    symbol: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    name: Optional[str] = Field(
        default=None,
        description="The name of the series.",
    )
    value: Optional[float] = Field(
        default=None,
        description="The reported value of the series.",
    )
