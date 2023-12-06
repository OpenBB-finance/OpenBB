"""FRED Search Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Optional, Union

from dateutil import parser
from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class SearchQueryParams(QueryParams):
    """FRED Search Query Params."""

    query: Optional[str] = Field(default=None, description="The search word(s).")


class SearchData(Data):
    """FRED Search Data."""

    release_id: Optional[Union[str, int]] = Field(
        default=None,
        description="The release ID for queries.",
    )
    series_id: Optional[str] = Field(
        default=None,
        description="The series ID for the item in the release.",
    )
    name: Optional[str] = Field(
        default=None,
        description="The name of the release.",
    )
    title: Optional[str] = Field(
        default=None,
        description="The title of the series.",
    )
    observation_start: Optional[dateType] = Field(
        default=None, description="The date of the first observation in the series."
    )
    observation_end: Optional[dateType] = Field(
        default=None, description="The date of the last observation in the series."
    )
    frequency: Optional[str] = Field(
        default=None,
        description="The frequency of the data.",
    )
    frequency_short: Optional[str] = Field(
        default=None,
        description="Short form of the data frequency.",
    )
    units: Optional[str] = Field(
        default=None,
        description="The units of the data.",
    )
    units_short: Optional[str] = Field(
        default=None,
        description="Short form of the data units.",
    )
    seasonal_adjustment: Optional[str] = Field(
        default=None,
        description="The seasonal adjustment of the data.",
    )
    seasonal_adjustment_short: Optional[str] = Field(
        default=None,
        description="Short form of the data seasonal adjustment.",
    )
    last_updated: Optional[datetime] = Field(
        default=None,
        description="The datetime of the last update to the data.",
    )
    notes: Optional[str] = Field(
        default=None, description="Description of the release."
    )
    press_release: Optional[bool] = Field(
        description="If the release is a press release.",
        default=None,
    )
    url: Optional[str] = Field(default=None, description="URL to the release.")

    @field_validator("last_updated", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):
        """Validate datetime format."""
        return parser.isoparse(v) if v else None
